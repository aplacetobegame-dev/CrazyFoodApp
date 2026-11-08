const express = require("express");
const path = require("node:path");
const { createRequestHandler } = require("expo-server/adapter/express");

const port = Number(process.env.PORT || 8080);
const dist = path.join(__dirname, "dist");
const app = express();

app.use(express.static(path.join(dist, "client")));
app.use(createRequestHandler({ build: path.join(dist, "server") }));

app.listen(port, () => {
  console.log(JSON.stringify({ event: "web_listening", port }));
});
