import discord
from discord.ext import commands, tasks
from discord import app_commands
import yt_dlp, asyncio, os, random
from flask import Flask, render_template_string, request
from threading import Thread

app = Flask('')
HTML = '''<!DOCTYPE html><html lang="ar" dir="rtl"><head><meta charset="UTF-8"><title>لوحة التحكم</title></head>
<body style="background:#450a0a;color:#fff;font-family:Tahoma;text-align:center;padding:50px;">
<h2>🤖 لوحة التحكم</h2>
<form method="POST" action="/send">
<select name="cid" style="padding:10px;width:300px;">
{% for c in channels %}<option value="{{c.id}}">{{c.name}}</option>{% endfor %}
</select><br><br>
<textarea name="msg" rows="3" style="padding:10px;width:300px;" required>سبحان الله وبحمده، سبحان الله العظيم</textarea><br><br>
<button type="submit" style="padding:10px 20px;background:#0ea5e9;color:#fff;border:none;border-radius:5px;">إرسال</button>
</form></body></html>'''

intents = discord.Intents.default()
intents.message_content = True
intents.presences = True
intents.members = True

class Bot(commands.Bot):
    def __init__(self): super().__init__(command_prefix="!", intents=intents)
    async def setup_hook(self): await self.tree.sync()

bot = Bot()
ATHKAR = ["سبحان الله وبحمده", "لا إله إلا أنت سبحانك", "استغفر الله العظيم واتوب إليه"]

@app.route('/')
def home():
    channels = [{'id': c.id, 'name': f"#{c.name}"} for g in bot.guilds for c in g.text_channels]
    return render_template_string(HTML, channels=channels)

@app.route('/send', methods=['POST'])
def send():
    cid, msg = int(request.form.get('cid')), request.form.get('msg')
    asyncio.run_coroutine_threadsafe(bot.get_channel(cid).send(f"📢 **إعلان:**\n{msg}"), bot.loop)
    return home()

@bot.event
async def on_ready():
    # هذا هو سطر حالة الاتصال والبث (Streaming)
    await bot.change_presence(activity=discord.Streaming(name="بث مباشر على Kick", url="https://www.kick.com/cass-sa"))
    if not athkar_loop.is_running(): athkar_loop.start()

@tasks.loop(hours=1)
async def athkar_loop():
    c = bot.get_channel(1571122362839990324) # روم الأذكار المخصص
    if c: await c.send(f"🤖 **تذكرة أذكار:**\n{random.choice(ATHKAR)}")

@bot.tree.command(name="شغل", description="تشغيل تلاوة القرآن")
@app_commands.describe(search="اسم السورة أو القارئ")
async def play(i: discord.Interaction, search: str):
    if not i.user.voice: return await i.response.send_message("❌ ادخل روم صوتي!", ephemeral=True)
    vc, vchan = i.guild.voice_client, i.user.voice.channel
    if not vc: await vchan.connect()
    elif vc.channel != vchan: await vc.move_to(vchan)
    if vc and vc.is_playing(): vc.stop()
    await i.response.send_message(f"🔍 جاري البحث: **{search}**...")
    with yt_dlp.YoutubeDL({'format': 'bestaudio', 'quiet': True}) as ydl:
        info = ydl.extract_info(f"قرآن كريم {search}", download=False)
        if 'entries' in info: info = info['entries'][0]
        vc.play(discord.FFmpegPCMAudio(info['url'], before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', options='-vn'))
    await i.followup.send(f"🎧 **تم التشغيل:** {info['title']}")

@bot.tree.command(name="اطلع", description="إيقاف وخروج")
async def leave(i: discord.Interaction):
    if i.guild.voice_client:
        await i.guild.voice_client.disconnect()
        await i.response.send_message("👋 تم الخروج.")
    else: await i.response.send_message("❌ البوت مو بروم صوتي.", ephemeral=True)

Thread(target=lambda: app.run(host='0.0.0.0', port=8080)).start()
bot.run(os.environ.get('TOKEN'))
