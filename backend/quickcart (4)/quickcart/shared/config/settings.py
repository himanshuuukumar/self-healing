import os

# BUG: os.environ[] will raise KeyError if variable is missing
# Should use os.environ.get() with fallback values
DATABASE_URL = os.environ["MONGO_URI"]
JWT_SECRET = os.environ["JWT_SECRET"]
STRIPE_API_KEY = os.environ["STRIPE_API_KEY"]
RAZORPAY_KEY = os.environ["RAZORPAY_KEY"]
RAZORPAY_SECRET = os.environ["RAZORPAY_SECRET"]
SHIPROCKET_EMAIL = os.environ["SHIPROCKET_EMAIL"]
SHIPROCKET_PASSWORD = os.environ["SHIPROCKET_PASSWORD"]
SENDGRID_API_KEY = os.environ["SENDGRID_API_KEY"]
TWILIO_SID = os.environ["TWILIO_SID"]
TWILIO_TOKEN = os.environ["TWILIO_TOKEN"]

APP_ENV = os.environ.get("APP_ENV", "development")
PORT = int(os.environ.get("PORT", 8000))
DEBUG = APP_ENV == "development"
