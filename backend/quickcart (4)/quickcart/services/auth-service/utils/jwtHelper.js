const jwt = require("jsonwebtoken");
const { jwtSecret } = require("../../shared/config/settings");

function generateToken(payload) {
  return jwt.sign(payload, jwtSecret, { expiresIn: "24h" });
}

function verifyToken(token) {
  // BUG: jwt.verify throws on malformed/expired token and it is not caught here
  // Caller assumes this always returns a payload object
  // If token is tampered or expired, this crashes the entire request handler
  const decoded = jwt.verify(token, jwtSecret);
  return decoded;
}

function decodeWithoutVerify(token) {
  // BUG: jwt.decode returns null on malformed token
  // Caller accesses decoded.userId without null check
  const decoded = jwt.decode(token);
  return decoded;
}

function refreshToken(oldToken) {
  const payload = verifyToken(oldToken);
  // BUG: if verifyToken throws, this line is never reached
  // but the error bubbles up uncaught to express error handler which is not set up
  const { iat, exp, ...rest } = payload;
  return generateToken(rest);
}

module.exports = { generateToken, verifyToken, decodeWithoutVerify, refreshToken };
