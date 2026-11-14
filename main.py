import discord
from discord.ext import commands, tasks
import yt_dlp
import requests
import asyncio
import os
import random
from flask import Flask, render_template_string, request, redirect, url_for
from threading import Thread

app = Flask('')

# حافظنا على التصميم الفخم وضفنا خانة لاختيار الروم والرسالة
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>لوحة تحكم بوت ديسكورد</title>
    <style>
        body { background-color: #0f172a; color: #f8fafc; font-family: Tahoma, sans-serif; text-align: center; padding: 30px 20px; }
        .card { background-color: #1e293b; border-radius: 15px; padding: 25px; max-width: 450px; margin: 0 auto; box-shadow: 0 4px 15px rgba(0,0,0,0.5); text-align: right; }
        h1 { color: #38bdf8; font-size: 20px; text-align: center; }
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
                <textarea name="message" id="message" rows="3" placeholder="اكتب رسالتك هنا أو اتركها للأذكار..." required>سبحان الله وبحمده، سبحان الله العظيم 🌿</textarea>
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

bot = commands.Bot(command_prefix='!', intents=intents)

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
    "سبحان الله وبحمده، سبحان الله العظيم 🌿",
    "لا إله إلا أنت سبحانك إني كنت من الظالمين 🤍",
    "استغفر الله العظيم واتوب إليه 🌙",
    "لا حول ولا قوة إلا بالله العلي العظيم ✨",
    "اللهم صل وسلم على نبينا محمد وعلى آله وصحبه أجمعين 🌹"
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
    
    # إرسال الرسالة عبر البوت باستخدام حلقة الحدث
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
    for guild in bot.guilds:
        target_channel = None
        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).send_messages:
                target_channel = channel
                break
        
        if target_channel:
            athkar = random.choice(ATHKAR_LIST)
            await target_channel.send(f"🤖 **تذكرة أذكار:**\n{athkar}")

@bot.command(name='شغل', aliases=['تشغيل', 'play'])
async def play_quran(ctx, *, search: str):
    if not ctx.author.voice:
        await ctx.send("❌ يجب أن تدخل إلى روم صوتي أولاً!")
        return
    voice_channel = ctx.author.voice.channel
    if ctx.voice_client is None:
        await voice_channel.connect()
    elif ctx.voice_client.channel != voice_channel:
        await ctx.voice_client.move_to(voice_channel)
    if ctx.voice_client.is_playing():
