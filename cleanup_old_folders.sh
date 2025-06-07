#!/bin/bash

# Clean up old folders and move to proper locations
echo "🧹 Cleaning up old folders and moving to proper locations"
echo "========================================================"

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

# Check what's in home directory
echo "🔍 Current home directory clutter:"
ls -la ~ | grep -E "(actions-runner|ContactPlus_Backups|actions-runner-osx)" || echo "No clutter found"

echo ""
log_info "Creating proper directory structure..."

# Create proper directories with sudo
echo "Creating /usr/local/var/github-actions-runner (requires password):"
sudo mkdir -p /usr/local/var/github-actions-runner
sudo chown $(whoami):staff /usr/local/var/github-actions-runner

# Create backup directory (no sudo needed)
BACKUP_DIR="$HOME/Documents/Developer/Private/ContactPlus/backups"
mkdir -p "$BACKUP_DIR"

# Create logs directory
LOGS_DIR="$HOME/Library/Logs/ContactPlus"
mkdir -p "$LOGS_DIR"

echo ""
log_info "Moving existing runner content..."

# Move the extracted runner files to proper location
if [ -d ~/actions-runner ]; then
    log_info "Moving runner files from ~/actions-runner to /usr/local/var/github-actions-runner"
    sudo cp -R ~/actions-runner/* /usr/local/var/github-actions-runner/
    sudo chown -R $(whoami):staff /usr/local/var/github-actions-runner/*
    log_success "Runner files moved successfully"
else
    log_warning "No ~/actions-runner directory found"
fi

echo ""
log_info "Cleaning up home directory..."

# Remove old directories from home
if [ -d ~/actions-runner ]; then
    log_info "Removing ~/actions-runner..."
    rm -rf ~/actions-runner
    log_success "Removed ~/actions-runner"
fi

if [ -d ~/ContactPlus_Backups ]; then
    log_info "Removing empty ~/ContactPlus_Backups..."
    rmdir ~/ContactPlus_Backups
    log_success "Removed ~/ContactPlus_Backups"
fi

if [ -f ~/actions-runner-osx-x64-2.311.0.tar.gz ]; then
    log_info "Removing downloaded archive from home..."
    rm ~/actions-runner-osx-x64-2.311.0.tar.gz
    log_success "Removed archive file"
fi

echo ""
echo "🧹 CLEANUP COMPLETE!"
echo "===================="
log_success "✅ Home directory cleaned"
log_success "✅ Runner moved to: /usr/local/var/github-actions-runner"
log_success "✅ Backups will go to: $BACKUP_DIR"
log_success "✅ Logs will go to: $LOGS_DIR"

echo ""
echo "📁 New Clean Structure:"
echo "  🏠 Home Directory: Clean (no service folders)"
echo "  🤖 Runner: /usr/local/var/github-actions-runner"
echo "  💾 Backups: $BACKUP_DIR"
echo "  📋 Logs: $LOGS_DIR"

echo ""
echo "🔍 Verifying cleanup:"
HOME_CLUTTER=$(ls -la ~ | grep -E "(actions-runner|ContactPlus_Backups|actions-runner-osx)" | wc -l)
if [ $HOME_CLUTTER -eq 0 ]; then
    log_success "✅ Home directory is now clean!"
else
    log_warning "⚠️  Some items may still need manual cleanup"
    ls -la ~ | grep -E "(actions-runner|ContactPlus_Backups|actions-runner-osx)"
fi

echo ""
echo "🚀 Next Steps:"
echo "1. Configure the runner in the new location:"
echo "   cd /usr/local/var/github-actions-runner"
echo "   ./config.sh --url https://github.com/nfc18/ContactPlus --token YOUR_TOKEN"
echo ""
echo "2. Start the runner:"
echo "   ./run.sh"
echo ""
echo "3. Your home directory is now properly organized! 🎉"