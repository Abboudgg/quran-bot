import discord
from discord.ext import commands, tasks
import yt_dlp
import requests
import asyncio
import os
import random
from flask import Flask, render_template_string
from threading import Thread

# إعداد خادم الويب ولوحة التحكم البسيطة
app = Flask('')

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>لوحة تحكم بوت القرآن والأذكار</title>
    <style>
        body { background-color: #0f172a; color: #f8fafc; font-family: Tahoma, sans-serif; text-align: center; padding: 50px 20px; }
        .card { background-color: #1e293b; border-radius: 15px; padding: 30px; max-width: 400px; margin: 0 auto; box-shadow: 0 4px 15px rgba(0,0,0,0.5); }
        h1 { color: #38bdf8; font-size: 22px; }
        p { color: #94a3b8; }
        .status { display: inline-block; width: 12px; height: 12px; background-color: #22c55e; border-radius: 50%; margin-left: 5px; }
        .btn { display: block; width: 100%; background: #0ea5e9; color: white; border: none; padding: 12px; border-radius: 8px; font-size: 16px; cursor: pointer; margin-top: 15px; font-weight: bold; text-decoration: none; }
        .btn:hover { background: #0284c7; }
    </style>
</head>
<body>
    <div class="card">
        <h1>🤖 لوحة تحكم بوت ديسكورد</h1>
        <p>حالة البوت: <span class="status"></span> <strong style="color: #22c55e;">متصل ويدير السيرفر 24/7</strong></p>
        <hr style="border: 0; border-top: 1px solid #334155; margin: 20px 0;">
        <p>💡 البوت يقوم حالياً بنشر الأذكار وتشغيل القرآن الكريم على روم ديسكورد.</p>
        <a href="https://www.kick.com/cass-sa" target="_blank" class="btn">📺 زيارة قناة Kick</a>
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

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
    "اللهم صل وسلم على نبينا محمد وعلى آله وصحبه أجمعين 🌹",
    "سبحان الله، والحمد لله، ولا إله إلا الله، والله أكبر 💫",
    "الحمد لله رب العالمين حمداً كثيراً طيباً مباركاً فيه 🌴"
]

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
        ctx.voice_client.stop()

    await ctx.send(f"🔍 جاري البحث عن التلاوة: **{search}**...")

    try:
        query = f"قرآن كريم {search}"
        with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(query, download=False)
            if 'entries' in info:
                info = info['entries'][0]
            
            url = info['url']
            title = info['title']

        source = discord.FFmpegPCMAudio(url, **FFMPEG_OPTIONS)
        ctx.voice_client.play(source)
        await ctx.send(f"🎧 **يتم الآن تشغيل:** {title}")

    except Exception as e:
        await ctx.send("❌ حدث خطأ أثناء محاولة تشغيل التلاوة. تأكد من الاسم أو الرابط وحاول مرة أخرى.")
        print(e)

@bot.command(name='اطلع', aliases=['إيقاف', 'stop', 'leave'])
async def leave_voice(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("👋 تم إيقاف التلاوة والخروج من الروم الصوتي.")
    else:
        await ctx.send("❌ البوت غير موجود في أي روم صوتي حالياً.")

@bot.command(name='قران')
async def send_ayah(ctx):
    try:
        response = requests.get("https://api.alquran.cloud/v1/ayah/random/ar.alafasy").json()
        text = response['data']['text']
        surah = response['data']['surah']['name']
        ayah_num = response['data']['numberInSurah']
        await ctx.send(f"📖 **القرآن الكريم**\n\n> {text}\n\n📍 **[سورة {surah} - آية {ayah_num}]**")
    except:
        await ctx.send("عذراً، تعذر جلب الآية حالياً.")

# تشغيل السيرفر والبود
keep_alive()
bot.run(os.environ.get('TOKEN'))
