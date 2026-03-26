import discord
from discord import app_commands

from cogs.utils.dropdown_bar import DropdownBar
from cogs.utils.notification_msg import NotificationMsg

class ClassName:
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="name", description="description")
    async def func_name(self, interaction: discord.Interaction):
        
        items = None
        active_items = None
        
        action_map = {
            None
        }
        
        view = DropdownBar(
            items,
            self.client or None,
            active_items or set(),
            action_map,
            mode=""
        )
        await interaction.response.send_message("", view=view, ephemeral=True)
        
        view.message = await interaction.original_response()