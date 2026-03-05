#!/bin/bash

###############################################################################
# Quiz Video Generator - Ubuntu Deployment Script
###############################################################################

set -e

echo "========================================="
echo "Quiz Video Generator - Setup Script"
echo "========================================="

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root (sudo ./setup.sh)"
    exit 1
fi

# Update system
echo "Updating system packages..."
apt-get update
apt-get upgrade -y

# Install dependencies
echo "Installing dependencies..."
apt-get install -y python3 python3-pip python3-venv nginx ffmpeg

# Create application directory
APP_DIR="/var/www/quiz-generator"
echo "Creating application directory at $APP_DIR..."
mkdir -p $APP_DIR

# Copy application files
echo "Copying application files..."
cp -r . $APP_DIR/
cd $APP_DIR

# Create virtual environment
echo "Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "Installing Python packages..."
pip install --upgrade pip
pip install -r requirements.txt

# Create necessary directories
echo "Creating application directories..."
mkdir -p videos frames music static/uploads

# Initialize database
echo "Initializing database..."
python3 -c "from app.database import init_db; init_db()"

# Set permissions
echo "Setting permissions..."
chown -R www-data:www-data $APP_DIR
chmod -R 755 $APP_DIR

# Install systemd service
echo "Installing systemd service..."
cp deployment/quiz-generator.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable quiz-generator
systemctl start quiz-generator

# Configure nginx
echo "Configuring nginx..."
cp deployment/nginx.conf /etc/nginx/sites-available/quiz-generator
ln -sf /etc/nginx/sites-available/quiz-generator /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test nginx configuration
nginx -t

# Restart nginx
systemctl restart nginx

# Check service status
echo ""
echo "========================================="
echo "Installation Complete!"
echo "========================================="
echo ""
echo "Service Status:"
systemctl status quiz-generator --no-pager || true
echo ""
echo "The application should now be running on:"
echo "  http://$(hostname -I | awk '{print $1}')"
echo ""
echo "Useful commands:"
echo "  sudo systemctl status quiz-generator    # Check service status"
echo "  sudo systemctl restart quiz-generator   # Restart service"
echo "  sudo journalctl -u quiz-generator -f    # View logs"
echo ""
echo "Don't forget to:"
echo "  1. Update the domain in /etc/nginx/sites-available/quiz-generator"
echo "  2. Configure your ElevenLabs API key in the Settings tab"
echo "  3. Set up SSL with certbot if using a domain"
echo ""
