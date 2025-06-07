# ContactPlus Production Deployment Guide

## 🚀 Production Deployment

### Prerequisites
- Linux server with Docker and Docker Compose installed
- Domain name (optional, for custom URL)
- SSL certificate (optional, for HTTPS)
- At least 2GB RAM and 10GB storage

### Step 1: Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Add current user to docker group
sudo usermod -aG docker $USER
newgrp docker
```

### Step 2: Deploy ContactPlus

```bash
# Clone repository
git clone <repository-url> /opt/contactplus
cd /opt/contactplus

# Create production environment file
cat > .env.production << EOF
# API Configuration
API_PORT=8080
API_HOST=0.0.0.0

# Web Configuration
WEB_PORT=80
REACT_APP_API_URL=http://your-domain.com/api/v1

# Database Configuration
DATABASE_PATH=/app/data/master_database
BACKUP_PATH=/app/backups

# Security
LOG_LEVEL=WARNING
EOF

# Create production docker-compose
cp docker-compose.yml docker-compose.prod.yml
# Edit docker-compose.prod.yml to use .env.production
```

### Step 3: Configure Nginx (Optional - for custom domain)

```bash
# Install Nginx
sudo apt install nginx -y

# Create Nginx configuration
sudo cat > /etc/nginx/sites-available/contactplus << EOF
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_cache_bypass \$http_upgrade;
    }

    location /api {
        proxy_pass http://localhost:8080;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_cache_bypass \$http_upgrade;
    }
}
EOF

# Enable site
sudo ln -s /etc/nginx/sites-available/contactplus /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl restart nginx
```

### Step 4: Start Services

```bash
# Start ContactPlus
cd /opt/contactplus
docker-compose -f docker-compose.prod.yml up -d

# Check status
docker-compose ps
```

### Step 5: Import Initial Data

```bash
# Copy your vCard files to the server
scp Imports/*.vcf user@server:/opt/contactplus/Imports/

# Import through web interface
# Navigate to http://your-domain.com/import
```

## 🔒 Security Hardening

### Enable HTTPS with Let's Encrypt

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get SSL certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo systemctl enable certbot.timer
```

### Firewall Configuration

```bash
# Configure UFW
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### Backup Strategy

```bash
# Create backup script
cat > /opt/contactplus/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/opt/contactplus/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup database
docker exec contactplus-core tar -czf - /app/data > $BACKUP_DIR/contactplus_backup_$DATE.tar.gz

# Keep only last 7 days of backups
find $BACKUP_DIR -name "contactplus_backup_*.tar.gz" -mtime +7 -delete

echo "Backup completed: contactplus_backup_$DATE.tar.gz"
EOF

chmod +x /opt/contactplus/backup.sh

# Add to crontab for daily backups
(crontab -l 2>/dev/null; echo "0 2 * * * /opt/contactplus/backup.sh") | crontab -
```

## 📊 Monitoring

### Set up monitoring alerts

```bash
# Create health check script
cat > /opt/contactplus/health_check.sh << 'EOF'
#!/bin/bash
API_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/api/v1/health)

if [ $API_HEALTH -ne 200 ]; then
    echo "ContactPlus API is down!" | mail -s "ContactPlus Alert" admin@example.com
    docker-compose -f /opt/contactplus/docker-compose.prod.yml restart contactplus-core
fi
EOF

chmod +x /opt/contactplus/health_check.sh

# Add to crontab for checks every 5 minutes
(crontab -l 2>/dev/null; echo "*/5 * * * * /opt/contactplus/health_check.sh") | crontab -
```

### View Logs

```bash
# View all logs
docker-compose -f docker-compose.prod.yml logs

# View specific service logs
docker-compose -f docker-compose.prod.yml logs contactplus-core

# Follow logs in real-time
docker-compose -f docker-compose.prod.yml logs -f
```

## 🔧 Maintenance

### Update ContactPlus

```bash
cd /opt/contactplus
git pull origin main
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d
```

### Database Maintenance

```bash
# Export full database
docker exec contactplus-core curl http://localhost:8080/api/v1/export/vcf > contacts_export.vcf

# Check database statistics
docker exec contactplus-core curl http://localhost:8080/api/v1/stats | jq
```

### Performance Tuning

```bash
# Adjust Docker resources in docker-compose.prod.yml
services:
  contactplus-core:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

## 🚨 Troubleshooting

### Service Won't Start

```bash
# Check logs
docker-compose -f docker-compose.prod.yml logs contactplus-core

# Check disk space
df -h

# Check memory
free -m

# Restart services
docker-compose -f docker-compose.prod.yml restart
```

### Database Issues

```bash
# Check database file permissions
docker exec contactplus-core ls -la /app/data

# Repair permissions
docker exec contactplus-core chown -R 1000:1000 /app/data
```

### Performance Issues

```bash
# Check resource usage
docker stats

# Clear Docker cache
docker system prune -a
```

## 📋 Checklist

- [ ] Server meets minimum requirements
- [ ] Docker and Docker Compose installed
- [ ] ContactPlus deployed and running
- [ ] Initial data imported
- [ ] Backups configured
- [ ] Monitoring set up
- [ ] SSL certificate installed (if using custom domain)
- [ ] Firewall configured
- [ ] Documentation updated with server details

## 🆘 Support

For production support:
1. Check logs first: `docker-compose logs`
2. Verify health: `curl http://localhost:8080/api/v1/health`
3. Check system resources: `htop` or `docker stats`
4. Review this guide for common issues