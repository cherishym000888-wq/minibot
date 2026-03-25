import discord
from discord.ext import commands
from config import TOKEN, GUILD_ID

intents = discord.Intents.default()

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    try:
        guild = discord.Object(id=GUILD_ID)
        synced = await bot.tree.sync(guild=guild)
        print(f"슬래시 명령어 동기화 완료: {len(synced)}개")
    except Exception as e:
        print(f"동기화 실패: {e}")

    print(f"{bot.user} 실행됨!")


async def main():
    async with bot:
        await bot.load_extension("cogs.vote")
        await bot.start(TOKEN)


import asyncio
asyncio.run(main())