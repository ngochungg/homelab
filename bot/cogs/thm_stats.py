import aiohttp
import discord
from discord import app_commands
from discord.ext import commands

from cogs.utils.notification_msg import NotificationMsg

# --- CONFIGURATION ---
# TryHackMe Public API V2 Endpoint
THM_API_BASE = "https://tryhackme.com/api/v2/public-profile?username="

class THMStats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="thm_stats", description="Fetch student statistics from TryHackMe")
    async def thm(self, interaction: discord.Interaction, username: str):
        """
        Feature: THM Profile Scraper
        Logic: Fetches public room completion, rank, and level data.
        Security Note: 
        - Uses 'aiohttp' for non-blocking I/O to prevent the Operator Bot from freezing.
        - Implements data sanitization for the 'rank' field to avoid formatting errors.
        """
        
        # 1. PREVENT INTERACTION TIMEOUT (Error 10062)
        # THM API latency can exceed 3s. defer() tells Discord to wait for the process.
        await interaction.response.defer()

        try:
            # 2. ASYNCHRONOUS HTTP REQUEST
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{THM_API_BASE}{username}") as response:
                    
                    # Check if the HTTP request was successful (Status 200)
                    if response.status != 200:
                        error_embed = NotificationMsg.error_msg(
                            title="User Not Found",
                            description=f"User `{username}` not found or API is down."
                        )
                        await interaction.followup.send(embed=error_embed)
                        return
                    
                    # Parse the JSON response body
                    payload = await response.json()
                    
                    # Check for logic errors returned by the API
                    if payload.get("status") == "error":
                        error_embed = NotificationMsg.error_msg(
                            title="THM Error",
                            description=f"THM Error: {payload.get('message')}"
                        )
                        return await interaction.followup.send(embed=error_embed)

                    # Extract the main data object
                    data = payload.get("data", {})

                    # 3. DATA SANITIZATION & FORMATTING
                    # Handling the 'rank' field: some users might have non-numeric ranks (e.g., "N/A")
                    rank_raw = data.get('rank', 'N/A')
                    if str(rank_raw).isdigit():
                        # Format number with commas (e.g., 1,234,567)
                        rank_display = f"#{int(rank_raw):,}" 
                    else:
                        rank_display = f"#{rank_raw}"

                    # 4. CONSTRUCTING THE DISCORD EMBED
                    # Using THM Red color scheme for a professional look
                    embed = discord.Embed(
                        title=f"🛡️ TryHackMe Stats: {username}",
                        description="Real-time profile data from TryHackMe API",
                        color=discord.Color.blue(),
                        url=f"https://tryhackme.com/p/{username}"
                    )
                    
                    # Set user avatar as thumbnail if available
                    if data.get("avatar"):
                        embed.set_thumbnail(url=data["avatar"])

                    # Adding statistical fields
                    embed.add_field(name="Global Rank", value=rank_display, inline=True)
                    embed.add_field(name="Percentile", value=f"Top {data.get('topPercentage', 0)}%", inline=True)
                    embed.add_field(name="Level", value=f"Level {data.get('level', 0)}", inline=True)
                    embed.add_field(name="Rooms Done", value=f"✅ {data.get('completedRoomsNumber', 0)}", inline=True)
                    embed.add_field(name="Badges", value=f"🏅 {data.get('badgesNumber', 0)}", inline=True)
                    
                    # Subscription status check
                    is_premium = "🟡 Premium" if data.get('subscribed') else "⚪ Free Tier"
                    embed.set_footer(text=f"Account Status: {is_premium} | Node: Dell Lab Operator")

                    # 5. SEND FINAL RESPONSE
                    await interaction.followup.send(embed=embed)

        except aiohttp.ClientError as network_err:
            # Handle network-level issues (DNS, connection timeout, etc.)
            await interaction.followup.send(f"🚨 Network error connecting to THM: `{str(network_err)}`")
        except Exception as general_err:
            # Catch-all for unexpected internal logic errors
            print(f"[DEBUG] System Error: {general_err}")
            await interaction.followup.send(f"⚠️ Internal system error: `{str(general_err)}`")

async def setup(bot):
    await bot.add_cog(THMStats(bot))