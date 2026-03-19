const { getCollection } = require("../../../shared/db/mongoClient");
const { verifyToken, generateToken } = require("../utils/jwtHelper");

async function createSession(userId) {
  const sessions = await getCollection("sessions");
  const session = {
    userId,
    createdAt: new Date(),
    expiresAt: new Date(Date.now() + 24 * 60 * 60 * 1000),
    active: true,
  };
  const result = await sessions.insertOne(session);
  return result.insertedId.toString();
}

async function validateSession(sessionId) {
  const sessions = await getCollection("sessions");
  const session = await sessions.findOne({ _id: sessionId });

  // BUG: session could be null — no null check before accessing session.expiresAt
  if (session.expiresAt < new Date()) {
    return null;
  }
  return session;
}

async function refreshSession(req, res) {
  const { sessionId } = req.body;

  // BUG: validateSession is async and returns a promise
  // It is NOT awaited here — promise rejection is completely unhandled
  // if validateSession throws, the error silently disappears
  const session = validateSession(sessionId);

  if (!session) {
    return res.status(401).json({ error: "Session expired" });
  }

  const newToken = generateToken({ userId: session.userId });
  res.json({ token: newToken });
}

async function invalidateSession(sessionId) {
  const sessions = await getCollection("sessions");
  await sessions.updateOne(
    { _id: sessionId },
    { $set: { active: false, invalidatedAt: new Date() } }
  );
}

module.exports = { createSession, validateSession, refreshSession, invalidateSession };
