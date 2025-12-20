import asyncio
from app.bot import create_bot


async def main():
    bot = create_bot()
    await bot.start(bot.config.DISCORD_TOKEN)


if __name__ == "__main__":
    asyncio.run(main())
