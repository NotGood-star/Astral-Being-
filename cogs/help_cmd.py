import discord
from discord import app_commands
from discord.ext import commands


class HelpCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def _build_help_embed(self) -> discord.Embed:
        e = self.bot.custom_emojis
        return self.bot.create_embed(
            title=f"{e.QUESTION} Qt Manager — All Commands",
            description=(
                f"{e.SHOP} **Global & Server Shop**\n"
                f"{e.ARROW} `!global shop` / `/globalshop` — View NotGood's global `/craze` shop\n"
                f"{e.ARROW} `!shop` / `/shop` — View this server's shop & details\n"
                f"{e.ARROW} `!owner` / `/owner` — View this server's Owner & OS leadership\n"
                f"{e.ARROW} `!setshop <url> [name]` / `/setshop` — Set server shop (Admin)\n"
                f"{e.ARROW} `!setpayments <methods>` — Set server payment methods (Admin)\n"
                f"{e.ARROW} `!setowner @Owner [@OSRole]` — Set server Owner & OS role (Admin)\n\n"
                f"{e.ARROW} **Custom Commands**\n"
                f"{e.ARROW} `!cc add <name> <response>` / `/cc_add` — Add/update custom command\n"
                f"{e.ARROW} `!cc remove <name>` / `/cc_remove` — Remove custom command\n"
                f"{e.ARROW} `!cc list` / `/cc_list` — List server custom commands\n\n"
                f"{e.QUESTION} **Help**\n"
                f"{e.ARROW} `!help` / `/help` — Show this command menu"
            ),
            color=discord.Color.blurple(),
        )

    @commands.command(name="help", aliases=["cmds", "commands"])
    async def prefix_help(self, ctx: commands.Context):
        await ctx.send(embed=self._build_help_embed())

    @app_commands.command(name="help", description="Show every command available in Qt Manager")
    async def slash_help(self, interaction: discord.Interaction):
        await interaction.response.send_message(embed=self._build_help_embed())


async def setup(bot: commands.Bot):
    await bot.add_cog(HelpCommand(bot))
  
