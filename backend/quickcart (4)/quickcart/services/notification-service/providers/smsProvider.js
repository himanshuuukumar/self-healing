const twilio = require("twilio");
const { twilioSid, twilioToken } = require("../../../shared/config/settings");

// BUG: if twilioSid or twilioToken are undefined, Twilio client throws on init
// This module-level crash takes down the entire notification service
const client = twilio(twilioSid, twilioToken);

async function sendOTP(phone, otp) {
  try {
    const message = await client.messages.create({
      body: `Your QuickCart OTP is: ${otp}. Valid for 10 minutes.`,
      from: process.env.TWILIO_PHONE,
      to: phone,
    });
    return message.sid;
  } catch (err) {
    console.error(`SMS OTP failed for ${phone}:`, err.message);
    throw err;
  }
}

async function sendOrderSMS(phone, orderDetails) {
  try {
    const message = await client.messages.create({
      body: `QuickCart: Order #${orderDetails.orderId} confirmed. Amount: ₹${orderDetails.amount}. Track at quickcart.in/track`,
      from: process.env.TWILIO_PHONE,
      to: phone,
    });
    return message.sid;
  } catch (err) {
    console.error(`Order SMS failed:`, err.message);
    throw err;
  }
}

async function sendDeliverySMS(phone, trackingId) {
  const message = await client.messages.create({
    body: `QuickCart: Your order has been shipped! Tracking ID: ${trackingId}`,
    from: process.env.TWILIO_PHONE,
    to: phone,
  });
  return message.sid;
}

module.exports = { sendOTP, sendOrderSMS, sendDeliverySMS };
