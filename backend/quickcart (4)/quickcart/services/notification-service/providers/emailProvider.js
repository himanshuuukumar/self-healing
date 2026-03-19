const sgMail = require("@sendgrid/mail");
const { sendgridKey } = require("../../../shared/config/settings");

sgMail.setApiKey(sendgridKey);

async function sendOrderConfirmation(to, orderDetails) {
  const msg = {
    to,
    from: "noreply@quickcart.in",
    subject: `Order Confirmed — #${orderDetails.orderId}`,
    html: `
      <h2>Your order has been confirmed!</h2>
      <p>Order ID: ${orderDetails.orderId}</p>
      <p>Amount: ₹${orderDetails.amount}</p>
      <p>Estimated delivery: ${orderDetails.estimatedDelivery}</p>
    `,
  };

  // BUG: sgMail.send() returns a promise
  // it is NOT awaited here — if SendGrid fails (bad API key, rate limit),
  // the rejection is completely unhandled and silently swallowed
  // Node will emit UnhandledPromiseRejectionWarning
  sgMail.send(msg);
}

async function sendShippingUpdate(to, trackingDetails) {
  const msg = {
    to,
    from: "noreply@quickcart.in",
    subject: `Your order is on the way!`,
    html: `
      <h2>Order Shipped</h2>
      <p>Tracking ID: ${trackingDetails.trackingId}</p>
      <p>Carrier: ${trackingDetails.carrier}</p>
      <a href="${trackingDetails.trackingUrl}">Track your order</a>
    `,
  };

  await sgMail.send(msg);
}

async function sendRefundNotification(to, refundDetails) {
  const msg = {
    to,
    from: "noreply@quickcart.in",
    subject: `Refund Processed — ₹${refundDetails.amount}`,
    html: `
      <h2>Refund Initiated</h2>
      <p>Amount: ₹${refundDetails.amount}</p>
      <p>Expected in 5-7 business days</p>
    `,
  };

  // BUG: same unhandled promise — fire and forget pattern
  // no way to know if the email actually sent
  sgMail.send(msg);
}

module.exports = {
  sendOrderConfirmation,
  sendShippingUpdate,
  sendRefundNotification,
};
