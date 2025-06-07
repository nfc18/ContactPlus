# GitHub Deployment to Mac - Setup Guide

Deploy ContactPlus automatically to your Mac via GitHub Actions whenever you push to the main branch.

## 🚀 **Quick Setup Overview**

1. **Set up GitHub repository** with your ContactPlus code
2. **Configure self-hosted runner** on your Mac
3. **Push to main branch** triggers automatic deployment
4. **Access ContactPlus** at http://localhost:3000

---

## 📋 **Step 1: GitHub Repository Setup**

### Create GitHub Repository
```bash
# In your ContactPlus directory
git init
git add .
git commit -m "Initial ContactPlus MVP commit"

# Create repository on GitHub and push
git remote add origin https://github.com/nfc18/ContactPlus.git
git branch -M main
git push -u origin main
```

### Verify Repository Structure
Your GitHub repo should contain:
```
ContactPlus/
├── .github/workflows/deploy_to_mac.yml    # ✅ Deployment workflow
├── docker-compose.yml                     # ✅ Service orchestration
├── contactplus-core/                      # ✅ API backend
├── contactplus-web/                       # ✅ React frontend
├── contactplus-monitor/                   # ✅ Health dashboard
├── tests/                                 # ✅ Test suite
└── scripts/setup_mac_runner.sh            # ✅ Runner setup
```

---

## 📋 **Step 2: Mac Self-Hosted Runner Setup**

### Run Setup Script
```bash
cd /Users/lk/Documents/Developer/Private/ContactPlus
./scripts/setup_mac_runner.sh
```

### Manual GitHub Configuration
1. **Go to your GitHub repository**
   - Navigate to: `Settings` → `Actions` → `Runners`
   
2. **Add new self-hosted runner**
   - Click `New self-hosted runner`
   - Select `macOS`
   - Copy the configuration command
   
3. **Configure the runner**
   ```bash
   cd ~/actions-runner
   ./config.sh --url https://github.com/nfc18/ContactPlus --token YOUR_TOKEN
   ```
   
4. **Runner configuration prompts**:
   - **Runner name**: `ContactPlus-Mac`
   - **Runner labels**: `self-hosted,macOS,ContactPlus`
   - **Work directory**: Press Enter for default

### Start Runner Service
The setup script automatically configures the runner as a macOS service that starts automatically.

**Manual service management**:
```bash
# Check runner status
launchctl list | grep github.actions.runner

# Stop runner
launchctl unload ~/Library/LaunchAgents/com.github.actions.runner.plist

# Start runner
launchctl load ~/Library/LaunchAgents/com.github.actions.runner.plist

# View runner logs
tail -f ~/Library/Logs/github-actions-runner.log
```

---

## 📋 **Step 3: Deployment Workflow**

### Automatic Deployment
The deployment automatically triggers when:
- **Push to main branch**
- **Manual workflow dispatch** (from GitHub Actions tab)

### Deployment Process
1. **🛑 Stop existing services** and create backup
2. **🔨 Build new Docker images** 
3. **🧪 Run integration tests** (optional, can be skipped)
4. **🚀 Deploy to production**
5. **🔍 Verify deployment** health
6. **✅ Update deployment status**

### Workflow Configuration

**File**: `.github/workflows/deploy_to_mac.yml`

**Key Features**:
- Automatic data backup before deployment
- Integration testing before production deployment
- Health verification after deployment
- Rollback capability on failure
- Resource cleanup

---

## 📋 **Step 4: Usage & Management**

### Trigger Deployment
```bash
# Make changes to your code
git add .
git commit -m "Update ContactPlus features"
git push origin main

# Deployment starts automatically
# Watch progress at: https://github.com/nfc18/ContactPlus/actions
```

### Manual Deployment
```bash
# If you need to deploy without GitHub
~/deploy_contactplus.sh
```

### Check Status
```bash
# Check ContactPlus status
~/check_contactplus.sh

# Output example:
# 📊 ContactPlus Status Check
# ==========================
# 🐳 Docker Containers:
# contactplus-core    Up
# contactplus-web     Up
# contactplus-monitor Up
# dozzle              Up
# 
# 🔗 Service Health:
# ✅ Web Interface: OK
# ✅ API Backend: OK
# ✅ Monitor: OK
# ✅ Logs: OK
# 
# 📊 Database Stats:
# Total Contacts: 6011
# Active Contacts: 6011
#   Sara_Export: 3075
#   iPhone_Contacts: 2931
#   ComplianceTest: 4
#   SpecialChars: 1
```

### Access ContactPlus
After successful deployment:
- **🌐 Web Interface**: http://localhost:3000
- **📊 API Documentation**: http://localhost:8080/docs
- **💻 System Monitor**: http://localhost:9090
- **📋 Live Logs**: http://localhost:8081

---

## 🔧 **Advanced Configuration**

### Environment Variables
Set in GitHub repository secrets for production:
```
# GitHub Settings → Secrets and variables → Actions
DATABASE_PATH=/app/data/master_database
LOG_LEVEL=INFO
BACKUP_RETENTION_DAYS=30
```

### Force Deployment (Skip Tests)
```bash
# In GitHub Actions tab, use "Run workflow" with:
# force_deploy: true
```

### Custom Deployment Branch
Edit `.github/workflows/deploy_to_mac.yml`:
```yaml
on:
  push:
    branches: [ main, production ]  # Add other branches
```

---

## 🛠️ **Troubleshooting**

### Runner Not Appearing
1. **Check runner service**:
   ```bash
   launchctl list | grep github.actions.runner
   ```

2. **Restart runner**:
   ```bash
   launchctl unload ~/Library/LaunchAgents/com.github.actions.runner.plist
   launchctl load ~/Library/LaunchAgents/com.github.actions.runner.plist
   ```

3. **Check logs**:
   ```bash
   tail -f ~/Library/Logs/github-actions-runner.log
   ```

### Deployment Fails
1. **Check GitHub Actions logs** in your repository
2. **Check Docker status**:
   ```bash
   docker ps
   docker-compose logs
   ```

3. **Manual deployment**:
   ```bash
   ~/deploy_contactplus.sh
   ```

### Port Conflicts
If ports 3000, 8080, 8081, or 9090 are in use:
```bash
# Find processes using ports
lsof -i :3000 -i :8080 -i :8081 -i :9090

# Kill conflicting processes if needed
sudo kill -9 PID_NUMBER
```

### Data Recovery
Backups are automatically created before each deployment:
```bash
# Backups location
ls -la ~/ContactPlus_Backups/

# Restore from backup
BACKUP_DATE="20241207_143000"  # Use actual backup timestamp
docker run --rm -v contactplus_contact_data:/data -v "$HOME/ContactPlus_Backups/$BACKUP_DATE:/backup" alpine \
  tar xzf /backup/contact_data.tar.gz -C /data
```

---

## 📊 **Monitoring & Maintenance**

### Log Monitoring
```bash
# GitHub Actions runner logs
tail -f ~/Library/Logs/github-actions-runner.log

# ContactPlus application logs (via Dozzle)
# Visit: http://localhost:8081

# Docker compose logs
docker-compose logs -f
```

### Resource Monitoring
```bash
# Check Docker resource usage
docker stats

# Check disk usage
docker system df

# Clean up old images (automatic in deployment)
docker image prune -f
```

### Updates & Maintenance
```bash
# Update GitHub Actions runner (when new version available)
cd ~/actions-runner
./config.sh remove  # Remove old configuration
# Download new version and reconfigure

# Update ContactPlus
# Just push to main branch - deployment is automatic!
```

---

## 🎯 **Production Checklist**

### Before First Deployment
- [ ] GitHub repository created and configured
- [ ] Self-hosted runner setup and running
- [ ] Docker Desktop installed and running
- [ ] Ports 3000, 8080, 8081, 9090 available
- [ ] Backup directory created

### After Each Deployment
- [ ] All services responding (check with `~/check_contactplus.sh`)
- [ ] Database contains expected number of contacts
- [ ] Web interface accessible at http://localhost:3000
- [ ] API responding at http://localhost:8080/api/v1/health
- [ ] Backup created successfully

### Regular Maintenance
- [ ] Monitor runner logs for errors
- [ ] Check backup directory size
- [ ] Update GitHub Actions runner periodically
- [ ] Monitor Docker resource usage

---

## 🎉 **Success!**

Once setup is complete:

1. **🔄 Automatic Deployment**: Push to main → Auto deploy to Mac
2. **📱 Access Your App**: http://localhost:3000
3. **📊 Monitor Health**: Built-in dashboards and logs
4. **💾 Data Safety**: Automatic backups before each deployment
5. **🔧 Easy Management**: Simple scripts for status and manual deployment

**Your ContactPlus MVP now deploys automatically to your Mac via GitHub Actions with professional CI/CD practices!** 🚀

---

## 📞 **Quick Reference**

**GitHub Repository**: https://github.com/nfc18/ContactPlus  
**Web Interface**: http://localhost:3000  
**API Docs**: http://localhost:8080/docs  
**System Monitor**: http://localhost:9090  
**Live Logs**: http://localhost:8081  

**Management Scripts**:
- Status Check: `~/check_contactplus.sh`
- Manual Deploy: `~/deploy_contactplus.sh`
- Runner Logs: `tail -f ~/Library/Logs/github-actions-runner.log`