import sqlite3
import discord
from discord.ext import commands


class ShopOwner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.bot.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS guild_shop_owner (
                    guild_id INTEGER PRIMARY KEY,
                    shop_name TEXT,
                    shop_url TEXT,
                    payment_info TEXT,
                    custom_owner_id INTEGER,
                    os_role_id INTEGER
                )
                """
            )

    def _get_config(self, guild_id: int):
        with sqlite3.connect(self.bot.db_path) as conn:
            return conn.execute(
                """
                SELECT shop_name, shop_url, payment_info, custom_owner_id, os_role_id
                FROM guild_shop_owner
                WHERE guild_id = ?
                """,
                (guild_id,),
            ).fetchone()

    @commands.command(name="setshop")
    @commands.has_permissions(administrator=True)
    async def set_shop(self, ctx: commands.Context, shop_url: str, *, shop_name: str = "Official Server Shop"):
        """Set this server's shop link and store title."""
        e = self.bot.custom_emojis

        if not (shop_url.startswith("http://") or shop_url.startswith("https://")):
            embed = self.bot.create_embed(
                title=f"{e.CROSS} Invalid Shop URL",
                description=f"{e.ARROW} Your link must start with `https://` or `http://`.",
                color=discord.Color.red(),
            )
            return await ctx.send(embed=embed)

        existing = self._get_config(ctx.guild.id)
        payment_info = existing[2] if existing and existing[2] else "Check shop page or open a ticket"
        custom_owner_id = existing[3] if existing else None
        os_role_id = existing[4] if existing else None

        with sqlite3.connect(self.bot.db_path) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO guild_shop_owner
                (guild_id, shop_name, shop_url, payment_info, custom_owner_id, os_role_id)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (ctx.guild.id, shop_name, shop_url, payment_info, custom_owner_id, os_role_id),
            )

        embed = self.bot.create_embed(
            title=f"{e.TICK} Server Shop Saved",
            description=(
                f"{e.SHOP} **Store:** {shop_name}\n"
                f"{e.ARROW} **Link:** {shop_url}\n"
                f"{e.CRYPTO} **Payments:** {payment_info}"
            ),
            color=discord.Color.green(),
        )
        await ctx.send(embed=embed)

    @commands.command(name="setpayments")
    @commands.has_permissions(administrator=True)
    async def set_payments(self, ctx: commands.Context, *, payment_methods: str):
        """Set accepted payment methods shown in !shop."""
        e = self.bot.custom_emojis
        existing = self._get_config(ctx.guild.id)

        shop_name = existing[0] if existing and existing[0] else f"{ctx.guild.name} Shop"
        shop_url = existing[1] if existing and existing[1] else ""
        custom_owner_id = existing[3] if existing else None
        os_role_id = existing[4] if existing else None

        with sqlite3.connect(self.bot.db_path) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO guild_shop_owner
                (guild_id, shop_name, shop_url, payment_info, custom_owner_id, os_role_id)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (ctx.guild.id, shop_name, shop_url, payment_methods, custom_owner_id, os_role_id),
            )

        embed = self.bot.create_embed(
            title=f"{e.TICK} Payment Methods Updated",
            description=f"{e.CRYPTO} **Accepted Payments:** {payment_methods}",
            color=discord.Color.green(),
        )
        await ctx.send(embed=embed)

    @commands.command(name="setowner")
    @commands.has_permissions(administrator=True)
    async def set_owner_info(
        self,
        ctx: commands.Context,
        owner: discord.Member,
        os_role: discord.Role = None,
    ):
        """Set the displayed per-server Owner and optional OS/Co-Owner role."""
        e = self.bot.custom_emojis
        existing = self._get_config(ctx.guild.id)

        shop_name = existing[0] if existing and existing[0] else f"{ctx.guild.name} Shop"
        shop_url = existing[1] if existing and existing[1] else ""
        payment_info = existing[2] if existing and existing[2] else "Check shop page or open a ticket"
        os_role_id = os_role.id if os_role else (existing[4] if existing else None)

        with sqlite3.connect(self.bot.db_path) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO guild_shop_owner
                (guild_id, shop_name, shop_url, payment_info, custom_owner_id, os_role_id)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (ctx.guild.id, shop_name, shop_url, payment_info, owner.id, os_role_id),
            )

        os_display = os_role.mention if os_role else (f"<@&{os_role_id}>" if os_role_id else "Not Set")
        embed = self.bot.create_embed(
            title=f"{e.TICK} Server Ownership Info Updated",
            description=(
                f"{e.OWNER} **Server Owner:** {owner.mention} (`{owner.id}`)\n"
                f"{e.OS} **OS / Co-Owner Role:** {os_display}"
            ),
            color=discord.Color.green(),
        )
        await ctx.send(embed=embed)

    @commands.command(name="shop")
    async def view_shop(self, ctx: commands.Context):
        """View this server's shop link, payment info, and owner details."""
        e = self.bot.custom_emojis
        cfg = self._get_config(ctx.guild.id)

        if not cfg or not cfg[1]:
            embed = self.bot.create_embed(
                title=f"{e.SHOP} {ctx.guild.name} Shop",
                description=(
                    f"{e.CROSS} No shop link has been configured for this server yet.\n"
                    f"{e.ARROW} Admins can configure it with `!setshop <url> <shop name>`."
                ),
                color=discord.Color.orange(),
            )
            return await ctx.send(embed=embed)

        shop_name, shop_url, payment_info, custom_owner_id, os_role_id = cfg
        owner_member = ctx.guild.get_member(custom_owner_id) if custom_owner_id else ctx.guild.owner
        owner_text = f"{owner_member.mention} (`{owner_member.id}`)" if owner_member else "Server Owner"
        os_text = f"<@&{os_role_id}>" if os_role_id else "Server Staff"

        embed = self.bot.create_embed(
            title=f"{e.SHOP} {shop_name}",
            description=(
                f"{e.ARROW} **Store Link:** [{shop_name}]({shop_url})\n"
                f"{e.CRYPTO} **Payments:** {payment_info}\n"
                f"{e.OWNER} **Server Owner:** {owner_text}\n"
                f"{e.OS} **OS / Management:** {os_text}\n"
                f"{e.TICKET} Need help with an order? Open a support ticket!"
            ),
            color=discord.Color.gold(),
        )
        if ctx.guild.icon:
            embed.set_thumbnail(url=ctx.guild.icon.url)

        view = discord.ui.View()
        view.add_item(discord.ui.Button(label=f"Open {shop_name}", url=shop_url, style=discord.ButtonStyle.link))
        await ctx.send(embed=embed, view=view)

    @commands.command(name="owner", aliases=["ownership", "os"])
    async def view_owner(self, ctx: commands.Context):
        """Display the server's ownership & OS leadership embed."""
        e = self.bot.custom_emojis
        cfg = self._get_config(ctx.guild.id)

        custom_owner_id = cfg[3] if cfg else None
        os_role_id = cfg[4] if cfg else None
        shop_url = cfg[1] if cfg and cfg[1] else None
        shop_name = cfg[0] if cfg and cfg[0] else "Server Shop"

        owner_member = ctx.guild.get_member(custom_owner_id) if custom_owner_id else ctx.guild.owner
        owner_text = f"{owner_member.mention} (`{owner_member.id}`)" if owner_member else "Unknown"

        os_role = ctx.guild.get_role(os_role_id) if os_role_id else None
        if os_role and os_role.members:
            os_members = ", ".join(m.mention for m in os_role.members[:10])
            os_text = f"{os_role.mention} — {os_members}"
        elif os_role:
            os_text = os_role.mention
        else:
            os_text = "Not configured (`!setowner @Owner @OSRole`)"

        desc = (
            f"{e.OWNER} **Server Owner:** {owner_text}\n"
            f"{e.OS} **OS / Co-Owners:** {os_text}\n"
            f"{e.MEMBER} **Total Members:** `{ctx.guild.member_count}`"
        )
        if shop_url:
            desc += f"\n{e.SHOP} **Official Shop:** [{shop_name}]({shop_url})"

        embed = self.bot.create_embed(
            title=f"{e.OWNER} {ctx.guild.name} • Ownership",
            description=desc,
            color=discord.Color.blurple(),
        )
        if owner_member and owner_member.display_avatar:
            embed.set_thumbnail(url=owner_member.display_avatar.url)

        await ctx.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(ShopOwner(bot))
            
