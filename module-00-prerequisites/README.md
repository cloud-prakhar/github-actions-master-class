# Module 00: Prerequisites & Environment Setup

**Difficulty:** Beginner | **Time:** 30-45 minutes | **Next:** [Module 01 — YAML Fundamentals](../module-01-yaml-fundamentals/README.md)

---

## Learning Objectives

By the end of this module you will:
- Have Git installed and configured
- Have a GitHub account with SSH authentication
- Have VS Code set up with the right extensions
- Understand the course repository structure
- Know how to navigate GitHub's Actions UI

---

## Required Setup

See the detailed step-by-step guide: **[docs/getting-started.md](../docs/getting-started.md)**

---

## Quick Verification Checklist

Run these commands. All should succeed before you continue.

```bash
git --version          # 2.x or higher
git config user.name   # your name
git config user.email  # your email
ssh -T git@github.com  # "Hi username! You've successfully authenticated"
gh auth status         # "Logged in to github.com"
node --version         # v18 or v20 (needed for Modules 08-12)
```

---

## What is GitHub Actions?

Before diving into YAML and Git, here is a one-paragraph mental model:

**GitHub Actions is automation built into GitHub.** Whenever something happens in your repository — someone pushes code, opens a pull request, or a timer fires — GitHub Actions can automatically run a set of instructions (a *workflow*). Those instructions might: run tests, build a Docker image, deploy to a server, send a Slack message, or anything else a computer can do. You write those instructions in YAML files stored in your repository.

That's it. Everything else in this course is the details.

---

## Key Concepts Preview

You will learn all of these in depth in later modules. For now, just notice the vocabulary:

```
Your Repository
│
└── .github/
    └── workflows/
        └── ci.yml          ← A WORKFLOW file written in YAML
                                │
                                ├── on: push        ← TRIGGER (event)
                                │
                                └── jobs:
                                    └── build:       ← JOB
                                        runs-on: ubuntu-latest   ← RUNNER
                                        steps:
                                          - uses: actions/checkout@v4   ← STEP
                                          - run: pytest tests/          ← STEP
```

---

## Course Navigation Tips

- Every module has a `README.md` — always read it top to bottom before looking at code
- Workflow files in `project/.github/workflows/` are the practical deliverables
- Exercise files have both a problem statement and a solution file
- Cross-references throughout modules link to the glossary (`docs/glossary.md`)

---

## Official References

- ⚡ **GitHub Actions Documentation** — [docs.github.com/en/actions](https://docs.github.com/en/actions)
- 📖 **Git Documentation** — [git-scm.com/doc](https://git-scm.com/doc)
- 🖥️ **GitHub CLI Manual** — [cli.github.com/manual](https://cli.github.com/manual/)
- 💻 **VS Code Download** — [code.visualstudio.com](https://code.visualstudio.com)
- 🔧 **YAML Extension for VS Code** (Red Hat) — [marketplace.visualstudio.com](https://marketplace.visualstudio.com/items?itemName=redhat.vscode-yaml)
- 🏃 **`act` Local Runner** (nektos/act) — [github.com/nektos/act](https://github.com/nektos/act)
- 🔑 **GitHub SSH Authentication** — [docs.github.com/en/authentication](https://docs.github.com/en/authentication/connecting-to-github-with-ssh)

---

## Next Steps

Complete the environment setup in [docs/getting-started.md](../docs/getting-started.md), then continue to:

**[Module 01 — YAML Fundamentals](../module-01-yaml-fundamentals/README.md)**
