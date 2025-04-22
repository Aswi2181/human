@echo off
echo Setting up environment for the Subscription Service...

rem Check if .env file exists
if exist .env (
    echo Found existing .env file.
) else (
    echo Creating .env file from template...
    copy .env.example .env
    echo Created .env file. Please edit it with your actual credentials.
)

echo Please enter your Stripe API keys:

rem Prompt for Stripe public key
set /p stripe_public_key="Stripe Public Key (starts with pk_test_): "
if not "%stripe_public_key%"=="" (
    powershell -Command "(Get-Content .env) -replace '^STRIPE_PUBLIC_KEY=.*', 'STRIPE_PUBLIC_KEY=%stripe_public_key%' | Set-Content .env"
)

rem Prompt for Stripe secret key
set /p stripe_secret_key="Stripe Secret Key (starts with sk_test_): "
if not "%stripe_secret_key%"=="" (
    powershell -Command "(Get-Content .env) -replace '^STRIPE_SECRET_KEY=.*', 'STRIPE_SECRET_KEY=%stripe_secret_key%' | Set-Content .env"
)

rem Prompt for Stripe webhook secret
set /p stripe_webhook_secret="Stripe Webhook Secret (starts with whsec_): "
if not "%stripe_webhook_secret%"=="" (
    powershell -Command "(Get-Content .env) -replace '^STRIPE_WEBHOOK_SECRET=.*', 'STRIPE_WEBHOOK_SECRET=%stripe_webhook_secret%' | Set-Content .env"
)

echo Please enter your email settings:

rem Prompt for email address
set /p email_user="Email Address: "
if not "%email_user%"=="" (
    powershell -Command "(Get-Content .env) -replace '^EMAIL_HOST_USER=.*', 'EMAIL_HOST_USER=%email_user%' | Set-Content .env"
)

rem Prompt for email password
set /p email_password="Email App Password: "
if not "%email_password%"=="" (
    powershell -Command "(Get-Content .env) -replace '^EMAIL_HOST_PASSWORD=.*', 'EMAIL_HOST_PASSWORD=%email_password%' | Set-Content .env"
)

echo Environment setup complete!
echo Now you can run your Django server with:
echo python manage.py runserver

pause 