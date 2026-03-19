const express = require("express");
const { notifyOrderConfirmed, notifyShipped, notifyRefund } = require("./controllers/notificationController");
const { connect } = require("../../shared/db/mongoClient");

const app = express();
app.use(express.json());

app.post("/notify/order-confirmed", async (req, res) => {
  const { orderId } = req.body;
  try {
    await notifyOrderConfirmed(orderId);
    res.json({ sent: true });
  } catch (err) {
    console.error("Notification failed:", err);
    res.status(500).json({ error: "Notification failed" });
  }
});

app.post("/notify/shipped", async (req, res) => {
  const { orderId, trackingDetails } = req.body;
  try {
    await notifyShipped(orderId, trackingDetails);
    res.json({ sent: true });
  } catch (err) {
    res.status(500).json({ error: "Notification failed" });
  }
});

app.post("/notify/refund", async (req, res) => {
  const { orderId } = req.body;
  try {
    await notifyRefund(orderId);
    res.json({ sent: true });
  } catch (err) {
    res.status(500).json({ error: "Notification failed" });
  }
});

app.get("/health", (req, res) => res.json({ status: "ok", service: "notification-service" }));

const PORT = process.env.NOTIFICATION_SERVICE_PORT || 3003;

async function start() {
  await connect();
  app.listen(PORT, () => {
    console.log(`Notification service running on port ${PORT}`);
  });
}

start();
module.exports = app;
