# Module 02: Git Fundamentals

**Difficulty:** Beginner | **Time:** 2-3 hours | **Prev:** [Module 01](../module-01-yaml-fundamentals/README.md) | **Next:** [Module 03 — GitHub Actions Introduction](../module-03-github-actions-intro/README.md)

---

## Learning Objectives

By the end of this module you will:
- Understand what Git is and why it exists
- Know the core Git concepts: repository, commit, branch, HEAD, staging area
- Use the essential Git commands confidently
- Understand GitHub Flow (the workflow used throughout this course)
- Create and merge pull requests
- Know how Git events (push, PR) connect to GitHub Actions triggers

---

## 1. What is Git?

Git is a **distributed version control system**. It tracks every change ever made to a codebase, who made it, and when. You can rewind to any point in history, work on multiple features simultaneously, and merge everyone's work together.

**Why does this matter for GitHub Actions?**
GitHub Actions is triggered by Git events. A `push` event, a pull request opened, a tag created — all of these are Git operations that flow through GitHub and can trigger automated workflows.

### Centralized vs Distributed

| Centralized (old) | Distributed (Git) |
|---|---|
| One server holds all history | Every developer has full history locally |
| Offline work is very limited | Full Git functionality offline |
| Server failure = data loss | Many full copies of the repo |
| Example: SVN, CVS | Example: Git |

---

## 2. Core Git Concepts

### Repository (Repo)
A directory tracked by Git. Contains your project files plus a hidden `.git/` folder that stores all version history.

```
my-project/
├── .git/           ← Git stores EVERYTHING here (don't touch manually)
├── src/
├── tests/
└── README.md
```

- **Local repository:** on your computer
- **Remote repository:** on GitHub, GitLab, Bitbucket, etc.

### Commit
A **snapshot** of the entire project at a point in time. Not a diff — a full snapshot (though Git stores it efficiently as diffs internally). Each commit has:
- A unique SHA hash (e.g., `a3f8c2d`)
- Author name and email
- Timestamp
- Commit message
- Reference to parent commit(s)

```
Commit history (newest first):
a3f8c2d ← Add login page (Alice, 2 hours ago)
b1d9e4f ← Fix signup validation (Bob, 5 hours ago)
c6a2f1e ← Initial project setup (Alice, 1 day ago)
```

### Branch
A lightweight, movable pointer to a commit. Creating a branch does NOT copy the code — it just creates a new pointer. This is why Git branches are instant and free.

```
main branch:    A ← B ← C ← D
                              ↑
                             HEAD
                              ↑
feature branch: A ← B ← C ← E ← F
```

### HEAD
A special pointer that tells Git "which commit you are currently looking at." Usually points to the tip of your current branch.

### Staging Area (Index)
A preparation zone between your working directory and commits. You `git add` files to the staging area, then `git commit` takes a snapshot of everything staged.

```
Working Directory → (git add) → Staging Area → (git commit) → Repository
(you edit files)               (files ready     (saved snapshot)
                                to commit)
```

### Working Directory
The actual files on your disk. Git calls untracked changes here "untracked" or "modified."

---

## 3. Essential Git Commands

### Setup (run once)
```bash
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
git config --global init.defaultBranch main
```

### Starting a Repository
```bash
# Create a new repo from scratch
git init

# Copy an existing remote repo
git clone git@github.com:username/repo.git
git clone https://github.com/username/repo.git

# Clone into a specific folder name
git clone git@github.com:username/repo.git my-folder
```

### Core Daily Workflow
```bash
# See what's changed
git status

# See the actual changes (unstaged)
git diff

# See staged changes (what will be committed)
git diff --staged

# Stage a specific file
git add src/app.py

# Stage all changed files
git add .

# Commit staged changes
git commit -m "Add user authentication"

# Stage + commit in one step (only for tracked files)
git commit -am "Fix typo in README"
```

### Synchronizing with Remote
```bash
# Download remote changes (doesn't modify working files)
git fetch origin

# Download AND merge remote changes into your current branch
git pull origin main

# Upload your commits to remote
git push origin main

# Push a new branch and set upstream tracking
git push -u origin feature/my-feature
```

### Branching
```bash
# List all local branches
git branch

# List all branches (local + remote)
git branch -a

# Create a new branch
git branch feature/add-login

# Switch to a branch
git checkout feature/add-login
# Modern syntax (Git 2.23+):
git switch feature/add-login

# Create AND switch in one step
git checkout -b feature/add-login
# Modern syntax:
git switch -c feature/add-login

# Delete a branch (after merging)
git branch -d feature/add-login

# Delete a branch (even if not merged — be careful!)
git branch -D feature/add-login

# Rename current branch
git branch -m new-name
```

### Viewing History
```bash
# Full commit log
git log

# Compact one-line log
git log --oneline

# Graph view (great for seeing branches)
git log --oneline --graph --all

# See what changed in a specific commit
git show a3f8c2d

# Search commits by message
git log --grep="authentication"

# Search commits by author
git log --author="Alice"
```

### Merging
```bash
# Merge a branch into current branch
git merge feature/add-login

# Merge with a merge commit always (no fast-forward)
git merge --no-ff feature/add-login

# Squash all branch commits into one before merging
git merge --squash feature/add-login
git commit -m "Add login feature (squashed)"
```

### Stashing (save work temporarily)
```bash
# Save uncommitted changes temporarily
git stash

# With a description
git stash push -m "half-finished login form"

# List all stashes
git stash list

# Apply the most recent stash
git stash pop

# Apply a specific stash
git stash apply stash@{2}
```

### Undoing Things
```bash
# Unstage a file (keep changes in working dir)
git restore --staged src/app.py

# Discard working directory changes (DANGEROUS — cannot undo!)
git restore src/app.py

# Undo last commit but keep changes staged
git reset --soft HEAD~1

# Undo last commit and unstage changes
git reset --mixed HEAD~1

# Undo last commit AND discard changes (DANGEROUS!)
git reset --hard HEAD~1

# Create a new commit that reverses a previous commit (safe)
git revert a3f8c2d
```

---

## 4. Branching Strategies

### GitHub Flow (Used in This Course)

The simplest branching strategy. Perfect for teams deploying frequently.

```
main branch (always deployable)
│
├── feature/user-auth       ← developer works here
│   └── [open PR → review → merge to main → delete branch]
│
├── bugfix/fix-login-404    ← another developer
│   └── [open PR → review → merge to main → delete branch]
│
└── feature/dashboard       ← another developer
    └── [open PR → review → merge to main → delete branch]
```

**Rules:**
1. `main` is always production-ready and deployable
2. Create a branch for every feature, bug fix, or experiment
3. Commit to your branch often
4. Open a Pull Request when ready for review
5. After PR is approved, merge to `main`
6. Delete the branch after merging

### Git Flow (for Release-Based Projects)

More complex. Used when you have scheduled releases.

```
main       ──A──────────────────────M───
develop    ──A──B──C──D──────────R──M──
feature    ──────B──C──┤
release    ──────────────D──R──┤
hotfix     ──────────────────────────H─
```

- `main` — production code only
- `develop` — integration branch for features
- `feature/*` — new features (branch from develop)
- `release/*` — release preparation (branch from develop)
- `hotfix/*` — emergency fixes (branch from main)

---

## 5. Pull Requests

A Pull Request (PR) is a GitHub feature (not a Git feature) that:
1. Proposes merging one branch into another
2. Shows a diff of all changes
3. Allows team members to leave comments and approve
4. Triggers CI/CD workflows
5. Enforces branch protection rules (required reviews, status checks)

### Creating a PR
```bash
# 1. Create and switch to your feature branch
git switch -c feature/add-search

# 2. Make your changes
# edit files...

# 3. Commit your work
git add .
git commit -m "Add search functionality to product listing"

# 4. Push to GitHub
git push -u origin feature/add-search

# 5. Open a PR via GitHub UI or CLI
gh pr create --title "Add search functionality" \
             --body "Implements search for product listing page"
```

### Merging Strategies
| Strategy | Creates merge commit | Preserves history | Good for |
|---|---|---|---|
| Merge commit | Yes | Full branch history | Long-lived features |
| Squash merge | No | Single tidy commit | Short features, experiments |
| Rebase merge | No | Linear history | Teams that prefer clean history |

---

## 6. Git and GitHub Actions — The Connection

This is why Git matters for your CI/CD pipelines:

```
Developer pushes to main
        │
        ▼
GitHub receives the push event
        │
        ▼
GitHub Actions sees the "push" trigger
        │
        ▼
Workflow starts automatically
    ├── Run tests
    ├── Build application
    └── Deploy to staging
```

**Git event → GitHub Actions trigger mapping:**

| Git Action | GitHub Actions Event |
|---|---|
| `git push` to a branch | `on: push` |
| PR opened / updated | `on: pull_request` |
| Tag pushed (`git tag v1.0 && git push --tags`) | `on: push` with `tags:` filter |
| PR merged (it's a push to main) | `on: push` on target branch |
| Release created on GitHub | `on: release` |

**Branch filters in GitHub Actions:**
```yaml
on:
  push:
    branches:
      - main          # only trigger on main
      - develop       # or develop
      - "feature/**"  # or any feature/* branch
```

---

## 7. Git Cheat Sheet

See the full reference: **[docs/git-cheatsheet.md](./docs/git-cheatsheet.md)**

---

## 8. GitHub Flow Walkthrough

See the detailed guide: **[docs/github-flow.md](./docs/github-flow.md)**

---

## Exercises

### Exercise 1 — Basic Workflow
1. Initialize a new Git repository locally
2. Create a `README.md` with some content
3. Stage and commit it
4. Create a branch called `feature/update-readme`
5. Make a change to `README.md` on that branch
6. Commit the change
7. Switch back to `main` and merge the feature branch
8. Delete the feature branch

### Exercise 2 — Remote Workflow
1. Create a new repository on GitHub (use the GitHub UI)
2. Clone it locally
3. Create a branch, add a file, push the branch
4. Open a Pull Request using `gh pr create`
5. Merge the PR on GitHub
6. Pull the changes back locally

### Exercise 3 — Explore the Course Repo
1. Run `git log --oneline --graph --all` in this course repo
2. Find out the first commit: `git log --oneline | tail -1`
3. See what files changed in that commit: `git show <sha>`
4. Check the current branch: `git branch`

---

## Common Mistakes

| Mistake | Fix |
|---|---|
| Committing directly to `main` | Always branch first: `git switch -c feature/...` |
| Forgetting to `git pull` before branching | Always `git pull origin main` first |
| Huge commits with many unrelated changes | Commit often, one logical change per commit |
| Vague commit messages ("fix bug", "update") | Be specific: "Fix null pointer in user login" |
| Pushing secrets or API keys | Add to `.gitignore`, use git-secrets tool |
| `git add .` without reviewing | Run `git status` and `git diff` first |

---

## References

- **Official Git documentation** — search "Git reference manual git-scm.com"
- **Pro Git Book** — search "Pro Git book online free" (free, comprehensive)
- **GitHub Flow guide** — search "GitHub Flow GitHub docs"
- **Conventional Commits** — search "Conventional Commits specification"

---

## Next Module

**[Module 03 — GitHub Actions Introduction](../module-03-github-actions-intro/README.md)**
