import stripe
import os

# 🔑 Replace with your Stripe Secret Key
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

def create_checkout_session():
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        mode="payment",
        line_items=[
            {
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": "AI Portfolio Pro",
                    },
                    "unit_amount": 5000,  # $50
                },
                "quantity": 1,
            }
        ],
        success_url="https://ai-portfolio-app.onrender.com?success=true",
        cancel_url="https://ai-portfolio-app.onrender.com?canceled=true",
    )

    return session.url