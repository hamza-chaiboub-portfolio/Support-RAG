# Deployment Guide

## Prerequisites
- Docker and Docker Compose installed
- Node.js 20+ (for local development)

## Frontend Deployment

The frontend is containerized using Docker and served via Nginx. It is integrated into the main `docker-compose.yml` file.

### Build and Run
To build and run the entire stack including the frontend:

```bash
cd docker
docker-compose up -d --build
```

The frontend will be available at `http://localhost:3001`.

### Configuration
The frontend configuration is handled via environment variables built into the Docker image or served via Nginx proxying.

- **API URL**: The Nginx configuration (`frontend/nginx.conf`) proxies requests from `/api/v1/` to the backend service (`http://backend:8000/api/v1/`). This avoids CORS issues and hardcoded URLs.

### Manual Build (Local)
If you need to build the frontend locally without Docker:

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Build the project:
   ```bash
   npm run build
   ```

4. The output will be in the `dist` folder, ready to be served by any static file server.

## Troubleshooting
- **CORS Errors**: Ensure you are accessing the app via the Nginx port (3001) so that API requests are proxied correctly.
- **Login Issues**: Check the network tab. If `/api/v1/auth/login` fails, ensure the backend service is running and accessible from the frontend container.
