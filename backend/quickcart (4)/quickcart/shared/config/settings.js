module.exports = {
  mongoUri: process.env.MONGO_URI,
  jwtSecret: process.env.JWT_SECRET,
  port: process.env.PORT || 3000,
  appEnv: process.env.APP_ENV || "development",
  sendgridKey: process.env.SENDGRID_API_KEY,
  twilioSid: process.env.TWILIO_SID,
  twilioToken: process.env.TWILIO_TOKEN,
};
