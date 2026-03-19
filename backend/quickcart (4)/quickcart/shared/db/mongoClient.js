const { MongoClient } = require("mongodb");

// BUG: client is module-level singleton, never closed, no reconnect on drop
let client = null;
let db = null;

async function connect() {
  const uri = process.env.MONGO_URI;
  // BUG: if MONGO_URI is undefined, MongoClient will throw uncaught error
  client = new MongoClient(uri);
  await client.connect();
  db = client.db("quickcart");
  return db;
}

async function getDb() {
  if (!db) {
    await connect();
  }
  return db;
}

async function getCollection(name) {
  const database = await getDb();
  return database.collection(name);
}

module.exports = { connect, getDb, getCollection };
