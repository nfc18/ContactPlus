#!/bin/bash

# Proper GitHub Actions Runner Setup for ContactPlus with Best Practices
echo "🔧 Setting up GitHub Actions Self-Hosted Runner (Proper Structure)"
echo "=================================================================="

# Proper Configuration with organized directories
RUNNER_VERSION="2.311.0"
RUNNER_DIR="/usr/local/var/github-actions-runner"
BACKUP_DIR="$HOME/Documents/Developer/Private/ContactPlus/backups"
LOGS_DIR="$HOME/Library/Logs/ContactPlus"
REPO_URL="https://github.com/nfc18/ContactPlus"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Create proper directory structure
log_info "Creating proper directory structure..."
sudo mkdir -p "$RUNNER_DIR"
mkdir -p "$BACKUP_DIR"
mkdir -p "$LOGS_DIR"

# Set proper ownership for runner directory
sudo chown $(whoami):staff "$RUNNER_DIR"

log_success "Directory structure created:"
echo "  📁 Runner: $RUNNER_DIR"
echo "  📁 Backups: $BACKUP_DIR" 
echo "  📁 Logs: $LOGS_DIR"

echo ""
echo "============================================================="
echo "🎯 MANUAL SETUP COMMANDS (Run in Terminal)"
echo "============================================================="
echo ""
echo "1. Download and extract runner to proper location:"
echo "   cd $RUNNER_DIR"
echo "   curl -o actions-runner-osx-x64-$RUNNER_VERSION.tar.gz -L \\"
echo "     https://github.com/actions/runner/releases/download/v$RUNNER_VERSION/actions-runner-osx-x64-$RUNNER_VERSION.tar.gz"
echo "   tar xzf ./actions-runner-osx-x64-$RUNNER_VERSION.tar.gz"
echo ""
echo "2. Get fresh registration token:"
echo "   cd $HOME/Documents/Developer/Private/ContactPlus"
echo "   gh api repos/nfc18/ContactPlus/actions/runners/registration-token --method POST"
echo ""
echo "3. Configure the runner:"
echo "   cd $RUNNER_DIR"
echo "   ./config.sh --url $REPO_URL --token YOUR_FRESH_TOKEN \\"
echo "              --name ContactPlus-Mac \\"
echo "              --labels self-hosted,macOS,ContactPlus \\"
echo "              --work _work \\"
echo "              --unattended"
echo ""
echo "4. Create proper service configuration:"

# Create proper service plist
cat > /tmp/com.github.actions.runner.contactplus.plist << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.github.actions.runner.contactplus</string>
    <key>ProgramArguments</key>
    <array>
        <string>$RUNNER_DIR/run.sh</string>
    </array>
    <key>WorkingDirectory</key>
    <string>$RUNNER_DIR</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>$LOGS_DIR/github-actions-runner.log</string>
    <key>StandardErrorPath</key>
    <string>$LOGS_DIR/github-actions-runner-error.log</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:/opt/homebrew/bin</string>
    </dict>
</dict>
</plist>
EOF

echo "   sudo cp /tmp/com.github.actions.runner.contactplus.plist ~/Library/LaunchAgents/"
echo "   launchctl load ~/Library/LaunchAgents/com.github.actions.runner.contactplus.plist"
echo ""

# Create updated deployment script with proper backup location
cat > "$HOME/deploy_contactplus.sh" << EOF
#!/bin/bash

# ContactPlus Deployment Script with Proper Directory Structure
echo "🚀 Deploying ContactPlus with proper backup structure..."

PROJECT_DIR="$HOME/Documents/Developer/Private/ContactPlus"
BACKUP_DIR="$PROJECT_DIR/backups"

cd "\$PROJECT_DIR"

# Create timestamped backup
BACKUP_TIMESTAMP=\$(date +%Y%m%d_%H%M%S)
BACKUP_PATH="\$BACKUP_DIR/\$BACKUP_TIMESTAMP"
mkdir -p "\$BACKUP_PATH"

echo "💾 Creating backup at: \$BACKUP_PATH"

# Backup Docker volumes if they exist
if docker volume ls | grep -q contactplus_contact_data; then
    echo "Backing up contact data..."
    docker run --rm -v contactplus_contact_data:/data -v "\$BACKUP_PATH:/backup" alpine \\
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
    echo "💾 Backup saved: \$BACKUP_PATH"
else
    echo "❌ Deployment failed"
    docker-compose logs
fi
EOF

chmod +x "$HOME/deploy_contactplus.sh"

# Create updated status script
cat > "$HOME/check_contactplus.sh" << EOF
#!/bin/bash

echo "📊 ContactPlus Status Check"
echo "=========================="

PROJECT_DIR="$HOME/Documents/Developer/Private/ContactPlus"
cd "\$PROJECT_DIR"

# Check if containers are running
echo "🐳 Docker Containers:"
docker-compose ps 2>/dev/null || echo "No containers running"

echo ""
echo "🔗 Service Health:"

services=(
    "Web Interface:http://localhost:3000"
    "API Backend:http://localhost:8080/api/v1/health"
    "Monitor:http://localhost:9090"
    "Logs:http://localhost:8081"
)

for service in "\${services[@]}"; do
    name=\$(echo \$service | cut -d: -f1)
    url=\$(echo \$service | cut -d: -f2-)
    
    if curl -f -s "\$url" > /dev/null 2>&1; then
        echo "✅ \$name: OK"
    else
        echo "❌ \$name: Not responding"
    fi
done

# Check database stats
if curl -f -s http://localhost:8080/api/v1/health > /dev/null 2>&1; then
    echo ""
    echo "📊 Database Stats:"
    curl -s http://localhost:8080/api/v1/stats | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    print(f'Total Contacts: {data.get(\"total_contacts\", 0)}')
    print(f'Active Contacts: {data.get(\"active_contacts\", 0)}')
    for source, count in data.get('contacts_by_source', {}).items():
        print(f'  {source}: {count}')
except:
    print('Unable to parse database stats')
"
fi

# Show backup information
echo ""
echo "💾 Backup Information:"
BACKUP_DIR="$BACKUP_DIR"
if [ -d "\$BACKUP_DIR" ]; then
    echo "Backup directory: \$BACKUP_DIR"
    echo "Available backups:"
    ls -la "\$BACKUP_DIR" | tail -5
else
    echo "No backups found"
fi

# Show runner status
echo ""
echo "🤖 GitHub Actions Runner:"
if launchctl list | grep -q "com.github.actions.runner.contactplus"; then
    echo "✅ Runner service is loaded"
else
    echo "❌ Runner service not found"
fi

echo ""
echo "📁 Directory Structure:"
echo "  📁 Project: \$PROJECT_DIR"
echo "  📁 Backups: $BACKUP_DIR"
echo "  📁 Runner: $RUNNER_DIR"
echo "  📁 Logs: $LOGS_DIR"
EOF

chmod +x "$HOME/check_contactplus.sh"

echo "5. Start the runner (after configuration):"
echo "   cd $RUNNER_DIR"
echo "   ./run.sh"
echo ""
echo "============================================================="
echo "✅ IMPROVED DIRECTORY STRUCTURE READY"
echo "============================================================="
echo ""
log_success "✅ Proper directories created"
log_success "✅ Updated deployment script: ~/deploy_contactplus.sh"
log_success "✅ Updated status script: ~/check_contactplus.sh"
echo ""
echo "📁 New Structure:"
echo "  📁 Runner: $RUNNER_DIR (system location)"
echo "  📁 Backups: $BACKUP_DIR (with project)"
echo "  📁 Logs: $LOGS_DIR (organized logs)"
echo ""
echo "🎯 Benefits:"
echo "  ✅ No clutter in home directory"
echo "  ✅ Backups organized with project"
echo "  ✅ Logs in proper macOS location"
echo "  ✅ Runner in system service location"
echo ""
echo "🚀 Next: Run the manual setup commands above!"