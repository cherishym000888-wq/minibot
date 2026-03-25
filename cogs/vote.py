import asyncio
import discord
from discord.ext import commands
from discord import app_commands

from config import ADMIN_ID, GUILD_ID, VOTE_IMAGE_URL


class VoteView(discord.ui.View):
    def __init__(self, choice1: str, choice2: str, guild: discord.Guild):
        super().__init__(timeout=None)
        self.choice1 = choice1
        self.choice2 = choice2
        self.guild = guild
        self.votes_a = set()
        self.votes_b = set()
        self.user_names = {}

        button_a = discord.ui.Button(
            label=choice1,
            style=discord.ButtonStyle.primary
        )
        button_b = discord.ui.Button(
            label=choice2,
            style=discord.ButtonStyle.danger
        )

        button_a.callback = self.vote_a_callback
        button_b.callback = self.vote_b_callback

        self.add_item(button_a)
        self.add_item(button_b)

    async def vote_a_callback(self, interaction: discord.Interaction):
        self.votes_b.discard(interaction.user.id)
        self.votes_a.add(interaction.user.id)
        self.user_names[interaction.user.id] = interaction.user.display_name

        await interaction.response.send_message(
            f"**{self.choice1}**에 투표했어요!",
            ephemeral=True
        )

    async def vote_b_callback(self, interaction: discord.Interaction):
        self.votes_a.discard(interaction.user.id)
        self.votes_b.add(interaction.user.id)
        self.user_names[interaction.user.id] = interaction.user.display_name

        await interaction.response.send_message(
            f"**{self.choice2}**에 투표했어요!",
            ephemeral=True
        )


class VoteCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="투표", description="A vs B 투표 시작")
    async def vote_slash(
        self,
        interaction: discord.Interaction,
        선택지1: str,
        선택지2: str,
        시간: int
    ):
        view = VoteView(선택지1, 선택지2, interaction.guild)

        embed = discord.Embed(
            title="🍒 당신의 마음에 더 꽂힌 목소리는!?",
            description=(
                f"🅰️ **{선택지1}**\n"
                f"🅱️ **{선택지2}**\n\n"
                f"⏳ {시간}초 동안 투표합니다!"
            ),
            color=discord.Color.blue()
        )
        embed.set_image(url=VOTE_IMAGE_URL)

        await interaction.response.send_message(embed=embed, view=view)

        await asyncio.sleep(시간)

        for item in view.children:
            item.disabled = True

        original_message = await interaction.original_response()
        await original_message.edit(view=view)

        vote_a = len(view.votes_a)
        vote_b = len(view.votes_b)

        if vote_a > vote_b:
            result = f"🏆 {선택지1} 승!"
        elif vote_b > vote_a:
            result = f"🏆 {선택지2} 승!"
        else:
            result = "🤝 무승부!"

        result_embed = discord.Embed(
            title="🍒 투표 결과!",
            description=(
                f"**{선택지1}**: {vote_a}표\n"
                f"**{선택지2}**: {vote_b}표\n\n"
                f"{result}"
            ),
            color=discord.Color.green()
        )

        await interaction.followup.send(embed=result_embed)

        admin_user = await self.bot.fetch_user(ADMIN_ID)

        users_a = []
        users_b = []

        for user_id in view.votes_a:
            users_a.append(view.user_names.get(user_id, "알 수 없음"))

        for user_id in view.votes_b:
            users_b.append(view.user_names.get(user_id, "알 수 없음"))

        detail_text = (
            f"📊 투표 상세 결과\n\n"
            f"{선택지1}:\n{', '.join(users_a) if users_a else '없음'}\n\n"
            f"{선택지2}:\n{', '.join(users_b) if users_b else '없음'}"
        )

        try:
            await admin_user.send(detail_text)
        except Exception as e:
            print(f"관리자 DM 실패: {e}")


async def setup(bot: commands.Bot):
    await bot.add_cog(VoteCog(bot), guild=discord.Object(id=GUILD_ID))