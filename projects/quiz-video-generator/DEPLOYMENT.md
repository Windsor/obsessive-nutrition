# Deployment Guide

## Local Development (Mac/Linux/Windows)

### Prerequisites
- Python 3.8+
- ffmpeg (install via: `brew install ffmpeg` on Mac, `apt install ffmpeg` on Ubuntu)

### Setup Steps

```bash
# 1. Navigate to project directory
cd quiz-video-generator

# 2. Create virtual environment
python3 -m venv venv

# 3. Activate virtual environment
source venv/bin/activate  # Mac/Linux
# OR
venv\Scripts\activate  # Windows

# 4. Install dependencies
pip install -r requirements.txt

# 5. Initialize database
python3 -c "from app.database import init_db; init_db()"

# 6. Test the setup
python3 test_app.py

# 7. Run the application
python3 app.py
```

Open your browser to `http://localhost:5000`

---

## Ubuntu Server Deployment

### Automated Setup (Recommended)

```bash
# 1. Copy project to server
scp -r quiz-video-generator user@your-server:/tmp/

# 2. SSH into server
ssh user@your-server

# 3. Run setup script
cd /tmp/quiz-video-generator
sudo ./setup.sh
```

The script automatically:
- Installs system dependencies
- Creates virtual environment
- Configures systemd service
- Sets up nginx reverse proxy
- Starts the application

### Manual Setup

If you prefer manual setup or the script fails:

#### 1. Install Dependencies

```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv nginx ffmpeg
```

#### 2. Create Application Directory

```bash
sudo mkdir -p /var/www/quiz-generator
sudo cp -r . /var/www/quiz-generator/
cd /var/www/quiz-generator
```

#### 3. Set Up Python Environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### 4. Initialize Database

```bash
python3 -c "from app.database import init_db; init_db()"
```

#### 5. Set Permissions

```bash
sudo chown -R www-data:www-data /var/www/quiz-generator
sudo chmod -R 755 /var/www/quiz-generator
```

#### 6. Configure systemd Service

```bash
sudo cp deployment/quiz-generator.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable quiz-generator
sudo systemctl start quiz-generator
```

#### 7. Configure nginx

```bash
# Copy nginx config
sudo cp deployment/nginx.conf /etc/nginx/sites-available/quiz-generator

# Enable the site
sudo ln -sf /etc/nginx/sites-available/quiz-generator /etc/nginx/sites-enabled/

# Remove default site
sudo rm -f /etc/nginx/sites-enabled/default

# Test configuration
sudo nginx -t

# Restart nginx
sudo systemctl restart nginx
```

---

## Post-Deployment Configuration

### 1. Update Domain/IP

Edit nginx configuration:
```bash
sudo nano /etc/nginx/sites-available/quiz-generator
```

Change `server_name` to your domain or server IP:
```nginx
server_name your-domain.com;  # or server_name 192.168.1.100;
```

Restart nginx:
```bash
sudo systemctl restart nginx
```

### 2. Configure ElevenLabs API

1. Visit your application in a browser
2. Go to the **Settings** tab
3. Enter your ElevenLabs API key
4. Optionally change the voice ID
5. Click **Save Settings**

### 3. Set Up SSL (Recommended for Production)

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Obtain SSL certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal is configured automatically
```

---

## Service Management

### Check Status
```bash
sudo systemctl status quiz-generator
```

### Start/Stop/Restart
```bash
sudo systemctl start quiz-generator
sudo systemctl stop quiz-generator
sudo systemctl restart quiz-generator
```

### View Logs
```bash
# Real-time logs
sudo journalctl -u quiz-generator -f

# Last 50 lines
sudo journalctl -u quiz-generator -n 50

# Logs with timestamps
sudo journalctl -u quiz-generator --since "1 hour ago"
```

### nginx Logs
```bash
# Error logs
sudo tail -f /var/log/nginx/error.log

# Access logs
sudo tail -f /var/log/nginx/access.log
```

---

## Updating the Application

```bash
# 1. Stop the service
sudo systemctl stop quiz-generator

# 2. Backup database
sudo cp /var/www/quiz-generator/quiz_generator.db /var/www/quiz_generator.db.backup

# 3. Update files
cd /var/www/quiz-generator
sudo git pull  # if using git
# OR manually copy updated files

# 4. Update dependencies
source venv/bin/activate
pip install -r requirements.txt

# 5. Restart service
sudo systemctl start quiz-generator
```

---

## Troubleshooting

### Service Won't Start

```bash
# Check service status
sudo systemctl status quiz-generator

# Check logs for errors
sudo journalctl -u quiz-generator -n 50

# Common issues:
# - Port 5000 already in use
# - Permission issues
# - Missing dependencies
```

### nginx Errors

```bash
# Test nginx configuration
sudo nginx -t

# Check nginx status
sudo systemctl status nginx

# Common issues:
# - Syntax errors in config
# - Port 80 already in use
# - Firewall blocking ports
```

### Video Generation Fails

```bash
# Verify ffmpeg is installed
ffmpeg -version

# Check write permissions
ls -la /var/www/quiz-generator/videos/
ls -la /var/www/quiz-generator/frames/

# Fix permissions if needed
sudo chown -R www-data:www-data /var/www/quiz-generator/videos
sudo chown -R www-data:www-data /var/www/quiz-generator/frames
```

### Database Issues

```bash
# Check database file exists
ls -la /var/www/quiz-generator/quiz_generator.db

# Reinitialize database (WARNING: deletes all data)
cd /var/www/quiz-generator
source venv/bin/activate
python3 -c "from app.database import init_db; init_db()"
```

---

## Firewall Configuration

If using UFW:

```bash
# Allow HTTP
sudo ufw allow 80/tcp

# Allow HTTPS
sudo ufw allow 443/tcp

# Allow SSH (if not already allowed)
sudo ufw allow 22/tcp

# Enable firewall
sudo ufw enable
```

---

## Performance Tuning

### For High Traffic

Edit `/etc/systemd/system/quiz-generator.service`:

```ini
[Service]
# Add more workers
ExecStart=/var/www/quiz-generator/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 app:app
```

Install gunicorn:
```bash
source /var/www/quiz-generator/venv/bin/activate
pip install gunicorn
```

### nginx Configuration

Edit `/etc/nginx/sites-available/quiz-generator`:

```nginx
# Add gzip compression
gzip on;
gzip_types text/plain text/css application/json application/javascript;

# Increase worker connections
worker_connections 1024;
```

---

## Backup Strategy

### Automated Daily Backup

Create `/etc/cron.daily/backup-quiz-generator`:

```bash
#!/bin/bash
BACKUP_DIR="/var/backups/quiz-generator"
mkdir -p $BACKUP_DIR
DATE=$(date +%Y%m%d)

# Backup database
cp /var/www/quiz-generator/quiz_generator.db $BACKUP_DIR/quiz_db_$DATE.db

# Backup videos (optional, can be large)
# tar -czf $BACKUP_DIR/videos_$DATE.tar.gz /var/www/quiz-generator/videos/

# Keep only last 7 days
find $BACKUP_DIR -type f -mtime +7 -delete
```

Make it executable:
```bash
sudo chmod +x /etc/cron.daily/backup-quiz-generator
```

---

## Security Recommendations

1. **Use HTTPS** - Always use SSL certificates in production
2. **Firewall** - Only allow necessary ports (80, 443, 22)
3. **API Keys** - Store ElevenLabs API key securely, don't commit to git
4. **Updates** - Keep system and dependencies updated
5. **Backups** - Regular database backups
6. **File Uploads** - The app validates file types, but consider additional security
7. **Rate Limiting** - Consider adding rate limiting for video generation

---

## Support

For issues:
1. Check application logs: `sudo journalctl -u quiz-generator -f`
2. Check nginx logs: `sudo tail -f /var/log/nginx/error.log`
3. Verify all dependencies are installed
4. Test with: `python3 test_app.py`
5. Check file permissions: `ls -la /var/www/quiz-generator/`
