import discord
from discord.ext import commands, tasks
from discord import app_commands
import yt_dlp
import requests
import asyncio
import os
import random
from flask import Flask, render_template_string, request
from threading import Thread

app = Flask('')

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>لوحة تحكم بوت ديسكورد</title>
    <style>
        body { 
            background: linear-gradient(135deg, #450a0a 0%, #1e1b4b 100%); 
            color: #f8fafc; 
            font-family: Tahoma, sans-serif; 
            text-align: center; 
            padding: 30px 20px; 
            margin: 0;
            min-height: 100vh;
        }
        .card { 
            background-color: rgba(30, 41, 59, 0.85); 
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 20px; 
            padding: 25px; 
            max-width: 450px; 
            margin: 0 auto; 
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.6); 
            text-align: right; 
        }
        h1 { color: #38bdf8; font-size: 20px; text-align: center; margin-top: 10px; }
        p { color: #94a3b8; font-size: 14px; }
        .status { display: inline-block; width: 10px; height: 10px; background-color: #22c55e; border-radius: 50%; margin-left: 5px; }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; color: #38bdf8; font-size: 14px; }
        select, input, textarea { width: 100%; padding: 10px; border-radius: 8px; border: 1px solid #334155; background: #0f172a; color: white; box-sizing: border-box; font-family: Tahoma; }
        .btn { display: block; width: 100%; background: #0ea5e9; color: white; border: none; padding: 12px; border-radius: 8px; font-size: 16px; cursor: pointer; font-weight: bold; text-align: center; text-decoration: none; margin-top: 10px; }
        .btn:hover { background: #0284c7; }
        .kick-btn { background: #22c55e; margin-top: 20px; }
        .kick-btn:hover { background: #16a34a; }
        .alert { background: #065f46; color: #6ee7b7; padding: 10px; border-radius: 8px; margin-bottom: 15px; text-align: center; font-size: 14px; }
    </style>
</head>
<body>
    <div class="card">
        <h1>🤖 لوحة تحكم بوت ديسكورد</h1>
        <p style="text-align: center;">حالة البوت: <span class="status"></span> <strong style="color: #22c55e;">متصل ويدير السيرفر 24/7</strong></p>
        <hr style="border: 0; border-top: 1px solid #334155; margin: 15px 0;">
        
        {% if sent %}
        <div class="alert">✅ تم ارسال الرسالة بنجاح إلى ديسكورد!</div>
        {% endif %}

        <form method="POST" action="/send">
            <div class="form-group">
                <label for="channel_id">اختر الروم النصي:</label>
                <select name="channel_id" id="channel_id" required>
                    {% for channel in channels %}
                    <option value="{{ channel.id }}">{{ channel.name }}</option>
                    {% endfor %}
                </select>
            </div>

            <div class="form-group">
                <label for="message">الرسالة المراد إرسالها:</label>
                <textarea name="message" id="message" rows="3" placeholder="اكتب رسالتك هنا..." required>سبحان الله وبحمده، سبحان الله العظيم</textarea>
            </div>

            <button type="submit" class="btn">🚀 إرسال إلى ديسكورد</button>
        </form>

        <a href="https://www.kick.com/cass-sa" target="_blank" class="btn kick-btn">📺 زيارة قناة Kick</a>
    </div>
</body>
</html>
"""

intents = discord.Intents.default()
intents.message_content = True
intents.presences = True
intents.members = True

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        await self.tree.sync()
        print("تم مزامنة أوامر السلاش بنجاح!")

bot = MyBot()

YDL_OPTIONS = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'default_search': 'ytsearch',
    'quiet': True
}

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

ATHKAR_LIST = [
    "سبحان الله وبحمده، سبحان الله العظيم",
    "لا إله إلا أنت سبحانك إني كنت من الظالمين",
    "استغفر الله العظيم واتوب إليه",
    "لا حول ولا قوة إلا بالله العلي العظيم",
    "اللهم صل وسلم على نبينا محمد وعلى آله وصحبه أجمعين"
]

@app.route('/')
def home():
    channels = []
    for guild in bot.guilds:
        for channel in guild.text_channels:
            channels.append({'id': channel.id, 'name': f"{guild.name} ➔ #{channel.name}"})
    return render_template_string(HTML_TEMPLATE, channels=channels, sent=False)

@app.route('/send', methods=['POST'])
def send_message():
    channel_id = int(request.form.get('channel_id'))
    message = request.form.get('message')
    
    future = asyncio.run_coroutine_threadsafe(send_discord_message(channel_id, message), bot.loop)
    try:
        future.result(timeout=5)
    except Exception as e:
        print(f"خطأ في الإرسال: {e}")

    channels = []
    for guild in bot.guilds:
        for channel in guild.text_channels:
            channels.append({'id': channel.id, 'name': f"{guild.name} ➔ #{channel.name}"})
            
    return render_template_string(HTML_TEMPLATE, channels=channels, sent=True)

async def send_discord_message(channel_id, message):
    channel = bot.get_channel(channel_id)
    if channel:
        await channel.send(f"📢 **رسالة من لوحة التحكم:**\n{message}")

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

@bot.event
async def on_ready():
    print(f'تم تشغيل البوت بنجاح: {bot.user.name}')
    activity = discord.Streaming(name="بث مباشر على Kick", url="https://www.kick.com/cass-sa")
    await bot.change_presence(activity=activity)
    if not send_athkar_loop.is_running():
        send_athkar_loop.start()

@tasks.loop(hours=1)
async def send_athkar_loop():
    channel_id = 1571122362839990324  # روم الأذكار المخصص
    channel = bot.get_channel(channel_id)
    if channel:
        athkar = random.choice(ATHKAR_LIST)
        await channel.send(f"🤖 **تذكرة أذكار:**\n{athkar}")

@send_athkar_loop.before_loop
async def before_athkar():
    await bot.wait_until_ready()

@bot.tree.command(name="شغل", description="تشغيل تلاوة القرآن الكريم في الروم الصوتي")
@app_commands.describe(search="اسم السورة أو القارئ")
async def play_quran(interaction: discord.Interaction, search: str):
    if not interaction.user.voice:
        await interaction.response.send_message("❌ يجب أن تدخل إلى روم صوتي أولاً!", ephemeral=True)
        return

    voice_channel = interaction.user.voice.channel
    guild = interaction.guild

    if guild.voice_client is None:
        await voice_channel.connect()
    elif guild.voice_client.channel != voice_channel:
        await guild.voice_client.move_to(voice_channel)

    if guild