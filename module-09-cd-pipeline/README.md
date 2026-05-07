# Module 09: Continuous Deployment (CD)

## Project 7: Deploy to Staging and Production

---

## Table of Contents

1. [Learning Objectives](#learning-objectives)
2. [What is Continuous Deployment/Delivery?](#what-is-continuous-deploymentdelivery)
3. [GitHub Environments](#github-environments)
4. [Deployment Patterns](#deployment-patterns)
5. [Workflow Structure for CD](#workflow-structure-for-cd)
6. [Secrets for Deployment](#secrets-for-deployment)
7. [Rollback Strategies](#rollback-strategies)
8. [Deployment Notifications](#deployment-notifications)
9. [Project: Deploy to Staging and Production](#project-deploy-to-staging-and-production)
10. [Exercises](#exercises)

---

## Learning Objectives

By the end of this module, you will be able to:

- **Understand the difference between Continuous Delivery and Continuous Deployment** and choose the right approach for your team
- **Deploy to multiple environments** (staging and production) using separate, sequenced pipeline jobs
- **Use GitHub Environments** with protection rules to create approval gates before production deployments
- **Implement deployment approval gates** that require a human reviewer before code goes to production
- **Understand rollback strategies** and implement a manual rollback workflow
- **Track deployments in GitHub** using the Deployments API and environment status
- **Manage deployment secrets** securely using environment-scoped secrets
- **Structure CD workflows** with proper job dependencies, concurrency controls, and notification hooks

---

## What is Continuous Deployment/Delivery?

### The Terminology Problem

The software industry uses two different terms that both abbreviate to "CD," and they mean different things:

- **Continuous Delivery**: Automatically deliver software to a staging environment. Deploying to production is manual but can happen at any time at the push of a button. The pipeline ensures software is always in a deployable state.

- **Continuous Deployment**: Fully automate the entire pipeline, including deployment to production. Every change that passes all tests is automatically deployed to production without any human intervention.

The distinction matters because they represent different levels of automation, risk tolerance, and team maturity.

### Continuous Delivery

```
Developer → [Commit] → [CI Pipeline] → [Auto-deploy to Staging]
                                              │
                                              ▼
                               [Manual Approval / Button Push]
                                              │
                                              ▼
                                   [Deploy to Production]
```

**When to choose Continuous Delivery:**
- Regulated industries (finance, healthcare, government) where production changes require audit trails and human sign-off
- Complex production environments where the cost of a bad deploy is very high
- Teams early in their CD journey who aren't yet confident enough in their test suite for full automation
- Products where "deploy to production" has external dependencies (customer communication, scheduled maintenance windows)
- B2B enterprise software with SLAs that make surprise deployments problematic

**Benefits of Continuous Delivery:**
- Software is always in a deployable state (no "it's not ready to ship" situations)
- Releases are low-risk because they happen frequently with small changes
- Teams can choose when to deploy based on business needs
- Human oversight provides a final check before production

### Continuous Deployment

```
Developer → [Commit] → [CI Pipeline] → [Auto-deploy to Staging]
                                              │
                               [Automated Integration Tests]
                                              │
                                   [Auto-deploy to Production]
                                              │
                               [Automated Health Checks / Smoke Tests]
```

**When to choose Continuous Deployment:**
- Teams with very high test coverage and confidence in their test suite
- Products where fast delivery of value to users is a competitive advantage
- Consumer products (SaaS, mobile backend, web apps) where users benefit from frequent improvements
- Organizations with strong DevOps culture and mature monitoring/alerting/rollback capabilities
- Teams that have moved past fear of production deployments

**Famous examples:** Amazon deploys to production every 11.7 seconds. Etsy deploys 25+ times per day. Netflix deploys thousands of times per week.

**Benefits of Continuous Deployment:**
- Extremely short feedback loop from development to user
- Small, frequent changes are easier to diagnose and roll back
- No release bottlenecks or release coordination overhead
- Forces teams to invest in monitoring and automated testing (good for quality)

### Which Should You Choose?

A pragmatic approach for most teams starting their CD journey:

1. **Start with Continuous Delivery** — Get the pipeline working, automate deployment to staging, and require manual approval for production.
2. **Increase automation gradually** — As confidence in your tests grows, consider automating some production deployments for low-risk changes.
3. **Move to Continuous Deployment for some paths** — Many teams use hybrid approaches: auto-deploy minor fixes, require approval for major releases.

The maturity journey: CI → Continuous Delivery → Continuous Deployment.

### The Deployment Pipeline

A fully realized deployment pipeline:

```
Code  →  Build  →  Unit Tests  →  Integration Tests  →  Staging Deploy
                                                               │
                                                    Smoke Tests on Staging
                                                               │
                                              [Approval Gate] (optional)
                                                               │
                                                    Production Deploy
                                                               │
                                                   Production Health Check
                                                               │
                                               [Notify team of success/failure]
```

Each stage is a gate: if any stage fails, the pipeline stops and the team is notified. Nothing progresses to production unless every previous stage passes.

---

## GitHub Environments

### What are GitHub Environments?

GitHub Environments are a first-class concept in GitHub Actions that allow you to:

1. **Organize deployment targets**: Define named environments (e.g., `staging`, `production`, `preview`)
2. **Store environment-specific secrets**: Each environment can have its own secrets that are only available when deploying to that environment
3. **Apply protection rules**: Require specific reviewers to approve before a job can access the environment
4. **Set deployment URLs**: Each deployment can report a URL that GitHub shows on the PR and in the Deployments panel
5. **Control which branches can deploy**: Restrict which branches are allowed to deploy to an environment

### Creating Environments

Environments are created in your repository settings:

1. Navigate to your repository on GitHub
2. Click **Settings** → **Environments** (in the left sidebar)
3. Click **New environment**
4. Name it (e.g., `staging` or `production`)
5. Configure protection rules (see below)

### Environment Secrets

Environment secrets are separate from repository secrets and are scoped to a specific environment. They are only injected into a job when:
1. The job references the environment via the `environment:` keyword
2. (If configured) Required reviewers have approved the deployment

```yaml
jobs:
  deploy-production:
    environment: production   # Only now are production secrets available
    steps:
      - name: Deploy
        run: deploy.sh
        env:
          API_KEY: ${{ secrets.PRODUCTION_API_KEY }}  # Environment-scoped secret
```

If the same secret name exists at both the repository level and the environment level, the environment-level secret takes precedence when the environment is referenced.

### Environment Variables (Non-Secret)

For non-sensitive configuration that varies by environment, use environment variables:

```yaml
# In GitHub Environment settings:
# staging environment: BASE_URL = https://staging.example.com
# production environment: BASE_URL = https://example.com

jobs:
  deploy:
    environment: ${{ inputs.environment }}
    steps:
      - run: echo "Deploying to ${{ vars.BASE_URL }}"
```

Note: `vars.` accesses environment variables (non-secret), while `secrets.` accesses secrets.

### Protection Rules

Protection rules control who can trigger deployments to an environment. They are the key mechanism for implementing approval gates.

**Required Reviewers**

Specify GitHub users or teams who must approve before the deployment job can start:

```
Settings → Environments → production → Required reviewers
Add: @username or @org/team-name
```

When a workflow reaches a job that uses the `production` environment, GitHub:
1. Pauses the job
2. Sends a notification to all required reviewers
3. Waits (up to 30 days) for approval
4. If approved: proceeds with the deployment
5. If rejected: fails the workflow

The requester (person who pushed the code) cannot approve their own deployment.

**Wait Timer**

You can add a mandatory wait period before deployment proceeds, even after approval:

```
Settings → Environments → production → Wait timer → 30 minutes
```

This gives time for:
- Monitoring alerting on staging to surface any issues
- Manual smoke testing
- Business stakeholders to object if timing is bad

**Deployment Branches**

Restrict which branches are allowed to deploy to an environment:

- **All branches**: Any branch can deploy (useful for preview environments)
- **Protected branches only**: Only branches with branch protection rules can deploy
- **Selected branches**: Specific branch name patterns (e.g., `main`, `release/*`)

For production environments, typically only `main` should be deployable.

### Using Environments in Workflow Jobs

```yaml
jobs:
  deploy-production:
    name: Deploy to Production
    runs-on: ubuntu-latest
    environment:
      name: production
      url: https://example.com   # Optional: shown in GitHub Deployments UI
    steps:
      - run: echo "Deploying to production"
```

When `environment:` is set in a job:
- Protection rules are enforced
- Environment secrets are injected
- A deployment record is created in GitHub's Deployments panel
- The deployment status (in_progress, success, failure) is tracked and visible on the commit

### Viewing Deployments in GitHub

GitHub has a Deployments panel (visible at `github.com/<owner>/<repo>/deployments`) that shows:
- All deployment events
- Which commit was deployed to which environment
- The deployment status
- The deployment URL (if provided)
- A link to the deployment workflow run

For pull requests, the deployment URL is shown directly on the PR page, making it easy to click through to the PR preview deployment.

---

## Deployment Patterns

### 1. Blue-Green Deployment

Run two identical production environments simultaneously: "blue" (currently live) and "green" (new version).

```
Internet Traffic → Load Balancer → Blue (current version, serving users)
                                → Green (new version, idle)
```

Deployment process:
1. Deploy new version to "green"
2. Run smoke tests against "green"
3. Switch the load balancer to route traffic to "green"
4. Keep "blue" running for quick rollback
5. Once confident, retire "blue"

**Advantages:**
- Zero-downtime deployment
- Instant rollback (just switch load balancer back to blue)
- Green is fully warmed up before receiving traffic

**Disadvantages:**
- Requires double the infrastructure cost during deployment
- Database schema changes require careful handling (both versions must be compatible)
- More complex infrastructure setup

### 2. Rolling Deployment

Gradually replace old version instances with new version instances, one at a time.

```
Before: [v1] [v1] [v1] [v1]
During: [v2] [v1] [v1] [v1]  →  [v2] [v2] [v1] [v1]  →  [v2] [v2] [v2] [v1]
After:  [v2] [v2] [v2] [v2]
```

**Advantages:**
- No extra infrastructure cost
- Gradual rollout reduces blast radius
- Can monitor for errors as rollout progresses and stop if needed

**Disadvantages:**
- Multiple versions running simultaneously during deployment (requires backward compatibility)
- Rollback requires rolling back each instance
- Harder to test the complete new version before traffic hits it

### 3. Canary Deployment

Route a small percentage of production traffic to the new version while the majority continues using the old version.

```
Users → Load Balancer → v1 (95% of traffic)
                     → v2 (5% of traffic — the "canary")
```

Gradually increase the canary percentage as confidence grows:
5% → 10% → 25% → 50% → 100%

**Advantages:**
- Limits blast radius of a bad deploy
- Real user traffic tests the new version before full rollout
- Data-driven rollout: increase traffic as metrics confirm stability

**Disadvantages:**
- Two versions in production simultaneously (requires backward compatibility)
- Requires sophisticated traffic routing infrastructure
- Can cause inconsistent user experiences if the same user hits different versions

### 4. Feature Flags

Deploy code to production but control which users can see new features via runtime configuration flags.

```
New code is deployed to 100% of servers
Flag OFF → Old behavior (100% of users)
Flag ON  → New behavior (targeted users or percentage)
```

**Advantages:**
- Decouples deployment from feature release
- Enables A/B testing and gradual rollout
- Instant rollback: just flip the flag
- No infrastructure changes needed

**Disadvantages:**
- Technical debt: flags must be cleaned up after full rollout
- Testing complexity: must test both flag states
- Requires a feature flag management system (LaunchDarkly, Flagsmith, etc.)

---

## Workflow Structure for CD

### CI Must Pass Before CD

Never deploy code that hasn't passed CI. The CD pipeline should either:

**Option 1: Combine CI and CD in one workflow (triggered on push to main)**
```yaml
jobs:
  test:      # CI part
  build:     # CI part
  deploy-staging:    # CD part, needs test + build
  deploy-production: # CD part, needs deploy-staging
```

**Option 2: Separate workflows, CD triggered by CI success**
```yaml
# ci.yml triggers on push to any branch
# cd.yml triggers only on push to main, OR uses workflow_run to trigger after ci.yml passes
on:
  workflow_run:
    workflows: ["CI Pipeline"]
    types: [completed]
    branches: [main]
```

For most teams, Option 1 (combined workflow) is simpler. Option 2 is better if your CI and CD have very different triggers or audiences.

### The `environment:` Keyword in Jobs

```yaml
jobs:
  deploy-staging:
    environment:
      name: staging
      url: https://staging.myapp.com   # Shown in PR and Deployments UI

  deploy-production:
    environment:
      name: production
      url: https://myapp.com
```

The `url` field creates a clickable "View deployment" link in the GitHub PR interface and Deployments panel.

### Deployment Concurrency

Prevent two deployments from running simultaneously to the same environment:

```yaml
jobs:
  deploy-production:
    concurrency:
      group: deploy-production
      cancel-in-progress: false   # Don't cancel a running deployment!
```

Note: Use `cancel-in-progress: false` for deployment jobs. Cancelling an in-progress deployment could leave your environment in an inconsistent state (half-deployed). Instead, queue subsequent deployments.

### Job Dependencies for a Multi-Environment Pipeline

```
build-and-push
      │
      ▼
deploy-staging  (environment: staging, auto-approves)
      │
      ▼
integration-tests  (runs against staging)
      │
      ▼
deploy-production  (environment: production, requires approval)
      │
      ▼
notify  (always runs)
```

Each job in this chain must succeed before the next starts, creating a deployment pipeline with natural gates.

### Reporting Deployment URLs

```yaml
jobs:
  deploy-staging:
    outputs:
      deployment-url: ${{ steps.deploy.outputs.url }}
    steps:
      - name: Deploy to staging
        id: deploy
        run: |
          # Simulate deployment, capture URL
          DEPLOY_URL="https://staging-${{ github.sha }}.myapp.com"
          echo "url=${DEPLOY_URL}" >> $GITHUB_OUTPUT

  integration-tests:
    needs: deploy-staging
    steps:
      - name: Run integration tests
        run: |
          # Use the staging URL from the previous job
          curl ${{ needs.deploy-staging.outputs.deployment-url }}/health
```

---

## Secrets for Deployment

### Types of Deployment Secrets

**Cloud Provider Credentials**

For AWS, you typically need:
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_REGION`

For GCP:
- `GCP_SERVICE_ACCOUNT_KEY` (base64-encoded JSON key file)
- `GCP_PROJECT_ID`

For Azure:
- `AZURE_CREDENTIALS` (JSON service principal credentials)

**Container Registry Credentials**

For Docker Hub:
- `DOCKERHUB_USERNAME`
- `DOCKERHUB_TOKEN`

For GitHub Container Registry (GHCR): Use `GITHUB_TOKEN` (automatically provided, no setup needed):
```yaml
- name: Log in to GHCR
  uses: docker/login-action@v3
  with:
    registry: ghcr.io
    username: ${{ github.actor }}
    password: ${{ secrets.GITHUB_TOKEN }}
```

**SSH Deployment Keys**

For server-based deployments via SSH:
- `SSH_PRIVATE_KEY`: The private key for SSH authentication
- `SSH_HOST`: The server's hostname or IP
- `SSH_USER`: The username to SSH as

**API Keys and Tokens**

For third-party services:
- `HEROKU_API_KEY`
- `NETLIFY_AUTH_TOKEN`
- `VERCEL_TOKEN`
- `RENDER_API_KEY`

### Organizing Secrets by Environment

Use environment-scoped secrets for credentials that differ between environments:

```
Repository Secrets (shared across all environments):
  - DOCKER_REGISTRY_URL
  - SLACK_WEBHOOK_URL

Staging Environment Secrets:
  - DATABASE_URL = postgres://staging-db:5432/app
  - API_SECRET_KEY = staging-secret-abc123
  - AWS_ACCESS_KEY_ID = (staging AWS account key)

Production Environment Secrets:
  - DATABASE_URL = postgres://prod-db:5432/app
  - API_SECRET_KEY = production-secret-xyz789
  - AWS_ACCESS_KEY_ID = (production AWS account key)
```

This separation ensures that a compromised staging secret can't affect production.

### Using OIDC for Keyless Authentication

OpenID Connect (OIDC) is a modern, more secure alternative to long-lived credential secrets. Instead of storing static access keys, GitHub Actions obtains a short-lived token from your cloud provider.

With AWS:
```yaml
jobs:
  deploy:
    permissions:
      id-token: write   # Required for OIDC
      contents: read
    steps:
      - name: Configure AWS credentials via OIDC
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123456789012:role/GitHubActionsRole
          aws-region: us-east-1
          # No access keys needed! The OIDC token is exchanged for temporary credentials
```

Benefits of OIDC:
- No long-lived secrets to rotate or accidentally expose
- Credentials are scoped to the specific workflow run
- Credentials automatically expire
- Full audit trail via AWS CloudTrail

Setup requires configuring a trust relationship in your AWS IAM role that trusts GitHub's OIDC provider (`token.actions.githubusercontent.com`).

### Secret Hygiene Best Practices

1. **Never echo secrets in logs**: GitHub automatically redacts known secrets, but don't rely on this
2. **Use the minimum necessary permissions**: Create service accounts with only the permissions needed for deployment
3. **Rotate secrets regularly**: Set reminders to rotate long-lived credentials every 90 days
4. **Use environment-scoped secrets**: Separate staging and production credentials
5. **Audit secret access**: Review who has access to environment secrets periodically
6. **Prefer OIDC over static keys** where your cloud provider supports it

---

## Rollback Strategies

### Why Rollbacks are Critical

No matter how thorough your testing, bugs reach production. When they do, the most important thing is how quickly you can restore service to the previous known-good state. Your rollback strategy should be:
- **Fast**: Minutes, not hours
- **Tested**: Regularly verify that rollbacks work (don't discover broken rollback during an incident)
- **Documented**: Everyone on the team knows how to roll back
- **Low-ceremony**: Rolling back should not require heroic effort or multiple approvals

### Manual Rollback Workflow (GitHub Actions)

A dedicated rollback workflow (like the one in this module) allows any authorized team member to roll back to a specific commit with minimal friction:

1. Identify the last known-good commit SHA from the Deployments panel
2. Go to Actions → Run workflow → Select the rollback workflow
3. Enter the target commit SHA and the reason for rollback
4. Approve and run

The rollback workflow should:
- Require the target commit SHA (don't guess)
- Require a reason (for incident postmortem records)
- Be scoped to the same environment protection rules as forward deployments
- Create a record in GitHub Deployments (so the team can see what was deployed)
- Notify the team when the rollback completes

### Automated Rollback on Health Check Failure

For more mature pipelines, implement automatic rollback if the post-deployment health check fails:

```yaml
- name: Deploy new version
  id: deploy
  run: ./scripts/deploy.sh ${{ env.IMAGE_TAG }}

- name: Health check after deployment
  id: health-check
  run: |
    for i in {1..12}; do
      STATUS=$(curl -s -o /dev/null -w "%{http_code}" https://example.com/health)
      if [ "$STATUS" = "200" ]; then
        echo "Health check passed"
        exit 0
      fi
      echo "Attempt $i: Health check returned $STATUS, retrying in 10s..."
      sleep 10
    done
    echo "Health check failed after 2 minutes"
    exit 1

- name: Automatic rollback on health check failure
  if: failure() && steps.health-check.outcome == 'failure'
  run: |
    echo "Health check failed! Rolling back to previous version..."
    ./scripts/rollback.sh ${{ steps.deploy.outputs.previous-version }}
    echo "Rollback complete."
```

### Git Revert

For code-level rollbacks, `git revert` creates a new commit that undoes the changes of a previous commit. Unlike `git reset`, it doesn't rewrite history and is safe to push to shared branches:

```bash
# Revert a single commit
git revert abc123 --no-edit

# Revert a range of commits
git revert abc123..def456 --no-edit

# Push the revert commit, which triggers the CI/CD pipeline
git push origin main
```

The advantage of git revert over simply redeploying an old SHA is that it creates a clear paper trail in git history: "we reverted this because of [reason]".

### Deployment History and the Deployments Panel

GitHub tracks all deployments in the Deployments panel. When using environments in your workflows:
- Each deployment is recorded with the commit SHA, who deployed, and the timestamp
- You can see the full deployment history for each environment
- The current active deployment for each environment is highlighted
- Failed deployments are marked in red

Use this panel to quickly identify:
- What version is currently running in each environment
- When the last successful deployment occurred
- Which commits are in staging but not yet in production

---

## Deployment Notifications

### Why Notifications Matter

Deployments affect the entire team:
- **Developers** need to know if their code reached production
- **QA** needs to know when staging is updated so they can test
- **Support** needs to know about production changes that might cause customer inquiries
- **On-call engineers** need to know about production changes in case they need to respond to incidents

### Slack Notifications

For Slack notifications, use the `slackapi/slack-github-action`:

```yaml
- name: Notify Slack on deployment success
  if: success()
  uses: slackapi/slack-github-action@v1.27.0
  with:
    channel-id: 'C1234567890'  # Slack channel ID
    slack-message: |
      :rocket: *Production Deployment Successful*
      Deployed: `${{ github.sha }}`
      By: @${{ github.actor }}
      Environment: production
      URL: https://example.com
  env:
    SLACK_BOT_TOKEN: ${{ secrets.SLACK_BOT_TOKEN }}

- name: Notify Slack on deployment failure
  if: failure()
  uses: slackapi/slack-github-action@v1.27.0
  with:
    channel-id: 'C1234567890'
    slack-message: |
      :fire: *Production Deployment FAILED*
      Commit: `${{ github.sha }}`
      Triggered by: @${{ github.actor }}
      View logs: ${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}
  env:
    SLACK_BOT_TOKEN: ${{ secrets.SLACK_BOT_TOKEN }}
```

### GitHub Deployment Status API

When you use the `environment:` keyword in jobs, GitHub automatically creates deployment records and updates their status as the workflow progresses. You can also update deployment status manually using the GitHub API:

```yaml
- name: Update deployment status
  uses: actions/github-script@v7
  with:
    script: |
      await github.rest.repos.createDeploymentStatus({
        owner: context.repo.owner,
        repo: context.repo.repo,
        deployment_id: ${{ env.DEPLOYMENT_ID }},
        state: 'success',
        environment_url: 'https://example.com',
        description: 'Deployment completed successfully'
      })
```

States available: `error`, `failure`, `inactive`, `in_progress`, `queued`, `pending`, `success`

---

## Project: Deploy to Staging and Production

### Project Structure

```
module-09-cd-pipeline/
├── README.md                         (this file)
└── project/
    └── .github/
        └── workflows/
            ├── cd.yml                (full CD pipeline)
            └── rollback.yml          (manual rollback workflow)
```

### What This Project Demonstrates

The CD workflow (`cd.yml`) implements a complete deployment pipeline:

1. **build-and-push**: Simulates building a Docker image and pushing to a registry. Outputs the image tag (short SHA) for downstream jobs.

2. **deploy-staging**: Uses `environment: staging` to deploy to the staging environment. Simulates a deployment and health check. Reports the staging URL as an output.

3. **integration-tests**: Simulates running integration tests against the staging deployment. This is a gate before production.

4. **deploy-production**: Uses `environment: production` to deploy to production. Only runs on the `main` branch. In a real setup, this would wait for required reviewer approval.

5. **notify**: Always runs after all deployment jobs. Prints a deployment summary with outcomes.

The rollback workflow (`rollback.yml`) provides:
- A manual trigger with inputs for environment, target SHA, and reason
- Environment-gated rollback (uses the same protection rules as forward deployments)
- Clear logging of what was rolled back and why
- Post-rollback notification

### Key Concepts Demonstrated

**Environment protection**: By setting `environment: production` on the deploy-production job, GitHub enforces any protection rules configured for that environment (required reviewers, wait timer, branch restrictions).

**Deployment outputs**: The staging deployment URL is passed to the integration-test job via job outputs, demonstrating inter-job data sharing.

**Conditional jobs**: `deploy-production` only runs when `github.ref == 'refs/heads/main'`, preventing feature branch pushes from triggering production deployments.

**Always-run notification**: The `notify` job uses `if: always()` to ensure the team gets notified whether the pipeline succeeded or failed.

---

## Exercises

### Exercise 1: Set Up a Staging Environment

1. Go to your repository Settings → Environments
2. Create a new environment called `staging`
3. Add an environment variable: `DEPLOY_TARGET` = `https://staging.example.com`
4. Run the CD workflow and verify the staging job can access `vars.DEPLOY_TARGET`

**Challenge:** Add a 5-minute wait timer to the staging environment. Observe how the deployment job waits before proceeding.

---

### Exercise 2: Configure Production Approval Gates

1. Create a `production` environment in your repository settings
2. Add yourself as a required reviewer
3. Restrict deployment to the `main` branch only
4. Push code to main and watch the pipeline pause at the production job
5. Go to the Actions tab, find the waiting deployment, and approve it
6. Watch the production deployment proceed

**Learning:** This is the approval gate mechanism that Continuous Delivery relies on. The pipeline is fully automated up to this point; humans intervene only for the production gate.

---

### Exercise 3: Simulate a Failed Deployment and Rollback

1. Modify `cd.yml` to make the staging health check fail (e.g., exit 1 unconditionally)
2. Push the change and watch the pipeline fail at health check
3. Use the `rollback.yml` workflow to roll back to the previous commit
4. Verify the rollback was recorded in the GitHub Deployments panel

**Learning:** Rollback is a normal part of the deployment lifecycle, not a rare emergency. Practice it regularly.

---

### Exercise 4: Add Deployment Notifications

Extend `cd.yml` to send a notification when deployment completes (success or failure). If you have a Slack workspace, use the Slack GitHub Action. Otherwise, simulate with an `echo` command that prints what the notification would contain.

The notification should include:
- Which environment was deployed to
- The commit SHA
- Who triggered the deployment
- A link to the workflow run
- Success/failure status

---

### Exercise 5: Implement a Canary Deployment

Extend the production deployment to simulate a canary approach:

```yaml
- name: Deploy canary (5% traffic)
  run: echo "Deploying $IMAGE_TAG to 5% of production traffic"

- name: Monitor canary for 2 minutes
  run: |
    echo "Monitoring canary deployment..."
    sleep 120
    # In reality: check error rate in monitoring system
    echo "Error rate within acceptable range"

- name: Promote canary to 100%
  run: echo "Canary healthy — promoting to 100% production traffic"
```

**Challenge:** Make the canary promotion conditional on a simulated error rate check. If the error rate (simulated by a random number) is above threshold, fail the step and simulate a canary rollback.

---

### Exercise 6: Add a Deployment Dashboard

GitHub's Deployments panel (`github.com/<owner>/<repo>/deployments`) shows all deployments across environments. After running several CD pipeline executions:

1. Open the Deployments panel for your repository
2. Identify the current deployment for each environment
3. Find a past deployment and click through to the workflow run
4. Observe the deployment status timeline

**Learning:** GitHub's built-in deployment tracking gives you a clear history of what was deployed, when, and by whom — without any extra tooling.

---

### Exercise 7: Implement Deployment Concurrency Control

Modify the `cd.yml` to prevent two production deployments from running simultaneously:

```yaml
jobs:
  deploy-production:
    concurrency:
      group: deploy-production
      cancel-in-progress: false   # Queue, don't cancel
```

Test by triggering the workflow twice in rapid succession. Observe that the second run waits for the first to complete rather than cancelling it.

**Contrast:** Also try `cancel-in-progress: true` and observe how the first deployment is cancelled. Discuss when each behavior is appropriate.

---

### Exercise 8: Multi-Region Deployment

Extend the CD pipeline to deploy to multiple regions in parallel after staging passes:

```yaml
  deploy-production-us:
    needs: integration-tests
    environment: production-us-east
    # ...

  deploy-production-eu:
    needs: integration-tests
    environment: production-eu-west
    # ...

  deploy-production-ap:
    needs: integration-tests
    environment: production-ap-southeast
    # ...
```

**Learning:** GitHub Actions supports deploying to multiple environments in parallel using independent jobs. Each environment can have its own secrets, protection rules, and deployment URL.

---

## Summary

In this module, you've learned:

- **Continuous Delivery vs. Continuous Deployment**: The distinction, when to use each, and how to progress from one to the other
- **GitHub Environments**: Creating environments, scoping secrets, applying protection rules (required reviewers, wait timers, branch restrictions), and tracking deployments
- **Deployment patterns**: Blue-green, rolling, canary, and feature flags — their tradeoffs and when to use each
- **CD workflow structure**: How to chain CI and CD jobs, pass data between jobs via outputs, and implement environment-specific logic
- **Secrets management**: Environment-scoped secrets, OIDC for keyless auth, and secret hygiene best practices
- **Rollback strategies**: Manual rollback workflows, automated rollback on health check failure, and git revert
- **Deployment notifications**: Keeping the team informed via Slack and GitHub's deployment status API

In **Module 10**, we'll explore advanced GitHub Actions patterns: reusable workflows, composite actions, and self-hosted runners.

---

*Module 09 of the GitHub Actions Master Class*
*Previous: [Module 08: Continuous Integration (CI)](../module-08-ci-pipeline/README.md)*
*Next: Module 10: Advanced Patterns*
