import discord
from discord.ext import commands, tasks
import yt_dlp
import requests
import asyncio
import os
import random
from flask import Flask
from threading import Thread

# إعداد خادم ويب وهمي عشان Render يعتبره Web Service مجاني وما يقفله
app = Flask('')

@app.route('/')
def home():
    return "Bot is running 24/7!"

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

# قائمة الأذكار
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

# تشغيل خادم الويب الوهمي أولاً لتجنب خطأ الـ Port
keep_alive()

# تشغيل البوت
bot.run(os.environ.get('TOKEN'))
