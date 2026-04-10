import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import aiohttp
import io
import os
import ipaddress
import re
# Utility for consistent error/info messages
from cogs.utils.notification_msg import NotificationMsg

ADMIN_ID = int(os.getenv('ADMIN_ID', 0))

class NmapScanner(commands.Cog):
    """
    Cog for network scanning using Nmap.
    Executes scans asynchronously to prevent bot downtime.
    """
    def __init__(self, bot):
        self.bot = bot

    async def _run_nmap(self, args: list[str], target: str) -> str:
        """Execute nmap with args and return stdout as text."""
        process = await asyncio.create_subprocess_exec(
            "nmap",
            *args,
            target,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()

        if stderr:
            print(f"[DEBUG] Nmap Stderr ({' '.join(args)} {target}): {stderr.decode(errors='replace')}")

        return stdout.decode(errors="replace").strip()

    def _get_sweep_target(self, target: str) -> str | None:
        """
        Build a valid subnet target for `nmap -sn`.
        - If target already includes CIDR, keep it.
        - If target is a single IPv4, convert to /24.
        - Otherwise return None.
        """
        try:
            if "/" in target:
                network = ipaddress.ip_network(target, strict=False)
            else:
                network = ipaddress.ip_network(f"{target}/24", strict=False)
            return str(network)
        except ValueError:
            return None

    def _extract_online_ips(self, sweep_result: str) -> list[str]:
        """
        Parse nmap -sn output and return online IPv4 addresses.
        Handles:
        - Nmap scan report for 10.0.0.5
        - Nmap scan report for host.local (10.0.0.5)
        """
        ip_matches = re.findall(r"Nmap scan report for (?:.+\()?(\d{1,3}(?:\.\d{1,3}){3})\)?", sweep_result)
        # Keep order and remove duplicates
        seen = set()
        ordered_ips = []
        for ip in ip_matches:
            if ip not in seen:
                seen.add(ip)
                ordered_ips.append(ip)
        return ordered_ips

    def _safe_filename(self, value: str) -> str:
        """Return a filesystem-safe filename stem."""
        safe = re.sub(r"[^A-Za-z0-9._-]+", "_", value)
        return safe.strip("._-") or "scan_output"

    async def _send_to_nmap_channel(
        self,
        interaction: discord.Interaction,
        message: str,
        filename_stem: str = "scan_output"
    ) -> None:
        # Prefer direct send to Discord channel `nmap_scan`.
        target_channel = None
        if interaction.guild:
            target_channel = discord.utils.get(interaction.guild.text_channels, name="nmap_scan")

        if target_channel:
            if len(message) > 1900:
                filename = f"{self._safe_filename(filename_stem)}.txt"
                file_result = io.BytesIO(message.encode("utf-8"))
                await target_channel.send(
                    content=f"📄 Output too long, sending as file: `{filename}`",
                    file=discord.File(fp=file_result, filename=filename)
                )
            else:
                await target_channel.send(message)
            return

        # Fallback to existing HTTP bridge when channel is not found.
        payload = {
            "type": "Nmap Scanner",
            "message": message,
            "to_channel": "nmap_scan",
        }
        async with aiohttp.ClientSession() as session:
            async with session.post("http://10.8.0.1:5000/message", json=payload):
                pass

    @app_commands.command(name="scan", description="Scan a network for open ports and services")
    @app_commands.describe(
        target="IPv4 or subnet (e.g., 10.8.0.1 or 10.8.0.0/24)",
        arguments="Reserved for compatibility (ignored by multi-stage scan flow)"
    )
    async def scan_network(self, interaction: discord.Interaction, target: str, arguments: str = "-F"):

        # Admin Check
        if interaction.user.id != ADMIN_ID:
            embed = NotificationMsg.error_msg(
                title="Permission Denied",
                description="You don't have permission to manage Docker containers."
            )
            
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        """
        Logic: Executes nmap binary via asyncio subprocess.
        Security Note: Arguments are restricted to prevent command injection.
        """

        # 1. PREVENT TIMEOUTS
        # Scans take time; defer() is mandatory here.
        await interaction.response.defer()

        # TODO: Add a cheat sheet for nmap
        # if 1 == 1:
        #     embed = discord.Embed(
        #         title="👁️ Nmap Cheat Sheet (Hacker's Eye)",
        #         description="Network scan commands from basics to real-world combos.\n*Replace `<IP>` with your target's IP address.*",
        #         color=0xff6600
        #     )

        #     # Block 1: Basic scans
        #     embed.add_field(
        #         name="📡 1. Ping Sweep & Port Scan",
        #         value="```bash\n"
        #             "nmap -sn 10.7.0.0/24   # Ping sweep: find live hosts on subnet\n"
        #             "nmap -F <IP>           # Fast: top 100 common ports\n"
        #             "nmap -p- <IP>          # All 65,535 TCP ports (slow but thorough)\n"
        #             "nmap -p 22,80,443 <IP> # Only the ports you list\n"
        #             "```",
        #         inline=False
        #     )

        #     # Block 2: Stealth
        #     embed.add_field(
        #         name="🥷 2. Stealth & Evasion",
        #         value="```bash\n"
        #             "nmap -sS <IP>          # SYN scan (half-open; quieter on targets)\n"
        #             "nmap -Pn <IP>          # Skip host discovery (when ICMP is blocked)\n"
        #             "nmap -D RND:10 <IP>    # Decoy: blend scan among random decoy IPs\n"
        #             "```",
        #         inline=False
        #     )

        #     # Block 3: Enumeration & NSE
        #     embed.add_field(
        #         name="🔍 3. Enumeration & NSE Scripts",
        #         value="```bash\n"
        #             "nmap -sV <IP>          # Service version detection\n"
        #             "nmap -O <IP>           # OS fingerprinting\n"
        #             "nmap -A <IP>           # Aggressive: OS, version, script, traceroute\n"
        #             "nmap --script vuln <IP># Run vuln scripts (CVE-style checks)\n"
        #             "nmap --script smb-os-discovery <IP>\n"
        #             "```",
        #         inline=False
        #     )

        #     # Block 4: Combos
        #     embed.add_field(
        #         name="🔥 4. Real-World Combos",
        #         value="**Combo 1: Quick recon (fast & useful)**\n"
        #             "```bash\n"
        #             "nmap -sS -sV -T4 -Pn <IP>\n"
        #             "```\n"
        #             "**Combo 2: Full pass (max detail, save to file)**\n"
        #             "```bash\n"
        #             "nmap -p- -sC -sV -Pn <IP> -oN scan_result.txt\n"
        #             "```",
        #         inline=False
        #     )
        #     return await interaction.followup.send(embed=embed)

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
            _ = arguments  # Kept for backward-compatible slash-command signature.
            sweep_target = self._get_sweep_target(target)
            if not sweep_target:
                error_embed = NotificationMsg.error_msg(
                    title="Invalid Target",
                    description="Target must be an IPv4 address or subnet (CIDR), e.g. 10.8.0.1 or 10.8.0.0/24."
                )
                return await interaction.followup.send(embed=error_embed)

            # Step A: Discover live hosts on target/24 (or provided CIDR)
            sweep_result = await self._run_nmap(["-sn"], sweep_target)
            if not sweep_result:
                error_embed = NotificationMsg.error_msg(
                    title="Scan Failed",
                    description="No output received from `nmap -sn`."
                )
                return await interaction.followup.send(embed=error_embed)

            online_ips = self._extract_online_ips(sweep_result)
            online_text = "\n".join(f"- {ip}" for ip in online_ips) if online_ips else "No live hosts found."
            await self._send_to_nmap_channel(
                interaction,
                f"[A] Host discovery result for `{sweep_target}`\n\n"
                f"{sweep_result}\n\n"
                f"Live IPs:\n{online_text}",
                filename_stem=f"stage_a_{sweep_target}"
            )

            if not online_ips:
                info_embed = NotificationMsg.info_msg(
                    title="Scan Complete",
                    description=f"No live hosts found in `{sweep_target}`. Step B/C skipped."
                )
                return await interaction.followup.send(embed=info_embed)

            # Step B: SYN + version scan for each live IP
            for live_ip in online_ips:
                stage_b_result = await self._run_nmap(["-sS", "-sV", "-T4", "-Pn"], live_ip)
                await self._send_to_nmap_channel(
                    interaction,
                    f"[B] SYN+Version scan for `{live_ip}`\n\n{stage_b_result or 'No output.'}",
                    filename_stem=f"stage_b_{live_ip}"
                )

            # Step C: Vulnerability scripts for each live IP
            for live_ip in online_ips:
                stage_c_result = await self._run_nmap(["--script", "vuln"], live_ip)
                await self._send_to_nmap_channel(
                    interaction,
                    f"[C] Vulnerability script scan for `{live_ip}`\n\n{stage_c_result or 'No output.'}",
                    filename_stem=f"stage_c_{live_ip}"
                )

            info_embed = NotificationMsg.info_msg(
                title="Scan Complete",
                description=(
                    f"Completed 3-stage scan flow for `{sweep_target}`.\n"
                    f"Live hosts found: `{len(online_ips)}`\n"
                    "All results were sent to `nmap_scan`."
                ),
            )
            await interaction.followup.send(embed=info_embed)

        except Exception as e:
                print(f"[ERROR] Nmap Execution Error: {e}")
                error_embed = NotificationMsg.error_msg(
                    title="Scan Failed",
                    description=f"An unexpected error occurred: {str(e)}"
                )
                return await interaction.followup.send(embed=error_embed)

async def setup(bot):
    await bot.add_cog(NmapScanner(bot))