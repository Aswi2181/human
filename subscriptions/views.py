from django.shortcuts import render
import json
import stripe
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .forms import SubscriptionForm
from .models import Subscriber
from .utils import generate_pdf, send_welcome_email
from .mongodb_utils import save_subscriber_to_mongodb, get_subscriber_by_email, update_subscriber_in_mongodb
import os
import logging

logger = logging.getLogger(__name__)

def subscription_form(request):
    """Handle the subscription form submission and redirect to payment"""
    if request.method == 'POST':
        logger.info(f"Received subscription form submission with data: {request.POST}")
        form = SubscriptionForm(request.POST)
        if form.is_valid():
            # Save the subscriber without marking as paid
            subscriber = form.save()
            logger.info(f"Created new subscriber in Django DB with email: {subscriber.email}")
            
            # Save to MongoDB
            mongodb_saved = save_subscriber_to_mongodb(subscriber)
            logger.info(f"MongoDB save result for {subscriber.email}: {'Success' if mongodb_saved else 'Failed'}")
            
            # Redirect to Stripe checkout
            return redirect(reverse('stripe_redirect') + f'?email={subscriber.email}')
        else:
            logger.warning(f"Form validation failed: {form.errors}")
    else:
        form = SubscriptionForm()
    
    return render(request, 'subscriptions/subscription_form.html', {'form': form})

def stripe_redirect(request):
    """Create a Stripe checkout session and redirect the user"""
    email = request.GET.get('email')
    if not email:
        return HttpResponse("Email parameter is required", status=400)
    
    subscriber = get_object_or_404(Subscriber, email=email)
    
    # Initialize Stripe
    stripe.api_key = settings.STRIPE_SECRET_KEY
    
    # Create a checkout session
    checkout_session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[
            {
                'price_data': {
                    'currency': settings.SUBSCRIPTION_CURRENCY,
                    'product_data': {
                        'name': 'Subscription',
                    },
                    'unit_amount': settings.SUBSCRIPTION_PRICE,
                },
                'quantity': 1,
            }
        ],
        mode='payment',
        success_url=request.build_absolute_uri(reverse('thank_you')) + f'?email={email}',
        cancel_url=request.build_absolute_uri(reverse('subscription_form')),
        client_reference_id=subscriber.id,
        customer_email=email,
    )
    
    return redirect(checkout_session.url)

@csrf_exempt
@require_POST
def stripe_webhook(request):
    """Handle Stripe webhook events"""
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
        
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            
            # Get the subscriber from client_reference_id
            subscriber_id = session.get('client_reference_id')
            if subscriber_id:
                subscriber = get_object_or_404(Subscriber, id=subscriber_id)
                
                # Update subscriber status
                subscriber.is_paid = True
                subscriber.payment_id = session.get('payment_intent')
                subscriber.save()
                
                # Update in MongoDB
                update_subscriber_in_mongodb(subscriber.email, {
                    'is_paid': True,
                    'payment_id': session.get('payment_intent')
                })
                
                # Process the successful payment (generate PDF and send email)
                process_successful_payment(subscriber)
            
        return HttpResponse(status=200)
    
    except Exception as e:
        logger.error(f"Stripe webhook error: {str(e)}")
        return HttpResponse(status=400)

def process_successful_payment(subscriber):
    """Process actions after successful payment"""
    try:
        # Generate PDF
        pdf_path = generate_pdf(subscriber)
        
        # Update MongoDB with PDF info
        if pdf_path:
            update_subscriber_in_mongodb(subscriber.email, {
                'pdf_generated': True,
                'pdf_path': subscriber.pdf_path
            })
            
            # Send email with PDF
            email_sent = send_welcome_email(subscriber, pdf_path)
            
            # Update MongoDB with email status
            if email_sent:
                update_subscriber_in_mongodb(subscriber.email, {
                    'email_sent': True
                })
            
        return True
    except Exception as e:
        logger.error(f"Error processing payment: {str(e)}")
        return False

def thank_you(request):
    """Render thank you page after successful payment"""
    email = request.GET.get('email')
    context = {'email': email} if email else {}
    return render(request, 'subscriptions/thank_you.html', context)

def resend_email(request, subscriber_id):
    """API endpoint to resend PDF email manually"""
    if not request.user.is_staff:
        return HttpResponse("Unauthorized", status=403)
    
    subscriber = get_object_or_404(Subscriber, id=subscriber_id)
    
    if not subscriber.is_paid:
        return HttpResponse("Subscriber has not made a payment", status=400)
    
    if subscriber.pdf_path:
        pdf_path = os.path.join(settings.MEDIA_ROOT, subscriber.pdf_path)
        sent = send_welcome_email(subscriber, pdf_path)
        
        # Update MongoDB if email was sent
        if sent:
            update_subscriber_in_mongodb(subscriber.email, {
                'email_sent': True
            })
            return HttpResponse("Email resent successfully")
        else:
            return HttpResponse("Failed to send email", status=500)
    else:
        # Generate PDF if it doesn't exist
        pdf_path = generate_pdf(subscriber)
        if pdf_path:
            # Update MongoDB with PDF info
            update_subscriber_in_mongodb(subscriber.email, {
                'pdf_generated': True,
                'pdf_path': subscriber.pdf_path
            })
            
            # Send email
            sent = send_welcome_email(subscriber, pdf_path)
            
            # Update MongoDB with email status
            if sent:
                update_subscriber_in_mongodb(subscriber.email, {
                    'email_sent': True
                })
                return HttpResponse("Email sent successfully")
            else:
                return HttpResponse("Failed to send email", status=500)
        else:
            return HttpResponse("Failed to generate PDF", status=500)
