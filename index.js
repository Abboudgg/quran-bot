const { Client, GatewayIntentBits } = require('discord.js');
const { joinVoiceChannel, createAudioPlayer, createAudioResource, AudioPlayerStatus } = require('@discordjs/voice');
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

// معلومات الروم والسيرفر
const channelId = '1571122362839990324';
const guildId = '1571120459775352925'; 

// رابط بث إذاعي مباشر للقرآن الكريم
const quranStreamUrl = 'https://backup.quran-radio.com:8443/live';

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

    // الانضمام للروم الصوتي مع التأكد من عدم كتم الصوت
    const connection = joinVoiceChannel({
      channelId: channel.id,
      guildId: guildId,
      adapterCreator: guild.voiceAdapterCreator,
      selfDeaf: false,
    });

    const player = createAudioPlayer();
    
    console.log('🔄
