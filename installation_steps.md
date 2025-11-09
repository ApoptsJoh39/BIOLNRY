# Django Marketplace Installation Guide

Follow these steps to set up and run the Django Marketplace with Stripe integration:

## Prerequisites
- Python 3.7 or higher
- pip (Python package manager)
- Git (optional, for version control)

## Installation Steps

1. **Create a virtual environment**:
   ```bash
   python -m venv venv
   ```

2. **Activate the virtual environment**:
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

3. **Install required packages**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Create an environment file**:
   Copy the `.env.example` file to `.env` and update it with your Stripe API keys:
   ```bash
   cp .env.example .env
   ```

5. **Apply migrations**:
   ```bash
   python manage.py migrate
   ```

6. **Create a superuser** (admin account):
   ```bash
   python manage.py createsuperuser
   ```

7. **Install Tailwind CSS dependencies**:
   ```bash
   python manage.py tailwind install
   ```

8. **Build Tailwind CSS**:
   ```bash
   python manage.py tailwind build
   ```

9. **Start the development server**:
   ```bash
   python manage.py runserver
   ```

10. **Set up Stripe webhooks** (for payment processing):
    - Install ngrok: Download from https://ngrok.com/download
    - Start ngrok to create a tunnel to your local server:
      ```bash
      ngrok http 8000
      ```
    - Copy the HTTPS URL provided by ngrok
    - Go to your Stripe Dashboard → Developers → Webhooks
    - Add a new endpoint using the ngrok URL + "/orders/webhook/stripe/"
    - Select the following events to listen for:
      - checkout.session.completed
    - Copy the webhook signing secret to your `.env` file

11. **Access the marketplace**:
    - Admin interface: http://127.0.0.1:8000/admin/
    - Main site: http://127.0.0.1:8000/

## Additional Setup

### Create Categories and Products
1. Log in to the admin interface
2. Create categories first
3. Then add products within those categories

### Test the Checkout Process
1. Add products to your cart
2. Proceed to checkout
3. Use Stripe test card details:
   - Card Number: 4242 4242 4242 4242
   - Expiration: Any future date
   - CVC: Any 3 digits
   - ZIP: Any 5 digits

## User Types
- **Guest**: No account, 10% markup on prices
- **Normal User**: Standard prices
- **Business User**: 25% discount on all products

## Important Notes
- Shipping delivery time is set to 15-30 business days
- Make sure to add your Stripe API keys in the `.env` file
- For production, update the SECRET_KEY and set DEBUG=False