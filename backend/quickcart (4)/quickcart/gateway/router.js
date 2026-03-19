const express = require("express");
const { createProxyMiddleware } = require("http-proxy-middleware");
const { tokenValidator } = require("../services/auth-service/middleware/tokenValidator");

const router = express.Router();

const AUTH_SERVICE = process.env.AUTH_SERVICE_URL || "http://localhost:3001";
const ORDER_SERVICE = process.env.ORDER_SERVICE_URL || "http://localhost:8001";
const PAYMENT_SERVICE = process.env.PAYMENT_SERVICE_URL || "http://localhost:8002";
const NOTIFICATION_SERVICE = process.env.NOTIFICATION_SERVICE_URL || "http://localhost:3003";
const DELIVERY_SERVICE = process.env.DELIVERY_SERVICE_URL || "http://localhost:8003";

// Public routes — no auth required
router.use("/auth", createProxyMiddleware({ target: AUTH_SERVICE, changeOrigin: true }));

// Protected routes — require valid JWT
router.use("/orders", tokenValidator, createProxyMiddleware({ target: ORDER_SERVICE, changeOrigin: true }));
router.use("/payments", tokenValidator, createProxyMiddleware({ target: PAYMENT_SERVICE, changeOrigin: true }));
router.use("/delivery", tokenValidator, createProxyMiddleware({ target: DELIVERY_SERVICE, changeOrigin: true }));

// Internal route — notifications triggered server-side only
router.use("/notify", createProxyMiddleware({ target: NOTIFICATION_SERVICE, changeOrigin: true }));

module.exports = router;
