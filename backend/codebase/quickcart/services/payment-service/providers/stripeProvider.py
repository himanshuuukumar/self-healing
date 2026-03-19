import time

class StripeError(Exception):
    pass

def create_payment_intent(amount: int, currency: str) -> dict:
    # Intentional bug: timeout
    # Simulation of a long API call that times out
    time.sleep(31)  
    raise StripeError('Request timed out connecting to https://api.stripe.com')
