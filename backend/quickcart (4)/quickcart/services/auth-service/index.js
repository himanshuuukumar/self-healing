const express = require("express");
const { register, login, getProfile } = require("./controllers/authController");
const { refreshSession } = require("./controllers/sessionController");
const { tokenValidator } = require("./middleware/tokenValidator");
const { connect } = require("../../shared/db/mongoClient");

const app = express();
app.use(express.json());

app.post("/auth/register", register);
app.post("/auth/login", login);
app.get("/auth/profile", tokenValidator, getProfile);
app.post("/auth/session/refresh", refreshSession);

const PORT = process.env.AUTH_SERVICE_PORT || 3001;

async function start() {
  await connect();
  app.listen(PORT, () => {
    console.log(`Auth service running on port ${PORT}`);
  });
}

start();
module.exports = app;
