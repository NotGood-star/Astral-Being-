import sqlite3
import discord
from discord import app_commands
from discord.ext import commands


class CustomCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.bot.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS custom_commands (
                    guild_id INTEGER,
                    name TEXT,
                    response TEXT,
                    PRIMARY KEY (guild_id, name)
                )
                """
            )

    def _save_cc(self, guild_id: int, name: str, response: str):
        with sqlite3.connect(self.bot.db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO custom_commands (guild_id, name, response) VALUES (?, ?, ?)",
                (guild_id, name, response),
            )

    def _delete_cc(self, guild_id: int, name: str) -> bool:
        with sqlite3.connect(self.bot.db_path) as conn:
            cur = conn.execute(
                "DELETE FROM custom_commands WHERE guild_id = ? AND name = ?",
                (guild_id, name),
            )
            return cur.rowcount > 0

    def _list_cc(self, guild_id: int):
        with sqlite3.connect(self.bot.db_path) as conn:
            return conn.execute(
                "SELECT name FROM custom_commands WHERE guild_id = ? ORDER BY name",
                (guild_id,),
            ).fetchall()

    # --- PREFIX COMMANDS ---
    @commands.group(name="cc", invoke_without_command=True)
    @commands.has_permissions(manage_guild=True)
    async def cc_root(self, ctx: commands.Context):
        e = self.bot.custom_emojis
        embed = self.bot.create_embed(
            title=f"{e.ARROW} Custom Commands",
            description=(
                f"{e.ARROW} `!cc add <name> <response>` / `/cc_add` — Create/update a command\n"
                f"{e.ARROW} `!cc remove <name>` / `/cc_remove` — Delete a command\n"
                f"{e.ARROW} `!cc list` / `/cc_list` — List server custom commands"
            ),
            color=discord.Color.gold(),
        )
        await ctx.send(embed=embed)

    @cc_root.command(name="add")
    @commands.has_permissions(manage_guild=True)
    async def cc_add(self, ctx: commands.Context, name: str, *, response: str):
        e = self.bot.custom_emojis
        cmd_name = name.lower().strip()
        self._save_cc(ctx.guild.id, cmd_name, response)
        embed = self.bot.create_embed(
            title=f"{e.TICK} Custom Command Saved",
            description=f"{e.ARROW} Trigger: `!{cmd_name}`\n{e.ARROW} Response: {response}",
            color=discord.Color.green(),
        )
        await ctx.send(embed=embed)

    @cc_root.command(name="remove")
    @commands.has_permissions(manage_guild=True)
    async def cc_remove(self, ctx: commands.Context, name: str):
        e = self.bot.custom_emojis
        cmd_name = name.lower().strip()
        deleted = self._delete_cc(ctx.guild.id, cmd_name)
        if deleted:
            embed = self.bot.create_embed(
                title=f"{e.TICK} Custom Command Removed",
                description=f"{e.ARROW} Deleted `!{cmd_name}`.",
                color=discord.Color.green(),
            )
        else:
            embed = self.bot.create_embed(
                title=f"{e.CROSS} Not Found",
                description=f"{e.ARROW} No custom command named `!{cmd_name}` exists.",
                color=discord.Color.red(),
            )
        await ctx.send(embed=embed)

    @cc_root.command(name="list")
    async def cc_list(self, ctx: commands.Context):
        e = self.bot.custom_emojis
        rows = self._list_cc(ctx.guild.id)
        if not rows:
            embed = self.bot.create_embed(
                title=f"{e.ARROW} Custom Commands",
                description=f"{e.CROSS} No custom commands set in this server.",
                color=discord.Color.blurple(),
            )
        else:
            items = "\n".join(f"{e.ARROW} `!{r[0]}`" for r in rows)
            embed = self.bot.create_embed(
                title=f"{e.ARROW} Server Custom Commands",
                description=items,
                color=discord.Color.blurple(),
            )
        await ctx.send(embed=embed)

    # --- SLASH COMMANDS ---
    @app_commands.command(name="cc_add", description="Add or update a custom command for this server")
    @app_commands.default_permissions(manage_guild=True)
    async def slash_cc_add(self, interaction: discord.Interaction, name: str, response: str):
        e = self.bot.custom_emojis
        cmd_name = name.lower().strip()
        self._save_cc(interaction.guild.id, cmd_name, response)
        embed = self.bot.create_embed(
            title=f"{e.TICK} Custom Command Saved",
            description=f"{e.ARROW} Trigger: `!{cmd_name}`\n{e.ARROW} Response: {response}",
            color=discord.Color.green(),
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="cc_remove", description="Remove a custom command from this server")
    @app_commands.default_permissions(manage_guild=True)
    async def slash_cc_remove(self, interaction: discord.Interaction, name: str):
        e = self.bot.custom_emojis
        cmd_name = name.lower().strip()
        deleted = self._delete_cc(interaction.guild.id, cmd_name)
        if deleted:
            embed = self.bot.create_embed(
                title=f"{e.TICK} Custom Command Removed",
                description=f"{e.ARROW} Deleted `!{cmd_name}`.",
                color=discord.Color.green(),
            )
        else:
            embed = self.bot.create_embed(
                title=f"{e.CROSS} Not Found",
                description=f"{e.ARROW} No custom command named `!{cmd_name}` exists.",
                color=discord.Color.red(),
            )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="cc_list", description="List custom commands configured in this server")
    async def slash_cc_list(self, interaction: discord.Interaction):
        e = self.bot.custom_emojis
        rows = self._list_cc(interaction.guild.id)
        if not rows:
            embed = self.bot.create_embed(
                title=f"{e.ARROW} Custom Commands",
                description=f"{e.CROSS} No custom commands set in this server.",
                color=discord.Color.blurple(),
            )
        else:
            items = "\n".join(f"{e.ARROW} `!{r[0]}`" for r in rows)
            embed = self.bot.create_embed(
                title=f"{e.ARROW} Server Custom Commands",
                description=items,
                color=discord.Color.blurple(),
            )
        await interaction.response.send_message(embed=embed)

    # --- CUSTOM TRIGGER LISTENER ---
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return
        if not message.content.startswith("!"):
            return

        # Skip if it's "!global shop" so shop_owner handles it cleanly
        lowered = message.content.strip().lower()
        if lowered == "!global shop" or lowered.startswith("!global shop "):
            return

        ctx = await self.bot.get_context(message)
        if ctx.valid:
            return

        cmd_name = message.content[1:].split(" ", 1)[0].lower().strip()
        if not cmd_name:
            return

        with sqlite3.connect(self.bot.db_path) as conn:
            row = conn.execute(
                "SELECT response FROM custom_commands WHERE guild_id = ? AND name = ?",
                (message.guild.id, cmd_name),
            ).fetchone()

        if row:
            e = self.bot.custom_emojis
            embed = self.bot.create_embed(
                title=f"{e.ARROW} {cmd_name.capitalize()}",
                description=row[0],
                color=discord.Color.dark_theme(),
            )
            await message.channel.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(CustomCommands(bot))
    
