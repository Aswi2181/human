# Setting Up Environment Variables in Render.com

Follow these steps to configure your environment variables in Render.com:

## 1. Log in to your Render Dashboard

Go to [https://dashboard.render.com](https://dashboard.render.com) and log in to your account.

## 2. Select Your Web Service

Click on the "subscription-service" web service from your dashboard.

## 3. Navigate to Environment Settings

In the left sidebar, click on "Environment" to access environment variable settings.

## 4. Add Environment Variables

Add the following environment variables by clicking on "Add Environment Variable" for each one:

### Stripe API Keys
- Key: `STRIPE_PUBLIC_KEY` - Value: your Stripe public key (starts with pk_test_ or pk_live_)
- Key: `STRIPE_SECRET_KEY` - Value: your Stripe secret key (starts with sk_test_ or sk_live_)
- Key: `STRIPE_WEBHOOK_SECRET` - Value: your webhook secret (starts with whsec_)

### Email Settings
- Key: `EMAIL_HOST_USER` - Value: your Gmail address
- Key: `EMAIL_HOST_PASSWORD` - Value: your Gmail app password

### Optional Settings
- Key: `SUBSCRIPTION_PRICE` - Value: price in cents (e.g., 1000 for $10.00)
- Key: `SUBSCRIPTION_CURRENCY` - Value: currency code (e.g., usd)

## 5. Save Changes

After adding all environment variables, click the "Save Changes" button.

## 6. Restart Your Service

Scroll to the top of the page and click the "Manual Deploy" button, then select "Clear build cache & deploy" to ensure the new environment variables are applied.

## 7. Verify Configuration

After deployment is complete, check your service logs to ensure everything is working correctly.

## Important Notes

- Keep your API keys and secrets secure.
- Never commit these values to your Git repository.
- For production, use live keys rather than test keys.
- The webhook URL to configure in your Stripe dashboard is: `https://human-x.onrender.com/stripe-webhook/` 