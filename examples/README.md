# GitHub Actions Examples

A collection of 10 standalone, well-commented examples covering the most important GitHub Actions concepts. Each example is self-contained — copy the workflow file to your repo and it works with zero additional setup.

## How to Use These Examples

Every example follows the same structure:

```
examples/
  XX-example-name/
    README.md                          ← explanation, concepts, tips
    .github/workflows/
      example-name.yml                 ← the workflow — copy this to your repo
```

**To try an example:**

1. Copy the `.github/workflows/<name>.yml` file into **your own repo** at `.github/workflows/<name>.yml`.
2. Commit and push to `main`.
3. Go to the **Actions** tab in your GitHub repo to watch it run.

No extra tools, no setup scripts, no secrets required (except where noted).

---

## Examples

| # | Topic | What You'll Learn | Needs Setup? |
|---|---|---|---|
| [01](./01-push-trigger/) | **Push Trigger** | Branch filters, path filters, `branches-ignore` | No |
| [02](./02-pull-request-events/) | **Pull Request Events** | PR activity types, merged vs closed, PR metadata | No |
| [03](./03-scheduled-cron/) | **Scheduled (Cron)** | Cron syntax, nightly jobs, pairing with `workflow_dispatch` | No |
| [04](./04-manual-dispatch/) | **Manual Dispatch** | Input types (string, choice, boolean), reading input values | No |
| [05](./05-concurrency-control/) | **Concurrency Control** | Groups, cancel-in-progress, per-branch vs per-deploy | No |
| [06](./06-environment-variables/) | **Environment Variables** | Workflow/job/step scopes, built-ins, `$GITHUB_ENV`, secrets pattern | No |
| [07](./07-job-outputs/) | **Job Outputs** | `$GITHUB_OUTPUT`, job `outputs:`, `needs.<job>.outputs.*` | No |
| [08](./08-conditional-logic/) | **Conditional Logic** | `if:` expressions, `success()`, `failure()`, `always()` | No |
| [09](./09-matrix-builds/) | **Matrix Builds** | Multi-version parallel jobs, `include`, `exclude`, `fail-fast` | No |
| [10](./10-dependency-caching/) | **Dependency Caching** | Built-in pip cache, `actions/cache`, cache keys, cache-hit | No |

---

## Recommended Learning Order

If you're new to GitHub Actions, work through the examples in order — each one builds on the previous. If you have specific questions, jump directly to the relevant example.

```
01 Push Trigger
    └─► 02 PR Events         (more event types)
          └─► 03 Scheduled   (time-based events)
                └─► 04 Manual Dispatch  (on-demand events)
                      └─► 05 Concurrency  (managing multiple runs)
                            └─► 06 Env Variables  (passing data within a job)
                                  └─► 07 Job Outputs  (passing data between jobs)
                                        └─► 08 Conditionals  (branching logic)
                                              └─► 09 Matrix  (parallel jobs)
                                                    └─► 10 Caching  (performance)
```

---

## Key Patterns at a Glance

### Trigger a workflow on push to main

```yaml
on:
  push:
    branches: [main]
```

### Trigger on PR, but only when a new commit arrives

```yaml
on:
  pull_request:
    types: [opened, synchronize]
```

### Run daily at 06:00 UTC

```yaml
on:
  schedule:
    - cron: "0 6 * * *"
```

### Cancel duplicate runs per branch

```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```

### Pass data from one step to the next

```yaml
- id: compute
  run: echo "result=hello" >> $GITHUB_OUTPUT

- run: echo "${{ steps.compute.outputs.result }}"
```

### Test across multiple Python versions

```yaml
strategy:
  matrix:
    python-version: ["3.12", "3.13", "3.14"]
steps:
  - uses: actions/setup-python@v5
    with:
      python-version: ${{ matrix.python-version }}
```

### Cache pip dependencies

```yaml
- uses: actions/setup-python@v5
  with:
    python-version: "3.14"
    cache: "pip"
```

---

## Relationship to the Course Modules

These examples are **shorter, focused demos** — each teaches one concept in isolation. The course [modules](../README.md) cover the same topics in depth with theory, exercises, and full projects. Use examples when you want a quick reference; use modules when you want to understand the full picture.
