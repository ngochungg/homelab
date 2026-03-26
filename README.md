# Homelab

This repository contains Docker Compose stacks for the homelab services I run.
Most “web” services are exposed via `traefik/` (Traefik) and Cloudflare, using the `catverse.dev` domain.

## Prerequisites

- Docker Engine + Docker Compose v2
- An external docker network named `frontend`
- (Optional, but required by some stacks) an external docker network named `backend`
- (For Traefik) a `.env` file inside `traefik/` with:
  - `TRAEFIK_DASHBOARD_CREDENTIALS`
  - `CF_DNS_API_TOKEN`
  - `TUNNEL_TOKEN`

## Quick start

1. Create the external networks (run once):

```bash
docker network create frontend
docker network create backend
```

2. Start Traefik first:

```bash
(cd traefik && docker compose up -d)
```

3. Start any other service stack from its directory:

```bash
(cd adguard && docker compose up -d)
```

## Services

- `traefik/`: Traefik reverse proxy + Cloudflare tunnel
  - Traefik dashboard: `https://traefik.catverse.dev`
- `adguard/`: AdGuard Home DNS filtering
  - Web UI: `https://ad.catverse.dev`
  - DNS listens on the host IP configured in `adguard/compose.yml` (currently `10.7.0.2`)
- `nginx/`: Nginx (Traefik-exposed example)
  - `https://nginx.catverse.dev`
- `mysql/`: MySQL + phpMyAdmin
  - `https://mysql.catverse.dev`
- `postgres/`: PostgreSQL + pgAdmin
  - `https://pgadmin.catverse.dev`
- `duplicati/`: Duplicati backups
  - `https://backup.catverse.dev`
- `gitea/`: Gitea + Gitea runner
  - `https://git.catverse.dev`
- `portainer/`: Portainer CE
  - `https://portal.catverse.dev`
- `minecraft/`: Minecraft server (direct ports, not Traefik-based)
- `coolercontrol/`: coolercontrol hardware agent
- `stardew_valley/stardew-multiplayer-docker/`: Stardew Valley multiplayer docker project (see its `README.md`)

## Notes

- Many `compose.yml` files expect the external `frontend` network so Traefik can route traffic.
- Services that use environment variables will need those set either in each directory’s `.env` (if referenced) or via your shell environment.
