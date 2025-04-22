# Subscription Service Backend

A Django-based backend service for handling subscriptions with Stripe payment processing, PDF generation, and email notifications.

## Features

- User email collection through a clean, responsive form
- Integration with Stripe payment gateway
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
- Stripe API keys
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

## Deployment to Render

This project is configured for easy deployment to Render.com with the following files:

- `build.sh`: Contains build commands for Render
- `render.yaml`: Defines the services and databases for Render
- `runtime.txt`: Specifies the Python version

### Steps to deploy on Render:

1. Create a Render account at https://render.com
2. Connect your GitHub repository
3. Click "New" and select "Blueprint" (to use the `render.yaml` configuration)
4. Select your repository and follow the prompts
5. Configure environment variables in the Render dashboard for:
   - Email settings (`EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`)
   - Stripe keys (`STRIPE_PUBLIC_KEY`, `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`)

For more details, see [Render's Python deployment documentation](https://render.com/docs/deploy-django).

## Integration with Your GoDaddy Website

### 1. Deploy the Backend Service

Deploy this Django application to Render.com using the instructions above.

### 2. Update Payment Webhook URLs

After deployment, update the webhook URL in your Stripe dashboard to point to your deployed application's webhook endpoint:

- `https://your-app-name.onrender.com/stripe-webhook/`

### 3. Add Subscription Form to Your GoDaddy Website

Add a simple form on your GoDaddy website that submits to your backend:

```html
<form action="https://your-app-name.onrender.com/" method="post">
  <input type="email" name="email" placeholder="Enter your email" required>
  <button type="submit">Subscribe</button>
</form>
```

Or use a redirect button:

```html
<a href="https://your-app-name.onrender.com/" class="button">Subscribe Now</a>
```

## Customization

### PDF Certificate Template

Edit the template at `templates/subscriptions/pdf_template.html` to customize the generated PDF.

### Email Content

Modify the `send_welcome_email` function in `subscriptions/utils.py` to customize the email content.

### Payment Settings

Adjust price and currency in the Render environment variables or in `subscription_service/settings.py`:

```python
SUBSCRIPTION_PRICE = 1000  # in cents or smallest currency unit
SUBSCRIPTION_CURRENCY = 'usd'
```

## License

This project is licensed under the MIT License - see the LICENSE file for details. 