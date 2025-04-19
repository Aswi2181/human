from django.shortcuts import render
import json
import stripe
import razorpay
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
        form = SubscriptionForm(request.POST)
        if form.is_valid():
            # Save the subscriber without marking as paid
            subscriber = form.save()
            
            # Save to MongoDB
            save_subscriber_to_mongodb(subscriber)
            
            # Choose payment gateway based on configuration or user preference
            payment_gateway = request.POST.get('payment_gateway', 'stripe')
            
            if payment_gateway == 'stripe':
                # Redirect to Stripe checkout
                return redirect(reverse('stripe_redirect') + f'?email={subscriber.email}')
            else:
                # Redirect to Razorpay checkout
                return redirect(reverse('razorpay_redirect') + f'?email={subscriber.email}')
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

def razorpay_redirect(request):
    """Create a Razorpay order and render the payment form"""
    email = request.GET.get('email')
    if not email:
        return HttpResponse("Email parameter is required", status=400)
    
    subscriber = get_object_or_404(Subscriber, email=email)
    
    # Initialize Razorpay client
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    
    # Create an order
    data = {
        "amount": settings.SUBSCRIPTION_PRICE,
        "currency": settings.SUBSCRIPTION_CURRENCY,
        "receipt": f"receipt_{subscriber.id}",
        "notes": {
            "email": email,
            "subscriber_id": subscriber.id
        }
    }
    
    order = client.order.create(data=data)
    
    context = {
        'order_id': order['id'],
        'amount': order['amount'],
        'currency': order['currency'],
        'key_id': settings.RAZORPAY_KEY_ID,
        'subscriber': subscriber,
        'callback_url': request.build_absolute_uri(reverse('razorpay_callback')),
    }
    
    return render(request, 'subscriptions/razorpay_checkout.html', context)

@csrf_exempt
def razorpay_callback(request):
    """Handle Razorpay payment callback"""
    if request.method == 'POST':
        try:
            payment_id = request.POST.get('razorpay_payment_id', '')
            order_id = request.POST.get('razorpay_order_id', '')
            signature = request.POST.get('razorpay_signature', '')
            
            # Initialize Razorpay client
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            
            # Verify signature
            params_dict = {
                'razorpay_payment_id': payment_id,
                'razorpay_order_id': order_id,
                'razorpay_signature': signature
            }
            
            client.utility.verify_payment_signature(params_dict)
            
            # Get payment details
            payment = client.payment.fetch(payment_id)
            
            # Get subscriber from notes
            subscriber_id = payment.get('notes', {}).get('subscriber_id')
            email = payment.get('notes', {}).get('email')
            
            if subscriber_id:
                subscriber = get_object_or_404(Subscriber, id=subscriber_id)
            elif email:
                subscriber = get_object_or_404(Subscriber, email=email)
            else:
                return HttpResponse("Could not identify subscriber", status=400)
            
            # Update subscriber status
            subscriber.is_paid = True
            subscriber.payment_id = payment_id
            subscriber.save()
            
            # Update in MongoDB
            update_subscriber_in_mongodb(subscriber.email, {
                'is_paid': True,
                'payment_id': payment_id
            })
            
            # Process the successful payment (generate PDF and send email)
            process_successful_payment(subscriber)
            
            return redirect(reverse('thank_you') + f'?email={subscriber.email}')
        
        except Exception as e:
            logger.error(f"Razorpay callback error: {str(e)}")
            return HttpResponse(f"Error: {str(e)}", status=400)
    
    return HttpResponse("Invalid request method", status=400)

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
