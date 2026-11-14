const { Client, GatewayIntentBits, REST, Routes, SlashCommandBuilder } = require('discord.js');
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

// إعداد سيرفر الويب لضمان عمل البوت 24 ساعة على Render
const express = require("express");
const app = express();

app.get('/', (req, res) => {
  res.send('<body><center><h1>Bot 24H ON!</h1></center></body>');
});

const PORT = process.env.PORT || 2000;
app.listen(PORT, () => {
  console.log(`Your app is listening on port ${PORT}`);
});

const radioUrl = 'https://backup.qurango.net/radio/yasser_aldosari'; 

const ATHKAR = [
  "✨ **سبحان الله وبحمده، سبحان الله العظيم**",
  "✨ **لا إله إلا أنت سبحانك إني كنت من الظالمين**",
  "✨ **استغفر الله العظيم واتوب إليه**",
  "✨ **لا حول ولا قوة إلا بالله العلي العظيم**",
  "✨ **اللهم صل وسلم على نبينا محمد**",
  "✨ **لا إله إلا الله وحدَهُ لا شريك له، له الملك وله الحمد وهو على كل شيء قدير**"
];

// تسجيل الأوامر (Slash Commands)
const commands = [
  new SlashCommandBuilder().setName('اذاعة').setDescription('تشغيل إذاعة القرآن الكريم (الشيخ ياسر الدوسري) في رومك الصوتي'),
  new SlashCommandBuilder().setName('اذكار').setDescription('إرسال ذكر مبارك في الشات'),
  new SlashCommandBuilder().setName('اطلع').setDescription('إيقاف البث والخروج من الروم الصوتي')
].map(command => command.toJSON());

client.once('ready', async () => {
  console.log(`✅ | Logged in as ${client.user.tag}`);
  
  // تسجيل الأوامر في سيرفرات البوت تلقائياً
  const rest = new REST({ version: '10' }).setToken(process.env.TOKEN);
  try {
    console.log('Started refreshing application (/) commands.');
    await rest.put(Routes.applicationCommands(client.user.id), { body: commands });
    console.log('Successfully reloaded application (/) commands.');
  } catch (error) {
    console.error(error);
  }
});

// التفاعل مع الأوامر
client.on('interactionCreate', async interaction => {
  if (!interaction.isChatInputCommand()) return;

  const { commandName } = interaction;

  if (commandName === 'اذاعة') {
    if (!interaction.member.voice.channel) {
      return interaction.reply({ content: '❌ يجب الدخول لروم صوتي أولاً!', ephemeral: true });
    }

    await interaction.deferReply();

    try {
      const channel = interaction.member.voice.channel;
      const connection = joinVoiceChannel({
        channelId: channel.id,
        guildId: interaction.guild.id,
        adapterCreator: interaction.guild.voiceAdapterCreator,
      });

      const player = createAudioPlayer();
      const resource = createAudioResource(radioUrl);

      player.play(resource);
      connection.subscribe(player);

      player.on(AudioPlayerStatus.Playing, () => {
        console.log('🎵 Playing Quran Radio');
      });

      player.on('error', error => {
        console.error(`Audio Error: ${error.message}`);
      });

      await interaction.editReply('✅ **تم تشغيل إذاعة القرآن الكريم (الشيخ ياسر الدوسري) بنجاح!** 📻🎧');
    } catch (error) {
      console.error(error);
      await interaction.editReply('❌ حدث خطأ أثناء تشغيل الإذاعة.');
    }
  }

  else if (commandName === 'اذكار') {
    const randomThikr = ATHKAR[Math.floor(Math.random() * ATHKAR.length)];
    await interaction.reply({ content: `📖 **ذكر من البوت:**\n${randomThikr}` });
  }

  else if (commandName === 'اطلع') {
    const guildConnection = require('@discordjs/voice').getVoiceConnection(interaction.guild.id);
    if (guildConnection) {
      guildConnection.destroy();
      await interaction.reply({ content: '👋 تم إيقاف البث والخروج من الروم بنجاح.' });
    } else {
      await interaction.reply({ content: '❌ البوت مو بروم صوتي أصلاً.', ephemeral: true });
    }
  }
});

client.login(process.env.TOKEN);
