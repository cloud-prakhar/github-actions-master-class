# GitHub Actions Master Class

> A complete, beginner-to-advanced course on GitHub Actions with hands-on projects, real workflows, and production-grade pipelines.

---

## What You Will Learn

This course takes you from zero knowledge of GitHub Actions to building production-grade CI/CD pipelines. You will understand not just *how* to write workflows, but *why* things work the way they do.

**Topics covered:**
- YAML syntax (the language of GitHub Actions)
- Git fundamentals and GitHub Flow
- Workflow structure: events, jobs, steps, runners
- Triggers: push, pull_request, schedule, workflow_dispatch
- Secrets, variables, and environment configuration
- Dependent jobs, artifacts, and data passing
- CI pipelines with caching, testing, and coverage
- CD pipelines with environment gates and approvals
- Matrix builds for cross-platform testing
- Reusable workflows and composite actions
- Real-world production CI/CD pipeline design

---

## Prerequisites

| Requirement | Details |
|---|---|
| A GitHub account | Free at github.com |
| Git installed | v2.x or later |
| A code editor | VS Code recommended |
| Basic terminal knowledge | cd, ls, mkdir, cat |
| No CI/CD experience needed | We start from zero |

---

## Course Structure

| Module | Name | Difficulty | Description |
|---|---|---|---|
| 00 | Prerequisites & Setup | Beginner | Install tools, configure Git, create GitHub account |
| 01 | YAML Fundamentals | Beginner | YAML syntax, types, collections, multiline, anchors |
| 02 | Git Fundamentals | Beginner | Git concepts, commands, GitHub Flow, pull requests |
| 03 | GitHub Actions Introduction | Beginner | Core concepts, first workflow, UI navigation |
| 04 | Workflow Triggers | Beginner-Intermediate | Push, PR, schedule, dispatch, event filters |
| 05 | Jobs & Steps Deep Dive | Intermediate | Job structure, step types, outputs, conditionals |
| 06 | Secrets, Variables & Environments | Intermediate | Secrets, vars, GITHUB_TOKEN, environments |
| 07 | Dependent Jobs & Artifacts | Intermediate | needs:, job outputs, upload/download artifacts |
| 08 | Continuous Integration (CI) | Intermediate | Full CI pipeline, caching, test reporting |
| 09 | Continuous Deployment (CD) | Intermediate-Advanced | Multi-environment deploy, gates, rollback |
| 10 | Matrix Builds & Advanced Features | Advanced | Matrix strategy, service containers, summaries |
| 11 | Reusable Workflows & Composite Actions | Advanced | workflow_call, composite actions, DRY pipelines |
| 12 | Real-World Full-Stack CI/CD | Advanced | Production pipeline, security scanning, full SDLC |

---

## How to Use This Course

### Option A — Follow Along (Recommended)
1. Fork this repository to your GitHub account
2. Clone your fork locally
3. Work through modules in order (00 to 12)
4. Each module's `project/` folder contains working workflows you can push to trigger
5. Read each `README.md` before looking at the workflow files

### Option B — Reference
- Jump directly to the module that covers your topic
- Use the glossary at `docs/glossary.md`
- Check `docs/resources.md` for official documentation links

### Option C — Local Testing with `act`
You can run GitHub Actions locally without pushing to GitHub using the `act` tool:
```bash
# Install act (macOS)
brew install act

# Run all workflows triggered by push
act push

# Run a specific workflow file
act -W .github/workflows/hello-world.yml
```

---

## Quick Start

```bash
# 1. Fork this repo on GitHub, then clone your fork
git clone https://github.com/YOUR_USERNAME/github-actions-master-class.git
cd github-actions-master-class

# 2. Read the prerequisites
cat module-00-prerequisites/README.md

# 3. Start with Module 01 (YAML)
cat module-01-yaml-fundamentals/README.md

# 4. When ready for your first workflow (Module 03),
#    copy the project folder structure to a test repo and push
```

---

## Module Navigation

- [Module 00 — Prerequisites](./module-00-prerequisites/README.md)
- [Module 01 — YAML Fundamentals](./module-01-yaml-fundamentals/README.md)
- [Module 02 — Git Fundamentals](./module-02-git-fundamentals/README.md)
- [Module 03 — GitHub Actions Introduction](./module-03-github-actions-intro/README.md)
- [Module 04 — Workflow Triggers](./module-04-workflow-triggers/README.md)
- [Module 05 — Jobs & Steps](./module-05-jobs-and-steps/README.md)
- [Module 06 — Secrets, Variables & Environments](./module-06-secrets-variables/README.md)
- [Module 07 — Dependent Jobs & Artifacts](./module-07-dependent-jobs/README.md)
- [Module 08 — Continuous Integration](./module-08-ci-pipeline/README.md)
- [Module 09 — Continuous Deployment](./module-09-cd-pipeline/README.md)
- [Module 10 — Matrix Builds & Advanced Features](./module-10-matrix-advanced/README.md)
- [Module 11 — Reusable Workflows & Composite Actions](./module-11-reusable-workflows/README.md)
- [Module 12 — Real-World Full-Stack CI/CD](./module-12-real-world-cicd/README.md)

---

## Additional Resources

| Resource | Description |
|---|---|
| `docs/getting-started.md` | Detailed environment setup guide |
| `docs/glossary.md` | GitHub Actions glossary with examples |
| `docs/resources.md` | Official docs, playgrounds, cheat sheets |

---

## Official References

- ⚡ **GitHub Actions Documentation** — [docs.github.com/en/actions](https://docs.github.com/en/actions)
- 🛒 **GitHub Actions Marketplace** — [github.com/marketplace?type=actions](https://github.com/marketplace?type=actions)
- 🎓 **GitHub Skills** (Learning Lab successor) — [skills.github.com](https://skills.github.com)
- 🏃 **`act` Local Runner** (nektos/act) — [github.com/nektos/act](https://github.com/nektos/act)
- 📄 **YAML 1.2 Specification** — [yaml.org/spec/1.2.2](https://yaml.org/spec/1.2.2/)
- 🐍 **Python 3 Documentation** — [docs.python.org/3](https://docs.python.org/3/)
- 🖥️ **GitHub CLI Manual** — [cli.github.com/manual](https://cli.github.com/manual/)
- 📖 **Git Reference Manual** — [git-scm.com/doc](https://git-scm.com/doc)

---

## Repository Layout

```
github-actions-master-class/
├── README.md                          <- You are here
├── .gitignore
├── docs/
│   ├── getting-started.md
│   ├── glossary.md
│   └── resources.md
├── module-00-prerequisites/
├── module-01-yaml-fundamentals/
│   ├── examples/
│   └── exercises/
├── module-02-git-fundamentals/
│   └── docs/
├── module-03-github-actions-intro/
│   └── project/.github/workflows/
├── module-04-workflow-triggers/
│   └── project/.github/workflows/
├── module-05-jobs-and-steps/
│   └── project/.github/workflows/
├── module-06-secrets-variables/
│   ├── docs/
│   └── project/.github/workflows/
├── module-07-dependent-jobs/
│   └── project/.github/workflows/
├── module-08-ci-pipeline/
│   └── project/                       <- Real Python 3.14 Flask app + CI
├── module-09-cd-pipeline/
│   └── project/.github/workflows/
├── module-10-matrix-advanced/
│   └── project/.github/workflows/
├── module-11-reusable-workflows/
│   └── project/
│       └── .github/
│           ├── workflows/
│           └── actions/               <- Composite actions
└── module-12-real-world-cicd/
    └── project/                       <- Full-stack app + pipeline
```

---

## License

MIT — free to use, share, and adapt for learning purposes.
