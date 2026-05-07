# Module 06: Secrets, Variables & Environments

## Project 4: Secrets & Configuration Management

---

## Overview

Every real-world application needs configuration: API keys, database connection strings, feature
flags, environment names, version numbers. GitHub Actions provides several distinct mechanisms for
managing these, each with different security properties, scopes, and use cases. This module teaches
you to choose the right mechanism for every situation and to handle sensitive data safely.

By the end of this module you will understand how workflow-level environment variables, repository
variables, repository secrets, organization secrets, environment secrets, and the built-in
`GITHUB_TOKEN` differ from one another, and you will be able to apply them correctly in real
pipelines.

---

## Learning Objectives

After completing this module you will be able to:

- Explain the difference between environment variables (`env:`), repository variables (`vars`
  context), repository secrets (`secrets` context), and environment-specific secrets.
- Configure repository secrets and variables through both the GitHub web UI and the GitHub CLI.
- Reference configuration values correctly in workflow YAML using the appropriate expression
  context.
- Use organization-level secrets to share credentials across multiple repositories.
- Define GitHub Environments (staging, production) and attach environment-specific secrets and
  protection rules to them.
- Use `GITHUB_TOKEN` correctly for API calls, creating comments, and pushing code, while
  restricting permissions to the minimum required.
- Apply security best practices to prevent secret leakage and unauthorized access.

---

## Prerequisites

- Completion of Modules 01–05 (triggers, jobs, steps, runners, expressions).
- A GitHub repository where you have Admin access (needed to manage secrets).
- GitHub CLI (`gh`) installed locally (optional, but used in examples).

---

## Table of Contents

1. [Types of Configuration in GitHub Actions](#1-types-of-configuration-in-github-actions)
2. [Environment Variables (env:)](#2-environment-variables-env)
3. [Repository Secrets](#3-repository-secrets)
4. [Repository Variables (vars context)](#4-repository-variables-vars-context)
5. [GITHUB_TOKEN](#5-github_token)
6. [GitHub Environments](#6-github-environments)
7. [Organization Secrets](#7-organization-secrets)
8. [Security Best Practices](#8-security-best-practices)
9. [Exercises](#9-exercises)
10. [Project Walkthrough](#10-project-walkthrough)

---

## 1. Types of Configuration in GitHub Actions

GitHub Actions offers five distinct configuration layers. Understanding where each type lives and
what security guarantees it provides is the foundation of writing safe, maintainable workflows.

### 1.1 The Five Types at a Glance

| Type | Context | Encrypted? | Scope | Visible in Logs? | Primary Use Case |
|------|---------|-----------|-------|-----------------|-----------------|
| Environment Variable (`env:`) | `env.NAME` / `$NAME` | No | Workflow, job, or step | Yes (unless masked) | Runtime config baked into workflow |
| Repository Variable | `vars.NAME` | No | Whole repository (or org) | Yes | Non-sensitive config like URLs, flags |
| Repository Secret | `secrets.NAME` | Yes | Whole repository | No (masked) | API keys, passwords, tokens |
| Organization Secret | `secrets.NAME` | Yes | Multiple repositories | No (masked) | Shared credentials across repos |
| Environment Secret | `secrets.NAME` | Yes | Single environment (staging, prod) | No (masked) | Env-specific credentials |

### 1.2 Choosing the Right Type

Use this decision tree when deciding where to store a value:

```
Is the value sensitive (password, token, private key)?
├── YES → Is it shared across many repositories?
│         ├── YES → Organization Secret
│         └── NO  → Is it specific to a deployment environment?
│                   ├── YES → Environment Secret
│                   └── NO  → Repository Secret
└── NO  → Does it change between environments (staging vs prod)?
          ├── YES → Repository Variable (different values per environment variable)
          └── NO  → env: block in the workflow YAML, or Repository Variable
```

### 1.3 Why the Distinction Matters

- **Secrets are encrypted at rest** and are never returned through the GitHub API after they are
  set. Even repository administrators cannot read a secret value once saved.
- **Variables are not encrypted**. Anyone with read access to the repository can see variable values
  through the API or the GitHub UI.
- **`env:` values are part of your workflow YAML**, which is committed to your repository. They
  should never contain sensitive data.
- **Environment secrets require the job to target a named environment**, which can itself require
  manual approval before the job runs. This is the safest mechanism for production credentials.

---

## 2. Environment Variables (env:)

Environment variables are the most basic configuration mechanism. They are set directly in your
workflow YAML file, are not encrypted, and are available to steps as standard OS environment
variables.

### 2.1 Setting Environment Variables

You can set environment variables at three scopes: the whole workflow, a specific job, or a single
step. A narrower scope always overrides a wider one.

**Workflow-level** (available in all jobs and steps):

```yaml
env:
  APP_NAME: my-application
  PYTHON_VERSION: "3.14"
  ENABLE_FEATURE_X: "true"

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - run: echo "Building $APP_NAME with Python $PYTHON_VERSION"
```

**Job-level** (overrides workflow-level for this job only):

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    env:
      APP_ENV: production    # only available in this job
    steps:
      - run: echo "Running in $APP_ENV environment"
```

**Step-level** (overrides job-level and workflow-level for this step only):

```yaml
steps:
  - name: Run with overridden version
    env:
      PYTHON_VERSION: "3.12"     # overrides the workflow-level PYTHON_VERSION for this step only
    run: echo "Using Python $PYTHON_VERSION"
```

### 2.2 Accessing Environment Variables

There are two ways to reference environment variables: as OS environment variables in shell scripts,
and as GitHub Actions expressions in YAML.

**In bash scripts** — use the standard `$VARIABLE_NAME` syntax:

```bash
echo "App name: $APP_NAME"
echo "Version: $PYTHON_VERSION"
```

**In PowerShell** — use `$env:VARIABLE_NAME`:

```powershell
Write-Output "App name: $env:APP_NAME"
```

**In YAML expressions** — use `${{ env.VARIABLE_NAME }}`. This is evaluated *before* the runner
executes the step, so you can use it in `if:` conditions, `with:` inputs, and other YAML fields:

```yaml
- name: Conditional step
  if: ${{ env.ENABLE_FEATURE_X == 'true' }}
  run: echo "Feature X is enabled"

- name: Use env in with
  uses: actions/setup-python@v5
  with:
    python-version: ${{ env.PYTHON_VERSION }}
```

### 2.3 Precedence Rules

When the same variable name is defined at multiple scopes, the most specific scope wins:

```
Step env: (highest priority)
  └── Job env:
        └── Workflow env: (lowest priority)
```

Example demonstrating precedence:

```yaml
env:
  MESSAGE: "from workflow"

jobs:
  precedence-demo:
    runs-on: ubuntu-latest
    env:
      MESSAGE: "from job"
    steps:
      - name: Prints "from job" (job overrides workflow)
        run: echo "$MESSAGE"

      - name: Prints "from step" (step overrides job)
        env:
          MESSAGE: "from step"
        run: echo "$MESSAGE"

      - name: Prints "from job" again (previous step override is gone)
        run: echo "$MESSAGE"
```

### 2.4 Built-in GitHub Environment Variables

GitHub automatically provides many environment variables in every workflow run. These are set by the
runner and cannot be overridden.

| Variable | Description | Example Value |
|----------|-------------|---------------|
| `GITHUB_TOKEN` | Auto-generated auth token for this run | `ghs_xxxxxxxxxxxx` |
| `GITHUB_SHA` | Full commit SHA that triggered the run | `a1b2c3d4e5...` |
| `GITHUB_REF` | Branch or tag ref that triggered the run | `refs/heads/main` |
| `GITHUB_REF_NAME` | Short branch or tag name | `main` |
| `GITHUB_ACTOR` | Username that triggered the workflow | `octocat` |
| `GITHUB_REPOSITORY` | Owner and repo name | `owner/repo` |
| `GITHUB_WORKSPACE` | Path to the checked-out repository | `/home/runner/work/repo/repo` |
| `GITHUB_RUN_ID` | Unique ID for this workflow run | `12345678` |
| `GITHUB_RUN_NUMBER` | Sequential run number for this workflow | `42` |
| `GITHUB_WORKFLOW` | Name of the workflow | `CI` |
| `GITHUB_JOB` | ID of the current job | `build` |
| `GITHUB_EVENT_NAME` | Event that triggered the workflow | `push` |
| `GITHUB_SERVER_URL` | GitHub server URL | `https://github.com` |
| `RUNNER_OS` | OS of the runner | `Linux` |
| `RUNNER_ARCH` | CPU architecture | `X64` |

Access them in scripts:

```bash
echo "Run triggered by: $GITHUB_ACTOR"
echo "Commit: $GITHUB_SHA"
echo "Branch: $GITHUB_REF_NAME"
echo "Build number: $GITHUB_RUN_NUMBER"
```

### 2.5 Setting Dynamic Environment Variables

Sometimes you need to compute a value in one step and use it in a later step. The `GITHUB_ENV` file
mechanism enables this. Write `NAME=VALUE` to the file pointed to by `$GITHUB_ENV`, and that
variable becomes available to all subsequent steps in the same job.

```yaml
steps:
  - name: Compute build version
    run: |
      # Compute a version string from the commit SHA and run number
      BUILD_VERSION="${GITHUB_RUN_NUMBER}-${GITHUB_SHA:0:7}"
      echo "BUILD_VERSION=$BUILD_VERSION" >> "$GITHUB_ENV"

  - name: Use the computed version
    run: |
      # BUILD_VERSION is now available as a normal env var
      echo "Building version: $BUILD_VERSION"
      echo "Tagging Docker image as: myapp:$BUILD_VERSION"
```

For multi-line values, use the heredoc delimiter syntax:

```yaml
- name: Set multi-line env var
  run: |
    echo "RELEASE_NOTES<<EOF" >> "$GITHUB_ENV"
    echo "Version 1.2.3" >> "$GITHUB_ENV"
    echo "- Fixed bug X" >> "$GITHUB_ENV"
    echo "- Added feature Y" >> "$GITHUB_ENV"
    echo "EOF" >> "$GITHUB_ENV"
```

> **Important**: Do not use `GITHUB_ENV` to store sensitive values. The file contents may be
> visible in runner logs. Use secrets for sensitive data.

---

## 3. Repository Secrets

Repository secrets store encrypted values that are available to workflow runs. Once saved, the
value cannot be retrieved through any GitHub API — only the workflow runner can decrypt and use it.

### 3.1 Adding Secrets via the GitHub UI

1. Navigate to your repository on GitHub.
2. Click **Settings** (you must have Admin access).
3. In the left sidebar, expand **Secrets and variables**, then click **Actions**.
4. Click **New repository secret**.
5. Enter a **Name** (e.g., `API_KEY`) and the secret **Value**.
6. Click **Add secret**.

The secret is now encrypted and stored. You cannot view the value again — only update or delete it.

### 3.2 Adding Secrets via the GitHub CLI

The `gh` CLI is useful for scripting secret management, especially when rotating many secrets:

```bash
# Set a secret interactively (prompts for value)
gh secret set API_KEY

# Set a secret from a variable
gh secret set API_KEY --body "$MY_API_KEY_VALUE"

# Set a secret from a file
gh secret set TLS_PRIVATE_KEY < private-key.pem

# Set a secret for a specific repository
gh secret set API_KEY --repo owner/repo-name

# List all secrets (shows names only, not values)
gh secret list

# Delete a secret
gh secret delete OLD_API_KEY
```

### 3.3 Using Secrets in Workflows

Reference secrets using the `secrets` context:

```yaml
steps:
  - name: Deploy to production
    env:
      # Pass secret as an environment variable to the script
      API_KEY: ${{ secrets.API_KEY }}
      DATABASE_URL: ${{ secrets.DATABASE_URL }}
    run: |
      ./deploy.sh --api-key "$API_KEY" --db "$DATABASE_URL"
```

Pass secrets to an action using `with:`:

```yaml
- name: Send Slack notification
  uses: slackapi/slack-github-action@v2
  with:
    webhook: ${{ secrets.SLACK_WEBHOOK_URL }}
    webhook-type: incoming-webhook
    payload: |
      {"text": "Deployment succeeded!"}
```

### 3.4 Secrets are Masked in Logs

When a secret value appears in the log output, GitHub automatically replaces it with `***`. This
protects against accidental exposure.

```yaml
- name: Attempting to print a secret (will be masked)
  env:
    MY_SECRET: ${{ secrets.API_KEY }}
  run: |
    echo "Secret value: $MY_SECRET"
    # Output will be: Secret value: ***
```

> **Warning**: The masking only applies to the *exact* secret value. If you encode or transform
> a secret (e.g., base64 encode it), the transformed value will NOT be masked. Never log secrets,
> even indirectly.

### 3.5 Checking if a Secret is Set

You cannot read a secret's value to check if it exists, but you can check if it is non-empty using
an expression:

```yaml
- name: Deploy (only if API key is configured)
  if: ${{ secrets.API_KEY != '' }}
  run: ./deploy.sh
```

### 3.6 Secrets in Pull Requests from Forks

By default, **secrets are not passed to workflows triggered by pull requests from forks**. This is
a critical security protection. A malicious contributor could create a PR that exfiltrates your
secrets if this were allowed.

For workflows triggered by `pull_request` from a fork:
- `secrets` context is empty.
- `GITHUB_TOKEN` has read-only permissions.

If you need to run steps requiring secrets for fork PRs, use `pull_request_target` (with extreme
caution — never check out untrusted code in that context).

### 3.7 Secret Naming Conventions

- Use `SCREAMING_SNAKE_CASE` for all secret names.
- Group related secrets with a common prefix: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`.
- Avoid generic names like `TOKEN` — be specific: `DOCKERHUB_TOKEN`, `PYPI_PUBLISH_TOKEN`.
- Do not prefix with `GITHUB_` — that prefix is reserved for GitHub-provided variables.

---

## 4. Repository Variables (vars context)

Repository variables are non-encrypted configuration values. They are useful for values that you
want to be visible and editable by collaborators without giving them access to secrets.

### 4.1 How Variables Differ from Secrets

| Aspect | Secret | Variable |
|--------|--------|----------|
| Encryption | Yes, at rest | No |
| Viewable after setting | No | Yes |
| Use case | Passwords, tokens, keys | URLs, flags, version numbers |
| Context | `secrets.NAME` | `vars.NAME` |

### 4.2 Setting Variables via the GitHub UI

1. Go to **Settings** > **Secrets and variables** > **Actions**.
2. Click the **Variables** tab.
3. Click **New repository variable**.
4. Enter a **Name** and **Value**, then click **Add variable**.

### 4.3 Using Variables in Workflows

```yaml
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to API endpoint
        run: |
          curl -X POST "${{ vars.API_BASE_URL }}/deploy" \
            -H "Authorization: Bearer ${{ secrets.API_TOKEN }}" \
            -d '{"version": "${{ vars.APP_VERSION }}"}'
```

Variables are accessed with `${{ vars.VARIABLE_NAME }}`. Unlike secrets, they can safely appear in
log output.

### 4.4 Use Cases for Variables

- **API endpoints**: `vars.STAGING_API_URL`, `vars.PRODUCTION_API_URL`
- **Feature flags**: `vars.ENABLE_NEW_CHECKOUT_FLOW` = `"true"`
- **Docker registry**: `vars.DOCKER_REGISTRY` = `registry.example.com`
- **Notification channels**: `vars.SLACK_CHANNEL_ID` = `C01234567`
- **Deployment region**: `vars.AWS_REGION` = `us-east-1`
- **App version**: `vars.CURRENT_STABLE_VERSION` = `"2.4.1"`

---

## 5. GITHUB_TOKEN

`GITHUB_TOKEN` is a special secret that GitHub automatically creates for every workflow run. It
allows your workflow to authenticate to the GitHub API without requiring you to store a personal
access token.

### 5.1 How GITHUB_TOKEN Works

At the start of each workflow run, GitHub:

1. Generates a short-lived token scoped to the repository.
2. Makes it available as `${{ secrets.GITHUB_TOKEN }}` (and as the `GITHUB_TOKEN` environment
   variable).
3. Automatically expires the token when the workflow run completes.

The token can authenticate to:
- The GitHub REST API (`api.github.com`)
- The GitHub GraphQL API
- The `gh` CLI (via the `GH_TOKEN` environment variable)
- `git` operations over HTTPS to the current repository

### 5.2 Default Permissions

By default, `GITHUB_TOKEN` has the following permissions (these may vary based on your
organization's settings):

| Permission | Default |
|-----------|---------|
| `actions` | read |
| `checks` | write |
| `contents` | write |
| `deployments` | write |
| `id-token` | none |
| `issues` | write |
| `metadata` | read (always granted) |
| `packages` | write |
| `pull-requests` | write |
| `repository-projects` | write |
| `security-events` | write |
| `statuses` | write |

> **Note**: GitHub and many organizations have moved toward restricting default permissions to
> `read-all`. Always explicitly declare the permissions your workflow needs.

### 5.3 Restricting Permissions with the `permissions` Block

The principle of least privilege requires granting only the permissions a workflow needs. Use the
`permissions` block to explicitly declare them:

```yaml
# Workflow-level: applies to all jobs
permissions:
  contents: read
  pull-requests: write

jobs:
  review:
    runs-on: ubuntu-latest
    # Job-level override (more restrictive or expansive)
    permissions:
      pull-requests: write
    steps:
      - run: gh pr comment ${{ github.event.pull_request.number }} --body "Tests passed"
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

Available permission values: `read`, `write`, `none`.

To grant no permissions at all to a job (e.g., a pure notification job):

```yaml
jobs:
  notify:
    permissions: {}
    runs-on: ubuntu-latest
```

### 5.4 Using GITHUB_TOKEN for API Calls

```yaml
- name: List open pull requests
  run: |
    curl -s \
      -H "Authorization: Bearer ${{ secrets.GITHUB_TOKEN }}" \
      -H "Accept: application/vnd.github+json" \
      "https://api.github.com/repos/${{ github.repository }}/pulls?state=open" \
      | jq '.[].title'
```

Using the `gh` CLI (simpler):

```yaml
- name: Add label to PR
  env:
    GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  run: |
    gh pr edit ${{ github.event.pull_request.number }} --add-label "reviewed"
```

### 5.5 GITHUB_TOKEN vs Personal Access Tokens

| Aspect | GITHUB_TOKEN | Personal Access Token (PAT) |
|--------|-------------|----------------------------|
| Lifetime | Duration of workflow run | Until expiration date (max 1 year) |
| Scope | Current repository only | Configurable (user or org) |
| Creation | Automatic | Manual |
| Rotation | Automatic | Manual |
| Cross-repo actions | No | Yes (if granted) |
| Who owns it | App (GitHub Actions) | A specific user |

Use `GITHUB_TOKEN` whenever possible. Only use a PAT when you need to:
- Access a different repository
- Perform actions across the organization
- Create workflows in another repo (pushing `.github/workflows/` files)

### 5.6 GITHUB_TOKEN Limitations

- Cannot trigger another workflow run by default. If you push a commit using `GITHUB_TOKEN`, the
  push event will not trigger further workflows (prevents infinite loops). Use a PAT or GitHub App
  token if you need to chain workflows.
- Cannot create or approve pull requests when branch protection rules require reviews from code
  owners (the bot cannot review its own PRs).

---

## 6. GitHub Environments

GitHub Environments are named deployment targets (e.g., `staging`, `production`) that you can
associate with specific secrets, protection rules, and approval requirements.

### 6.1 Creating an Environment

1. Go to **Settings** > **Environments**.
2. Click **New environment**.
3. Enter a name (e.g., `production`).
4. Configure protection rules:
   - **Required reviewers**: list of people who must approve before the environment is used.
   - **Wait timer**: minimum number of minutes to wait before proceeding.
   - **Deployment branches and tags**: restrict which branches can deploy to this environment.

### 6.2 Environment-Specific Secrets

Secrets attached to an environment are only available when a job references that environment with
the `environment:` key. This means:

- Your staging job gets the staging database URL.
- Your production job gets the production database URL.
- Even if someone gains access to the staging secrets, they cannot access production.

Set environment secrets the same way as repository secrets, but from the **Environments** settings
page rather than the top-level **Secrets and variables** page.

### 6.3 Using Environments in Jobs

```yaml
jobs:
  deploy-staging:
    runs-on: ubuntu-latest
    environment: staging            # This job targets the "staging" environment
    steps:
      - name: Deploy to staging
        env:
          DB_URL: ${{ secrets.DATABASE_URL }}   # staging-specific secret
          API_KEY: ${{ secrets.API_KEY }}        # staging-specific secret
        run: ./scripts/deploy.sh staging

  deploy-production:
    runs-on: ubuntu-latest
    needs: deploy-staging
    environment:
      name: production
      url: https://myapp.example.com  # shown in the deployment UI
    steps:
      - name: Deploy to production
        env:
          DB_URL: ${{ secrets.DATABASE_URL }}   # production-specific secret
          API_KEY: ${{ secrets.API_KEY }}        # production-specific secret
        run: ./scripts/deploy.sh production
```

When a job references an environment with **required reviewers**, the workflow pauses and sends a
notification to the reviewers. The job only runs after someone approves.

### 6.4 Environment Protection Rules in Practice

```
Workflow triggers → staging job runs (no approval needed)
                 → staging deployment completes
                 → production job queued (waiting for approval)
                 → Reviewer receives notification
                 → Reviewer approves
                 → production job runs
```

This ensures human oversight for every production deployment.

### 6.5 Environment Variables vs Environment Secrets

Environments also support variables (non-encrypted), accessible via `vars.VAR_NAME` when the job
targets that environment. This lets you have:

- `vars.API_BASE_URL` = `https://staging-api.example.com` (staging environment)
- `vars.API_BASE_URL` = `https://api.example.com` (production environment)

Same variable name, different values per environment — no if/else needed in your workflow YAML.

---

## 7. Organization Secrets

If you maintain multiple repositories that all need the same credentials (e.g., a shared Docker
Hub account, a shared Slack webhook), organization secrets let you define them once and share them
across repositories.

### 7.1 Creating Organization Secrets

1. Go to your GitHub Organization's **Settings**.
2. Click **Secrets and variables** > **Actions**.
3. Click **New organization secret**.
4. Set the name, value, and **repository access** policy:
   - **All repositories**: every repo in the org can use this secret.
   - **Private repositories**: only private repos.
   - **Selected repositories**: explicitly list which repos can access it.

### 7.2 Using Organization Secrets

Organization secrets are accessed exactly like repository secrets — using `${{ secrets.SECRET_NAME
}}`. There is no difference in the workflow YAML:

```yaml
- name: Push Docker image
  env:
    DOCKER_TOKEN: ${{ secrets.DOCKERHUB_TOKEN }}   # org-level secret
    DOCKER_USERNAME: ${{ secrets.DOCKERHUB_USERNAME }}
  run: |
    echo "$DOCKER_TOKEN" | docker login --username "$DOCKER_USERNAME" --password-stdin
    docker push myorg/myapp:latest
```

### 7.3 Secret Precedence

If a repository secret and an organization secret share the same name, the **repository secret
takes precedence**. This lets individual repos override shared credentials when needed.

---

## 8. Security Best Practices

### 8.1 Never Hardcode Secrets

Every secret must live in GitHub's secrets store, not in workflow YAML files, scripts, or
application code. Hardcoded secrets in Git history are effectively public, even if the file is
later deleted.

```yaml
# BAD: hardcoded API key
- run: curl -H "Authorization: Bearer sk-live-abc123xyz" https://api.example.com/

# GOOD: use a secret
- run: curl -H "Authorization: Bearer ${{ secrets.API_KEY }}" https://api.example.com/
```

### 8.2 Rotate Secrets Regularly

- Set calendar reminders to rotate API keys and passwords every 90 days.
- Immediately rotate any secret that may have been exposed.
- When a team member leaves, rotate all secrets they had access to.
- Use the GitHub CLI to update secrets as part of a rotation script.

### 8.3 Use the Minimum Permissions Required

- Always specify a `permissions:` block in your workflow.
- Start with `permissions: {}` (no permissions) and add only what is needed.
- Do not give `contents: write` if you only need to read code.
- Review permissions after adding new steps or jobs.

### 8.4 Audit Secret Access

GitHub's audit log records when secrets are accessed. Regularly review:
- Which workflows access which secrets.
- Whether any secrets are unused and can be deleted.
- Whether access patterns match expectations.

### 8.5 OpenID Connect (OIDC) for Cloud Authentication

Instead of storing long-lived cloud credentials as secrets, use OIDC to get short-lived tokens from
cloud providers. This is the most secure approach for AWS, Azure, and GCP deployments.

```yaml
permissions:
  id-token: write    # required for OIDC
  contents: read

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Configure AWS credentials via OIDC
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123456789:role/GitHubActionsRole
          aws-region: us-east-1
          # No AWS_ACCESS_KEY_ID or AWS_SECRET_ACCESS_KEY needed!
```

With OIDC, there are no long-lived credentials to rotate, steal, or accidentally expose.

---

## 9. Exercises

### Exercise 1: Environment Variable Precedence

**Goal**: Understand how env: scoping works.

Create a workflow with:
- Workflow-level `env:` that sets `GREETING=Hello` and `TARGET=World`
- A job with job-level `env:` that overrides `TARGET=GitHub`
- A step with step-level `env:` that overrides `GREETING=Goodbye`
- Multiple steps that print `"$GREETING, $TARGET!"` to demonstrate what each scope sees

**Expected output**:
- Step 1 (no override): `Hello, GitHub!`
- Step 2 (with step override): `Goodbye, GitHub!`
- Step 3 (after step 2): `Hello, GitHub!`

---

### Exercise 2: Dynamic Environment Variables

**Goal**: Practice using `GITHUB_ENV` to pass data between steps.

Create a workflow that:
1. In step 1, computes `DEPLOY_TAG` as `deploy-${{ github.run_number }}-${{ github.sha }}` (use
   the first 8 characters of the SHA).
2. Writes `DEPLOY_TAG` to `$GITHUB_ENV`.
3. In step 2, uses `$DEPLOY_TAG` to print a message: `"Deploying tag: $DEPLOY_TAG"`.
4. In step 3, uses the env expression `${{ env.DEPLOY_TAG }}` in the step name field itself (not
   just the run command) — demonstrating that `GITHUB_ENV` values are NOT available in step names
   (which are evaluated before the step runs). Use a static name and print the tag in `run:`.

---

### Exercise 3: GITHUB_TOKEN API Call

**Goal**: Use GITHUB_TOKEN to interact with the GitHub API.

Create a workflow triggered on `push` to `main` that:
1. Lists all labels in the repository using the GitHub REST API with `GITHUB_TOKEN`.
2. Creates a commit status (check) on the pushed commit using the API, marking it as `success`
   with the description `"Workflow completed"`.
3. Uses `permissions:` to grant only `contents: read` and `statuses: write`.

**Hint**: The endpoint for commit statuses is:
`POST /repos/{owner}/{repo}/statuses/{sha}`

---

### Exercise Solutions

<details>
<summary>Exercise 1 Solution</summary>

```yaml
name: Env Precedence Demo

on: [push]

env:
  GREETING: Hello
  TARGET: World

jobs:
  demonstrate-precedence:
    runs-on: ubuntu-latest
    env:
      TARGET: GitHub          # overrides workflow-level TARGET
    steps:
      - name: Step 1 - No override
        run: echo "$GREETING, $TARGET!"
        # Prints: Hello, GitHub!

      - name: Step 2 - Step-level override
        env:
          GREETING: Goodbye   # overrides job-level and workflow-level
        run: echo "$GREETING, $TARGET!"
        # Prints: Goodbye, GitHub!

      - name: Step 3 - After override
        run: echo "$GREETING, $TARGET!"
        # Prints: Hello, GitHub! (step-level override is gone)
```

</details>

<details>
<summary>Exercise 2 Solution</summary>

```yaml
name: Dynamic Env Demo

on: [push]

jobs:
  dynamic-env:
    runs-on: ubuntu-latest
    steps:
      - name: Compute deploy tag
        run: |
          SHORT_SHA="${{ github.sha }}"
          SHORT_SHA="${SHORT_SHA:0:8}"
          DEPLOY_TAG="deploy-${{ github.run_number }}-${SHORT_SHA}"
          echo "DEPLOY_TAG=$DEPLOY_TAG" >> "$GITHUB_ENV"
          echo "Computed tag: $DEPLOY_TAG"

      - name: Use deploy tag
        run: echo "Deploying tag: $DEPLOY_TAG"

      - name: Demonstrate GITHUB_ENV availability
        run: |
          echo "DEPLOY_TAG is: ${{ env.DEPLOY_TAG }}"
          echo "Note: This works because GITHUB_ENV sets vars for subsequent steps"
```

</details>

<details>
<summary>Exercise 3 Solution</summary>

```yaml
name: GITHUB_TOKEN API Demo

on:
  push:
    branches: [main]

permissions:
  contents: read
  statuses: write

jobs:
  api-demo:
    runs-on: ubuntu-latest
    steps:
      - name: List repository labels
        run: |
          curl -s \
            -H "Authorization: Bearer ${{ secrets.GITHUB_TOKEN }}" \
            -H "Accept: application/vnd.github+json" \
            "https://api.github.com/repos/${{ github.repository }}/labels" \
            | jq '.[].name'

      - name: Create commit status
        run: |
          curl -s -X POST \
            -H "Authorization: Bearer ${{ secrets.GITHUB_TOKEN }}" \
            -H "Accept: application/vnd.github+json" \
            "https://api.github.com/repos/${{ github.repository }}/statuses/${{ github.sha }}" \
            -d '{
              "state": "success",
              "description": "Workflow completed",
              "context": "my-workflow/status"
            }'
```

</details>

---

## 10. Project Walkthrough

This module includes three workflow files in `project/.github/workflows/`:

### `env-variables-demo.yml`

Demonstrates all aspects of environment variables:
- Workflow, job, and step-level `env:` with precedence demonstration
- Built-in `GITHUB_*` variables
- Dynamic variables via `$GITHUB_ENV`

Run it: Push any commit to the branch and watch the Actions log.

### `secrets-demo.yml`

Demonstrates secure secret usage patterns:
- Referencing secrets in `env:` and `with:`
- Masking behavior
- Conditional steps based on secret availability

> **Setup required**: This workflow references `secrets.API_KEY` and `secrets.DATABASE_URL`. Add
> these to your repository secrets (any placeholder value works for demonstration purposes).

### `github-token-demo.yml`

Demonstrates `GITHUB_TOKEN`:
- Restricted `permissions:` block
- REST API calls using the token
- `gh` CLI usage with `GH_TOKEN`

---

## Summary

| Mechanism | Where Defined | Encrypted | Context | Best For |
|-----------|--------------|-----------|---------|---------|
| `env:` in YAML | Workflow file | No | `env.NAME` / `$NAME` | Runtime non-sensitive config |
| Repository Variable | GitHub Settings | No | `vars.NAME` | URLs, feature flags, versions |
| Repository Secret | GitHub Settings | Yes | `secrets.NAME` | API keys, passwords |
| Environment Secret | GitHub Environments | Yes | `secrets.NAME` (with `environment:`) | Env-specific credentials |
| Organization Secret | Org Settings | Yes | `secrets.NAME` | Shared credentials |
| `GITHUB_TOKEN` | Auto-generated | Yes | `secrets.GITHUB_TOKEN` | GitHub API, git auth |

The golden rules:
1. Never put sensitive values in workflow YAML files.
2. Always use the `permissions:` block to restrict `GITHUB_TOKEN`.
3. Use environment secrets + protection rules for production deployments.
4. Prefer OIDC over long-lived credentials for cloud providers.

---

## References

- 🔐 **Encrypted Secrets in GitHub Actions** — [docs.github.com/en/actions/security-guides/encrypted-secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- 🌍 **Variables in GitHub Actions** — [docs.github.com/en/actions/learn-github-actions/variables](https://docs.github.com/en/actions/learn-github-actions/variables)
- 🤖 **Automatic Token Authentication (GITHUB_TOKEN)** — [docs.github.com/en/actions/security-guides/automatic-token-authentication](https://docs.github.com/en/actions/security-guides/automatic-token-authentication)
- 🏗️ **Using Environments for Deployment** — [docs.github.com/en/actions/deployment/targeting-different-environments/using-environments-for-deployment](https://docs.github.com/en/actions/deployment/targeting-different-environments/using-environments-for-deployment)
- 🔑 **About Security Hardening with OpenID Connect (OIDC)** — [docs.github.com/en/actions/deployment/security-hardening-your-deployments/about-security-hardening-with-openid-connect](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/about-security-hardening-with-openid-connect)
- 🖥️ **GitHub CLI: `gh secret`** — [cli.github.com/manual/gh_secret](https://cli.github.com/manual/gh_secret)
- 🌐 **GitHub REST API — Repository Secrets** — [docs.github.com/en/rest/actions/secrets](https://docs.github.com/en/rest/actions/secrets)
- 🔒 **Security Hardening for GitHub Actions** — [docs.github.com/en/actions/security-guides/security-hardening-for-github-actions](https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions)

---

*Next: [Module 07 — Dependent Jobs & Artifacts](../module-07-dependent-jobs/README.md)*
