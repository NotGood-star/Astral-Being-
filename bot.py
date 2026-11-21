import asyncio
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import discord
from discord.ext import commands


# --- RENDER PORT KEEP-ALIVE SERVER ---
class KeepAliveHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Qt Manager is online.")

    def log_message(self, format, *args):
        return


def start_web_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), KeepAliveHandler)
    threading.Thread(target=server.serve_forever, daemon=True).start()


# --- CUSTOM EMOJI REGISTRY ---
class Emojis:
    ARROW = "<a:CT_Diamond_Arrow:1571018824793333830>"
    TICK = "<:verified:1569265818078945290>"
    CROSS = "<a:Sw_white_wrong:1571024421949280316>"
    TICKET = "<a:437007ticket:1571140935381946560>"
    SHOP = "<:icongoldentosbook:1569265543842631780>"
    OS = "<:co_owner:1569264188445036634>"
    OWNER = "<:manager:1571024422079299645>"
    COIN = "<:booster3:1569264184976482384>"
    DAILY = "<:giftbox:1569264552808284210>"
    LEADERBOARD = "<:Golden_Trophy:1571018824818495629>"
    MODERATION = "<:moderator:1569264561595351172>"
    UPDATES = "<:news:1569266865186934875>"
    QUESTION = "<:helper:1569266738984652872>"
    CRYPTO = "<:cryptos:1569266034966270132>"
    MEMBER = "<:user:1569265753608425563>"
    GIVEAWAY = "<a:bellPixel:1571024422033162290>"
    REACTION_JOIN = "<a:money:1571018824768028682>"
    REWARDS = "<a:Rewards:1571024422037364776>"


# --- BOT CLIENT ---
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True


class QtManagerBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents, help_command=None)
        self.emojis = Emojis
        self.db_path = "qt_manager.db"

    def create_embed(
        self,
        title: str,
        description: str,
        color: discord.Color = discord.Color.blurple(),
        footer: str = "Qt Manager • Public Discord Bot",
    ) -> discord.Embed:
        embed = discord.Embed(title=title, description=description, color=color)
        embed.set_footer(text=footer)
        return embed

    async def setup_hook(self):
        if os.path.isdir("./cogs"):
            for file in sorted(os.listdir("./cogs")):
                if file.endswith(".py") and not file.startswith("_"):
                    await self.load_extension(f"cogs.{file[:-3]}")

    async def on_ready(self):
        print(f"Logged in as {self.user} (ID: {self.user.id})")


bot = QtManagerBot()


async def main():
    start_web_server()
    token = os.environ.get("DISCORD_TOKEN")
    if not token:
        raise RuntimeError("Missing DISCORD_TOKEN environment variable.")
    async with bot:
        await bot.start(token)


if __name__ == "__main__":
    asyncio.run(main())
                                                      
