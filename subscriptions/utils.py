import os
from datetime import datetime
from io import BytesIO
from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import get_template
from xhtml2pdf import pisa

def generate_pdf(subscriber):
    """Generate a PDF certificate or welcome letter for the subscriber"""
    template = get_template('subscriptions/pdf_template.html')
    context = {
        'subscriber': subscriber,
        'date': datetime.now().strftime('%d-%m-%Y'),
        'email': subscriber.email,
    }
    
    html = template.render(context)
    result = BytesIO()
    
    # Convert HTML to PDF
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
    
    if not pdf.err:
        # Save PDF to a file
        filename = f"welcome_{subscriber.email.replace('@', '_').replace('.', '_')}.pdf"
        pdf_directory = os.path.join(settings.MEDIA_ROOT, 'pdfs')
        
        # Ensure the directory exists
        os.makedirs(pdf_directory, exist_ok=True)
        
        pdf_path = os.path.join(pdf_directory, filename)
        
        with open(pdf_path, 'wb') as f:
            f.write(result.getvalue())
        
        # Update subscriber record
        subscriber.pdf_generated = True
        subscriber.pdf_path = f'pdfs/{filename}'
        subscriber.save()
        
        return pdf_path
    
    return None

def send_welcome_email(subscriber, pdf_path=None):
    """Send welcome email with PDF attachment to the subscriber"""
    subject = 'Welcome to Our Subscription Service!'
    message = f'Thank you for subscribing to our service, {subscriber.email}!'
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [subscriber.email]
    
    email = EmailMessage(subject, message, from_email, recipient_list)
    
    if pdf_path and os.path.exists(pdf_path):
        with open(pdf_path, 'rb') as f:
            email.attach(os.path.basename(pdf_path), f.read(), 'application/pdf')
    
    sent = email.send()
    
    if sent:
        subscriber.email_sent = True
        subscriber.save()
        
    return sent 