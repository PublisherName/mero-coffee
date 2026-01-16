## Create a gunicorn service

```bash
sudo nano /etc/systemd/system/gunicorn.service
```

```text
    [Unit]
    Description=gunicorn daemon
    Requires=gunicorn.socket
    After=network.target

    [Service]
    User=ubuntu
    Group=www-data
    WorkingDirectory=/home/ubuntu/django/MeroCoffee
    ExecStart=/home/ubuntu/django/MeroCoffee/.venv/bin/gunicorn --workers >

    [Install]
    WantedBy=multi-user.target
```

```bash
sudo systemctl start gunicorn
sudo systemctl enable gunicorn
sudo systemctl status gunicorn
```

## Nginx server block configuration:

```bash
cp ngnix/merocoffee /etc/nginx/sites-available/merocoffee

sudo ln -s /etc/nginx/sites-available/merocoffee /etc/

nginx/sites-enabled

sudo nginx -t

sudo systemctl restart nginx

```
## SSL using certbot

```bash
sudo apt install certbot python3-certbot-nginx

sudo certbot --nginx -d coffe.subashghimire.info.np

sudo nginx -t

sudo systemctl restart nginx
```

### UFW firewall update

```bash
sudo ufw allow 'Nginx Full'
sudo ufw reload
```

### File permission to server static
```bash
sudo chown -R www-data:www-data /home/ubuntu/django/MeroCoffee/public /home/ubuntu/django/MeroCoffee/media

sudo chmod -R 755 /home/ubuntu/django/MeroCoffee/public /home/ubuntu/django/MeroCoffee/media

sudo chmod 755 /home/ubuntu/django/MeroCoffee /home/ubuntu
```

### Suppress warning (non-optimal hash table for proxy headers)
```bash
sudo nano /etc/nginx/nginx.conf
```

```text
http {
    proxy_headers_hash_max_size 1024;
    proxy_headers_hash_bucket_size 128;
    # ... rest
}
```
```bash
sudo nginx -t && sudo systemctl reload nginx
```

### Reflect env changes:

```bash
sudo systemctl daemon-reload
sudo systemctl restart gunicorn.service
sudo systemctl reload nginx
```

Keep the branch up to date:

```bash
git fetch origin
git reset --hard origin/develop
```
### Create celery worker
```bash
sudo nano /etc/systemd/system/merocoffee-celery.service
```
```text
[Unit]
Description=Celery service for MeroCoffee
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/home/ubuntu/django/MeroCoffee
ExecStart=/home/ubuntu/django/MeroCoffee/.venv/bin/celery -A root worker -l info
Restart=always

[Install]
WantedBy=multi-user.target
```

### Reload and start celery

```bash
sudo systemctl daemon-reload && sudo systemctl start merocoffee-celery && sudo systemctl enable merocoffee-celery
```
