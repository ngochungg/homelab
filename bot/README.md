# Homelab Operator Discord Bot

A Discord bot for homelab operations and cybersecurity-lab helper commands:

- **Docker management** (list containers, restart/stop, view logs)
- **System monitoring** (CPU/RAM/disk status + periodic alerts)
- **Nmap scanning** (async subprocess wrapper)
- **Reverse shell payload generator** (helper output for labs)
- **TryHackMe stats** (public profile fetch)
- **AI ask** (Gemini API wrapper)

## Requirements

- **Python** 3.10+ recommended
- A Discord application + bot token
- (Optional) **Docker Engine** доступ via `/var/run/docker.sock` for `/docker`
- (Optional) **nmap** installed on the host for `/scan`

## Install

Create a virtualenv and install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
```

If you want to use the **TryHackMe stats** cog, also install `aiohttp`:

```bash
pip install aiohttp
```

## Configuration

### Environment variables

Create a `.env` file in the repo root:

```env
DISCORD_TOKEN=your_discord_bot_token
MY_GUILD_ID=123456789012345678
ADMIN_ID=123456789012345678
NOTIFICATION_CHANNEL_ID=123456789012345678
GOOGLE_API_KEY=your_google_api_key
```

- **`DISCORD_TOKEN`**: Discord bot token
- **`MY_GUILD_ID`**: guild/server ID used to sync application commands
- **`ADMIN_ID`**: user ID allowed to run `/docker`
- **`NOTIFICATION_CHANNEL_ID`**: channel ID for monitor alerts
- **`GOOGLE_API_KEY`**: used by the `/ask` command

### `config.json` (required for monitoring)

`cogs/monitor_bot.py` reads `config.json` from the repo root. Example:

```json
{
  "system": {
    "cpu_threshold": 80,
    "ram_threshold": 80
  },
  "disks": [
    { "name": "root", "path": "/", "threshold": 90 }
  ]
}
```

## Run

```bash
source .venv/bin/activate
python main.py
```

On startup the bot loads all `.py` files in `./cogs/` as extensions and syncs application commands to `MY_GUILD_ID`.

## Commands

- **`/docker`**: interactive Docker container manager (admin-only)
  - Actions: Restart, Stop, Logs
- **`/status`**: current node health (CPU/RAM/disk)
- **`/scan target arguments`**: run `nmap` asynchronously
  - Default args: `-F`
- **`/payload lhost lport shell_type`**: reverse-shell payload helper
- **`/thm_stats username`**: TryHackMe public profile stats
- **`/ask prompt`**: send a prompt to Gemini and return the response

## Notes / Security

- **Nmap**: the target string is sanitized for obvious shell metacharacters; still treat this command as operator-only in untrusted servers.
- **Docker**: requires socket access. If running in a container, you typically need to mount the socket (`-v /var/run/docker.sock:/var/run/docker.sock`) and ensure permissions allow access.
- **Discord limits**: long outputs (e.g., nmap results) are sent as a file attachment when needed.

# discord-bot
# bot
