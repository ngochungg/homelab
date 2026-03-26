# Portfolio Docker Setup

This document explains how to run the portfolio application using Docker.

## Prerequisites

- Docker installed on your system
- Docker Compose (usually comes with Docker Desktop)

## Quick Start

### Production Build
```bash
# Build and run the production version
npm run docker:prod

# Or manually:
docker-compose up portfolio
```

### Development Build
```bash
# Run development version with hot reload
npm run docker:dev

# Or manually:
docker-compose --profile dev up portfolio-dev
```

## Manual Docker Commands

### Build the Docker Image
```bash
# Build production image
docker build -t portfolio .

# Build development image
docker build -f Dockerfile.dev -t portfolio-dev .
```

### Run Containers
```bash
# Run production container
docker run -p 3000:3000 portfolio

# Run development container
docker run -p 3001:3000 -v $(pwd):/app -v /app/node_modules portfolio-dev
```

## Docker Services

### Production Service (`portfolio`)
- **Port**: 3000
- **Environment**: Production
- **Features**: Optimized build, served with `serve`
- **Access**: http://localhost:3000

### Development Service (`portfolio-dev`)
- **Port**: 3001
- **Environment**: Development
- **Features**: Hot reload, volume mounting
- **Access**: http://localhost:3001

## Docker Compose Profiles

- **Default**: Runs production service
- **Dev**: Runs development service with hot reload

## Useful Commands

```bash
# Stop all services
docker-compose down

# Rebuild and start
docker-compose up --build

# View logs
docker-compose logs -f

# Remove containers and volumes
docker-compose down -v

# Clean up Docker system
docker system prune
```

## Troubleshooting

### Port Already in Use
If port 3000 is already in use, modify the port mapping in `docker-compose.yml`:
```yaml
ports:
  - "3001:3000"  # Change 3001 to any available port
```

### Permission Issues (Linux/macOS)
If you encounter permission issues with volume mounting:
```bash
sudo chown -R $USER:$USER .
```

### Node Modules Issues
If you have issues with node_modules in development:
```bash
docker-compose down -v
docker-compose --profile dev up portfolio-dev
```
