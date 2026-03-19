const { getCollection } = require("../../../shared/db/mongoClient");
const { sendOrderConfirmation, sendShippingUpdate, sendRefundNotification } = require("../providers/emailProvider");
const { sendOrderSMS, sendDeliverySMS } = require("../providers/smsProvider");

async function getUserContactInfo(userId) {
  const users = await getCollection("users");
  return users.findOne({ _id: userId });
}

async function notifyOrderConfirmed(orderId) {
  const orders = await getCollection("orders");
  const order = await orders.findOne({ _id: orderId });

  if (!order) {
    console.error(`notifyOrderConfirmed: order ${orderId} not found`);
    return;
  }

  const user = await getUserContactInfo(order.userId);

  // BUG: user could be null if userId is stale/deleted
  // accessing user.email and user.phone crashes with TypeError
  const email = user.email;
  const phone = user.phone;

  const orderDetails = {
    orderId,
    amount: order.finalAmount,
    estimatedDelivery: "3-5 business days",
  };

  // BUG: sendOrderConfirmation internally does NOT await sgMail.send()
  // so even awaiting here, a SendGrid failure will be an unhandled rejection
  await sendOrderConfirmation(email, orderDetails);

  // BUG: sendOrderSMS is awaited but if Twilio fails,
  // the error propagates and crashes the entire notification flow
  // without sending the email notification status back
  await sendOrderSMS(phone, orderDetails);
}

async function notifyShipped(orderId, trackingDetails) {
  const orders = await getCollection("orders");
  const order = await orders.findOne({ _id: orderId });
  const user = await getUserContactInfo(order.userId);

  await sendShippingUpdate(user.email, trackingDetails);

  // BUG: not awaited — if Twilio throws, unhandled promise rejection
  sendDeliverySMS(user.phone, trackingDetails.trackingId);
}

async function notifyRefund(orderId) {
  const orders = await getCollection("orders");
  const order = await orders.findOne({ _id: orderId });
  const user = await getUserContactInfo(order.userId);

  const refundDetails = {
    amount: order.finalAmount,
    orderId,
  };

  // BUG: sendRefundNotification internally doesn't await sgMail
  // so any failure here is silent — user never knows their refund was processed
  await sendRefundNotification(user.email, refundDetails);
}

module.exports = { notifyOrderConfirmed, notifyShipped, notifyRefund };
