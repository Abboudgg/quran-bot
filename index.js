const { Client, GatewayIntentBits } = require('discord.js');
const { joinVoiceChannel, createAudioPlayer, createAudioResource, AudioPlayerStatus } = require('@discordjs/voice');
require('dotenv').config();

// حماية البوت من الانهيار المفاجئ إذا حصل خطأ غير متوقع
process.on('unhandledRejection', error => {
  console.error('Unhandled promise rejection:', error);
});

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

app.get('/', (req, res) => {
  res.send('<body><center><h1>Bot 24H ON!</h1></center></body>');
});

app.listen(PORT, () => {
  console.log(`Your app is listening on port ${PORT}`);
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

    const connection = joinVoiceChannel({
      channelId: channel.id,
      guildId: guildId,
      adapterCreator: guild.voiceAdapterCreator,
      selfDeaf: false,
    });

    const player = createAudioPlayer();
    
    console.log('🔄 Connecting to Quran Radio Stream...');
    const resource = createAudioResource(quranStreamUrl);

    player.play(resource);
    connection.subscribe(player);

    player.on(AudioPlayerStatus.Playing, () => {
      console.log('▶️ Playing Quran Radio successfully 24/7!');
    });

    player.on('error', error => {
      console.error(`⚠️ Audio Player Error: ${error.message}`);
    });

    player.on(AudioPlayerStatus.Idle, () => {
      console.log('🔄 Restarting stream...');
      setTimeout(() => {
        try {
          player.play(createAudioResource(quranStreamUrl));
        } catch (e) {
          console.error("Error restarting stream:", e);
        }
      }, 5000);
    });

  } catch (error) {
    console.error(`❌ Failed to join or play: ${error.message}`);
  }
}

if (!process.env.TOKEN) {
  console.error("❌ ERROR: BOT TOKEN IS MISSING IN ENVIRONMENT VARIABLES!");
} else {
  client.login(process.env.TOKEN);
}