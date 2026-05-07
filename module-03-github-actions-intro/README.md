# Module 03: GitHub Actions Introduction

**Difficulty:** Beginner | **Time:** 2-3 hours | **Prev:** [Module 02](../module-02-git-fundamentals/README.md) | **Next:** [Module 04 — Workflow Triggers](../module-04-workflow-triggers/README.md)

## Project 1: Hello World Workflow

---

## Learning Objectives

By the end of this module you will:
- Understand what GitHub Actions is and how it fits into the development lifecycle
- Know every core component: workflow, event, job, step, runner, action
- Write and trigger your first workflow
- Navigate the GitHub Actions UI to read logs and re-run jobs
- Use the GitHub Actions Marketplace to find and use pre-built actions

---

## 1. What is GitHub Actions?

GitHub Actions is an **automation platform built directly into GitHub**. It lets you run custom software workflows in response to events in your repository — no external CI server needed.

### What can it do?

- **Continuous Integration (CI):** Run tests on every pull request
- **Continuous Deployment (CD):** Deploy to production after every merge to `main`
- **Automation:** Label issues, send Slack notifications, schedule reports
- **Cross-platform builds:** Build on Linux, Windows, and macOS simultaneously
- **Anything you can script:** If it runs in a shell, GitHub Actions can automate it

### How it compares

| Feature | GitHub Actions | Jenkins | CircleCI |
|---|---|---|---|
| Hosted | Yes (built into GitHub) | No (self-hosted) | Yes |
| Free tier | 2,000 min/month (public: unlimited) | Free (your hardware) | 6,000 credits/month |
| Config location | In your repo (.github/workflows/) | External | In your repo (.circleci/) |
| Marketplace | Yes (thousands of actions) | Plugin ecosystem | Orbs |
| Trigger on GitHub events | Native | Webhook setup | Webhook setup |

### Pricing (GitHub Free tier)
- **Public repositories:** Unlimited GitHub Actions minutes
- **Private repositories:** 2,000 minutes/month free, then pay-per-use
- **Storage for artifacts/caches:** 500 MB free for private repos

---

## 2. Core Components

Understanding these 6 concepts is the foundation for everything else in the course.

### Workflow
A YAML file stored in `.github/workflows/`. Defines the entire automation: what triggers it, what jobs run, and what each job does.

```
your-repo/
└── .github/
    └── workflows/
        ├── ci.yml        ← Workflow 1: CI Pipeline
        └── deploy.yml    ← Workflow 2: Deployment
```

A repository can have unlimited workflow files.

### Event (Trigger)
What causes a workflow to run. Could be a GitHub event (`push`, `pull_request`, `release`) or a time-based trigger (`schedule`) or a manual trigger (`workflow_dispatch`).

```yaml
on:
  push:              # triggered when someone pushes code
  pull_request:      # triggered when a PR is opened/updated
  schedule:          # triggered on a time schedule
  workflow_dispatch: # triggered manually by a user
```

### Job
A group of steps that run together on the same machine. Jobs run in **parallel by default** (unless you declare dependencies with `needs:`).

```yaml
jobs:
  lint:       # Job 1 — runs in parallel with "test"
    runs-on: ubuntu-latest
    steps: ...

  test:       # Job 2 — runs in parallel with "lint"
    runs-on: ubuntu-latest
    steps: ...
```

### Step
A single task within a job. Steps run **sequentially** within a job. A step is either:
- A shell command (`run:`)
- A pre-built action (`uses:`)

```yaml
steps:
  - name: Checkout code         # Step 1 (action)
    uses: actions/checkout@v4

  - name: Run tests             # Step 2 (shell command)
    run: pytest tests/
```

### Runner
The virtual machine (VM) that executes a job. GitHub provides hosted runners:
- `ubuntu-latest` — Ubuntu Linux (most common, fastest startup)
- `windows-latest` — Windows Server
- `macos-latest` — macOS

Each job gets a **fresh, clean runner** — no state from previous jobs or runs.

### Action
A reusable package that performs one task. Actions are the building blocks you `uses:` in steps. They come from:
1. **GitHub Marketplace** (thousands of community/official actions)
2. **The same repository** (`./.github/actions/`)
3. **Another repository** (`owner/repo@version`)

Popular actions you will use throughout this course:
```yaml
uses: actions/checkout@v4        # clone your repo onto the runner
uses: actions/setup-python@v5    # install Python
uses: actions/cache@v4           # cache pip packages
uses: actions/upload-artifact@v4 # save files for later
uses: actions/download-artifact@v4
```

---

## 3. Workflow File Structure

Every workflow file follows this structure:

```
.github/workflows/my-workflow.yml
│
├── name: (optional) display name
│
├── on: (required) trigger events
│
├── env: (optional) workflow-level env vars
│
├── permissions: (optional) GITHUB_TOKEN permissions
│
├── concurrency: (optional) prevent duplicate runs
│
└── jobs: (required)
    │
    └── <job-id>: (required, at least one)
        │
        ├── runs-on: (required) which runner
        ├── needs: (optional) job dependencies
        ├── if: (optional) run condition
        ├── env: (optional) job-level env vars
        ├── outputs: (optional) values to pass downstream
        │
        └── steps: (required)
            │
            └── - name: (optional but recommended)
                  uses: OR run: (required, one or the other)
                  with: (optional, for uses:)
                  env: (optional, step-level env vars)
                  if: (optional, step condition)
                  id: (optional, for referencing outputs)
```

---

## 4. Project 1: Hello World Workflow

### What we build

A simple workflow that:
- Triggers on push and pull_request
- Runs on Ubuntu
- Prints a greeting, date/time, GitHub context info, and lists workspace files

### Step-by-step: Create Your First Workflow

**Step 1:** In your GitHub repository, create the directories:
```
.github/
└── workflows/
```

**Step 2:** Create `.github/workflows/hello-world.yml`

**Step 3:** Copy the content from [project/.github/workflows/hello-world.yml](./project/.github/workflows/hello-world.yml)

**Step 4:** Commit and push:
```bash
git add .github/workflows/hello-world.yml
git commit -m "ci: add hello world workflow"
git push origin main
```

**Step 5:** Go to your GitHub repository → **Actions** tab

**Step 6:** Click the workflow run to see logs

### Reading Workflow Logs

The GitHub Actions UI shows:
```
Workflow Run: "Hello World Workflow"
│
├── Job: greet (ubuntu-latest)
│   │
│   ├── ✅ Set up job
│   ├── ✅ Checkout repository
│   ├── ✅ Say hello
│   ├── ✅ Print date and time
│   ├── ✅ Print GitHub context
│   └── ✅ Complete job
│
└── Run metadata: duration, trigger, actor
```

Click any step to expand and see its output.

---

## 5. Navigating the GitHub Actions UI

### Actions Tab
Find it at: `github.com/YOUR_USERNAME/REPO_NAME/actions`

Shows:
- All workflows (left sidebar)
- All recent runs (main area)
- Status icons: ✅ success, ❌ failed, 🟡 in progress, ⬜ skipped

### Workflow Run Page
Click any run to see:
- Which commit triggered it
- All jobs and their status
- Duration of each job
- Artifacts produced
- "Re-run failed jobs" button

### Job Log Page
Click a job to see:
- Each step with expand/collapse
- Real-time streaming for in-progress runs
- "Search logs" for finding specific output
- Download log option

---

## 6. The GitHub Actions Marketplace

Find pre-built actions at `marketplace.github.com/actions`.

### How to use an action
```yaml
- name: Setup Python
  uses: actions/setup-python@v5    # owner/repo@version
  with:
    python-version: '3.14'         # action inputs (from the action's README)
```

### Security: Always Pin Action Versions

```yaml
# RISKY — "latest" could change unexpectedly
uses: actions/checkout@main

# BETTER — pinned to a tag
uses: actions/checkout@v4

# BEST — pinned to exact commit SHA (immutable, supply-chain safe)
uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683  # v4.2.2
```

For learning purposes in this course, we use `@v4` style tags. In production, use SHA pinning.

---

## 7. Common Beginner Mistakes

| Mistake | Problem | Fix |
|---|---|---|
| Wrong file location | Workflow not picked up | Must be in `.github/workflows/` |
| YAML indentation error | Workflow fails to parse | Use 2 spaces, never tabs |
| Forgot `actions/checkout` | Files not available | Always add checkout as first step |
| Using `main` instead of `ubuntu-latest` for `runs-on` | Parse error | `runs-on: ubuntu-latest` |
| Hardcoding secrets | Security risk | Use `${{ secrets.NAME }}` |
| Not reading error messages | Wasted debugging time | Click the failed step in the UI |

---

## Project Files

| File | What it teaches |
|---|---|
| [hello-world.yml](./project/.github/workflows/hello-world.yml) | Basic workflow structure, steps, context variables |
| [first-workflow-anatomy.yml](./project/.github/workflows/first-workflow-anatomy.yml) | Every YAML element labeled and explained |

---

## References

- ⚡ **Understanding GitHub Actions** — [docs.github.com/en/actions/learn-github-actions/understanding-github-actions](https://docs.github.com/en/actions/learn-github-actions/understanding-github-actions)
- 🚀 **Quickstart for GitHub Actions** — [docs.github.com/en/actions/quickstart](https://docs.github.com/en/actions/quickstart)
- 🛒 **GitHub Actions Marketplace** — [github.com/marketplace?type=actions](https://github.com/marketplace?type=actions)
- 📦 **actions/checkout** — [github.com/actions/checkout](https://github.com/actions/checkout)
- 🐍 **actions/setup-python** — [github.com/actions/setup-python](https://github.com/actions/setup-python)
- 💾 **actions/cache** — [github.com/actions/cache](https://github.com/actions/cache)
- 📤 **actions/upload-artifact** — [github.com/actions/upload-artifact](https://github.com/actions/upload-artifact)
- 🖥️ **About GitHub-hosted Runners** — [docs.github.com/en/actions/using-github-hosted-runners/about-github-hosted-runners](https://docs.github.com/en/actions/using-github-hosted-runners/about-github-hosted-runners)

---

## Next Module

**[Module 04 — Workflow Triggers](../module-04-workflow-triggers/README.md)**
