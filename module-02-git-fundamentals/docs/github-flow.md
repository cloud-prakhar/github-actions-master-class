# GitHub Flow — Complete Guide

GitHub Flow is the branching strategy used throughout this course. It is simple, powerful, and connects directly to GitHub Actions CI/CD pipelines.

---

## What is GitHub Flow?

GitHub Flow is a lightweight workflow with one rule: **`main` is always deployable.**

Everything else follows from that rule:
- Never commit untested code directly to `main`
- All work happens on feature branches
- Branches merge to `main` only after review and CI passes
- After merging, deploy immediately (or automatically)

---

## The Flow — Step by Step

```
main:    ──●──────────────────────────────●──────►
                                          │
              ●──●──●  (your branch)  ──►merge
              │
          git switch -c feature/my-thing
```

### Step 1: Pull Latest main

Before starting any work, sync with the remote:

```bash
git switch main
git pull origin main
```

Why: Ensures your branch starts from the latest state, minimizing merge conflicts later.

### Step 2: Create a Branch

Name branches clearly. Include the type of change and a short description:

```bash
git switch -c feature/user-authentication
git switch -c fix/login-null-pointer
git switch -c docs/update-api-guide
git switch -c chore/upgrade-flask-3
```

**Branch naming conventions:**
```
feature/  — new functionality
fix/      — bug fixes
docs/     — documentation only
chore/    — maintenance (deps, config)
test/     — adding tests
refactor/ — code changes without behavior change
hotfix/   — urgent production fixes
```

### Step 3: Commit Early and Often

Make small, focused commits. Each commit should do one logical thing:

```bash
# Bad commit — too many unrelated things
git commit -m "fix stuff and add feature and update docs"

# Good commits — one thing each
git commit -m "feat(auth): add password hashing with bcrypt"
git commit -m "feat(auth): add login endpoint POST /auth/login"
git commit -m "test(auth): add unit tests for login flow"
```

**When to commit:**
- After you get a small piece working
- Before switching to a different task
- After fixing a bug
- After writing tests

### Step 4: Push Your Branch

Push early — this creates a backup and lets others see your work:

```bash
git push -u origin feature/user-authentication
```

The `-u` flag sets the upstream, so future pushes are just `git push`.

### Step 5: Open a Pull Request

When your feature is ready for review (or even if it's still in progress — use Draft PRs):

```bash
# Via GitHub CLI
gh pr create \
  --title "feat(auth): add user authentication" \
  --body "## Summary
- Add login/logout endpoints
- Add password hashing with bcrypt
- Add JWT token generation

## Test plan
- [ ] Unit tests pass
- [ ] Manual login test on staging
- [ ] Logout clears session"

# Via GitHub UI: click "Compare & pull request" banner that appears after push
```

**What happens when you open a PR:**
```
PR opened
    │
    ▼
GitHub Actions CI starts
    ├── Lint check
    ├── Unit tests
    └── Security scan
    │
    ▼
Status checks appear on PR page
    │
    ├── CI passes → green checkmark ✅
    │   └── Reviewers can now approve
    │
    └── CI fails → red X ❌
        └── Fix the issue and push again (CI re-runs automatically)
```

### Step 6: Review and Discuss

Reviewers look at your changes and leave comments:
- **Comment:** Ask questions or suggest changes
- **Approve:** The code is ready to merge
- **Request changes:** Changes required before merging

**As the author:**
- Address every comment (either make the change or explain why not)
- Push new commits to the same branch — the PR updates automatically
- Don't `git push --force` on a PR branch while others are reviewing

### Step 7: Merge

Once approved and CI passes:

```bash
# Via GitHub UI: click "Merge pull request"
# Or via CLI:
gh pr merge --squash --delete-branch
```

**Merging options:**
| Option | What it does | When to use |
|---|---|---|
| Merge commit | Keeps all commits, adds merge commit | Long-lived features |
| Squash and merge | All commits become one | Short features, clean history |
| Rebase and merge | Replays commits on top of main | Teams preferring linear history |

### Step 8: Delete the Branch and Deploy

After merging:
```bash
# Delete the remote branch (or let GitHub do it automatically)
git push origin --delete feature/user-authentication

# Delete your local branch
git branch -d feature/user-authentication

# Pull the merged changes locally
git switch main
git pull origin main
```

GitHub Actions can now automatically deploy `main` to production.

---

## The Full Picture

```
Developer Workflow                    GitHub Actions Pipeline
─────────────────                    ───────────────────────
git switch -c feature/x
  │
  ▼
[code, commit, commit]
  │
  ▼
git push origin feature/x ──────────► PR opened → CI runs
  │                                       ├── lint
  │                                       ├── test
  │                                       └── security scan
  │
  ▼                                   CI passes → PR can merge
[review, address comments]
  │
  ▼
PR approved
  │
  ▼
Merge to main ──────────────────────► push to main → CD runs
  │                                       └── deploy to production
  ▼
Delete branch
```

---

## Draft Pull Requests

Open a PR before your code is complete to get early feedback or show work-in-progress:

```bash
gh pr create --draft --title "WIP: feat(auth): user authentication"
```

Draft PRs:
- Cannot be merged (protected by GitHub)
- Run CI just like regular PRs
- Signal to reviewers: "not ready yet"
- Convert to ready with: `gh pr ready`

---

## Branch Protection Rules

Configure these in your GitHub repository settings (Settings → Branches → Add rule):

| Rule | Why |
|---|---|
| Require PR before merging | No direct pushes to `main` |
| Require status checks to pass | CI must pass before merge |
| Require at least 1 approval | Code review is mandatory |
| Dismiss stale reviews | New pushes invalidate old approvals |
| Require branches to be up to date | No merging outdated branches |

With these rules, GitHub Actions becomes the **gatekeeper** — code cannot reach `main` unless the pipeline passes.

---

## Common Workflow Commands Reference

```bash
# Start a new task
git switch main && git pull origin main
git switch -c feature/my-task

# During development
git add -p                         # stage interactively
git commit -m "feat: implement X"
git push origin feature/my-task    # backup + share

# Keep your branch up to date with main
git fetch origin
git rebase origin/main             # replay your commits on top of latest main

# Open PR
gh pr create --title "feat: implement X" --body "..."

# After merge
git switch main && git pull origin main
git branch -d feature/my-task
```
