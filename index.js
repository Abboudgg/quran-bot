const { Client, GatewayIntentBits, EmbedBuilder } = require('discord.js');
const { joinVoiceChannel, createAudioPlayer, createAudioResource, AudioPlayerStatus } = require('@discordjs/voice');
const play = require('play-dl'); 
require('dotenv').config();

const client = new Client({
  intents: [
    GatewayIntentBits.Guilds, 
    GatewayIntentBits.GuildVoiceStates, 
    GatewayIntentBits.GuildMessages, 
    GatewayIntentBits.MessageContent
  ]
});

// إعداد سيرفر الويب لعمل البوت 24 ساعة على Render
const express = require("express");
const app = express();
const PORT = process.env.PORT || 2000;
app.listen(PORT, () => {
  console.log(`Your app is listening on port ${PORT}`);
});
app.get('/', (req, res) => {
  res.send('<body><center><h1>Bot 24H ON!</h1></center></body>');
});

const channelId = '1571122362839990324';
const guildId = '1571120459775352925'; 
const Url = 'https://youtu.be/mQ70kbDmsKA';

client.once('ready', async () => {
  console.log(`✅ | Logged in as ${client.user.tag}`);
  try {
    await joinAndPlayQuran(guildId, channelId);
  } catch (err) {
    console.error("❌ Error in ready voice connection:", err);
  }
});

async function joinAndPlayQuran(guildId, channelId) {
  try {
    const guild = await client.guilds.fetch(guildId);
    const channel = await guild.channels.fetch(channelId);
    
    if (!channel) {
      console.log("❌ Voice channel not found!");
      return;
    }

    const connection = joinVoiceChannel({
      channelId: channel.id,
      guildId: guildId,
      adapterCreator: guild.voiceAdapterCreator,
    });

    const player = createAudioPlayer();
    
    console.log('🔄 Fetching stream from YouTube...');
    const stream = await play.stream(Url);
    const resource = createAudioResource(stream.stream, { inputType: stream.type });

    player.play(resource);
    connection.subscribe(player);

    player.on(AudioPlayerStatus.Playing, () => {
      console.log('▶️ Playing Quran successfully!');
    });

    player.on('error', error => {
      console.error(`⚠️ Audio Player Error: ${error.message}`);
    });

  } catch (error) {
    console.error(`❌ Failed to join or play: ${error.message}`);
  }
}

client.login(process.env.TOKEN);
