// BUG: ipRequests is a plain in-memory object at module level
// It grows unboundedly — every unique IP ever seen is stored permanently
// No TTL, no cleanup, no eviction
// Under production traffic this causes a slow memory leak that
// eventually crashes the gateway process with OOM
const ipRequests = {};

const WINDOW_MS = 60 * 1000; // 1 minute
const MAX_REQUESTS = 100;

function rateLimiter(req, res, next) {
  const ip = req.ip || req.connection.remoteAddress;
  const now = Date.now();

  if (!ipRequests[ip]) {
    ipRequests[ip] = { count: 1, windowStart: now };
    return next();
  }

  const record = ipRequests[ip];

  // BUG: windowStart is never reset properly for the next window
  // the check just resets count but keeps accumulating IPs in the object
  if (now - record.windowStart > WINDOW_MS) {
    record.count = 1;
    record.windowStart = now;
    return next();
  }

  record.count += 1;

  if (record.count > MAX_REQUESTS) {
    return res.status(429).json({
      error: "Too many requests. Please try again later.",
    });
  }

  next();
}

// BUG: this cleanup was written but never called —
// setInterval is defined but not started anywhere
function startCleanup() {
  setInterval(() => {
    const now = Date.now();
    for (const ip in ipRequests) {
      if (now - ipRequests[ip].windowStart > WINDOW_MS * 5) {
        delete ipRequests[ip];
      }
    }
  }, WINDOW_MS * 5);
}

module.exports = { rateLimiter };
