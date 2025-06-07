#!/bin/bash

# ContactPlus Deployment Script with Proper Directory Structure
echo "🚀 Deploying ContactPlus with proper backup structure..."

PROJECT_DIR="/Users/lk/Documents/Developer/Private/ContactPlus"
BACKUP_DIR="/backups"

cd "$PROJECT_DIR"

# Create timestamped backup
BACKUP_TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_PATH="$BACKUP_DIR/$BACKUP_TIMESTAMP"
mkdir -p "$BACKUP_PATH"

echo "💾 Creating backup at: $BACKUP_PATH"

# Backup Docker volumes if they exist
if docker volume ls | grep -q contactplus_contact_data; then
    echo "Backing up contact data..."
    docker run --rm -v contactplus_contact_data:/data -v "$BACKUP_PATH:/backup" alpine \
        tar czf /backup/contact_data.tar.gz -C /data .
fi

# Stop existing services
docker-compose down || true

# Pull latest changes
git pull origin main || echo "Git pull failed or not needed"

# Start services
docker-compose up -d

# Wait for services
sleep 30

# Check health
if curl -f -s http://localhost:8080/api/v1/health > /dev/null; then
    echo "✅ ContactPlus deployed successfully!"
    echo "🔗 Web: http://localhost:3000"
    echo "🔗 API: http://localhost:8080"
    echo "🔗 Monitor: http://localhost:9090"
    echo "🔗 Logs: http://localhost:8081"
    echo "💾 Backup saved: $BACKUP_PATH"
else
    echo "❌ Deployment failed"
    docker-compose logs
fi
