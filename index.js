const { Client, GatewayIntentBits, EmbedBuilder } = require('discord.js');
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

// إعداد سرفر الويب عشان يظل البوت شغال 24 ساعة على Render
const express = require("express");
const app = express();

app.get('/', (req, res) => {
  res.send('<body><center><h1>Bot 24H ON!</h1></center></body>');
});

const PORT = process.env.PORT || 2000;
app.listen(PORT, () => {
  console.log(`Your app is listening on port ${PORT}`);
});

const channelId = '1210233988699131946';
const guildId = '1011820688228765828'; 
// رابط مباشر وثابت لإذاعة القرآن الكريم (الشيخ ياسر الدوسري)
const radioUrl = 'https://backup.qurango.net/radio/yasser_aldosari'; 

client.on('ready', () => {
  console.log(`✅ | Logged in as ${client.user.tag}`);
  joinAndPlayQuran(guildId, channelId);
});

async function joinAndPlayQuran(guildId, channelId) {
  try {
    const channel = await client.channels.fetch(channelId);
    if (!channel) return console.log("❌ الروم الصوتي غير موجود!");

    const connection = joinVoiceChannel({
      channelId: channel.id,
      guildId: guildId,
      adapterCreator: channel.guild.voiceAdapterCreator,
    });

    const player = createAudioPlayer();

    // تشغيل الرابط المباشر بدون الحاجة لـ play-dl أو يوتيوب
    const resource = createAudioResource(radioUrl);

    player.play(resource);
    connection.subscribe(player);

    player.on(AudioPlayerStatus.Playing, () => {
      console.log('🎵 Playing Quran Radio (Yasser Al-Dosari)');
    });

    player.on('error', error => {
      console.error(`Audio Error: ${error.message}`);
      // إعادة المحاولة تلقائياً لو انقطع البث
      setTimeout(() => joinAndPlayQuran(guildId, channelId), 5000);
    });

  } catch (error) {
    console.error(`Connection Error: ${error.message}`);
  }
}

client.login(process.env.TOKEN);
