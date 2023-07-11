//Using elevenlabs api to generate audio for the latest response
const fetch = require("node-fetch");
const fs = require("fs");

const url =
  "https://api.elevenlabs.io/v1/text-to-speech/pTL1YWXSHGzMbeBqSp5z/stream";

const headers = {
  Accept: "audio/mpeg",
  "Content-Type": "application/json",
  "xi-api-key": "f847bcf3852b9864940d67cdb2ff7ccc",
};

const data = {
  text: "hi how are you",
  model_id: "eleven_monolingual_v1",
  voice_settings: {
    stability: 0.5,
    similarity_boost: 0.5,
  },
};

fetch(url, {
  method: "POST",
  headers: headers,
  body: JSON.stringify(data),
  responseType: "stream",
})
  .then((response) => {
    const fileStream = fs.createWriteStream("output.mp3");
    response.body.pipe(fileStream);

    response.body.on("error", (err) => {
      console.error("Error receiving response:", err);
    });

    fileStream.on("finish", () => {
      console.log("Audio file saved!");
    });
  })
  .catch((error) => {
    console.error("Error:", error);
  });
