# Getting Started — Environment Setup Guide

Complete this guide before starting Module 01. It takes about 20-30 minutes.

---

## What You Will Set Up

- Git (version control)
- A GitHub account
- GitHub CLI (`gh`)
- VS Code with recommended extensions
- SSH key for GitHub authentication
- Python 3.14 (needed for Modules 08–12)

---

## Step 1: Install Git

### Windows
1. Download from git-scm.com — search "Git for Windows"
2. Run the installer; accept defaults
3. Choose "Git Bash" as the default terminal when prompted
4. Verify: open Git Bash and run:
   ```bash
   git --version
   # Should show: git version 2.x.x
   ```

### macOS
```bash
# Option A: Homebrew (recommended)
brew install git

# Option B: Xcode Command Line Tools
xcode-select --install

git --version
```

### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install git -y
git --version
```

---

## Step 2: Configure Git

Run these commands in your terminal (replace with your actual name and email):

```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
git config --global core.editor "code --wait"   # use VS Code as editor
git config --global init.defaultBranch main
git config --global pull.rebase false

# Verify
git config --list
```

---

## Step 3: Create a GitHub Account

1. Go to github.com
2. Click "Sign up"
3. Choose a username (this will be public)
4. Verify your email address
5. Choose the Free plan

---

## Step 4: Set Up SSH Authentication

SSH keys let you push/pull without typing your password every time.

```bash
# Generate a new SSH key (replace with your email)
ssh-keygen -t ed25519 -C "your.email@example.com"
# Press Enter for default file location
# Optionally set a passphrase

# Start the SSH agent
eval "$(ssh-agent -s)"

# Add your key
ssh-add ~/.ssh/id_ed25519

# Copy the public key to clipboard
# macOS:
cat ~/.ssh/id_ed25519.pub | pbcopy

# Linux:
cat ~/.ssh/id_ed25519.pub   # then manually copy the output

# Windows (Git Bash):
cat ~/.ssh/id_ed25519.pub | clip
```

Now add it to GitHub:
1. Go to github.com → Settings → SSH and GPG keys
2. Click "New SSH key"
3. Give it a title (e.g., "My Laptop")
4. Paste the public key
5. Click "Add SSH key"

Verify it works:
```bash
ssh -T git@github.com
# Should show: Hi username! You've successfully authenticated...
```

---

## Step 5: Install GitHub CLI

The GitHub CLI (`gh`) lets you interact with GitHub from the terminal — create PRs, manage secrets, trigger workflows, and more.

### macOS
```bash
brew install gh
```

### Windows
```powershell
winget install --id GitHub.cli
# Or download from: search "GitHub CLI releases"
```

### Linux (Ubuntu/Debian)
```bash
# Search "GitHub CLI installation Linux" on GitHub's official page
# for the current installation commands
sudo apt install gh
```

Authenticate:
```bash
gh auth login
# Follow the prompts: choose GitHub.com → SSH → authenticate via browser
```

Verify:
```bash
gh --version
gh auth status
```

---

## Step 6: Install VS Code

1. Search "Visual Studio Code download" — download for your OS
2. Install it
3. Open VS Code

### Recommended Extensions

Install these from the Extensions panel (Ctrl+Shift+X / Cmd+Shift+X):

| Extension | Publisher | Why |
|---|---|---|
| GitHub Actions | GitHub | Workflow autocompletion, validation, run history |
| YAML | Red Hat | YAML validation and IntelliSense |
| GitLens | GitKraken | Git blame, history, and visualization |
| GitHub Pull Requests | GitHub | Manage PRs without leaving VS Code |

---

## Step 7: Install Python 3.14 (for Modules 08-12)

Modules 08–12 use a Python 3.14 Flask application for all code examples.

### macOS / Linux — pyenv (recommended)
```bash
# Install pyenv
curl https://pyenv.run | bash

# Add pyenv to your shell (add these lines to ~/.bashrc or ~/.zshrc)
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"

# Restart your shell, then install Python 3.14
pyenv install 3.14
pyenv global 3.14

python --version   # Should show: Python 3.14.x
pip --version      # Should show: pip 24.x from ...
```

### Windows
1. Search "Python 3.14 download" on python.org
2. Download the Windows installer (64-bit)
3. During installation, check **"Add Python to PATH"**
4. Open a new terminal and verify:
```powershell
python --version   # Should show: Python 3.14.x
pip --version
```

### macOS / Linux — official installer
```bash
# If you prefer not to use pyenv, download from python.org
# Search "Python 3.14 download" and follow the installer instructions
python3 --version
```

---

## Step 8: Fork and Clone This Repository

```bash
# 1. Fork via GitHub UI: go to this repo → click "Fork" → "Create fork"

# 2. Clone your fork (replace YOUR_USERNAME)
git clone git@github.com:YOUR_USERNAME/github-actions-master-class.git
cd github-actions-master-class

# 3. Set the original repo as "upstream" (for pulling updates)
git remote add upstream git@github.com:ORIGINAL_OWNER/github-actions-master-class.git

# Verify remotes
git remote -v
# origin    git@github.com:YOUR_USERNAME/github-actions-master-class.git (fetch)
# upstream  git@github.com:ORIGINAL_OWNER/github-actions-master-class.git (fetch)
```

---

## Step 9: Verify Your Setup

Run through this checklist:

```bash
# Git
git --version                    # should be 2.x+
git config user.name             # should print your name
git config user.email            # should print your email

# GitHub SSH
ssh -T git@github.com            # should say "Hi username!"

# GitHub CLI
gh auth status                   # should show "Logged in to github.com"

# Python (for later modules)
python --version                 # should be Python 3.14.x
pip --version                    # should be pip 24.x or similar
```

---

## Understanding the Course Repository

```
github-actions-master-class/
│
├── module-XX-name/
│   ├── README.md         ← READ THIS FIRST for every module
│   ├── examples/         ← Reference YAML files (not runnable workflows)
│   ├── exercises/        ← Hands-on practice
│   └── project/          ← Actual GitHub Actions project
│       └── .github/
│           └── workflows/
│               └── *.yml ← The real workflow files
```

**To test a module's workflows:**
1. Copy the `project/` folder contents into a new GitHub repository
2. Push to GitHub
3. Watch the Actions tab

---

## How to Follow Along

1. **Read the README** at the start of each module — understand the theory first
2. **Study the example files** in the `examples/` folder
3. **Do the exercises** before looking at solutions
4. **Create a test repo** on GitHub to try the actual workflow files
5. **Read the workflow YAML line by line** — every comment is educational

---

## Testing Workflows Without Pushing (act)

The `act` tool runs GitHub Actions locally in Docker containers. This is optional but very useful.

```bash
# Install (macOS)
brew install act

# First run — it will ask which Docker image to use
# Choose "Micro" for fast startup, "Medium" for better compatibility

# Run from a directory that has .github/workflows/
cd module-03-github-actions-intro/project
act push
```

Requirements: Docker must be installed and running.

---

## Common Setup Issues

### "Permission denied (publickey)" when cloning
- Your SSH key is not added to GitHub, or the SSH agent isn't running
- Re-run: `eval "$(ssh-agent -s)" && ssh-add ~/.ssh/id_ed25519`
- Or use HTTPS instead: `git clone https://github.com/...`

### VS Code "GitHub Actions" extension not showing workflows
- The extension looks for `.github/workflows/*.yml` relative to the workspace root
- Make sure you opened the right folder in VS Code

### `act` fails with Docker errors
- Ensure Docker Desktop is running
- Try `act --container-architecture linux/amd64` on Apple Silicon Macs

### `gh auth login` opens browser but doesn't complete
- Try: `gh auth login --web` or use a Personal Access Token instead

---

## You're Ready!

Once you've completed this guide, head to:

**[Module 01 — YAML Fundamentals](../module-01-yaml-fundamentals/README.md)**
