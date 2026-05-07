# GitHub Actions Glossary

A reference for every term you will encounter in this course. Terms are listed alphabetically. Each entry includes a plain-English definition and a minimal YAML snippet where applicable.

---

## Action

A reusable unit of automation — a single task that performs one thing (checkout code, set up Python, send a Slack message). Actions are the building blocks of steps. They are hosted on the GitHub Actions Marketplace or in your own repository.

```yaml
steps:
  - uses: actions/checkout@v4      # this "uses" an action
  - uses: actions/setup-python@v5
    with:
      python-version: '3.14'
```

---

## Artifact

A file or set of files produced by a workflow job that can be uploaded, stored by GitHub, and downloaded by other jobs or users. Artifacts persist after the run ends (up to 90 days by default).

```yaml
- uses: actions/upload-artifact@v4
  with:
    name: build-output
    path: dist/

- uses: actions/download-artifact@v4
  with:
    name: build-output
```

---

## Cache

Stored data (e.g., pip packages, Maven `.m2`) that is reused across workflow runs to avoid re-downloading dependencies. A cache key controls when the cache is invalidated.

```yaml
- uses: actions/cache@v4
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements*.txt') }}
```

---

## Composite Action

A type of custom action that bundles multiple steps (using `uses:` or `run:`) into a single reusable unit. Defined in an `action.yml` file. Unlike reusable workflows, composite actions are steps — not jobs.

```yaml
# action.yml
runs:
  using: composite
  steps:
    - run: pip install -r requirements.txt
      shell: bash
    - run: pytest tests/
      shell: bash
```

---

## Concurrency

A setting that prevents multiple runs of the same workflow (or job) from running simultaneously. The `cancel-in-progress` option cancels the older run when a new one starts.

```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```

---

## Context

A collection of information about the current run, repository, event, and more. Available as `${{ <context>.<property> }}` in workflow expressions.

Common contexts:
- `github` — event info, SHA, actor, ref, repo name
- `env` — environment variables
- `secrets` — encrypted secrets
- `vars` — repository/org variables
- `inputs` — workflow_dispatch or workflow_call inputs
- `steps` — outputs of previous steps
- `needs` — outputs of dependency jobs
- `runner` — runner OS, temp dir
- `job` — current job status

---

## Deployment Environment

A named target for deployments (e.g., `staging`, `production`). Environments can have secrets, variables, and protection rules (required reviewers, wait timers, branch restrictions).

```yaml
jobs:
  deploy:
    environment: production    # links this job to the production environment
    runs-on: ubuntu-latest
```

---

## Environment Protection Rules

Rules configured on a GitHub Environment that must be satisfied before a deployment job proceeds. Examples: requiring approval from specific reviewers, enforcing that only the `main` branch can deploy to `production`.

---

## Environment Variable

A named value available to processes running in a step. Set via `env:` at the workflow, job, or step level, or dynamically via `$GITHUB_ENV`.

```yaml
env:
  APP_NAME: my-app           # workflow-level

jobs:
  build:
    env:
      APP_ENV: production    # job-level
    steps:
      - run: echo "Building $APP_NAME in $APP_ENV"
        env:
          BUILD_ID: abc123   # step-level
```

---

## Event

Something that happens on GitHub (or externally) that triggers a workflow. Also called a "trigger." Examples: `push`, `pull_request`, `schedule`, `workflow_dispatch`, `release`.

---

## Expression

A value evaluated at runtime inside `${{ }}`. Can include contexts, functions (`contains()`, `startsWith()`, `toJSON()`), and operators.

```yaml
if: ${{ github.ref == 'refs/heads/main' && github.event_name == 'push' }}
```

---

## Fan-in

A pipeline pattern where multiple parallel jobs must all complete before a downstream job runs. Achieved with a `needs` array.

```yaml
report:
  needs: [test-unit, test-integration, test-e2e]   # fan-in
```

---

## Fan-out

A pipeline pattern where one job triggers multiple parallel downstream jobs.

```yaml
test-unit:
  needs: setup        # all three fan-out from setup
test-integration:
  needs: setup
test-e2e:
  needs: setup
```

---

## GITHUB_TOKEN

An automatically created short-lived token scoped to the current repository. Available as `secrets.GITHUB_TOKEN`. Used to authenticate API calls, push code, create releases, comment on PRs, etc.

```yaml
- name: Create release
  run: gh release create v1.0.0
  env:
    GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

---

## GitHub-Hosted Runner

A virtual machine managed by GitHub that runs your jobs. Available options: `ubuntu-latest`, `ubuntu-22.04`, `windows-latest`, `macos-latest`, etc.

```yaml
runs-on: ubuntu-latest
```

---

## if Condition

A YAML key on a job or step that controls whether it runs. Evaluated as an expression; the job/step is skipped if it evaluates to `false`.

```yaml
- name: Deploy to production
  if: github.ref == 'refs/heads/main'
  run: ./deploy.sh
```

---

## Input (workflow_dispatch / workflow_call)

A parameter passed into a manually triggered workflow or a reusable workflow. Defined under `on.workflow_dispatch.inputs` or `on.workflow_call.inputs`. Accessed via `${{ inputs.name }}`.

```yaml
on:
  workflow_dispatch:
    inputs:
      environment:
        type: choice
        options: [dev, staging, production]
        required: true
```

---

## Job

A set of steps that executes sequentially on the same runner. Jobs in a workflow run in parallel by default unless linked with `needs`.

```yaml
jobs:
  build:           # job ID
    runs-on: ubuntu-latest
    steps:
      - run: echo "building"
```

---

## Job Output

A named value produced by a job and made available to downstream jobs via the `needs` context.

```yaml
jobs:
  build:
    outputs:
      version: ${{ steps.get-version.outputs.version }}
    steps:
      - id: get-version
        run: echo "version=1.2.3" >> $GITHUB_OUTPUT

  deploy:
    needs: build
    steps:
      - run: echo "Deploying ${{ needs.build.outputs.version }}"
```

---

## Matrix Strategy

A way to run the same job multiple times with different parameter combinations (OS, language version, etc.). Creates parallel jobs automatically.

```yaml
strategy:
  matrix:
    os: [ubuntu-latest, windows-latest]
    python-version: ['3.12', '3.13', '3.14']
```

---

## needs

A job-level key that declares one or more jobs that must complete successfully before this job runs.

```yaml
deploy:
  needs: [build, test]
```

---

## Organization Secret

A secret configured at the GitHub organization level and shared with selected repositories. Accessed the same way as repository secrets: `${{ secrets.SECRET_NAME }}`.

---

## Output (step)

A value set by a step and accessible in later steps of the same job via `steps.<id>.outputs.<name>`.

```yaml
- id: my-step
  run: echo "result=hello" >> $GITHUB_OUTPUT

- run: echo "${{ steps.my-step.outputs.result }}"
```

---

## Permissions

Controls what the `GITHUB_TOKEN` is allowed to do. Set at workflow or job level.

```yaml
permissions:
  contents: read
  pull-requests: write
```

---

## Pull Request Event (pull_request)

Triggers when a pull request is opened, updated, closed, etc. Activity types include: `opened`, `synchronize`, `reopened`, `closed`, `labeled`.

```yaml
on:
  pull_request:
    types: [opened, synchronize, reopened]
    branches: [main]
```

---

## Push Event

Triggers when commits are pushed to a branch or tag.

```yaml
on:
  push:
    branches: [main, develop]
    paths: ['src/**']
```

---

## Repository Variable (vars context)

A non-sensitive configuration value stored at the repository or organization level. Visible in logs. Accessed via `${{ vars.VAR_NAME }}`.

---

## Reusable Workflow

A workflow file that can be called by other workflows using `uses:`. Triggered by `on: workflow_call`. Accepts inputs, secrets, and can return outputs.

```yaml
# Caller workflow
jobs:
  call-build:
    uses: ./.github/workflows/build.yml
    with:
      python-version: '3.14'
    secrets: inherit
```

---

## Runner

The machine (virtual or physical) that executes a job. GitHub provides hosted runners; you can also register self-hosted runners.

---

## Schedule Event (schedule)

Triggers a workflow on a POSIX cron schedule.

```yaml
on:
  schedule:
    - cron: '0 6 * * 1-5'   # 6 AM UTC, Monday-Friday
```

---

## Secret

An encrypted value stored in GitHub (repository, environment, or organization level) and injected into workflows at runtime. Never visible in logs.

```yaml
- run: ./deploy.sh
  env:
    API_KEY: ${{ secrets.API_KEY }}
```

---

## Self-Hosted Runner

A machine you own and register with GitHub to run workflow jobs. Useful for specialized hardware, private network access, or cost optimization at scale.

---

## Step

A single task within a job. Steps run sequentially. Each step is either a shell command (`run:`) or an action (`uses:`).

```yaml
steps:
  - name: Checkout code
    uses: actions/checkout@v4
  - name: Run tests
    run: pytest tests/
```

---

## Trigger

See **Event**.

---

## Workflow

A YAML file stored in `.github/workflows/` that defines an automated process. A workflow has at least one trigger (`on:`), at least one job, and at least one step.

```
.github/
└── workflows/
    ├── ci.yml
    └── deploy.yml
```

---

## workflow_call

An event type that makes a workflow reusable — callable by other workflows.

---

## workflow_dispatch

An event type that allows a workflow to be triggered manually from the GitHub UI or CLI.

```yaml
on:
  workflow_dispatch:
    inputs:
      version:
        type: string
        required: true
```
