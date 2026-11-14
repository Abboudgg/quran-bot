import discord
from discord.ext import commands, tasks
from discord import app_commands
import yt_dlp, asyncio, os, random
from flask import Flask, render_template_string, request
from threading import Thread

app = Flask('')
HTML = '''<!DOCTYPE html><html lang="ar" dir="rtl"><head><meta charset="UTF-8"><title>لوحة التحكم</title></head>
<body style="background:linear-gradient(135deg, #450a0a 0%, #1e1b4b 100%);color:#fff;font-family:Tahoma;text-align:center;padding:40px;min-height:100vh;">
<div style="background:rgba(30, 41, 59, 0.85);padding:25px;border-radius:20px;max-width:450px;margin:auto;box-shadow:0 8px 32px rgba(0,0,0,0.6);">
<h2>🤖 لوحة تحكم البوت</h2>
<form method="POST" action="/send">
<select name="cid" style="padding:10px;width:100%;border-radius:8px;background:#0f172a;color:#fff;border:1px solid #334155;margin-bottom:15px;">
{% for c in channels %}<option value="{{c.id}}">{{c.name}}</option>{% endfor %}
</select>
<textarea name="msg" rows="3" style="padding:10px;width:100%;border-radius:8px;background:#0f172a;color:#fff;border:1px solid #334155;box-sizing:border-box;margin-bottom:15px;" required>سبحان الله وبحمده، سبحان الله العظيم</textarea>
<button type="submit" style="padding:12px;width:100%;background:#0ea5e9;color:#fff;border:none;border-radius:8px;font-weight:bold;cursor:pointer;">🚀 إرسال إلى ديسكورد</button>
</form>
<a href="https://www.kick.com/cass-sa" target="_blank" style="display:block;margin-top:15px;padding:12px;background:#22c55e;color:#fff;text-decoration:none;border-radius:8px;font-weight:bold;">📺 زيارة قناة Kick</a>
</div></body></html>'''

intents = discord.Intents.default()
intents.message_content = True
intents.presences = True
intents.members = True
intents.voice_states = True

class Bot(commands.Bot):
    def __init__(self): super().__init__(command_prefix="!", intents=intents)
    async def setup_hook(self): await self.tree.sync()

bot = Bot()
ATHKAR = [
    "سبحان الله وبحمده، سبحان الله العظيم",
    "لا إله إلا أنت سبحانك إني كنت من الظالمين",
    "استغفر الله العظيم واتوب إليه",
    "لا حول ولا قوة إلا بالله العلي العظيم"
]

@app.route('/')
def home():
    channels = [{'id': c.id, 'name': f"{g.name} ➔ #{c.name}"} for g in bot.guilds for c in g.text_channels]
    return render_template_string(HTML, channels=channels)

@app.route('/send', methods=['POST'])
def send():
    cid, msg = int(request.form.get('cid')), request.form.get('msg')
    asyncio.run_coroutine_threadsafe(bot.get_channel(cid).send(f"📢 **تنبيه من لوحة التحكم:**\n{msg}"), bot.loop)
    return home()

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Streaming(name="بث مباشر على Kick", url="https://kick.com/cass-sa"))
    if not athkar_loop.is_running(): athkar_loop.start()

@tasks.loop(hours=1)
async def athkar_loop():
    c = bot.get_channel(1571122362839990324)
    if c: await c.send(f"🤖 **تذكرة أذكار:**\n{random.choice(ATHKAR)}")

@bot.tree.command(name="شغل", description="تشغيل أي سورة بالاسم مع الشيخ مباشرة")
@app_commands.describe(surah="اكتب اسم السورة (مثل: الملك، الكهف، البقرة)", sheikh="اكتب اسم الشيخ (مثل: ياسر الدوسري، العفاسي)")
async def play(i: discord.Interaction, surah: str, sheikh: str):
    if not i.user.voice:
        return await i.response.send_message("❌ يجب الدخول لروم صوتي أولاً!", ephemeral=True)
    
    await i.response.send_message(f"🔍 جاري البحث عن **سورة {surah}** بصوت **{sheikh}**...", ephemeral=False)

    try:
        voice_channel = i.user.voice.channel
        guild = i.guild

        if guild.voice_client is None:
            vc = await voice_channel.connect()
        elif guild.voice_client.channel != voice_channel:
            await guild.voice_client.move_to(voice_channel)
            vc = guild.voice_client
        else:
            vc = guild.voice_client

        if vc.is_playing():
            vc.stop()

        query = f"سورة {surah} القارئ {sheikh} قران كريم"
        ydl_opts = {
            'format': 'bestaudio/best',
            'noplaylist': True,
            'default_search': 'ytsearch1',
            'quiet': True,
            'extract_flat': False
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(query, download=False)
            if 'entries' in info:
                info = info['entries'][0]
            url = info['url']
            title = info['title']

        ffmpeg_options = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            'options': '-vn'
        }

        vc.play(discord.FFmpegPCMAudio(url, **ffmpeg_options))
        await i.followup.send(f"🎧 **يتم الآن تشغيل:** {title}")

    except Exception as e:
        await i.followup.send("❌ حدث خطأ أثناء التشغيل، تأكد من كتابة اسم السورة والشيخ بشكل صحيح.")
        print(e)

@bot.tree.command(name="اطلع", description="إيقاف التلاوة والخروج من الروم الصوتي")
async def leave(i: discord.Interaction):
    if i.guild.voice_client:
        await i.guild.voice_client.disconnect()
        await i.response.send_message("👋 تم إيقاف التلاوة والخروج بنجاح.")
    else: await i.response.send_message("❌ البوت ليس في أي روم صوتي حالياً.", ephemeral=True)

Thread(target=lambda: app.run(host='0.0.0.0', port=8080)).start()
bot.run(os.environ.get('TOKEN'))
