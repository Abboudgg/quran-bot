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
    "لا حول ولا قوة إلا بالله العلي
