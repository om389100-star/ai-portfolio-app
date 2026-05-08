import stripe
import os

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

def create_checkout_session():

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        mode="subscription",

        line_items=[
            {
                "price": "price_XXXXXXXXXXXX",
                "quantity": 1,
            }
        ],

        success_url="https://ai-portfolio-app.onrender.com?success=true",
        cancel_url="https://ai-portfolio-app.onrender.com?canceled=true",
    )

    return session.url