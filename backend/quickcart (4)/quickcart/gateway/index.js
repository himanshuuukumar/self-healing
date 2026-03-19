const express = require("express");
const cors = require("cors");
const router = require("./router");
const { rateLimiter } = require("./middleware/rateLimiter");

const app = express();

app.use(cors());
app.use(express.json());
app.use(rateLimiter);
app.use("/api/v1", router);

app.get("/health", (req, res) => res.json({ status: "ok", service: "gateway" }));

const PORT = process.env.GATEWAY_PORT || 3000;
app.listen(PORT, () => {
  console.log(`API Gateway running on port ${PORT}`);
});

module.exports = app;
