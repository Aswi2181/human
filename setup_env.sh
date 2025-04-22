#!/bin/bash

# Colors for console output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}Setting up environment for the Subscription Service...${NC}"

# Check if .env file exists
if [ -f .env ]; then
    echo -e "${GREEN}Found existing .env file.${NC}"
else
    echo -e "${BLUE}Creating .env file from template...${NC}"
    cp .env.example .env
    echo -e "${GREEN}Created .env file. Please edit it with your actual credentials.${NC}"
fi

echo -e "${BLUE}Please enter your Stripe API keys:${NC}"

# Prompt for Stripe public key
read -p "Stripe Public Key (starts with pk_test_): " stripe_public_key
if [ -n "$stripe_public_key" ]; then
    sed -i "s/^STRIPE_PUBLIC_KEY=.*/STRIPE_PUBLIC_KEY=$stripe_public_key/" .env
fi

# Prompt for Stripe secret key
read -p "Stripe Secret Key (starts with sk_test_): " stripe_secret_key
if [ -n "$stripe_secret_key" ]; then
    sed -i "s/^STRIPE_SECRET_KEY=.*/STRIPE_SECRET_KEY=$stripe_secret_key/" .env
fi

# Prompt for Stripe webhook secret
read -p "Stripe Webhook Secret (starts with whsec_): " stripe_webhook_secret
if [ -n "$stripe_webhook_secret" ]; then
    sed -i "s/^STRIPE_WEBHOOK_SECRET=.*/STRIPE_WEBHOOK_SECRET=$stripe_webhook_secret/" .env
fi

echo -e "${BLUE}Please enter your email settings:${NC}"

# Prompt for email address
read -p "Email Address: " email_user
if [ -n "$email_user" ]; then
    sed -i "s/^EMAIL_HOST_USER=.*/EMAIL_HOST_USER=$email_user/" .env
fi

# Prompt for email password
read -p "Email App Password: " email_password
if [ -n "$email_password" ]; then
    sed -i "s/^EMAIL_HOST_PASSWORD=.*/EMAIL_HOST_PASSWORD=$email_password/" .env
fi

echo -e "${GREEN}Environment setup complete!${NC}"
echo -e "${BLUE}Now you can run your Django server with:${NC}"
echo "python manage.py runserver"

# Make the script executable
chmod +x setup_env.sh 