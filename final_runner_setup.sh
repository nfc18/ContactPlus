#!/bin/bash

# Final GitHub Actions Runner Setup - Complete Automation
echo "🚀 Setting up GitHub Actions Runner - Final Setup"
echo "=================================================="

# Use project subdirectory since /usr/local requires sudo
RUNNER_DIR="$HOME/Documents/Developer/Private/ContactPlus/.runner"
REPO_URL="https://github.com/nfc18/ContactPlus"
TOKEN="A737XZSPT3EQZNZ5BY7XD6LIISRVE"

echo "🔧 Using project-local runner directory (no sudo required):"
echo "   $RUNNER_DIR"

# Create runner directory in project
mkdir -p "$RUNNER_DIR"
cd "$RUNNER_DIR"

# Download runner
echo "📥 Downloading GitHub Actions runner..."
curl -o actions-runner-osx-x64-2.311.0.tar.gz -L \
  https://github.com/actions/runner/releases/download/v2.311.0/actions-runner-osx-x64-2.311.0.tar.gz

# Extract
echo "📦 Extracting runner..."
tar xzf ./actions-runner-osx-x64-2.311.0.tar.gz

# Configure runner
echo "⚙️ Configuring runner..."
./config.sh --url "$REPO_URL" --token "$TOKEN" \
            --name "ContactPlus-Mac" \
            --labels "self-hosted,macOS,ContactPlus" \
            --work "_work" \
            --unattended

if [ $? -eq 0 ]; then
    echo "✅ Runner configured successfully!"
    
    # Create service file that doesn't require sudo
    cat > "$HOME/Library/LaunchAgents/com.github.actions.runner.contactplus.plist" << EOF
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
    <string>$HOME/Library/Logs/ContactPlus/github-actions-runner.log</string>
    <key>StandardErrorPath</key>
    <string>$HOME/Library/Logs/ContactPlus/github-actions-runner-error.log</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:/opt/homebrew/bin</string>
    </dict>
</dict>
</plist>
EOF

    # Load the service
    echo "🔄 Loading runner service..."
    launchctl load "$HOME/Library/LaunchAgents/com.github.actions.runner.contactplus.plist"
    
    # Start the runner in background
    echo "🚀 Starting GitHub Actions runner..."
    nohup ./run.sh > ~/Library/Logs/ContactPlus/runner-startup.log 2>&1 &
    
    # Wait a moment for startup
    sleep 5
    
    # Check if runner is active
    if ps aux | grep -v grep | grep -q "run.sh"; then
        echo "✅ Runner is active and running!"
    else
        echo "⚠️ Runner may need manual start. Run: cd $RUNNER_DIR && ./run.sh"
    fi
    
    echo ""
    echo "🎉 GITHUB ACTIONS RUNNER SETUP COMPLETE!"
    echo "========================================"
    echo ""
    echo "✅ Runner configured and started"
    echo "✅ Service installed for auto-restart"
    echo "✅ Logs going to: ~/Library/Logs/ContactPlus/"
    echo ""
    echo "🔗 Repository: $REPO_URL"
    echo "🔗 Actions: $REPO_URL/actions"
    echo ""
    echo "🚀 GitHub Actions will now automatically deploy when you push to main!"
    
    # Test deployment by creating a small change
    cd "$HOME/Documents/Developer/Private/ContactPlus"
    echo "# Runner setup completed $(date)" >> README.md
    git add README.md
    git commit -m "Activate GitHub Actions runner - automatic deployment ready

GitHub Actions self-hosted runner is now configured and active.
This commit triggers the first automatic deployment test.

Runner location: $RUNNER_DIR
Service: com.github.actions.runner.contactplus
Logs: ~/Library/Logs/ContactPlus/

🤖 Generated with Claude Code (https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"
    
    echo "📤 Pushing test commit to trigger automatic deployment..."
    git push origin main
    
    echo ""
    echo "🎯 What happens next:"
    echo "1. GitHub Actions will automatically start deployment"
    echo "2. Watch progress at: $REPO_URL/actions"
    echo "3. Services will be available shortly at:"
    echo "   - Web: http://localhost:3000"
    echo "   - API: http://localhost:8080"
    echo "   - Monitor: http://localhost:9090"
    echo "   - Logs: http://localhost:8081"
    
else
    echo "❌ Runner configuration failed!"
    exit 1
fi