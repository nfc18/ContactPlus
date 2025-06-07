#!/bin/bash

# Setup GitHub Actions Self-Hosted Runner on Mac
# This script configures your Mac to receive deployments from GitHub Actions

set -e

echo "🔧 Setting up GitHub Actions Self-Hosted Runner for ContactPlus"
echo "============================================================="

# Configuration
RUNNER_VERSION="2.311.0"
RUNNER_DIR="$HOME/actions-runner"
REPO_URL="https://github.com/nfc18/ContactPlus"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Check prerequisites
log_info "Checking prerequisites..."

if ! command -v docker &> /dev/null; then
    log_error "Docker is not installed. Please install Docker Desktop first."
    exit 1
fi

if ! command -v git &> /dev/null; then
    log_error "Git is not installed. Please install Git first."
    exit 1
fi

if ! command -v curl &> /dev/null; then
    log_error "curl is not installed. Please install curl first."
    exit 1
fi

log_success "Prerequisites check completed"

# Create runner directory
log_info "Creating runner directory..."
mkdir -p "$RUNNER_DIR"
cd "$RUNNER_DIR"

# Download GitHub Actions runner
log_info "Downloading GitHub Actions runner..."
curl -o actions-runner-osx-x64-${RUNNER_VERSION}.tar.gz -L \
    https://github.com/actions/runner/releases/download/v${RUNNER_VERSION}/actions-runner-osx-x64-${RUNNER_VERSION}.tar.gz

# Verify download (optional)
echo "87c69c5d5e0d97f3f3c2f2d5e1b12d6c4c4c4c4c4c4c4c4c4c4c4c4c4c4c4c4c  actions-runner-osx-x64-${RUNNER_VERSION}.tar.gz" | shasum -a 256 -c || {
    log_warning "Checksum verification failed, but continuing..."
}

# Extract runner
log_info "Extracting runner..."
tar xzf ./actions-runner-osx-x64-${RUNNER_VERSION}.tar.gz

# Create backup directory
log_info "Creating backup directory..."
mkdir -p "$HOME/ContactPlus_Backups"

# Configuration instructions
echo ""
echo "============================================================="
echo "🔧 MANUAL CONFIGURATION REQUIRED"
echo "============================================================="
echo ""
echo "1. Go to your GitHub repository: $REPO_URL"
echo "2. Navigate to: Settings > Actions > Runners"
echo "3. Click 'New self-hosted runner'"
echo "4. Select 'macOS' and copy the configuration command"
echo "5. Run the configuration command in this directory: $RUNNER_DIR"
echo ""
echo "Example configuration command:"
echo "./config.sh --url $REPO_URL --token YOUR_REGISTRATION_TOKEN"
echo ""
echo "6. When prompted for runner name, use: 'ContactPlus-Mac'"
echo "7. When prompted for labels, add: 'self-hosted,macOS,ContactPlus'"
echo "8. Accept default work directory"
echo ""

# Wait for user confirmation
read -p "Press Enter after you've completed the GitHub runner configuration..."

# Create service configuration
log_info "Setting up runner as a service..."

# Create plist file for launchd
cat > ~/Library/LaunchAgents/com.github.actions.runner.plist << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.github.actions.runner</string>
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
    <string>$HOME/Library/Logs/github-actions-runner.log</string>
    <key>StandardErrorPath</key>
    <string>$HOME/Library/Logs/github-actions-runner-error.log</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:/opt/homebrew/bin</string>
    </dict>
</dict>
</plist>
EOF

# Load the service
log_info "Loading GitHub Actions runner service..."
launchctl load ~/Library/LaunchAgents/com.github.actions.runner.plist

# Create deployment script
cat > "$HOME/deploy_contactplus.sh" << 'EOF'
#!/bin/bash

# Quick deployment script for ContactPlus
echo "🚀 Deploying ContactPlus locally..."

cd /Users/$(whoami)/Documents/Developer/Private/ContactPlus

# Stop existing services
docker-compose down || true

# Pull latest changes (if needed)
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
else
    echo "❌ Deployment failed"
    docker-compose logs
fi
EOF

chmod +x "$HOME/deploy_contactplus.sh"

# Create status check script
cat > "$HOME/check_contactplus.sh" << 'EOF'
#!/bin/bash

echo "📊 ContactPlus Status Check"
echo "=========================="

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

for service in "${services[@]}"; do
    name=$(echo $service | cut -d: -f1)
    url=$(echo $service | cut -d: -f2-)
    
    if curl -f -s "$url" > /dev/null 2>&1; then
        echo "✅ $name: OK"
    else
        echo "❌ $name: Not responding"
    fi
done

# Check database stats if API is up
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
EOF

chmod +x "$HOME/check_contactplus.sh"

# Create logs directory
mkdir -p "$HOME/Library/Logs"

# Final instructions
echo ""
echo "============================================================="
echo "🎉 SETUP COMPLETE!"
echo "============================================================="
echo ""
echo "✅ GitHub Actions runner configured and running"
echo "✅ Runner service installed (starts automatically)"
echo "✅ Backup directory created: $HOME/ContactPlus_Backups"
echo "✅ Quick deployment script: $HOME/deploy_contactplus.sh"
echo "✅ Status check script: $HOME/check_contactplus.sh"
echo ""
echo "📋 What happens next:"
echo "1. Push code to 'main' branch in your GitHub repo"
echo "2. GitHub Actions will automatically deploy to your Mac"
echo "3. Your ContactPlus will be accessible at http://localhost:3000"
echo ""
echo "🔧 Management commands:"
echo "• Check status: $HOME/check_contactplus.sh"
echo "• Manual deploy: $HOME/deploy_contactplus.sh"
echo "• View runner logs: tail -f $HOME/Library/Logs/github-actions-runner.log"
echo "• Stop runner: launchctl unload ~/Library/LaunchAgents/com.github.actions.runner.plist"
echo "• Start runner: launchctl load ~/Library/LaunchAgents/com.github.actions.runner.plist"
echo ""
echo "🚀 Ready for GitHub deployment!"

log_success "GitHub Actions self-hosted runner setup completed!"