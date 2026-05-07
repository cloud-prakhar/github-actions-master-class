# Module 04: Workflow Triggers Deep Dive

**Difficulty:** Beginner-Intermediate | **Time:** 2-3 hours | **Prev:** [Module 03](../module-03-github-actions-intro/README.md) | **Next:** [Module 05 — Jobs & Steps](../module-05-jobs-and-steps/README.md)

## Project 2: Multi-Trigger Workflows

---

## Learning Objectives

By the end of this module you will:
- Understand every common GitHub Actions trigger event
- Apply branch, path, and tag filters to push and pull_request events
- Configure scheduled workflows using POSIX cron syntax
- Build manually-triggered workflows with typed inputs
- Control concurrency to prevent duplicate runs
- Know which trigger to use for each use case

---

## 1. The `on:` Key

Every workflow starts with an `on:` block. This block defines all the events that can trigger the workflow.

```yaml
# Single event (simplest form)
on: push

# Multiple events (list form)
on: [push, pull_request]

# Events with configuration (mapping form — most flexible)
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  schedule:
    - cron: '0 6 * * *'
  workflow_dispatch: {}
```

---

## 2. Push Events

Triggers when commits are pushed to a branch or a tag is pushed.

### Basic Push Trigger
```yaml
on:
  push:        # triggers on push to ANY branch
```

### Branch Filters
```yaml
on:
  push:
    branches:
      - main             # exact match
      - develop
      - "release/**"     # wildcard: release/1.0, release/2.0, etc.
      - "feature/**"     # any feature/* branch

    branches-ignore:     # alternative: EXCLUDE these branches
      - "dependabot/**"  # skip automated dependency update branches
```

> You cannot use `branches:` and `branches-ignore:` together on the same event.

### Path Filters — Only Trigger When Specific Files Change
```yaml
on:
  push:
    branches: [main]
    paths:
      - "src/**"           # any file in src/ directory
      - "tests/**"         # any file in tests/ directory
      - "requirements*.txt" # requirements.txt or requirements-dev.txt

    paths-ignore:          # trigger UNLESS only these files changed
      - "docs/**"
      - "*.md"
      - ".gitignore"
```

**When to use path filters:**
- Monorepos where different services have their own CI
- Skip expensive CI when only docs changed
- Trigger deployment only when source code changes

### Tag Filters — Trigger on Release Tags
```yaml
on:
  push:
    tags:
      - "v*"        # v1.0.0, v2.1.3, etc.
      - "v[0-9]+.[0-9]+.[0-9]+"  # strict semver pattern
```

---

## 3. Pull Request Events

Triggers when activity happens on a pull request.

### Basic Pull Request Trigger
```yaml
on:
  pull_request:        # triggers on all PR activity to any branch
```

### Activity Types
By default, `pull_request` triggers on: `opened`, `synchronize` (new push), `reopened`.

You can specify exactly which activities trigger:
```yaml
on:
  pull_request:
    types:
      - opened        # PR first created
      - synchronize   # new commits pushed to the PR
      - reopened      # closed PR reopened
      - closed        # PR closed (merged or abandoned)
      - labeled       # a label added
      - unlabeled     # a label removed
      - ready_for_review  # draft PR marked as ready
```

### Branch Filters on PRs
```yaml
on:
  pull_request:
    branches:
      - main          # only PRs that TARGET main
      - develop       # or PRs that TARGET develop
```

### `pull_request` vs `pull_request_target`

| | `pull_request` | `pull_request_target` |
|---|---|---|
| Code runs | Untrusted fork code | YOUR repository code |
| Secrets access | Not available for forks | Available |
| Security | Safer for forks | Dangerous — audit carefully |
| Use case | Standard CI | PRs that need to post comments/labels |

---

## 4. Schedule Events (Cron)

Triggers on a time-based schedule. Uses POSIX cron syntax.

```yaml
on:
  schedule:
    - cron: '0 6 * * 1-5'    # 6:00 AM UTC, Monday-Friday
```

### Cron Syntax

```
┌───── minute (0-59)
│ ┌─── hour (0-23)
│ │ ┌─ day of month (1-31)
│ │ │ ┌ month (1-12 or JAN-DEC)
│ │ │ │ ┌ day of week (0-6 or SUN-SAT, 0=Sunday)
│ │ │ │ │
* * * * *
```

| Expression | Meaning |
|---|---|
| `0 0 * * *` | Daily at midnight UTC |
| `0 6 * * 1-5` | 6 AM UTC, Mon-Fri |
| `0 */6 * * *` | Every 6 hours |
| `0 9 * * 1` | 9 AM UTC every Monday |
| `30 14 1 * *` | 2:30 PM UTC, 1st of every month |
| `0 0 * * 0` | Every Sunday at midnight |
| `*/15 * * * *` | Every 15 minutes |

### Important Cron Notes
- All times are **UTC** — no timezone support
- GitHub may delay scheduled runs by up to 15 minutes during high load
- If a repo is inactive for 60+ days, GitHub **disables** scheduled workflows
- Use `workflow_dispatch` alongside `schedule` to run manually when needed

---

## 5. Manual Triggers (workflow_dispatch)

Allows users to trigger the workflow from the GitHub UI or CLI.

### Basic Manual Trigger
```yaml
on:
  workflow_dispatch: {}    # no inputs
```

### With Input Parameters
```yaml
on:
  workflow_dispatch:
    inputs:
      environment:
        description: 'Deployment target'
        type: choice
        options: [dev, staging, production]
        required: true
        default: dev

      version:
        description: 'Version to deploy (e.g. 1.2.3)'
        type: string
        required: true

      dry_run:
        description: 'Dry run only (no actual changes)'
        type: boolean
        default: false

      log_level:
        description: 'Log verbosity'
        type: choice
        options: [debug, info, warning, error]
        default: info
```

**Accessing inputs in the workflow:**
```yaml
steps:
  - run: |
      echo "Environment: ${{ inputs.environment }}"
      echo "Version: ${{ inputs.version }}"
      echo "Dry run: ${{ inputs.dry_run }}"
```

**Triggering from CLI:**
```bash
# Run with defaults
gh workflow run my-workflow.yml

# Run with specific inputs
gh workflow run my-workflow.yml \
  -f environment=staging \
  -f version=1.2.3 \
  -f dry_run=true

# On a specific branch
gh workflow run my-workflow.yml --ref develop -f environment=dev
```

---

## 6. Other Important Events

### Release Events
```yaml
on:
  release:
    types: [published]    # only on published releases, not drafts
```

### Issue and PR Comments
```yaml
on:
  issue_comment:
    types: [created]
```

### Create/Delete Branch or Tag
```yaml
on:
  create:    # branch or tag was created
  delete:    # branch or tag was deleted
```

### Workflow Call (Reusable Workflows — Module 11)
```yaml
on:
  workflow_call:
    inputs:
      python-version:
        type: string
    secrets:
      API_KEY:
        required: true
```

---

## 7. Concurrency Control

Prevents multiple runs of the same workflow from stepping on each other.

```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```

### Group Key Strategies
```yaml
# Per branch — cancel older run on same branch
group: ${{ github.workflow }}-${{ github.ref }}

# Per PR — cancel older run on same PR
group: ${{ github.workflow }}-${{ github.event.pull_request.number || github.ref }}

# Per workflow only — only one run at a time globally
group: ${{ github.workflow }}
```

### `cancel-in-progress`
- `true`: Cancel the older run when a new one starts (great for PRs — test latest code)
- `false`: Queue the new run, let the current one finish (great for deployments)

---

## 8. Combining Triggers

A single workflow can have multiple triggers. Use `github.event_name` to differentiate:

```yaml
on:
  push:
    branches: [main]
  schedule:
    - cron: '0 0 * * *'
  workflow_dispatch: {}

jobs:
  run:
    runs-on: ubuntu-latest
    steps:
      - name: Show trigger
        run: |
          echo "Triggered by: ${{ github.event_name }}"
          if [ "${{ github.event_name }}" == "schedule" ]; then
            echo "This is the daily scheduled run"
          elif [ "${{ github.event_name }}" == "workflow_dispatch" ]; then
            echo "This was triggered manually"
          else
            echo "This was triggered by a push to main"
          fi
```

---

## Project Files

| File | What it teaches |
|---|---|
| [push-triggers.yml](./project/.github/workflows/push-triggers.yml) | Branch + path filters on push |
| [pull-request-triggers.yml](./project/.github/workflows/pull-request-triggers.yml) | PR event types, branch filters |
| [scheduled-workflow.yml](./project/.github/workflows/scheduled-workflow.yml) | Cron scheduling, cron syntax |
| [manual-dispatch.yml](./project/.github/workflows/manual-dispatch.yml) | All input types, workflow_dispatch |

---

## References

- **Events that trigger workflows** — search "Events that trigger workflows GitHub Actions docs"
- **Workflow syntax: on** — search "Workflow syntax for GitHub Actions on"
- **Cron expression tester** — search "crontab guru" (interactive cron builder)

---

## Next Module

**[Module 05 — Jobs & Steps Deep Dive](../module-05-jobs-and-steps/README.md)**
