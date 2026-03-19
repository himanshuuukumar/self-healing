const { verifyToken } = require("../utils/jwtHelper");

function tokenValidator(req, res, next) {
  // BUG: assumes Authorization header always exists
  // If request has no Authorization header, split() is called on undefined → crash
  const token = req.headers.authorization.split(" ")[1];

  const decoded = verifyToken(token);

  // BUG: if verifyToken throws (expired/malformed token), decoded is never set
  // and the error propagates as an unhandled exception
  req.user = decoded;
  next();
}

function optionalTokenValidator(req, res, next) {
  const authHeader = req.headers.authorization;
  if (!authHeader) {
    next();
    return;
  }

  const token = authHeader.split(" ")[1];
  // BUG: decoded could be null from decodeWithoutVerify
  // and req.user.userId access downstream will crash
  const { decodeWithoutVerify } = require("../utils/jwtHelper");
  req.user = decodeWithoutVerify(token);
  next();
}

module.exports = { tokenValidator, optionalTokenValidator };
