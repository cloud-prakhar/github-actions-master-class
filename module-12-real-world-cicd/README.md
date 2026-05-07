# Module 12: Real-World Full-Stack CI/CD Pipeline

**Difficulty:** Advanced | **Time:** 3-4 hours | **Prev:** [Module 11](../module-11-reusable-workflows/README.md)

## Project 10: Production-Grade Pipeline for Python 3.14

---

## Learning Objectives

By the end of this module you will:
- Design and build a complete, production-grade CI/CD pipeline from scratch
- Understand the difference between "it works" CI and truly production-ready CI
- Integrate security scanning into the pipeline
- Implement multi-environment deployments with approval gates
- Use job summaries to communicate pipeline status clearly
- Optimize pipeline speed with smart caching and parallelism
- Handle all the edge cases: PR-only checks, main-only deploys, manual triggers

---

## 1. What Makes a Pipeline "Production-Grade"?

A basic CI pipeline runs tests. A production-grade pipeline:

| Basic CI | Production-Grade CI/CD |
|---|---|
| Runs tests | Runs tests + security + code quality |
| One job | Parallel jobs (faster feedback) |
| No caching | Pip cache keyed on requirements hash |
| Deploys everywhere | Deploys based on branch + environment gates |
| No notifications | Job summaries + team notifications |
| No rollback | Rollback workflow ready |
| Trusted forks | Fork PRs handled carefully |
| One environment | Staging → Production with approvals |

---

## 2. Pipeline Architecture

```
TRIGGER
  │
  ├── push to main/develop → Full CI + Deploy to staging → (approval) → Deploy to production
  ├── pull_request to main → CI only (no deploy)
  └── workflow_dispatch    → CI + optional deploy
       │
       ▼
  code-quality ─┬──→ test ──→ build ──→ deploy-staging ──→ deploy-production
  security-scan ─┘                                      ↘
                                                         pipeline-summary (always)
```

**Parallel first gates** (code-quality + security-scan) run simultaneously. Both must pass before tests run. This catches cheap errors fast.

**Sequential thereafter** ensures you never deploy broken code: tests → build → staging → production.

---

## 3. Project Structure

```
module-12-real-world-cicd/
└── project/
    ├── src/
    │   └── app.py               ← Flask REST API (Python 3.14)
    ├── tests/
    │   └── test_app.py          ← pytest test suite
    ├── requirements.txt         ← Runtime deps (flask, gunicorn)
    ├── Dockerfile               ← Multi-stage production Docker build
    └── .github/
        └── workflows/
            └── full-cicd.yml    ← The complete pipeline
```

---

## 4. Application Overview

The demo application is a simple Flask REST API with:
- `GET /health` — health check endpoint
- `GET /api/users` — list all users
- `GET /api/users/<id>` — get a specific user
- `POST /api/users` — create a new user

**Run locally:**
```bash
cd module-12-real-world-cicd/project
pip install -r requirements.txt
PYTHONPATH=src python src/server.py
```

**Run tests locally:**
```bash
pip install flask pytest pytest-flask pytest-cov
PYTHONPATH=src pytest tests/ -v --cov=src
```

---

## 5. Dockerfile — Multi-Stage Build

The Dockerfile uses a two-stage build:

```
Stage 1: builder (python:3.14-slim)
  └── pip install dependencies into /install

Stage 2: production (python:3.14-slim)
  ├── Copy /install from builder
  ├── Copy src/ from host
  ├── Create non-root user
  └── CMD: gunicorn (production WSGI server)
```

**Why gunicorn instead of Flask's dev server?**
- Flask's dev server is single-threaded — handles one request at a time
- gunicorn spawns multiple worker processes (4 by default in our Dockerfile)
- gunicorn handles request queuing, timeouts, and graceful restarts

**Build and run locally:**
```bash
cd module-12-real-world-cicd/project
docker build -t demo-app:local .
docker run -p 3000:3000 demo-app:local
curl http://localhost:3000/health
```

---

## 6. Pipeline Stages Explained

### Stage 1 & 2: code-quality + security-scan (parallel)

**code-quality:** Flake8 style checking. Catches: unused imports, undefined names, style violations, common bugs. Fast (~20 seconds).

**security-scan:** pip-audit + safety. Checks every dependency against the CVE database. Catches known vulnerabilities before they reach staging. Fast (~30 seconds).

**Why parallel?** Neither depends on the other. Running them simultaneously cuts ~20 seconds from the pipeline.

### Stage 3: test

Runs after both gates pass. Executes the full pytest suite with coverage measurement. Uploads the HTML coverage report as an artifact.

### Stage 4: build

Builds the Docker image (simulated in this demo — in a real pipeline you'd push to a container registry like GHCR or ECR). Produces the image tag as an output.

### Stage 5: deploy-staging

Deploys to the `staging` GitHub Environment. Runs automatically on `main` and `develop` pushes. Uses `environment: staging` which enables environment-specific secrets.

### Stage 6: deploy-production

Deploys to `production`. Has two extra constraints:
1. Only runs on the `main` branch (not `develop` or PRs)
2. The `production` GitHub Environment has **required reviewers** configured — the job pauses and waits for a human to approve before continuing

### Stage 7: pipeline-summary (always)

Runs regardless of other outcomes. Prints a comprehensive ASCII table + writes a markdown summary to `$GITHUB_STEP_SUMMARY` (visible in the Actions UI).

---

## 7. Setting Up GitHub Environments

To make the deployment jobs work with real protection rules:

1. Go to your repository → **Settings** → **Environments**
2. Create `staging`:
   - No required reviewers (auto-deploy)
   - Deployment branch: `main`, `develop`
3. Create `production`:
   - **Required reviewers**: add yourself or your team
   - Deployment branch: `main` only
   - **Wait timer**: 0 minutes (or add a delay)

With these settings, the `deploy-production` job pauses after `deploy-staging` completes and shows a "Review deployments" button in the GitHub UI.

---

## 8. Security Considerations

| Area | Implementation |
|---|---|
| Dependency vulnerabilities | pip-audit + safety in CI |
| Container security | Non-root user in Dockerfile |
| Secrets | Never hardcoded, always `${{ secrets.NAME }}` |
| Token permissions | Minimal `permissions:` per job |
| Fork PRs | `pull_request` event (not `pull_request_target`) |
| Environment gates | Required reviewers for production |

---

## 9. Optimizing Pipeline Speed

| Optimization | Impact |
|---|---|
| Pip caching (`cache: pip` in setup-python) | First run: 2-3 min, subsequent: 15 seconds |
| Parallel jobs (code-quality + security-scan) | Saves ~20 seconds per run |
| `cancel-in-progress: true` | Stops redundant runs on fast-moving PRs |
| Fail fast (lint → test order) | Don't run 3-minute tests if 20-second lint fails |
| Skip deploy on PRs | PRs only run CI, never touch environments |

---

## 10. What to Learn Next

You've completed the course! To continue growing:

### GitHub Actions Advanced Topics
- **OIDC (OpenID Connect):** Authenticate to AWS/GCP/Azure without storing credentials as secrets
- **Custom JavaScript Actions:** Write actions in TypeScript/JavaScript for complex automation
- **GitHub Actions for mobile:** Fastlane integration, iOS/Android workflows
- **GitHub Actions at scale:** Enterprise patterns, runner groups, cost optimization

### Certifications
- 🏅 **GitHub Actions Certification** — [examregistration.github.com](https://examregistration.github.com/)
- 🔐 **GitHub Advanced Security Certification** — [examregistration.github.com](https://examregistration.github.com/)

### Community
- 🛒 **GitHub Actions Marketplace** — [github.com/marketplace?type=actions](https://github.com/marketplace?type=actions)
- ⭐ **awesome-github-actions** (curated resources) — [github.com/sdras/awesome-actions](https://github.com/sdras/awesome-actions)
- 💬 **GitHub Community Discussions** — [github.com/orgs/community/discussions](https://github.com/orgs/community/discussions)

---

## References

- ⚡ **GitHub Actions Documentation** — [docs.github.com/en/actions](https://docs.github.com/en/actions)
- 🏗️ **Using Environments for Deployment** — [docs.github.com/en/actions/deployment/targeting-different-environments/using-environments-for-deployment](https://docs.github.com/en/actions/deployment/targeting-different-environments/using-environments-for-deployment)
- 🔒 **Security Hardening for GitHub Actions** — [docs.github.com/en/actions/security-guides/security-hardening-for-github-actions](https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions)
- 🔑 **About Security Hardening with OpenID Connect (OIDC)** — [docs.github.com/en/actions/deployment/security-hardening-your-deployments/about-security-hardening-with-openid-connect](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/about-security-hardening-with-openid-connect)
- 🌐 **Flask** (Python Web Framework) — [flask.palletsprojects.com](https://flask.palletsprojects.com/)
- 🦄 **Gunicorn** (Python WSGI Server) — [gunicorn.org](https://gunicorn.org/)
- 🐳 **Docker Multi-Stage Builds** — [docs.docker.com/build/building/multi-stage](https://docs.docker.com/build/building/multi-stage/)
- 🧪 **pytest** — [docs.pytest.org](https://docs.pytest.org/en/latest/)
- 📐 **Flake8** (Python Linter) — [flake8.pycqa.org](https://flake8.pycqa.org/en/latest/)
- 🔍 **pip-audit** (Dependency Vulnerability Scanner) — [pypi.org/project/pip-audit](https://pypi.org/project/pip-audit/)
- 🛡️ **Safety** (Python Dependency Checker) — [pypi.org/project/safety](https://pypi.org/project/safety/)
- 🏅 **GitHub Actions Certification** — [examregistration.github.com](https://examregistration.github.com/)

---

## Course Complete!

You have now built 10 projects covering the full GitHub Actions spectrum from Hello World to production-grade CI/CD. The skills you practiced here apply to any language, any cloud provider, and any team size.

**Suggested next steps:**
1. Apply these patterns to a real project you're working on
2. Contribute an action to the GitHub Marketplace
3. Set up branch protection rules on your repositories using CI as the gate
4. Explore OIDC authentication to eliminate long-lived credentials from your secrets
