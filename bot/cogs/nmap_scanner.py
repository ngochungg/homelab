import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import io

# Utility for consistent error/info messages
from cogs.utils.notification_msg import NotificationMsg

class NmapScanner(commands.Cog):
    """
    Cog for network scanning using Nmap.
    Executes scans asynchronously to prevent bot downtime.
    """
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="scan", description="Scan a network for open ports and services")
    @app_commands.describe(
        target="IP Address, Hostname, or Subnet (e.g., 10.8.0.1 or 10.8.0.0/24)",
        arguments="Nmap arguments (e.g., -F, -Pn, -sV). Default is -F (Fast Scan)"
    )
    async def scan_network(self, interaction: discord.Interaction, target: str, arguments: str = "-F"):
        """
        Logic: Executes nmap binary via asyncio subprocess.
        Security Note: Arguments are restricted to prevent command injection.
        """

        # 1. PREVENT TIMEOUTS
        # Scans take time; defer() is mandatory here.
        await interaction.response.defer()

        # 2. BASIC SECURITY CHECK (Sanitization)
        # Prevent users from injecting shell commands like "target; rm -rf /"
        forbidden_chars = [';', '&', '|', '>', '<', '$', '(', ')', '`']
        if any(char in target for char in forbidden_chars):
            error_embed = NotificationMsg.error_msg(
                title="Security Violation",
                description="Command injection attempt detected. Please use only IP addresses or hostnames."
            )
            return await interaction.followup.send(embed=error_embed)

        try:
            # 3. EXECUTE ASYNC SUBPROCESS
            # We use create_subprocess_exec for non-blocking execution.
            # 'nmap' must be installed on the host OS (apt install nmap).
            process = await asyncio.create_subprocess_exec(

                'nmap', *arguments.split(), target,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            # Wait for the process to complete
            stdout, stderr = await process.communicate()

            if stderr:
                print(f"[DEBUG] Nmap Stderr: {stderr.decode()}")

            # Handle the output
            result = stdout.decode().strip()

            if not result:

                error_embed = NotificationMsg.error_msg(
                    title="Scan Failed",
                    description="No output received from Nmap. Please check your target and arguments."
                )
                return await interaction.followup.send(embed=error_embed)

            # 5. SEND RESULTS
            # If the result is too long for Discord ( > 2000 chars), send it as a file.
            if len(result) > 1900:

                file_result = io.BytesIO(result.encode('utf-8'))
                await interaction.followup.send(
                    content=f"📄 Scan results for `{target}` are too long, sending as file:",
                    file=discord.File(fp=file_result, filename=f"scan_{target}.txt")
                )
            else:
                embed = NotificationMsg.info_msg(
                    title=f"Scan Results for {target}",
                    description=result,
                )
                await interaction.followup.send(embed=embed)

        except Exception as e:
                print(f"[ERROR] Nmap Execution Error: {e}")
                error_embed = NotificationMsg.error_msg(
                    title="Scan Failed",
                    description=f"An unexpected error occurred: {str(e)}"
                )
                return await interaction.followup.send(embed=error_embed)

async def setup(bot):
    await bot.add_cog(NmapScanner(bot))