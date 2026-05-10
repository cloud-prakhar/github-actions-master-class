# GitHub Actions Master Class

> A complete, beginner-to-advanced course on GitHub Actions with hands-on projects, real workflows, and production-grade pipelines.

---

## ⭐ Support This Course

If this course helps you, the kindest thing you can do is:

- **⭐ Star this repository** — it helps others discover the course and takes just one click
- **🍴 Fork it** — forking is how you follow along; every fork also helps the course reach more learners
- **📢 Share it** — pass it on to a teammate, post it in a community, or mention it in a blog post

This course is free and always will be. Stars and forks are the only way to know it's useful — thank you!

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

## Standalone Examples

In addition to the course modules, there is an [`examples/`](./examples/) directory with 10 short, focused examples — one concept each. These are ideal as quick references or for learners who want to try a specific concept without working through a full module.

| # | Example | Topic |
|---|---|---|
| 01 | [Push Trigger](./examples/01-push-trigger/) | Branch/path filters on push |
| 02 | [Pull Request Events](./examples/02-pull-request-events/) | PR activity types and metadata |
| 03 | [Scheduled Cron](./examples/03-scheduled-cron/) | Time-based triggers |
| 04 | [Manual Dispatch](./examples/04-manual-dispatch/) | `workflow_dispatch` with inputs |
| 05 | [Concurrency Control](./examples/05-concurrency-control/) | Cancel duplicate runs |
| 06 | [Environment Variables](./examples/06-environment-variables/) | Scopes, built-ins, secrets pattern |
| 07 | [Job Outputs](./examples/07-job-outputs/) | Pass data between jobs |
| 08 | [Conditional Logic](./examples/08-conditional-logic/) | `if:`, `failure()`, `always()` |
| 09 | [Matrix Builds](./examples/09-matrix-builds/) | Parallel multi-version jobs |
| 10 | [Dependency Caching](./examples/10-dependency-caching/) | Faster pip installs |

Each example is a single workflow YAML with heavy comments, plus a README explaining the concept, how to try it, and common mistakes. No additional setup required.

---

## Additional Resources

| Resource | Description |
|---|---|
| `examples/` | 10 standalone concept examples (copy-and-run) |
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
├── examples/                          <- 10 standalone concept examples
│   ├── README.md
│   ├── 01-push-trigger/
│   ├── 02-pull-request-events/
│   ├── 03-scheduled-cron/
│   ├── 04-manual-dispatch/
│   ├── 05-concurrency-control/
│   ├── 06-environment-variables/
│   ├── 07-job-outputs/
│   ├── 08-conditional-logic/
│   ├── 09-matrix-builds/
│   └── 10-dependency-caching/        <- each has README.md + .github/workflows/
├── module-00-prerequisites/
│   └── README.md
├── module-01-yaml-fundamentals/
│   ├── README.md
│   ├── examples/                      <- 6 annotated YAML files
│   └── exercises/                     <- 2 exercises with solutions
├── module-02-git-fundamentals/
│   ├── README.md
│   └── docs/
│       ├── git-cheatsheet.md
│       └── github-flow.md
├── module-03-github-actions-intro/
│   └── project/.github/workflows/
├── module-04-workflow-triggers/
│   └── project/.github/workflows/
├── module-05-jobs-and-steps/
│   └── project/.github/workflows/
├── module-06-secrets-variables/
│   ├── README.md
│   ├── docs/
│   │   └── security-best-practices.md
│   └── project/.github/workflows/
├── module-07-dependent-jobs/
│   └── project/.github/workflows/
├── module-08-ci-pipeline/
│   └── project/                       <- Python 3.14 Flask app + full CI
│       ├── .flake8
│       ├── requirements.txt
│       ├── requirements-dev.txt
│       ├── src/
│       │   ├── app.py
│       │   └── server.py
│       ├── tests/
│       │   └── test_app.py
│       └── .github/workflows/
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
    └── project/                       <- Full-stack app + production pipeline
        ├── Dockerfile
        ├── requirements.txt
        ├── src/
        │   └── app.py
        ├── tests/
        │   └── test_app.py
        └── .github/workflows/
```

---

## License

MIT — free to use, share, and adapt for learning purposes.

---

## 🙏 Found This Useful?

If this course saved you time or helped you learn something new, consider:

| Action | Why it helps |
|---|---|
| ⭐ **Star the repo** | Helps other learners find this course through GitHub search and trending |
| 🍴 **Fork it** | Creates your own copy to experiment with — and signals to others it's worth a look |
| 📣 **Share with your team** | The best way to learn is alongside others — share the link in Slack, Discord, or LinkedIn |
| 🐛 **Open an issue** | Found a mistake or have a suggestion? Issues are always welcome |

Every star genuinely makes a difference — thank you for learning here. 🚀
