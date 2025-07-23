import discord
from discord.ext import commands
import asyncio
import time
from collections import defaultdict
from keep_alive import keep_alive
import os

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Anti-spam config
MESSAGE_LIMIT = 5
TIME_WINDOW = 10  # secondes
MUTE_DURATION = 15 * 60  # 15 minutes

user_messages = defaultdict(list)

@bot.event
async def on_ready():
    print(f"✅ Le bot est connecté en tant que {bot.user}.")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    user_id = message.author.id
    now = time.time()

    user_messages[user_id].append(now)
    user_messages[user_id] = [t for t in user_messages[user_id] if now - t <= TIME_WINDOW]

    if len(user_messages[user_id]) >= MESSAGE_LIMIT:
        guild = message.guild
        muted_role = discord.utils.get(guild.roles, name="Muted")

        if not muted_role:
            muted_role = await guild.create_role(name="Muted")
            for channel in guild.channels:
                await channel.set_permissions(muted_role, send_messages=False, speak=False)

        await message.author.add_roles(muted_role)
        await message.channel.send(f"🚫 {message.author.mention}, arrete de flood tu pue la merde (tu as été mute pendant 15 minutes ducoup sale trdc).")

        user_messages[user_id] = []

        await asyncio.sleep(MUTE_DURATION)
        await message.author.remove_roles(muted_role)
        await message.channel.send(f"🔈 {message.author.mention}, tu es maintenant démuté.")

    await bot.process_commands(message)

# Lancer le mini serveur keep-alive
keep_alive()

# Lancer le bot avec le token stocké dans les variables secrètes
TOKEN = os.environ['TOKEN']
bot.run(TOKEN)
