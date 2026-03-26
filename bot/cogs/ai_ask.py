import discord

from discord import app_commands
from discord.ext import commands

from cogs.utils.gemini_client import GeminiClient

class AI(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Define GeminiClient with the desired model (e.g., "google/gemini-2.0-flash-001")
        self.ai = GeminiClient("gemini-2.5-flash")

    @app_commands.command(name="ask", description="Ask AI")
    async def ask(self, interaction: discord.Interaction, prompt: str):
        await interaction.response.defer()

        # Define instructions for the AI to ensure concise answers and handle ambiguity
        instructions = "[Answer the following question in a concise manner " \
        "maximum 500 words. If the question is ambiguous, ask for clarification. " \
        "Prioritize getting straight to the point, using the first line if necessary.]\n\n"

        # Call the Gemini API with the user's prompt and get the response
        enhanced_prompt = f"{instructions}{prompt}"
        answer = self.ai.fetch(enhanced_prompt)

        # Check if the answer exceeds Discord's message limit and truncate if necessary
        if len(answer) > 1900:  # Discord message limit
            answer = answer[:1900] + "..."  # Truncate and add ellipsis if too long

        await interaction.followup.send(f"**AI:** {answer}")

async def setup(bot):
    await bot.add_cog(AI(bot))
