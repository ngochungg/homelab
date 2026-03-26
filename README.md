# homelab

This repo is a collection of Docker Compose stacks for the services in this homelab.
Most HTTP(S) services are exposed via `traefik/` and Cloudflare tunnels, under the `catverse.dev` domain.

## What to do (recommended order)

1. Create the external Docker networks (once on the host):

```bash
docker network create frontend
docker network create backend
```

2. Create the required `.env` files (see the next section).

3. Start Traefik first (required for most domain-based URLs):

```bash
cd traefik
docker compose up -d
```

4. Start databases first (because some apps depend on them):

```bash
cd mysql
docker compose up -d

cd postgres
docker compose up -d
```

5. Start the rest of the stacks (each in its own directory):

```bash
cd gitea && docker compose up -d
cd portainer && docker compose up -d
cd duplicati && docker compose up -d
cd adguard && docker compose up -d
cd nginx && docker compose up -d
cd minecraft && docker compose up -d
cd coolercontrol && docker compose up -d
cd bot && docker compose up -d
```

Note: Stardew Valley has its own setup requirements and is best followed via its sub-README:
`stardew_valley/stardew-multiplayer-docker/README.md`.

## Which `.env` goes where (and what keys)

Docker Compose will read `.env` in the same directory as the `compose.yml` for variable substitution (where those `${VAR}` placeholders exist).
Some stacks also reference `.env` explicitly using `env_file`.

`traefik/.env` (required)
- `TRAEFIK_DASHBOARD_CREDENTIALS` (basic auth for dashboard, usually `user:pass`)
- `CF_DNS_API_TOKEN` (Cloudflare DNS provider token for the ACME challenge)
- `TUNNEL_TOKEN` (Cloudflare tunnel token)

`bot/.env` (required if you run the Discord bot)
- `DISCORD_TOKEN`
- `MY_GUILD_ID`
- `ADMIN_ID`
- `NOTIFICATION_CHANNEL_ID`
- `GOOGLE_API_KEY`

`mysql/.env` (required for MySQL + phpMyAdmin)
- `MYSQL_ROOT_PASSWORD`
- `MYSQL_USER`
- `MYSQL_PASSWORD`
- `MYSQL_DATABASE`
- `MYSQL_HOST` (what phpMyAdmin should connect to; usually `mysql` or `mysql:3306`)

`postgres/.env` (required for PostgreSQL + pgAdmin)
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `POSTGRES_DB`

`duplicati/.env` (required for backups)
- `SETTINGS_ENCRYPTION_KEY`
- `DUPLICATI__WEBSERVICE_PASSWORD`

`gitea/.env` (required if you run the Gitea runner)
- `GITEA_RUNNER_REGISTRATION_TOKEN`

`stardew_valley/stardew-multiplayer-docker/.env` (required for Steam build automation)
- `STEAM_USER`
- `STEAM_PASS`
- `STEAM_GUARD`

Optional Stardew env vars
- Many other mod settings are referenced as `${VAR-default}` in `stardew_valley/.../compose.yml`; you can omit them if you want the defaults.

## Service URLs

- Traefik dashboard: `https://traefik.catverse.dev`
- AdGuard Home UI: `https://ad.catverse.dev`
- Nginx example UI: `https://nginx.catverse.dev`
- MySQL: `https://mysql.catverse.dev` (phpMyAdmin)
- PostgreSQL: `https://pgadmin.catverse.dev`
- Duplicati: `https://backup.catverse.dev`
- Gitea: `https://git.catverse.dev`
- Portainer: `https://portal.catverse.dev`

DNS note: AdGuard DNS listens on the host IP/ports defined in `adguard/compose.yml` (currently mapped to `10.7.0.2`).

