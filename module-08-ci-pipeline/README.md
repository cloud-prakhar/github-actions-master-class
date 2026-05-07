# Module 08: Continuous Integration (CI)

## Project 6: Full CI Pipeline for a Python 3.14 Flask Application

---

## Table of Contents

1. [Learning Objectives](#learning-objectives)
2. [What is Continuous Integration?](#what-is-continuous-integration)
3. [A Complete CI Pipeline](#a-complete-ci-pipeline)
4. [Dependency Caching](#dependency-caching)
5. [Running Tests in GitHub Actions](#running-tests-in-github-actions)
6. [Code Coverage](#code-coverage)
7. [PR Status Checks](#pr-status-checks)
8. [CI Best Practices](#ci-best-practices)
9. [Project: Full CI Pipeline for Python 3.14 Flask](#project-full-ci-pipeline-for-python-314-flask)
10. [Exercises](#exercises)

---

## Learning Objectives

By the end of this module, you will be able to:

- **Build a production-grade CI pipeline** that mirrors what real teams use every day
- **Run linting, testing, and building** as separate, well-structured pipeline stages
- **Implement dependency caching** to dramatically reduce pipeline run times and costs
- **Run tests across multiple operating systems and Python versions** using matrix strategies
- **Generate and upload code coverage reports** as build artifacts for review
- **Set up CI status checks** that protect pull requests from merging broken code
- **Configure fail-fast vs. complete-all-checks** behavior depending on your team's needs
- **Understand the tradeoffs** between pipeline speed, thoroughness, and cost

---

## What is Continuous Integration?

### Definition

Continuous Integration (CI) is a software development practice where developers frequently merge their code changes into a shared repository — often multiple times per day. Each merge triggers an automated build and test sequence to detect integration problems as early as possible.

The term was popularized by Kent Beck as part of Extreme Programming (XP) and later refined by Martin Fowler, whose article "Continuous Integration" (2006, updated 2024) remains the definitive reference on the topic.

The core principle is simple: **integrate early and often, and verify every integration automatically**.

### The Problem CI Solves

Before CI, teams worked in long-lived feature branches — sometimes for weeks or months. When it came time to merge, they faced "merge hell": a nightmare of conflicting changes, broken builds, and failed tests that took days to resolve. The longer you wait to integrate, the more painful the integration becomes.

CI eliminates this by making integration a non-event. If every developer integrates their work daily and every integration is verified automatically, conflicts are small and caught immediately.

### Core Principles of CI

1. **Maintain a single source repository**: Everyone works from one canonical branch (or merges to it frequently).

2. **Automate the build**: The entire build process — compilation, packaging, asset generation — must run with a single command, without human intervention.

3. **Make the build self-testing**: The automated build must include running all tests. A build that compiles but doesn't pass tests is not a successful build.

4. **Every commit triggers a build**: Automation runs on every push, not just at release time.

5. **Fix broken builds immediately**: A broken CI build is the highest-priority issue for the team. No new work proceeds until the build is green again.

6. **Keep the build fast**: If the CI pipeline takes 30 minutes, developers will stop running it. Aim for under 10 minutes for the core feedback loop.

7. **Build in a production-like environment**: Your CI environment should mirror production as closely as possible to catch environment-specific bugs.

8. **Make it easy for everyone to see what's happening**: CI results should be visible to the whole team.

### Benefits of CI

**Early Bug Detection**
Bugs caught the day they're introduced are dramatically cheaper to fix than bugs found days or weeks later. When a test fails within minutes of a commit, the developer still has the context of what they changed. When the same bug surfaces in QA three weeks later, debugging becomes a forensic exercise.

**Consistent Code Quality**
With linting and static analysis running on every commit, code style drift becomes impossible. Every line of code that merges to main has been checked against the same rules, every time. No more "I forgot to run the linter" incidents.

**Reduced Integration Risk**
Since changes are integrated frequently and each integration is verified, the risk of any single merge causing major problems is dramatically reduced. You're making many small bets instead of one large gamble.

**Confidence to Refactor**
When developers know that a comprehensive test suite runs on every change, they're more willing to refactor and improve the codebase. Without CI, refactoring feels risky. With CI, you have a safety net.

**Faster Release Cycles**
When code is continuously verified, you're always close to releasable. There's no "stabilization sprint" needed before a release because the code has been stable throughout development.

**Better Team Collaboration**
CI makes the health of the codebase visible to everyone. When the build is broken, everyone knows. When it's fixed, everyone knows. This shared visibility builds a culture of collective ownership.

### CI vs. CD (Delivery) vs. CD (Deployment)

These three terms are often confused and used interchangeably, but they represent distinct stages of the software delivery lifecycle:

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│   Developer  →  [Commit]  →  [Build]  →  [Test]  →  [Lint]   │
│                                                                 │
│   This is Continuous Integration (CI)                          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│   [CI Passes]  →  [Package]  →  [Deploy to Staging]           │
│                  →  [Integration Tests]  →  [Staging OK]       │
│                                                                 │
│   This is Continuous Delivery (CD - Delivery)                  │
│   (Production deployment requires manual approval)             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│   [Staging OK]  →  [Automatic Deploy to Production]           │
│                                                                 │
│   This is Continuous Deployment (CD - Deployment)              │
│   (No human approval needed)                                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Continuous Integration (CI)**
Automatically builds and tests every change. The output is a verified, tested artifact that might be deployed. Nothing ships automatically — the focus is on verification.

**Continuous Delivery (CD - Delivery)**
Extends CI. After verification, the artifact is automatically deployed to a staging or pre-production environment. It is always in a deployable state, but deploying to production requires a human to push a button. Teams that want confidence before production choose this approach.

**Continuous Deployment (CD - Deployment)**
The most aggressive form: every change that passes all automated tests is automatically deployed to production. No human approval. This requires extremely high confidence in your test suite. Companies like Netflix and Etsy famously deploy to production hundreds of times per day.

In this module, we focus on CI. Module 09 covers the CD pipeline.

### The CI Feedback Loop

The power of CI comes from the tightness of the feedback loop:

```
Write Code → Commit → Push → [CI Runs Automatically] → Get Result
     ↑                                                      │
     └──────────────────── Fix if broken ──────────────────┘
```

The goal is to make this loop as fast as possible. Ideally:
- The developer pushes code
- Within 1-2 minutes, they know if linting passed
- Within 5-7 minutes, they know if all tests passed
- Within 10 minutes, they have full confidence the change is good

When the loop is tight, developers stay in context and fix issues immediately. When it's slow (30+ minutes), developers switch to other tasks, forget the context, and find the feedback useless.

---

## A Complete CI Pipeline

### Pipeline Triggers

For CI, you typically want to trigger on two events:

```yaml
on:
  push:
    branches:
      - main
      - develop
      - 'feature/**'   # Wildcard: any branch starting with feature/
  pull_request:
    branches:
      - main
      - develop
```

**Why both `push` and `pull_request`?**

- `push`: Runs CI when you push directly to a tracked branch. Catches problems on your main integration branches immediately.
- `pull_request`: Runs CI when a PR is opened or updated. This is what powers the status checks on PR pages in GitHub.

For most teams, the most important trigger is `pull_request` to `main`. This ensures nothing broken can be merged into the primary branch.

**Limiting which branches trigger CI**

For large repositories, you may not want CI to run on every single branch push. Consider:

```yaml
on:
  push:
    branches:
      - main
      - develop
  pull_request:
    branches:
      - main
```

This runs CI on pushes to `main` and `develop` (your integration branches) and on any PR targeting `main`. Feature branch pushes don't trigger CI unless a PR is opened.

### Pipeline Stages

A well-structured CI pipeline progresses through increasingly expensive checks:

```
Stage 1: Install
    ↓ (download and cache dependencies)
Stage 2: Lint
    ↓ (fast: catches syntax errors, style issues, obvious bugs)
Stage 3: Build
    ↓ (compile, transpile, bundle assets)
Stage 4: Test
    ↓ (run unit and integration tests)
Stage 5: Coverage
    ↓ (generate coverage report, check thresholds)
Stage 6: Report
    (upload artifacts, post status, send notifications)
```

**Why this order?**

The pipeline is ordered from fastest/cheapest to slowest/most expensive. If linting fails (usually takes < 30 seconds), there's no point running the test suite (which might take 5 minutes). Fail fast on cheap checks before investing in expensive ones.

### What Belongs in CI

Things that belong in CI:

- **Linting and static analysis**: Fast, catches code quality issues
- **Unit tests**: Fast, test individual components in isolation
- **Build verification**: Ensure the project compiles and bundles correctly
- **Code coverage**: Measure how well tests cover the codebase
- **Security scanning**: SAST (Static Application Security Testing) tools
- **License compliance**: Ensure dependencies don't violate your license policy
- **Dependency vulnerability scanning**: Check for known CVEs in dependencies

Things that don't belong in CI (belong in CD or separate pipelines):

- **Deployment**: CI is about verification, not delivery
- **Long-running performance tests**: Better as a scheduled job or pre-release check
- **Manual approval gates**: These belong in CD workflows with `environment` protection rules
- **Production database migrations**: Far too risky for automated CI

### Job Structure in GitHub Actions

```yaml
jobs:
  lint:
    name: Lint Code
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.14'
          cache: pip
      - run: pip install flake8
      - run: flake8 src/ tests/ --max-line-length=120

  test:
    name: Run Tests
    runs-on: ubuntu-latest
    needs: lint          # Only runs if lint passes
    steps:
      # ...

  build:
    name: Build Docker Image
    runs-on: ubuntu-latest
    needs: test          # Only runs if test passes
    steps:
      # ...
```

The `needs` keyword creates a dependency graph. GitHub Actions executes jobs in parallel by default. Using `needs`, you can sequence them.

---

## Dependency Caching

### Why Caching Matters

Every time your CI pipeline runs, it runs `pip install -r requirements.txt`, which downloads all your project dependencies from the internet. For a project with many dependencies, this can take 1-3 minutes.

If your CI pipeline runs 50 times a day (common for an active team), that's:
- 50 × 2 minutes = 100 minutes of CI time per day just downloading packages
- Over a month: ~50 hours of wasted CI time
- In GitHub Actions terms: that's real money if you're on a paid plan

Caching solves this by storing the downloaded packages in GitHub's cache storage. On subsequent runs, the cache is restored instead of downloading from PyPI, reducing install time from 2 minutes to ~10 seconds.

### actions/cache@v4

GitHub provides the `actions/cache` action for caching:

```yaml
- name: Cache pip packages
  uses: actions/cache@v4
  with:
    path: ~/.cache/pip    # The pip cache directory
    key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements*.txt') }}
    restore-keys: |
      ${{ runner.os }}-pip-
```

**Understanding the three parameters:**

**`path`**: The directory to cache. For pip, this is `~/.cache/pip` (pip's local package cache). Caching this directory means pip finds packages already downloaded and skips the network fetch.

**`key`**: The cache key. If a cache with this exact key exists, it's restored. If not, the action continues and at the end of the job, saves the cache under this key. The key should change whenever `requirements.txt` changes — meaning new packages were added or versions updated.

**`restore-keys`**: Fallback keys to try if the primary key doesn't match. If `ubuntu-latest-pip-abc123` doesn't exist, try finding any cache that starts with `ubuntu-latest-pip-`. This fallback cache might be slightly out of date, but it's better than downloading everything from scratch.

### Cache Key Strategy

The cache key is critical. A good cache key:
1. **Changes when the cache should be invalidated** (dependencies change)
2. **Stays the same when nothing relevant changed** (same run, same dependencies)
3. **Is OS-specific** when native extensions are involved (different OS = different compiled wheels)

```yaml
# Good: OS + Python version + requirements hash
key: ${{ runner.os }}-pip-${{ matrix.python-version }}-${{ hashFiles('**/requirements*.txt') }}

# Good: Just OS + requirements hash (when not using matrix)
key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements*.txt') }}

# Bad: Static key (never invalidates, always stale after first run)
key: pip-cache

# Bad: No OS prefix (macOS cache used on Linux, compiled extension incompatibilities)
key: pip-${{ hashFiles('**/requirements*.txt') }}
```

### The hashFiles() Function

`hashFiles('**/requirements*.txt')` generates a SHA-256 hash of the contents of all `requirements*.txt` files (matching `requirements.txt`, `requirements-dev.txt`, etc.). When any dependency is added, removed, or pinned to a different version:
1. The requirements file changes
2. The hash changes
3. The old cache key no longer matches
4. A new cache is created with the updated dependencies
5. Old caches eventually expire (GitHub keeps caches for 7 days by default)

### setup-python Built-in Caching

`actions/setup-python@v5` has built-in pip caching support — the simplest approach:

```yaml
- uses: actions/setup-python@v5
  with:
    python-version: '3.14'
    cache: 'pip'                              # Built-in pip caching!
    cache-dependency-path: 'requirements*.txt'
```

This is equivalent to using `actions/cache@v4` with the correct pip paths. Use this shorthand unless you need a custom cache key or path.

### Caching in Other Ecosystems (Reference)

**Maven (Java)**
```yaml
- uses: actions/cache@v4
  with:
    path: ~/.m2/repository
    key: ${{ runner.os }}-maven-${{ hashFiles('**/pom.xml') }}
    restore-keys: |
      ${{ runner.os }}-maven-
```

**Go modules**
```yaml
- uses: actions/cache@v4
  with:
    path: ~/go/pkg/mod
    key: ${{ runner.os }}-go-${{ hashFiles('**/go.sum') }}
    restore-keys: |
      ${{ runner.os }}-go-
```

### Cache Limitations

- **Cache size**: GitHub limits each cache to 10 GB. Individual caches must be under 10 GB.
- **Total cache storage**: 10 GB per repository by default.
- **Cache eviction**: Caches that haven't been accessed in 7 days are automatically evicted. When you hit the 10 GB limit, the least recently used caches are evicted first.
- **Cache scope**: Caches are scoped to branches. A cache created on a feature branch can't be used by another feature branch, but can fall back to the base branch cache.

---

## Running Tests in GitHub Actions

### Installing Test Dependencies

In CI, always pin exact versions by installing from a lockfile or pinned `requirements.txt`:

```yaml
- name: Install dependencies
  run: pip install -r requirements.txt -r requirements-dev.txt
```

**Why pin versions?**

- Pinned versions (`flask==3.1.0`) install the same package every time, on every machine
- Unpinned versions (`flask`) might resolve to different releases on different runs, causing intermittent failures
- `requirements-dev.txt` contains test-only tools (`pytest`, `flake8`, `pytest-cov`) that should not ship in production images but are needed in CI

A typical Python CI install sequence:

```yaml
- uses: actions/setup-python@v5
  with:
    python-version: '3.14'
    cache: pip
    cache-dependency-path: 'requirements*.txt'

- name: Install dependencies
  run: pip install -r requirements.txt -r requirements-dev.txt
```

### Running Tests

```yaml
- name: Run tests
  run: pytest tests/ -v
  env:
    PYTHONPATH: src   # Allow imports from src/ without packaging
```

Or with coverage and a short-summary:

```yaml
- name: Run tests with coverage
  run: pytest tests/ -v --cov=src --cov-report=term-missing --cov-report=xml
  env:
    PYTHONPATH: src
```

### Test Output and GitHub Integration

By default, pytest outputs results to stdout. GitHub Actions captures this and shows it in the workflow logs. For structured test output (visible in the PR interface), use the JUnit XML reporter:

```yaml
- name: Run tests
  run: pytest tests/ --junitxml=test-results/results.xml
  env:
    PYTHONPATH: src

- name: Publish test results
  uses: EnricoMi/publish-unit-test-result-action@v2
  if: always()   # Run even if tests fail
  with:
    files: test-results/**/*.xml
```

This adds a "Test Results" section to your PR showing which tests passed and which failed, without having to scroll through logs.

### Failing the Job When Tests Fail

pytest exits with code `1` when any test fails. GitHub Actions interprets any non-zero exit code as a job failure and marks the step as failed automatically. You don't need to do anything special:

```yaml
- name: Run tests
  run: pytest tests/    # If any test fails, pytest exits 1, step fails, job fails
```

### Preventing Flaky Tests from Blocking CI

Flaky tests (tests that randomly pass or fail) are a major CI problem. Use `pytest-rerunfailures`:

```yaml
- name: Install test tools
  run: pip install pytest pytest-rerunfailures

- name: Run tests with retry
  run: pytest tests/ --reruns 2 --reruns-delay 1
  # Retries each failing test up to 2 times with a 1-second delay
```

Or use a simple shell retry for the entire suite:

```yaml
- name: Run tests with retry
  run: pytest tests/ || pytest tests/ || pytest tests/
```

### Test Timeouts

Long-running tests can block CI. Set a timeout at the job level:

```yaml
- name: Run tests
  run: pytest tests/
  timeout-minutes: 10   # Kill the step if it runs longer than 10 minutes
```

Or per-test timeouts with `pytest-timeout`:

```yaml
- run: pip install pytest-timeout
- run: pytest tests/ --timeout=30   # Each test must complete within 30 seconds
```

### Separating Unit Tests from Integration Tests

For faster feedback, run cheap unit tests separately from slower integration tests:

```yaml
jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - run: pytest tests/unit/ -v

  integration-tests:
    runs-on: ubuntu-latest
    needs: unit-tests   # Only run if unit tests pass
    steps:
      - run: pytest tests/integration/ -v
```

---

## Code Coverage

### What is Code Coverage?

Code coverage measures what percentage of your source code is executed by your test suite. It's expressed as a percentage across different dimensions:

- **Line coverage**: What percentage of lines were executed?
- **Branch coverage**: What percentage of conditional branches (if/else) were exercised?
- **Function coverage**: What percentage of functions were called?
- **Statement coverage**: What percentage of statements were executed?

High coverage doesn't guarantee bug-free code, but low coverage is a strong signal that large portions of the code are untested.

### Generating Coverage with pytest-cov

`pytest-cov` is the standard coverage plugin for pytest. Install it alongside pytest:

```yaml
- name: Install test dependencies
  run: pip install pytest pytest-cov
```

Run with coverage measurement:

```yaml
- name: Run tests with coverage
  run: |
    pytest tests/ \
      --cov=src \
      --cov-report=term-missing \
      --cov-report=html:htmlcov \
      --cov-report=xml:coverage.xml \
      --cov-fail-under=80
  env:
    PYTHONPATH: src
```

Key flags:
- `--cov=src` — measure coverage for the `src/` package directory
- `--cov-report=term-missing` — print missing lines to the terminal
- `--cov-report=html:htmlcov` — generate an HTML report in `htmlcov/`
- `--cov-report=xml:coverage.xml` — XML format for Codecov and other tools
- `--cov-fail-under=80` — fail the step if overall coverage drops below 80%

`--cov-fail-under` causes pytest to exit with code 2 if coverage falls below the threshold, which makes the CI step fail automatically.

You can also configure thresholds in `setup.cfg` or `pyproject.toml` so they don't clutter the command line:

```ini
# setup.cfg
[tool:pytest]
addopts = --cov=src --cov-report=term-missing --cov-fail-under=80
```

### Uploading Coverage as an Artifact

```yaml
- name: Run tests with coverage
  run: pytest tests/ --cov=src --cov-report=html:htmlcov
  env:
    PYTHONPATH: src

- name: Upload coverage report
  uses: actions/upload-artifact@v4
  with:
    name: coverage-report
    path: htmlcov/
    retention-days: 30   # Keep for 30 days
```

This makes the coverage HTML report downloadable from the workflow run page.

### Uploading to Codecov

Codecov is a popular coverage reporting service that integrates with GitHub PRs:

```yaml
- name: Upload to Codecov
  uses: codecov/codecov-action@v4
  with:
    token: ${{ secrets.CODECOV_TOKEN }}
    files: ./coverage/lcov.info
    fail_ci_if_error: true
    verbose: true
```

After setup, Codecov posts a comment on each PR showing coverage changes: "+2.3% coverage" or "-1.1% coverage", making it easy to see the coverage impact of each change.

### Coverage Best Practices

- **Start with a low threshold** (e.g., 60%) and increase it over time as you add tests
- **Don't chase 100% coverage** — some code is genuinely hard to test (error handlers, edge cases) and the marginal value decreases
- **Focus on critical paths** — 80% coverage of your core business logic is worth more than 90% coverage including trivial getters/setters
- **Use branch coverage** — line coverage can be misleading; branch coverage tells you if both sides of conditions are tested

---

## PR Status Checks

### How CI Status Shows on PRs

When your workflow runs in response to a `pull_request` event, GitHub displays the status of each job directly on the PR page:

```
✅ lint (push) — All checks have passed
✅ test (push) — All checks have passed
✅ build (push) — All checks have passed
```

Each job in your workflow appears as a separate status check. Developers can click on any check to see the detailed logs.

### Required Status Checks

You can configure certain checks as "required" in branch protection rules. If a required check fails (or hasn't run), the PR cannot be merged.

**Setting up required status checks:**
1. Go to your repository settings
2. Navigate to Branches → Branch protection rules
3. Add a rule for your main branch
4. Check "Require status checks to pass before merging"
5. Search for and add specific check names (e.g., "lint", "test", "build")

**Important:** The status check name must match exactly. In GitHub Actions, the check name is the `name` field of the job:

```yaml
jobs:
  lint:
    name: "Lint Code"    # This is the status check name: "Lint Code"
```

Or if no `name` is specified, it uses the job ID:

```yaml
jobs:
  lint:                  # Status check name: "lint"
    runs-on: ubuntu-latest
```

### Making CI Non-Blocking (but Visible)

Sometimes you want CI to run but not block merging (useful for new pipelines or informational checks):

```yaml
jobs:
  experimental-check:
    runs-on: ubuntu-latest
    continue-on-error: true   # Job failure won't fail the workflow
```

Use this for experimental checks, performance benchmarks, or checks you're still tuning.

### Status Check Names Across Matrix Jobs

When using matrix strategies, each matrix combination creates a separate status check:

```yaml
jobs:
  test:
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest]
        python-version: ['3.12', '3.13', '3.14']
```

This creates six status checks:
- `test (ubuntu-latest, 3.12)`
- `test (ubuntu-latest, 3.13)`
- `test (ubuntu-latest, 3.14)`
- `test (windows-latest, 3.12)`
- ... and so on

If you want a single status check for "all matrix jobs passed", use a summary job:

```yaml
  all-tests-pass:
    needs: test
    runs-on: ubuntu-latest
    if: always()
    steps:
      - name: Check test results
        if: ${{ needs.test.result != 'success' }}
        run: exit 1
```

---

## CI Best Practices

### 1. Keep CI Fast (Target: Under 10 Minutes)

A slow CI pipeline is a neglected CI pipeline. When developers have to wait 30 minutes for feedback, they:
- Switch tasks and lose context
- Stop running CI locally before pushing
- Start looking for ways to skip CI
- Lose confidence that CI provides value

Target under 10 minutes for the core feedback loop (lint + test). If you can't get there, investigate:
- Are you parallelizing jobs that could run concurrently?
- Are you caching dependencies?
- Are your tests doing unnecessary work?
- Can some slow tests be moved to a separate, scheduled job?

### 2. Cache Dependencies Aggressively

As covered in the caching section: never download what you can cache. This alone often halves pipeline run times.

### 3. Fail Fast for Obvious Errors

Structure your pipeline to catch cheap, fast errors before running expensive ones:

```
lint (30 seconds) → unit tests (2 minutes) → integration tests (5 minutes) → e2e tests (10 minutes)
```

If linting fails, don't bother running the e2e tests. Use `needs` to sequence jobs.

### 4. Separate Lint from Tests

Lint and tests serve different purposes and should be separate jobs:
- Lint failures are code quality issues
- Test failures are functional bugs

Separating them gives clearer signal: "lint failed" vs "tests failed" vs "both failed".

### 5. Use Specific Action Versions

Always pin action versions:

```yaml
# Bad: unpinned, could break when action updates
uses: actions/checkout@main

# Better: pinned to major version
uses: actions/checkout@v4

# Best: pinned to exact SHA (most secure, immune to tag manipulation)
uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683
```

For security-sensitive workflows, use SHA pinning. For typical CI, major version pinning (v4) is a reasonable balance between security and convenience.

### 6. Set Timeouts on Jobs

Prevent runaway jobs from consuming CI minutes:

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    timeout-minutes: 15   # Fail if job runs longer than 15 minutes
```

Without this, a hung test could run for the maximum allowed time (6 hours), consuming your entire CI budget.

### 7. Don't Commit Secrets to CI Configuration

Never hardcode credentials in workflow files:

```yaml
# BAD: Secret in plain text
- run: aws deploy --key "AKIAIOSFODNN7EXAMPLE"

# GOOD: Reference a GitHub Secret
- run: aws deploy
  env:
    AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
```

### 8. Pin Python Dependency Versions for Reproducible Installs

As mentioned earlier, using pinned `requirements.txt` files ensures reproducible dependency installation. Every run installs exactly the same versions, every time.

### 9. The [skip ci] Convention

Most CI systems (including GitHub Actions) recognize special commit message flags:

```bash
git commit -m "Update README [skip ci]"
# OR
git commit -m "docs: fix typo\n\n[skip ci]"
```

Adding `[skip ci]`, `[ci skip]`, `skip-checks: true`, or similar to your commit message instructs CI to skip the run.

**When is it appropriate to skip CI?**

Acceptable:
- Documentation-only changes (typo fixes in README)
- Comment changes in code
- Changes to `.gitignore`
- Non-functional changes that genuinely can't affect anything

Not acceptable:
- "I'm in a hurry and the tests are slow"
- "I'll fix the failing tests later"
- Any change to source code, configuration, or tests

Skipping CI is a tool to reduce noise, not a shortcut to avoid fixing problems. Many teams disable `[skip ci]` entirely for protected branches.

### 10. Fail Fast vs. Complete All Checks

GitHub Actions has a `fail-fast` option for matrix jobs:

```yaml
strategy:
  fail-fast: true   # Default: cancel remaining matrix jobs if one fails
  matrix:
    python-version: ['3.12', '3.13', '3.14']
```

With `fail-fast: true` (default): If the Python 3.12 job fails, GitHub immediately cancels the remaining matrix jobs. This saves CI minutes but gives you less information — you only know it failed on 3.12, not whether it also fails on other versions.

With `fail-fast: false`: All matrix jobs run to completion. You see the full picture: "fails on Python 3.12 and 3.13, passes on 3.14". This costs more CI minutes but gives more diagnostic information.

For CI on PRs, `fail-fast: true` is usually the right choice — you want fast feedback and once you know it's broken, the other results don't matter. For compatibility testing (verifying your library works on multiple Python versions), `fail-fast: false` is better.

### 11. Use Environments and Concurrency Controls

Prevent multiple CI runs from racing on the same branch:

```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```

This cancels any in-progress CI run for the same branch when a new push arrives. No point running CI on an old commit if a newer one just landed.

---

## Project: Full CI Pipeline for Python 3.14 Flask

### Project Structure

```
module-08-ci-pipeline/
├── README.md                          (this file)
└── project/
    ├── requirements.txt               (runtime dependencies: flask, gunicorn)
    ├── requirements-dev.txt           (dev tools: pytest, flake8, pytest-cov)
    ├── .flake8                        (flake8 linting configuration)
    ├── src/
    │   ├── app.py                     (Flask application factory)
    │   └── server.py                  (gunicorn entry point)
    ├── tests/
    │   └── test_app.py                (pytest test suite)
    └── .github/
        └── workflows/
            └── ci.yml                 (CI pipeline workflow)
```

### What This Project Demonstrates

1. **Multi-job pipeline**: Separate jobs for lint (flake8), test (pytest), and build summary
2. **Job dependencies**: Test only runs if lint passes; build summary only runs if tests pass
3. **Dependency caching**: pip cache keyed on requirements files hash via `setup-python`
4. **Coverage reporting**: pytest-cov HTML report uploaded as workflow artifact
5. **CI status summary**: Final job that reports overall pipeline status
6. **Proper secrets handling**: No hardcoded credentials
7. **Timeout protection**: Jobs have maximum run time configured

### How to Use This Project

1. Fork or clone the repository
2. Navigate to `module-08-ci-pipeline/project/`
3. Create a virtual environment: `python -m venv .venv && source .venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt -r requirements-dev.txt`
5. Run tests locally: `PYTHONPATH=src pytest tests/ -v`
6. Review the workflow at `.github/workflows/ci.yml`
7. Push a change and watch the Actions tab in GitHub

### Key Workflow Concepts Demonstrated

**Cache hit vs. cache miss:**
- First run: No cache exists. pip downloads all packages from PyPI. Cache is saved at end of job.
- Subsequent runs: Cache key matches. pip cache restored. Install uses cached wheels.

**Job sequencing:**
```
lint ──→ test ──→ build
              ↓
         ci-status (always runs)
```

**Artifact uploads:**
After a successful test run, the coverage report is uploaded as a workflow artifact. You can download it from the Actions tab for 30 days.

---

## Exercises

### Exercise 1: Add a New API Endpoint and Tests

Add a `/multiply` endpoint to `src/app.py` that takes query params `a` and `b` and returns their product.

1. Add the endpoint to `src/app.py`
2. Write a test for it in `tests/test_app.py`
3. Push your changes and watch the CI pipeline run

**Expected outcome:** All tests pass, CI is green.

**Challenge:** Intentionally write a bug in the implementation (but correct tests). Watch CI fail and identify the issue from the pytest output in the logs.

---

### Exercise 2: Break the Linter and Fix It

1. Open `src/app.py` and add a variable that's assigned but never used:
   ```python
   unused = 42
   ```
2. Commit and push
3. Watch the lint job fail in the CI pipeline (flake8 reports `F841 local variable 'unused' is assigned to but never used`)
4. Notice that the test job doesn't run (because it `needs: lint`)
5. Remove the unused variable and push again
6. Watch the full pipeline go green

**Learning:** Failing fast on lint prevents wasted compute on a pipeline that will ultimately fail.

---

### Exercise 3: Observe Caching in Action

1. Look at the first run of your CI pipeline — note how long the `pip install` step takes
2. Push a small change (like adding a comment to `src/app.py`)
3. Look at the second run — the pip install step should be dramatically faster
4. In the workflow logs, look for `Cache restored from key:` vs `Cache not found for key:`

**Learning:** Caching provides significant time savings on subsequent runs.

---

### Exercise 4: Add Matrix Testing Across Python Versions

Extend the test job to run on multiple Python versions:

```yaml
jobs:
  test:
    strategy:
      matrix:
        python-version: ['3.12', '3.13', '3.14']
    steps:
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
          cache: pip
```

Push the change and watch three parallel test jobs run simultaneously.

**Challenge:** After adding matrix testing, configure required status checks so that all three Python version checks must pass before a PR can be merged.

---

### Exercise 5: Raise the Coverage Threshold and Watch CI Fail

1. Find the `--cov-fail-under` flag in your `ci.yml` workflow
2. Raise the threshold to `99`
3. Push and watch the test job fail (unless your tests actually achieve 99% coverage)
4. Lower the threshold back to something achievable (e.g. `80`)
5. Push and watch it pass

**Learning:** Coverage thresholds are enforced in CI, not just locally. Setting them appropriately prevents coverage regression.

---

### Exercise 6: Add a Security Audit Step

Add a new job to the CI pipeline that runs `pip-audit`:

```yaml
  security:
    name: Security Audit
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.14'
          cache: pip
      - run: pip install pip-audit
      - run: pip-audit -r requirements.txt
        # Fails if any dependency has a known CVE
```

**Challenge:** Add `continue-on-error: true` to the audit step and observe how the job reports a warning instead of a failure. When would you use this vs. hard failing?

---

### Exercise 7: Implement Concurrency Control

Add concurrency control to prevent overlapping CI runs on the same PR:

```yaml
concurrency:
  group: ci-${{ github.event.pull_request.number || github.ref }}
  cancel-in-progress: true
```

Test it by:
1. Opening a PR
2. Pushing two commits in quick succession
3. Observing that the first CI run is cancelled and only the second completes

**Learning:** Concurrency control saves CI minutes and reduces noise from outdated runs.

---

### Exercise 8: Create a Workflow Status Badge

Add a status badge to the project README:

```markdown
![CI](https://github.com/YOUR_USERNAME/YOUR_REPO/actions/workflows/ci.yml/badge.svg)
```

When the CI pipeline is green, the badge shows green. When it's failing, it shows red. This provides at-a-glance pipeline health visibility from the repository homepage.

---

## Summary

In this module, you've learned:

- **What CI is** and why it's fundamental to modern software development
- **The difference between CI, CD (Delivery), and CD (Deployment)** and when to use each
- **How to structure a multi-stage CI pipeline** with proper job dependencies
- **Dependency caching** with `actions/cache@v4` and why cache key strategy matters
- **Running tests in GitHub Actions** and how exit codes drive job success/failure
- **Code coverage generation** and enforcement through thresholds
- **PR status checks** and how to configure required checks in branch protection rules
- **CI best practices**: speed, caching, fail-fast, security, and maintainability

In **Module 09**, we'll take the artifacts produced by this CI pipeline and build the CD pipeline that deploys them to staging and production environments with approval gates and rollback capabilities.

---

## References

- ⚡ **About Continuous Integration** — [docs.github.com/en/actions/automating-builds-and-tests/about-continuous-integration](https://docs.github.com/en/actions/automating-builds-and-tests/about-continuous-integration)
- 💾 **Caching Dependencies to Speed Up Workflows** — [docs.github.com/en/actions/using-workflows/caching-dependencies-to-speed-up-workflows](https://docs.github.com/en/actions/using-workflows/caching-dependencies-to-speed-up-workflows)
- 💾 **actions/cache** — [github.com/actions/cache](https://github.com/actions/cache)
- 🐍 **actions/setup-python** — [github.com/actions/setup-python](https://github.com/actions/setup-python)
- 🧪 **pytest Documentation** — [docs.pytest.org](https://docs.pytest.org/en/latest/)
- 📊 **pytest-cov** (Coverage Plugin) — [pytest-cov.readthedocs.io](https://pytest-cov.readthedocs.io/en/latest/)
- 📐 **Flake8** (Python Linter) — [flake8.pycqa.org](https://flake8.pycqa.org/en/latest/)
- 🔍 **pip-audit** (Dependency Vulnerability Scanner) — [pypi.org/project/pip-audit](https://pypi.org/project/pip-audit/)
- 📈 **Codecov** (Coverage Reporting Service) — [about.codecov.io](https://about.codecov.io/)
- 🌐 **Flask** (Python Web Framework) — [flask.palletsprojects.com](https://flask.palletsprojects.com/)
- 🔒 **Branch Protection Rules** — [docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)

---

*Module 08 of the GitHub Actions Master Class*
*Next: [Module 09: Continuous Deployment (CD)](../module-09-cd-pipeline/README.md)*
