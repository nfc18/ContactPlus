# GitHub Repository Setup Commands

To complete the GitHub deployment setup, run these commands:

## 1. Create GitHub Repository

Visit https://github.com/new and create a repository named `ContactPlus` (or your preferred name).

## 2. Configure Git Remote

```bash
# Replace YOUR_USERNAME with your GitHub username
git remote add origin https://github.com/YOUR_USERNAME/ContactPlus.git

# Or if you prefer SSH:
# git remote add origin git@github.com:YOUR_USERNAME/ContactPlus.git
```

## 3. Push to GitHub

```bash
git branch -M main
git push -u origin main
```

## 4. Set up Self-Hosted Runner

```bash
# Run the setup script
./scripts/setup_mac_runner.sh
```

Then follow the GitHub instructions to configure the runner:
1. Go to your repository Settings → Actions → Runners
2. Click "New self-hosted runner"
3. Select "macOS"
4. Follow the configuration steps

## 5. Update Repository URL in Scripts

Edit these files to replace `YOUR_USERNAME` with your actual GitHub username:
- `scripts/setup_mac_runner.sh` (line 14)
- `GITHUB_DEPLOYMENT_GUIDE.md` (line 24)

## 6. Test Deployment

Once the runner is configured, push any change to trigger automatic deployment:

```bash
echo "# Test deployment" >> README.md
git add README.md
git commit -m "Test automatic deployment"
git push origin main
```

## Current Status

✅ Local git repository initialized  
✅ Initial commit created with all ContactPlus MVP code  
⏳ Waiting for GitHub repository creation  
⏳ Waiting for remote configuration  
⏳ Waiting for self-hosted runner setup  

## Next Steps

1. Create GitHub repository manually
2. Run the remote configuration commands above
3. Set up the self-hosted runner
4. Test the automatic deployment workflow

Your ContactPlus MVP is ready to deploy automatically via GitHub Actions! 🚀