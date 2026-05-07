# Git Cheat Sheet

Quick reference for the most common Git commands.

---

## Setup

```bash
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
git config --global core.editor "code --wait"
git config --global init.defaultBranch main
git config --list                              # view all settings
```

---

## Creating Repositories

```bash
git init                                       # init new repo in current dir
git init my-project                            # init in new folder
git clone <url>                                # clone remote repo
git clone <url> <folder>                       # clone into specific folder
git clone --depth 1 <url>                      # shallow clone (only latest commit)
```

---

## Basic Workflow

```bash
git status                                     # show working tree status
git diff                                       # changes not yet staged
git diff --staged                              # changes staged for commit
git diff HEAD                                  # all changes vs last commit

git add <file>                                 # stage specific file
git add .                                      # stage everything in current dir
git add -p                                     # stage hunks interactively

git commit -m "message"                        # commit with message
git commit -am "message"                       # stage all tracked + commit
git commit --amend                             # edit the last commit
```

---

## Branching

```bash
git branch                                     # list local branches
git branch -a                                  # list all (local + remote)
git branch -v                                  # list with last commit

git switch main                                # switch to branch
git switch -c feature/new-thing               # create and switch

git branch -d feature/done                     # delete (safe — merged only)
git branch -D feature/nope                     # force delete (unmerged)
git branch -m old-name new-name               # rename branch
```

---

## Remote Operations

```bash
git remote -v                                  # show remotes
git remote add origin <url>                    # add remote named "origin"
git remote set-url origin <new-url>            # change remote URL

git fetch origin                               # download (don't merge)
git pull origin main                           # fetch + merge
git pull --rebase origin main                  # fetch + rebase

git push origin main                           # push to remote
git push -u origin feature/x                  # push + set upstream
git push --tags                               # push all tags
git push origin --delete feature/old          # delete remote branch
```

---

## Merging

```bash
git merge feature/x                            # merge into current branch
git merge --no-ff feature/x                   # always create merge commit
git merge --squash feature/x                  # squash all commits to one
git merge --abort                             # abort in-progress merge
```

---

## Rebasing

```bash
git rebase main                                # rebase current branch onto main
git rebase -i HEAD~3                           # interactive rebase (last 3 commits)
git rebase --continue                         # continue after resolving conflict
git rebase --abort                            # abort rebase
```

---

## Inspection & History

```bash
git log                                        # full log
git log --oneline                             # compact log
git log --oneline --graph --all               # visual branch graph
git log --stat                                # log with file stats
git log -p                                    # log with full diff
git log --author="Alice"                      # filter by author
git log --grep="keyword"                      # filter by commit message
git log --since="2 weeks ago"                 # filter by date
git log -- path/to/file                       # history of a file

git show <commit>                              # show commit details + diff
git show HEAD                                  # show latest commit
git blame <file>                              # who changed each line
git diff <branch1>..<branch2>                 # diff between two branches
```

---

## Tagging

```bash
git tag                                        # list all tags
git tag v1.0.0                                # create lightweight tag
git tag -a v1.0.0 -m "Release 1.0.0"         # annotated tag
git push origin v1.0.0                        # push specific tag
git push origin --tags                        # push all tags
git tag -d v1.0.0                             # delete local tag
git push origin :refs/tags/v1.0.0            # delete remote tag
```

---

## Stashing

```bash
git stash                                      # save changes temporarily
git stash push -m "description"              # stash with name
git stash list                                # list all stashes
git stash pop                                 # apply latest and remove
git stash apply stash@{0}                    # apply without removing
git stash drop stash@{0}                     # delete a stash
git stash clear                              # delete all stashes
```

---

## Undoing Changes

```bash
# Unstage (keep working dir changes)
git restore --staged <file>

# Discard working dir changes (CANNOT UNDO!)
git restore <file>

# Undo last commit, keep staged
git reset --soft HEAD~1

# Undo last commit, unstage (default)
git reset --mixed HEAD~1

# Undo last commit, discard changes (CANNOT UNDO!)
git reset --hard HEAD~1

# Safe undo — create new reverting commit
git revert <commit-sha>
git revert HEAD                               # revert latest commit
```

---

## Resolving Conflicts

```bash
# After a merge conflict:
# 1. Open the conflicting files and fix the <<<<< ===== >>>>> markers
# 2. Stage the fixed files
git add <resolved-file>
# 3. Complete the merge
git commit

# Or abort entirely
git merge --abort
```

---

## Useful Aliases (add to ~/.gitconfig)

```ini
[alias]
  st = status
  co = checkout
  br = branch
  ci = commit
  lg = log --oneline --graph --all --decorate
  last = log -1 HEAD
  unstage = restore --staged
  undo = reset --soft HEAD~1
```

---

## .gitignore Patterns

```gitignore
# Files
secret.key
.env
*.pyc
__pycache__/

# Directories
__pycache__/
dist/
.venv/
*.egg-info/
htmlcov/

# Wildcards
*.log          # any .log file
**/temp/       # any directory named temp
!important.log # exception: do NOT ignore this file
```

---

## Commit Message Best Practices (Conventional Commits)

```
<type>(<scope>): <short description>

[optional body]

[optional footer]
```

**Types:**
- `feat:` — new feature
- `fix:` — bug fix
- `docs:` — documentation only
- `style:` — formatting, no logic change
- `refactor:` — code change that is neither fix nor feature
- `test:` — adding or fixing tests
- `chore:` — build process, dependency updates
- `ci:` — CI/CD pipeline changes

**Examples:**
```
feat(auth): add OAuth2 login with GitHub
fix(api): handle null response from payment service
docs: update README with local setup instructions
ci: add Python 3.14 to matrix build
test(login): add integration tests for MFA flow
```
