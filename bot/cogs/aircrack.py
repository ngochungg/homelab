from cogs.utils import ANSI_erase
import discord
import asyncio
from discord.ext import commands
from discord import app_commands
import os
import re
import signal

from cogs.utils.notification_msg import NotificationMsg
from cogs.utils.ANSI_erase import ANSI_erase

PATH_CAP = os.getenv("CAP_FILE_PATH")
PATH_WORDLIST = os.getenv("WORDLIST_PATH")

class AircrackView(discord.ui.View):
    def __init__(self, process, interaction):
        super().__init__(timeout=None)
        self.process = process
        self.interaction = interaction

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.danger)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.process.returncode is None:
            try:
                pgid = self.process.pid
                os.killpg(pgid, signal.SIGKILL)

                button.disabled = True
                button.label = "Cancelled"
                button.style = discord.ButtonStyle.secondary

                await interaction.response.edit_message(content="Aircrack process cancelled.", view=self)

            except Exception as e:
                try:
                    self.process.kill()
                    button.disabled = True
                    button.label = "Cancelled"
                    button.style = discord.ButtonStyle.secondary

                    await interaction.response.edit_message(content="Aircrack process cancelled.", view=self)

                except:
                    await interaction.response.edit_message(content="Aircrack process failed to cancel.", view=self)

        else:
            button.disabled = True
            button.label = "Cancelled"
            button.style = discord.ButtonStyle.secondary

            await interaction.response.edit_message(content="Aircrack process already completed.", view=self)

class Aircrack(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.path_cap = os.getenv("CAP_FILE_PATH")
        self.path_wordlist = os.getenv("WORDLIST_PATH")

    async def file_autocomplete(self, current: str, target_path: str, extensions: tuple) -> list[app_commands.Choice[str]]:
        if not target_path or not os.path.exists(target_path):
            return [app_commands.Choice(name=f"No files found. {target_path}", value="error")]
        
        try:
            files = [f for f in os.listdir(target_path) if f.endswith(extensions)]
            choices = [
                app_commands.Choice(name=f, value=f) 
                for f in files if current.lower() in f.lower()
            ]
            return choices[:25]
        except Exception as exception:
            return [app_commands.Choice(name=f"Error: {exception}", value="error")]

    async def wordlist_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        return await self.file_autocomplete(current, self.path_wordlist, ('.txt', '.lst', '.dict'))

    async def cap_file_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        return await self.file_autocomplete(current, self.path_cap, ('.cap', '.pcap', '.hccapx'))

    @app_commands.command(name="aircrack", description="Aircrack a network")
    @app_commands.describe(
        cap_file="The file containing the capture",
        wordlist="The wordlist to use"
    )
    @app_commands.autocomplete(cap_file=cap_file_autocomplete)
    @app_commands.autocomplete(wordlist=wordlist_autocomplete)
    async def aircrack(self,interaction: discord.Interaction, cap_file: str = None, wordlist: str = None):
        await interaction.response.defer(thinking=True)

        full_cap = os.path.join(self.path_cap, cap_file)
        full_word = os.path.join(self.path_wordlist, wordlist)

        try:
            process = await asyncio.create_subprocess_exec(
                "aircrack-ng", full_cap, "-w", full_word,
                stdout=asyncio.subprocess.PIPE, 
                stderr=asyncio.subprocess.PIPE,
                start_new_session=True
            )

            view = AircrackView(process, interaction)
            await interaction.followup.send(content=f"🚀 Cracking `{cap_file}` with `{wordlist}`", view=view)

            stdout, stderr = await process.communicate()
            raw_output = (stdout.decode() + stderr.decode()).strip()

            clean_text = ANSI_erase.erase_ansi(raw_output)

            for item in view.children:
                item.disabled = True
            
            key_match = re.search(r"KEY FOUND! \[ (.+?) \]", clean_text)
            if key_match:
                key = key_match.group(1)
                desc = f"🔑 Key found: {key}"
                embed = NotificationMsg.success_msg(title="Aircrack Result", description=desc)
                await interaction.edit_original_response(content="Aircrack process completed.", embed=embed, view=view)

            elif "KEY NOT FOUND" in clean_text:
                desc = f"Key not found"
                embed = NotificationMsg.error_msg(title="Aircrack Result", description=desc)
                await interaction.edit_original_response(content="Aircrack process completed.", embed=embed, view=view)

            # Exit code khi bị SIGKILL thường là -9
            elif process.returncode in [-9, 9, -15, 15]:
                await interaction.edit_original_response(content="Aircrack process cancelled.", embed=None, view=view)

            else:
                error_log = clean_text[:1000]
                embed = NotificationMsg.error_msg(title="Lỗi Thực Thi", description=f"```\n{error_log}\n```")
                await interaction.edit_original_response(content="Aircrack process failed.", embed=embed, view=view)
        
        except Exception as e:
            if view:
                await interaction.edit_original_response(content=f"🚨 Aircrack process failed: {e}", view=view)
            else:
                await interaction.edit_original_response(content=f"🚨 Aircrack process failed: {e}")

async def setup(bot):
    await bot.add_cog(Aircrack(bot))