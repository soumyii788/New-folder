# Production Deployment Guide

## Prerequisites
- A cloud instance (AWS EC2, DigitalOcean Droplet, Linode) running Ubuntu 22.04 LTS.
- Minimum 4GB RAM, 2 vCPUs recommended for Postgres + Redis + Python combo.
- A domain name pointing to your server's IP address.

## 1. Initial Server Setup
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install docker.io docker-compose -y
sudo systemctl enable docker
sudo systemctl start docker
```

## 2. Clone the Repository
```bash
git clone <your-repo-url> /opt/scrap_marketplace
cd /opt/scrap_marketplace
```

## 3. Environment Variables
Copy the example env file and fill in production-level secrets.
```bash
cp .env.example .env
nano .env
```
*Ensure `DEBUG=False` and `ALLOWED_HOSTS` includes your domain (e.g., `api.scrapexample.com`).*

## 4. Build and Start the Docker Services
```bash
sudo docker-compose up --build -d
```
Verify everything is running smoothly:
```bash
sudo docker-compose ps
```

## 5. Migrate Database & Collect Static
Initialize the database schemas inside the Docker container:
```bash
sudo docker-compose exec web python backend/manage.py migrate
sudo docker-compose exec web python backend/manage.py collectstatic --noinput
```

## 6. Create Admin User
```bash
sudo docker-compose exec web python backend/manage.py createsuperuser
```

## 7. Configuring HTTPS (SSL/TLS)
For production, you need SSL. You can use Certbot inside the host to proxy to the Nginx container, or add an Nginx-Certbot container. 

Alternatively, if you're using AWS, you can put an Application Load Balancer (ALB) with ACM certificates in front of your server, terminating SSL at the load balancer.

### Example: Host-Level Certbot Reverse Proxy
If running Nginx on the host directly instead of dockerizing it:
1. `sudo apt install certbot python3-certbot-nginx`
2. Configure local nginx to point to `localhost:8000` (Web) and `localhost:8001` (WebSocket).
3. `sudo certbot --nginx -d api.scrapexample.com`

## 8. Logs & Monitoring
Monitor Gunicorn and Django outputs:
```bash
sudo docker-compose logs -f web
```
Monitor Celery Background Tasks:
```bash
sudo docker-compose logs -f celery_worker
```
