# Subscription Service Backend

A Django-based backend service for handling subscriptions with Stripe/Razorpay payment processing, PDF generation, and email notifications.

## Features

- User email collection through a clean, responsive form
- Integration with Stripe and Razorpay payment gateways
- Webhook handling for payment verification
- Dynamic PDF generation (certificates/welcome letters)
- Automated email sending with PDF attachments
- Admin panel for managing subscribers
- API endpoint for manual resending of emails

## Setup Instructions

### 1. Clone the repository

```bash
git clone <repository-url>
cd subscription-service
```

### 2. Create and activate a virtual environment

```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Unix/MacOS
python -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment settings

Edit `subscription_service/settings.py` and update the following:

- Email configuration (replace with your SMTP details)
- Stripe API keys (if using Stripe)
- Razorpay API keys (if using Razorpay)
- Other settings as needed

### 5. Apply database migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create a superuser for admin access

```bash
python manage.py createsuperuser
```

### 7. Run the development server

```bash
python manage.py runserver
```

The application will be available at http://127.0.0.1:8000/

## Integration with Your GoDaddy Website

### 1. Deploy the Backend Service

Deploy this Django application to a hosting service that supports Python/Django (Heroku, PythonAnywhere, DigitalOcean, etc.).

### 2. Update Payment Webhook URLs

After deployment, update the webhook URLs in your Stripe/Razorpay dashboard to point to your deployed application's webhook endpoints:

- For Stripe: `https://your-domain.com/stripe-webhook/`
- For Razorpay: `https://your-domain.com/razorpay-callback/`

### 3. Add Subscription Form to Your GoDaddy Website

Add a simple form on your GoDaddy website that submits to your backend:

```html
<form action="https://your-domain.com/" method="post">
  <input type="email" name="email" placeholder="Enter your email" required>
  <button type="submit">Subscribe</button>
</form>
```

Or use a redirect button:

```html
<a href="https://your-domain.com/" class="button">Subscribe Now</a>
```

## Customization

### PDF Certificate Template

Edit the template at `templates/subscriptions/pdf_template.html` to customize the generated PDF.

### Email Content

Modify the `send_welcome_email` function in `subscriptions/utils.py` to customize the email content.

### Payment Settings

Adjust price and currency in `subscription_service/settings.py`:

```python
SUBSCRIPTION_PRICE = 1000  # in cents or smallest currency unit
SUBSCRIPTION_CURRENCY = 'inr'  # or 'usd'
```

## License

This project is licensed under the MIT License - see the LICENSE file for details. 