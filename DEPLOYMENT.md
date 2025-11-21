# MeroCoffee Deployment Guide

This guide covers deploying MeroCoffee to production with PostgreSQL, security configurations, and best practices.

---

## Prerequisites

- Python 3.13+
- PostgreSQL 12+ (for production)
- Redis (optional, for future caching/Celery)
- Web server (nginx recommended)
- Process manager (systemd, supervisor, or Docker)

---

## Environment Setup

### 1. Clone and Install Dependencies

```bash
git clone https://github.com/PublisherName/MeroCoffee.git
cd MeroCoffee
uv sync --frozen
```

### 2. Configure Environment Variables

Create a `.env` file based on `.env.example`:

```bash
cp .env.example .env
```

Edit `.env` with production values:

```env
# CRITICAL: Set to False in production
DEBUG=False

# Generate a secure secret key
# Run: python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
DJANGO_SECRET_KEY=your-generated-secret-key-here

# Your production domain(s)
DJANGO_ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Production site URL
SITE_BASE_URL=https://yourdomain.com

# PostgreSQL Database
DATABASE_URL=postgresql://username:password@localhost:5432/merocoffee

# Email Configuration (example with Gmail)
SMTP_URL=smtp://your-email@gmail.com:your-app-password@smtp.gmail.com:587?_default_from_email=noreply@yourdomain.com

# Token salt for email verification
# Run: python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
TOKEN_SALT=your-generated-token-salt-here

# Token expiration (hours)
TOKEN_EXPIRATION_HOURS=48

# Log directory
LOG_DIR=logs

# Security (production only)
SECURE_SSL_REDIRECT=True
```

---

## Database Setup

### PostgreSQL Installation

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

**macOS:**
```bash
brew install postgresql@16
brew services start postgresql@16
```

### Create Database and User

```bash
# Access PostgreSQL
sudo -u postgres psql

# Create database and user
CREATE DATABASE merocoffee;
CREATE USER merocoffee_user WITH PASSWORD 'secure_password_here';
ALTER ROLE merocoffee_user SET client_encoding TO 'utf8';
ALTER ROLE merocoffee_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE merocoffee_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE merocoffee TO merocoffee_user;

# Exit PostgreSQL
\q
```

### Run Migrations

```bash
# Test database connection
uv run python manage.py check --database default

# Run migrations
uv run python manage.py migrate

# Create superuser
uv run python manage.py createsuperuser
```

---

## Static Files

### Collect Static Files

```bash
uv run python manage.py collectstatic --no-input
```

Static files will be collected to the `public/` directory and served by WhiteNoise in production.

---

## Security Checklist

Before deploying to production, verify:

- [ ] `DEBUG=False` in `.env`
- [ ] `DJANGO_SECRET_KEY` is set to a unique, random value
- [ ] `DJANGO_ALLOWED_HOSTS` includes your domain(s)
- [ ] `TOKEN_SALT` is set to a unique, random value
- [ ] `DATABASE_URL` points to PostgreSQL (not SQLite)
- [ ] HTTPS is configured (SSL certificate installed)
- [ ] `SECURE_SSL_REDIRECT=True` in `.env`
- [ ] Email SMTP settings are configured
- [ ] Firewall rules are configured
- [ ] Database backups are scheduled

### Run Django Security Check

```bash
uv run python manage.py check --deploy
```

This command will warn you about any security issues.

---

## Deployment Options

### Option 1: Traditional Server (systemd + nginx)

#### 1. Install nginx

```bash
sudo apt install nginx
```

#### 2. Create systemd service

Create `/etc/systemd/system/merocoffee.service`:

```ini
[Unit]
Description=MeroCoffee Gunicorn Service
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/MeroCoffee
Environment="PATH=/path/to/MeroCoffee/.venv/bin"
ExecStart=/path/to/MeroCoffee/.venv/bin/gunicorn root.wsgi:application --bind 127.0.0.1:8000 --workers 4

[Install]
WantedBy=multi-user.target
```

#### 3. Configure nginx

Create `/etc/nginx/sites-available/merocoffee`:

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    # SSL Configuration
    ssl_certificate /path/to/ssl/cert.pem;
    ssl_certificate_key /path/to/ssl/key.pem;

    # Security headers
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Static files
    location /static/ {
        alias /path/to/MeroCoffee/public/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Media files
    location /media/ {
        alias /path/to/MeroCoffee/media/;
        expires 7d;
    }

    # Proxy to Gunicorn
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

#### 4. Enable and start services

```bash
# Enable nginx site
sudo ln -s /etc/nginx/sites-available/merocoffee /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Enable and start gunicorn service
sudo systemctl enable merocoffee
sudo systemctl start merocoffee
sudo systemctl status merocoffee
```

---

### Option 2: Docker Deployment

#### 1. Build Docker image

```bash
docker build -t merocoffee:latest .
```

#### 2. Run with docker-compose

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  db:
    image: postgres:16
    environment:
      POSTGRES_DB: merocoffee
      POSTGRES_USER: merocoffee_user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  web:
    image: merocoffee:latest
    command: gunicorn root.wsgi:application --bind 0.0.0.0:8000 --workers 4
    volumes:
      - static_volume:/app/public
      - media_volume:/app/media
    ports:
      - "8000:8000"
    env_file:
      - .env
    depends_on:
      - db
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - static_volume:/static:ro
      - media_volume:/media:ro
      - /etc/letsencrypt:/etc/letsencrypt:ro
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - web
    restart: unless-stopped

volumes:
  postgres_data:
  static_volume:
  media_volume:
```

#### 3. Deploy

```bash
docker-compose -f docker-compose.prod.yml up -d
```

---

## SSL Certificate (Let's Encrypt)

### Install Certbot

```bash
sudo apt install certbot python3-certbot-nginx
```

### Obtain Certificate

```bash
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

Certbot will automatically configure nginx for HTTPS.

### Auto-renewal

```bash
# Test renewal
sudo certbot renew --dry-run

# Renewal is automatic via systemd timer
sudo systemctl status certbot.timer
```

---

## Monitoring and Maintenance

### View Logs

```bash
# Application logs
tail -f logs/custom.log
tail -f logs/django_error.log

# Systemd service logs
sudo journalctl -u merocoffee -f

# nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### Database Backups

Create a backup script `/usr/local/bin/backup-merocoffee.sh`:

```bash
#!/bin/bash
BACKUP_DIR="/backups/merocoffee"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup PostgreSQL
pg_dump -U merocoffee_user merocoffee | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# Backup media files
tar -czf $BACKUP_DIR/media_$DATE.tar.gz /path/to/MeroCoffee/media/

# Keep only last 30 days of backups
find $BACKUP_DIR -type f -mtime +30 -delete

echo "Backup completed: $DATE"
```

Make it executable and add to cron:

```bash
chmod +x /usr/local/bin/backup-merocoffee.sh

# Add to crontab (daily at 2 AM)
0 2 * * * /usr/local/bin/backup-merocoffee.sh
```

---

## Performance Optimization

### Database Connection Pooling

Already configured in `settings.py`:
- `conn_max_age=600` - Connections persist for 10 minutes
- `conn_health_checks=True` - Verify connections before use

### Gunicorn Workers

Calculate optimal workers:
```
workers = (2 × CPU_cores) + 1
```

For a 2-core server:
```bash
gunicorn root.wsgi:application --bind 0.0.0.0:8000 --workers 5
```

### Static File Caching

WhiteNoise is configured to serve static files with compression and caching headers automatically.

---

## Troubleshooting

### Database Connection Issues

```bash
# Test PostgreSQL connection
psql -U merocoffee_user -d merocoffee -h localhost

# Check DATABASE_URL format
echo $DATABASE_URL
```

### Static Files Not Loading

```bash
# Recollect static files
uv run python manage.py collectstatic --clear --no-input

# Check nginx static file path
sudo nginx -t
```

### 500 Internal Server Error

```bash
# Check application logs
tail -n 100 logs/django_error.log

# Check gunicorn service
sudo systemctl status merocoffee
sudo journalctl -u merocoffee -n 50
```

### Email Not Sending

```bash
# Test email configuration
uv run python manage.py shell
>>> from django.core.mail import send_mail
>>> send_mail('Test', 'Test message', 'from@example.com', ['to@example.com'])
```

---

## Updating the Application

```bash
# Pull latest changes
git pull origin main

# Install new dependencies
uv sync --frozen

# Run migrations
uv run python manage.py migrate

# Collect static files
uv run python manage.py collectstatic --no-input

# Restart service
sudo systemctl restart merocoffee
```

---

## Support

For issues or questions:
- GitHub Issues: https://github.com/PublisherName/MeroCoffee/issues
- Email: event@subashghimire.info.np

---

## Security Reporting

If you discover a security vulnerability, please email event@subashghimire.info.np directly. Do not create a public issue.
