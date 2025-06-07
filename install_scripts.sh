#!/bin/bash

# Install ContactPlus management scripts system-wide
echo "🔧 Installing ContactPlus management scripts system-wide"
echo "======================================================="

PROJECT_DIR="/Users/lk/Documents/Developer/Private/ContactPlus"

# Create symlinks in /usr/local/bin for easy access
echo "Creating system-wide symlinks (requires password):"

# Remove any existing symlinks first
sudo rm -f /usr/local/bin/check-contactplus
sudo rm -f /usr/local/bin/deploy-contactplus

# Create new symlinks
sudo ln -s "$PROJECT_DIR/scripts/check_contactplus.sh" /usr/local/bin/check-contactplus
sudo ln -s "$PROJECT_DIR/scripts/deploy_contactplus.sh" /usr/local/bin/deploy-contactplus

echo ""
echo "✅ Scripts installed system-wide!"
echo "================================="
echo ""
echo "📁 Script Locations:"
echo "  📄 Source: $PROJECT_DIR/scripts/"
echo "  🔗 System: /usr/local/bin/"
echo ""
echo "🚀 Usage (from anywhere):"
echo "  check-contactplus    # Check ContactPlus status"
echo "  deploy-contactplus   # Deploy ContactPlus manually"
echo ""
echo "🎯 Benefits:"
echo "  ✅ Scripts organized with project"
echo "  ✅ Accessible from anywhere via PATH"
echo "  ✅ No clutter in home directory"
echo "  ✅ Professional system integration"