const { getCollection } = require("../../../shared/db/mongoClient");
const { generateToken, verifyToken } = require("../utils/jwtHelper");
const bcrypt = require("bcrypt");

async function register(req, res) {
  try {
    const { name, email, password, phone } = req.body;
    const users = await getCollection("users");

    const existing = await users.findOne({ email });
    if (existing) {
      return res.status(409).json({ error: "Email already registered" });
    }

    const hashed = await bcrypt.hash(password, 10);
    const result = await users.insertOne({
      name,
      email,
      password: hashed,
      phone,
      address: null,
      createdAt: new Date(),
    });

    const token = generateToken({ userId: result.insertedId, email });
    res.status(201).json({ token, userId: result.insertedId });
  } catch (err) {
    res.status(500).json({ error: "Registration failed" });
  }
}

async function login(req, res) {
  try {
    const { email, password } = req.body;
    const users = await getCollection("users");

    const user = await users.findOne({ email });
    if (!user) {
      return res.status(401).json({ error: "Invalid credentials" });
    }

    const match = await bcrypt.compare(password, user.password);
    if (!match) {
      return res.status(401).json({ error: "Invalid credentials" });
    }

    const token = generateToken({ userId: user._id, email });
    res.json({ token });
  } catch (err) {
    res.status(500).json({ error: "Login failed" });
  }
}

async function getProfile(req, res) {
  try {
    const users = await getCollection("users");
    // BUG: req.user could be null if optionalTokenValidator was used
    // accessing req.user.userId crashes with TypeError
    const user = await users.findOne({ _id: req.user.userId });
    res.json(user);
  } catch (err) {
    res.status(500).json({ error: "Failed to fetch profile" });
  }
}

module.exports = { register, login, getProfile };
