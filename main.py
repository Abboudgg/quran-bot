import discord
from discord.ext import commands, tasks
from discord import app_commands
import asyncio, os, random
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
    "✨ **سبحان الله وبحمده، سبحان الله العظيم**",
    "✨ **لا إله إلا أنت سبحانك إني كنت من الظالمين**",
    "✨ **استغفر الله العظيم واتوب إليه**",
    "✨ **لا حول ولا قوة إلا بالله العلي العظيم**",
    "✨ **اللهم صل وسلم على نبينا محمد**",
    "✨ **لا إله إلا الله وحدَهُ لا شريك له، له الملك وله الحمد وهو على كل شيء قدير**"
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
    if c: await c.send(f"🤖 **تذكرة أذكار تلقائية:**\n{random.choice(ATHKAR)}")

@bot.tree.command(name="test", description="اختبار استجابة البوت")
async def test_bot(i: discord.Interaction):
    await i.response.send_message("🏓 البوت شغال وبأفضل شكل يا عبد الله!", ephemeral=True)

@bot.tree.command(name="testin", description="يدخل البوت إلى الروم الصوتي فوراً")
async def test_in(i: discord.Interaction):
    if not i.user.voice:
        return await i.response.send_message("❌ ادخل روم صوتي أولاً!", ephemeral=True)
    
    await i.response.defer(ephemeral=True)
    vc = i.guild.voice_client
    vchan = i.user.voice.channel
    if vc is None:
        await vchan.connect()
    elif vc.channel != vchan:
        await vc.move_to(vchan)
    await i.followup.send(f"✅ دخلت الروم: **{vchan.name}** بنجاح!", ephemeral=True)

@bot.tree.command(name="اذاعة", description="تشغيل بث إذاعة القرآن الكريم السعودية المباشر مع بار تحميل")
async def radio(i: discord.Interaction):
    if not i.user.voice:
        return await i.response.send_message("❌ يجب الدخول لروم صوتي أولاً!", ephemeral=True)
    
    await i.response.send_message("⏳ جاري بدء تشغيل الإذاعة...", ephemeral=False)
    msg = await i.original_response()

    try:
        await msg.edit(content="🔍 `[██░░░░░░░░] 20%` - جاري تجهيز الاتصال...")
        await asyncio.sleep(0.4)

        vchan = i.user.voice.channel
        vc = i.guild.voice_client
        
        await msg.edit(content="🔊 `[█████░░░░░] 50%` - جاري الدخول للروم الصوتي...")
        if vc is None:
            vc = await vchan.connect()
        elif vc.channel != vchan:
            await vc.move_to(vchan)

        if vc.is_playing():
            vc.stop()

        await msg.edit(content="🎵 `[████████░░] 80%` - جاري ربط بث الإذاعة الرسمية...")
        
        # رابط إذاعة القرآن الكريم الرسمي السعودي
        radio_url = "https://radioplus.sba.sa/live/4"

        audio_source = discord.FFmpegPCMAudio(
            radio_url, 
            before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 
            options='-vn'
        )
        
        vc.play(audio_source)
        await msg.edit(content="✅ `[██████████] 100%` - **تم تشغيل إذاعة القرآن الكريم (السعودية) بنجاح!** 📻🎧")

    except Exception as e:
        await msg.edit(content="❌ حدث خطأ أثناء تشغيل الإذاعة.")
        print(f"Radio Error: {e}")

@bot.tree.command(name="اذكار", description="إرسال ذكر مبارك مع بار تحميل")
@app_commands.describe(channel="اختر روم نصي مخصص لإرسال الأذكار فيه (اختياري)")
async def send_athkar(i: discord.Interaction, channel: discord.TextChannel = None):
    target_channel = channel or i.channel
    
    await i.response.send_message("⏳ جاري تحضير الذكر...", ephemeral=True)
    msg = await i.original_response()

    await msg.edit(content="🔍 `[████░░░░░░] 40%` - جاري جلب الأذكار...")
    await asyncio.sleep(0.4)

    await msg.edit(content="✨ `[██████████] 100%` - تم إرسال الذكر بنجاح!")
    
    selected_thikr = random.choice(ATHKAR)
    await target_channel.send(f"📖 **ذكر من البوت:**\n{selected_thikr}")

@bot.tree.command(name="اطلع", description="إيقاف البث والخروج من الروم")
async def leave(i: discord.Interaction):
    if i.guild.voice_client:
        await i.guild.voice_client.disconnect()
        await i.response.send_message("👋 تم إيقاف البث والخروج بنجاح.")
    else:
        await i.response.send_message("❌ البوت مو بروم صوتي أصلاً.", ephemeral=True)

Thread(target=lambda: app.run(host='0.0.0.0', port=8080)).start()
bot.run(os.environ.get('TOKEN'))