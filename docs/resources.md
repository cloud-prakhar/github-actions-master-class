# Resources & References

All the links, tools, playgrounds, and cheat sheets you need alongside this course.

---

## Official Documentation

Search these topics on **docs.github.com** for authoritative, always-up-to-date content:

| Topic | What to search |
|---|---|
| GitHub Actions overview | "Understanding GitHub Actions" |
| Workflow syntax reference | "Workflow syntax for GitHub Actions" |
| Events that trigger workflows | "Events that trigger workflows" |
| Contexts reference | "Contexts" GitHub Actions |
| Expressions syntax | "Expressions" GitHub Actions |
| Environment variables | "Variables" GitHub Actions |
| Encrypted secrets | "Using secrets in GitHub Actions" |
| Environments | "Using environments for deployment" |
| Caching dependencies | "Caching dependencies to speed up workflows" |
| Artifacts | "Storing workflow data as artifacts" |
| Matrix strategy | "Using a matrix for your jobs" |
| Reusable workflows | "Reusing workflows" |
| Composite actions | "Creating a composite action" |
| GITHUB_TOKEN | "Automatic token authentication" |
| Security hardening | "Security hardening for GitHub Actions" |
| Self-hosted runners | "About self-hosted runners" |
| Service containers | "About service containers" |
| Job summaries | "Adding a job summary" |
| Workflow commands | "Workflow commands for GitHub Actions" |

---

## GitHub Actions Marketplace

The Marketplace hosts thousands of pre-built actions maintained by GitHub, companies, and the community.

- URL: `marketplace.github.com/actions`
- Search for actions by category: CI, deployment, code quality, notifications, etc.
- Always check: number of stars, last updated date, whether the author is verified

**Most commonly used actions in this course:**

| Action | Purpose |
|---|---|
| `actions/checkout@v4` | Check out your repository code |
| `actions/setup-python@v5` | Install Python |
| `actions/setup-python@v5` | Install Python |
| `actions/cache@v4` | Cache dependencies |
| `actions/upload-artifact@v4` | Save files from a job |
| `actions/download-artifact@v4` | Load files in a later job |
| `actions/github-script@v7` | Run JavaScript with GitHub API access |

---

## Interactive Playgrounds

### GitHub Workflow Editor (in-browser)
GitHub's repository UI has built-in workflow editing with syntax highlighting, autocompletion, and validation. Navigate to:
```
Your repo → Actions tab → New workflow → Set up a workflow yourself
```
The editor validates YAML as you type and suggests event names, action names, and more.

### act — Run Workflows Locally
`act` lets you run GitHub Actions on your local machine using Docker. It mirrors the GitHub runner environment.

- Repository: Search "nektos/act" on GitHub
- Installation:
  ```bash
  # macOS
  brew install act

  # Windows (via Chocolatey)
  choco install act-cli

  # Linux
  curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash
  ```
- Usage:
  ```bash
  act                              # Run all push-triggered workflows
  act pull_request                 # Simulate a pull_request event
  act workflow_dispatch            # Trigger workflow_dispatch
  act -W .github/workflows/ci.yml  # Run a specific workflow
  act -j build                     # Run a specific job
  act --list                       # List all workflows and jobs
  ```

### YAML Lint Tools
- Search "YAML Lint online" — paste YAML to validate syntax
- VS Code YAML extension: install "YAML" by Red Hat for real-time validation
- `yamllint` CLI tool: `pip install yamllint` then `yamllint your-file.yaml`

---

## Recommended VS Code Extensions

| Extension | Purpose |
|---|---|
| GitHub Actions (by GitHub) | Workflow autocomplete, validation, run history |
| YAML (by Red Hat) | YAML syntax validation and IntelliSense |
| GitLens | Advanced Git history and blame |
| GitHub Pull Requests | Manage PRs from within VS Code |

---

## Learning Resources

### GitHub Learning Lab / GitHub Skills
Search "GitHub Skills" on github.com — free interactive courses running directly in your own GitHub repositories. Relevant courses:
- "Hello GitHub Actions"
- "Continuous Integration"
- "Continuous Delivery"
- "Publish to GitHub Packages"

### Books
- *Learning GitHub Actions* by Brent Laster (O'Reilly)
- *GitHub Actions Cookbook* — search O'Reilly

### Video Courses
- Search "GitHub Actions full course" on YouTube — many free comprehensive tutorials
- Search "GitHub Actions" on platforms like Udemy, Pluralsight, LinkedIn Learning

---

## GitHub Actions Cheat Sheet

```yaml
# ─── WORKFLOW SKELETON ───────────────────────────────────────────
name: Workflow Name

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  schedule:
    - cron: '0 6 * * 1-5'          # 6 AM UTC Mon-Fri
  workflow_dispatch:
    inputs:
      env:
        type: choice
        options: [dev, staging, production]

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

permissions:
  contents: read

env:
  APP_NAME: my-app                  # workflow-level env var

# ─── JOB SKELETON ────────────────────────────────────────────────
jobs:
  build:
    name: Build
    runs-on: ubuntu-latest
    timeout-minutes: 15
    env:
      APP_ENV: production           # job-level env var
    outputs:
      version: ${{ steps.version.outputs.value }}

    steps:
      # ─── ACTION STEP ─────────────────────────────────────────
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.14'
          cache: 'pip'

      # ─── SHELL STEP ──────────────────────────────────────────
      - name: Install dependencies
        run: pip install -r requirements.txt -r requirements-dev.txt

      # ─── MULTILINE STEP ──────────────────────────────────────
      - name: Lint and test
        run: |
          flake8 src/ tests/ --max-line-length=120
          pytest tests/ -v --cov=src

      # ─── STEP OUTPUT ─────────────────────────────────────────
      - id: version
        run: echo "value=1.0.0" >> $GITHUB_OUTPUT

      # ─── CONDITIONAL STEP ────────────────────────────────────
      - name: Deploy
        if: github.ref == 'refs/heads/main'
        run: ./deploy.sh

      # ─── STEP WITH ENV ───────────────────────────────────────
      - name: Notify
        run: curl -X POST $WEBHOOK_URL
        env:
          WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK }}

      # ─── ALWAYS RUN ──────────────────────────────────────────
      - name: Cleanup
        if: always()
        run: ./cleanup.sh

# ─── DEPENDENT JOB ───────────────────────────────────────────────
  deploy:
    needs: build                    # waits for build
    runs-on: ubuntu-latest
    environment: production
    steps:
      - run: echo "Version: ${{ needs.build.outputs.version }}"

# ─── MATRIX JOB ──────────────────────────────────────────────────
  test-matrix:
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest]
        python-version: ['3.13', '3.14']
      fail-fast: false
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

# ─── REUSABLE WORKFLOW CALL ──────────────────────────────────────
  call-reusable:
    uses: ./.github/workflows/reusable.yml
    with:
      python-version: '3.14'
    secrets: inherit
```

---

## Key GitHub Contexts Quick Reference

```
github.actor          → username who triggered the run
github.event_name     → push | pull_request | schedule | workflow_dispatch
github.ref            → refs/heads/main | refs/tags/v1.0.0
github.sha            → full commit SHA
github.repository     → owner/repo-name
github.workspace      → /home/runner/work/repo-name/repo-name
github.run_id         → unique run ID (number)
github.run_number     → sequential run number for this workflow

runner.os             → Linux | Windows | macOS
runner.arch           → X64 | ARM64
runner.temp           → temp directory path

steps.<id>.outputs.<name>   → output from a step in the current job
needs.<job>.outputs.<name>  → output from a dependency job
needs.<job>.result          → success | failure | cancelled | skipped
```

---

## Cron Syntax Reference

```
┌───────────── minute (0-59)
│ ┌───────────── hour (0-23)
│ │ ┌───────────── day of month (1-31)
│ │ │ ┌───────────── month (1-12 or JAN-DEC)
│ │ │ │ ┌───────────── day of week (0-6 or SUN-SAT)
│ │ │ │ │
* * * * *

Examples:
0 6 * * 1-5      → 6:00 AM UTC, Monday through Friday
0 0 * * *        → Midnight UTC every day
0 */6 * * *      → Every 6 hours
0 9 * * 1        → 9:00 AM UTC every Monday
30 14 1 * *      → 2:30 PM UTC on the 1st of every month
```

---

## Debugging Tips

1. **Add `env: ACTIONS_STEP_DEBUG: true`** as a secret to enable verbose step logging
2. **Use `echo` liberally** to print context values during debugging
3. **Check the "Raw logs"** button in the Actions UI for unformatted output
4. **Use `actions/github-script`** to print full event payload: `console.log(JSON.stringify(context.payload, null, 2))`
5. **Validate YAML offline** before pushing using `yamllint` or an online validator
6. **Check action version compatibility** — always read the action's README for the correct `with:` inputs
7. **Re-run failed jobs** — GitHub UI has a "Re-run failed jobs" button
8. **Enable debug logging** by setting `ACTIONS_RUNNER_DEBUG: true` secret to `true`
