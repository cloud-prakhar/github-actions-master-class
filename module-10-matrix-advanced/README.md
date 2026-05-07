# Module 10: Matrix Builds & Advanced Features
## Project 8: Cross-Platform Matrix Build

---

## Overview

Welcome to Module 10! This is where GitHub Actions starts to feel genuinely powerful. Up until now, our workflows have run single jobs on a single operating system with a single configuration. In real-world software development, you often need to verify that your code works across many environments — different operating systems, different language runtime versions, different dependency combinations.

Matrix builds solve this problem elegantly. Instead of writing duplicate jobs for each configuration, you declare a matrix of dimensions and GitHub Actions automatically generates and runs all the combinations in parallel. In this module, we also cover several advanced features: concurrency control, container jobs, service containers (like databases), job summaries, and workflow commands.

---

## Learning Objectives

By the end of this module, you will be able to:

1. **Use matrix strategy** to build and test across multiple configurations in parallel
2. **Build on multiple operating systems and runtime versions** simultaneously
3. **Include and exclude** specific matrix combinations to handle edge cases
4. **Understand and configure concurrency groups** to prevent race conditions
5. **Run jobs inside Docker containers** for reproducible environments
6. **Use service containers** to spin up databases and caches for integration tests
7. **Write rich job summaries** visible in the GitHub Actions UI
8. **Use workflow commands** to set outputs, mask secrets, and emit annotations

---

## Table of Contents

1. [Matrix Strategy — The Basics](#1-matrix-strategy--the-basics)
2. [Multi-Dimensional Matrix](#2-multi-dimensional-matrix)
3. [Include and Exclude](#3-include-and-exclude)
4. [Fail-Fast and Max-Parallel](#4-fail-fast-and-max-parallel)
5. [Concurrency Groups](#5-concurrency-groups)
6. [Container Jobs](#6-container-jobs)
7. [Service Containers](#7-service-containers)
8. [Job Summaries](#8-job-summaries)
9. [Workflow Commands](#9-workflow-commands)
10. [Project Walkthrough](#10-project-walkthrough)
11. [Exercises](#11-exercises)

---

## 1. Matrix Strategy — The Basics

### What Problem Does Matrix Solve?

Imagine you maintain a Python library. Your users might be running Python 3.12, 3.13, or 3.14. On Ubuntu, Windows, or macOS. That is potentially 3 × 3 = 9 different environments where your library must work correctly.

Without matrix builds, you would write nine separate jobs or nine separate workflow files — a maintenance nightmare. If you want to add one more step (say, running `pip-audit`), you would need to add it in nine places.

With matrix builds, you declare the dimensions once, and GitHub Actions creates all the job instances automatically. Adding a new step means editing one place.

### Basic Matrix Syntax

The `strategy.matrix` keyword accepts an object where each key becomes a variable you can reference in your job:

```yaml
jobs:
  build:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        python-version: ['3.12', '3.13', '3.14']
    steps:
      - name: Print environment info
        run: |
          echo "Running on ${{ matrix.os }}"
          echo "Python version: ${{ matrix.python-version }}"
```

This single job definition generates **9 parallel jobs**:

| Job # | os              | python-version |
|-------|-----------------|----------------|
| 1     | ubuntu-latest   | 3.12           |
| 2     | ubuntu-latest   | 3.13           |
| 3     | ubuntu-latest   | 3.14           |
| 4     | windows-latest  | 3.12           |
| 5     | windows-latest  | 3.13           |
| 6     | windows-latest  | 3.14           |
| 7     | macos-latest    | 3.12           |
| 8     | macos-latest    | 3.13           |
| 9     | macos-latest    | 3.14           |

### Accessing Matrix Values

Within the job, you access matrix variables using the expression syntax:

```yaml
${{ matrix.os }}             # The current OS value
${{ matrix.python-version }} # The current Python version
```

These expressions work anywhere in the job definition — in `runs-on`, in step `run` commands, in `env` values, in `if` conditions, etc.

### Matrix with a Single Dimension

A matrix does not have to be multi-dimensional. A single-dimension matrix is still very useful:

```yaml
strategy:
  matrix:
    python-version: ['3.11', '3.12', '3.13', '3.14']
```

This creates 4 jobs, one for each version. You might use this to test a library against multiple runtime versions on a single operating system.

---

## 2. Multi-Dimensional Matrix

### How Combinations Are Generated

When you specify multiple dimensions, GitHub Actions computes the **Cartesian product** — every possible combination of values across all dimensions.

```yaml
strategy:
  matrix:
    os: [ubuntu-latest, windows-latest]
    python-version: ['3.13', '3.14']
    database: [postgres, mysql]
```

This generates 2 × 2 × 2 = **8 jobs**:
- ubuntu + python 3.13 + postgres
- ubuntu + python 3.13 + mysql
- ubuntu + python 3.14 + postgres
- ubuntu + python 3.14 + mysql
- windows + python 3.13 + postgres
- windows + python 3.13 + mysql
- windows + python 3.14 + postgres
- windows + python 3.14 + mysql

### Practical Example: Python Library Testing

Here is a realistic multi-dimensional matrix for a Python library:

```yaml
jobs:
  test:
    name: Test on ${{ matrix.os }} / Python ${{ matrix.python-version }}
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        python-version: ['3.12', '3.13', '3.14']
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
          cache: 'pip'
      - run: pip install -r requirements.txt -r requirements-dev.txt
      - run: pytest tests/
        env:
          PYTHONPATH: src
```

### Job Naming in Matrix Builds

By default, GitHub Actions names matrix jobs using the matrix values. You can customize this with the `name` field on the job:

```yaml
jobs:
  test:
    name: "Test (${{ matrix.os }}, Python ${{ matrix.python-version }})"
```

This produces clear, readable job names in the GitHub Actions UI like "Test (ubuntu-latest, Python 3.14)".

---

## 3. Include and Exclude

The basic matrix generates all combinations, but real-world needs are rarely perfectly uniform. Some combinations require special handling; others don't make sense at all.

### The `exclude` Keyword

Use `exclude` to remove specific combinations from the matrix. Each item in the exclude list is a partial match — any job where all specified properties match will be removed.

```yaml
strategy:
  matrix:
    os: [ubuntu-latest, windows-latest, macos-latest]
    python-version: ['3.12', '3.13', '3.14']
    exclude:
      # Windows + Python 3.12 has a known compatibility issue, skip it
      - os: windows-latest
        python-version: '3.12'
      # macOS + Python 3.14 not yet stable in our support matrix
      - os: macos-latest
        python-version: '3.14'
```

This reduces the original 9 combinations to 7.

**Important**: Exclude entries are matched by property values. If you specify multiple properties in an exclude entry, ALL of them must match for the job to be excluded.

### The `include` Keyword

The `include` keyword has two distinct use cases:

**Use Case 1: Add extra properties to existing combinations**

You can add additional configuration variables to specific existing combinations:

```yaml
strategy:
  matrix:
    os: [ubuntu-latest, windows-latest, macos-latest]
    python-version: ['3.12', '3.13', '3.14']
    include:
      # Add an extra property to the Windows + Python 3.14 combination
      - os: windows-latest
        python-version: '3.14'
        pip-command: "pip.exe"  # Windows may need explicit .exe extension
      # All other combinations get the default
      - os: ubuntu-latest
        pip-command: "pip"
      - os: macos-latest
        pip-command: "pip"
```

Then in your steps, you can use `${{ matrix.pip-command }}` and it resolves to the right value per OS.

**Use Case 2: Add entirely new combinations**

If an `include` entry does not match any existing combination, it is added as a new job:

```yaml
strategy:
  matrix:
    os: [ubuntu-latest, windows-latest]
    python-version: ['3.12', '3.13']
    include:
      # Add an extra combination not in the original matrix
      - os: ubuntu-latest
        python-version: '3.14'
        experimental: true
```

This adds a 5th job (ubuntu + Python 3.14, marked as experimental) to the original 4.

### Practical Example: Platform-Specific Commands

A common use case is handling platform differences:

```yaml
strategy:
  matrix:
    include:
      - os: ubuntu-latest
        python-version: '3.14'
        shell: bash
        path-separator: "/"
      - os: windows-latest
        python-version: '3.14'
        shell: pwsh
        path-separator: "\\"
      - os: macos-latest
        python-version: '3.14'
        shell: bash
        path-separator: "/"
```

### Order of Operations: include vs exclude

GitHub Actions processes the matrix in this order:

1. Generate all combinations from the base matrix
2. Apply `exclude` to remove unwanted combinations
3. Apply `include` to add extra properties or new entries

Understanding this order helps predict the final set of jobs.

---

## 4. Fail-Fast and Max-Parallel

### Fail-Fast Behavior

By default, `fail-fast` is `true`. This means: if any job in the matrix fails, GitHub Actions immediately cancels all remaining in-progress jobs in that matrix.

```yaml
strategy:
  fail-fast: true  # Default: cancel all jobs when one fails
  matrix:
    os: [ubuntu-latest, windows-latest, macos-latest]
    python-version: ['3.12', '3.13', '3.14']
```

**When `fail-fast: true` is appropriate:**
- During development when you want fast feedback — no point running 8 more jobs if the first one reveals a fundamental problem
- When CI minutes are expensive and you want to stop burning resources on a broken build
- In deployment pipelines where one failure should block the rest

**When `fail-fast: false` is better:**
- When you want to see ALL failures across all configurations, not just the first one
- When debugging cross-platform issues — you need to know which platforms fail and which succeed
- For compatibility matrices where partial success is meaningful information

```yaml
strategy:
  fail-fast: false  # Let all matrix jobs run even if some fail
  matrix:
    os: [ubuntu-latest, windows-latest, macos-latest]
    python-version: ['3.12', '3.13', '3.14']
```

### Max-Parallel

By default, GitHub Actions runs as many matrix jobs in parallel as your runner limits allow. Use `max-parallel` to limit concurrency:

```yaml
strategy:
  max-parallel: 4
  matrix:
    os: [ubuntu-latest, windows-latest, macos-latest]
    python-version: ['3.12', '3.13', '3.14']
```

With 9 total combinations and `max-parallel: 4`, at most 4 jobs run simultaneously. When one finishes, the next queued job starts.

**When to use max-parallel:**
- **Rate limiting**: Your external API or service can only handle N concurrent connections
- **Cost control**: macOS runners are expensive; limit parallel macOS jobs
- **Shared resources**: Avoid overwhelming a shared database or cache

---

## 5. Concurrency Groups

### The Problem: Race Conditions in CI/CD

Without concurrency control, multiple workflow runs can execute simultaneously. This creates problems:

- Two PRs both deploy to staging at the same time — they overwrite each other
- A developer pushes three commits in quick succession — three separate CI runs start, consuming 3× the resources
- A deployment workflow starts while a previous deployment is still running — the environment ends up in an unknown state

### Concurrency Groups

The `concurrency` keyword lets you define a group. Only one workflow run in a group can be active at a time:

```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```

**How it works:**
- `group`: A string that identifies the concurrency group. Runs with the same group string are serialized.
- `cancel-in-progress: true`: When a new run starts and finds an existing run in the same group, it cancels the existing run.
- `cancel-in-progress: false`: The new run waits until the existing run completes.

### Common Concurrency Patterns

**Pattern 1: Per-PR concurrency (most common)**
```yaml
concurrency:
  group: pr-${{ github.event.pull_request.number }}
  cancel-in-progress: true
```
Each PR gets its own group. When you push a new commit to a PR, the previous CI run is cancelled.

**Pattern 2: Per-branch concurrency**
```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```
Each branch gets its own group. Pushing to `feature/xyz` cancels any in-progress run for `feature/xyz`.

**Pattern 3: Deployment protection (don't cancel in-progress)**
```yaml
concurrency:
  group: deploy-production
  cancel-in-progress: false  # Wait, don't cancel
```
Only one production deployment runs at a time. The next deployment queues up and waits.

**Pattern 4: Workflow-level vs job-level**

Concurrency can be set at the workflow level (applies to the entire workflow) or at the job level (applies only to that job):

```yaml
jobs:
  deploy:
    concurrency:
      group: deploy-${{ github.ref }}
      cancel-in-progress: false
```

### Dynamic Group Names

Group names are expressions, so you can make them dynamic:

```yaml
concurrency:
  # Use workflow name + PR number for PRs, workflow name + branch for pushes
  group: ${{ github.workflow }}-${{ github.event.pull_request.number || github.ref }}
  cancel-in-progress: true
```

The `||` operator here is a logical OR. If `github.event.pull_request.number` is set (we're in a PR), use that; otherwise fall back to `github.ref`.

---

## 6. Container Jobs

### What Are Container Jobs?

By default, your job steps run directly on the GitHub-hosted runner (a virtual machine). Container jobs run your steps inside a Docker container on that VM instead.

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    container:
      image: python:3.14-slim
    steps:
      - uses: actions/checkout@v4
      - run: python --version  # Runs inside the container
```

### Benefits of Container Jobs

1. **Reproducibility**: Pin to an exact Docker image digest for 100% reproducible environments
2. **Consistency**: Match your local development Docker setup exactly
3. **Tooling**: Use specialized images pre-loaded with all your build tools
4. **Isolation**: Dependencies in the container don't conflict with the runner's software

### Container Configuration Options

The `container` keyword accepts several options:

```yaml
container:
  image: postgres:15-alpine          # Required: the Docker image
  credentials:                       # For private registries
    username: ${{ secrets.DOCKER_USERNAME }}
    password: ${{ secrets.DOCKER_PASSWORD }}
  env:                               # Environment variables for the container
    POSTGRES_PASSWORD: mysecret
  ports:                             # Expose container ports to the host
    - 5432
  volumes:                           # Mount volumes
    - /tmp/cache:/app/.cache
  options: --cpus 1                  # Additional docker run options
```

### Container Networking

When you use container jobs, GitHub Actions creates a Docker network. The job container and any service containers (covered next) are all on this network and can communicate with each other by service name.

### When to Use Container Jobs

- Your project requires specific system libraries not available on the runner
- You want to mirror your production Docker environment exactly
- Your build system requires a specific OS version or distribution
- You use a language not pre-installed on GitHub-hosted runners

---

## 7. Service Containers

### What Are Service Containers?

Service containers run alongside your job as sidecar containers — they are separate Docker containers that provide services your tests depend on. The most common use case is running a database for integration tests.

```yaml
jobs:
  integration-test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: testpassword
          POSTGRES_DB: testdb
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
```

### How Service Containers Work

1. GitHub Actions starts the service containers before the job steps begin
2. They run in the same Docker network as the job
3. Your steps can connect to them via `localhost` and the mapped port
4. They are automatically stopped and removed after the job completes

### The `services` Keyword Structure

```yaml
services:
  <service-name>:          # Arbitrary name, used as the hostname in container networking
    image: <docker-image>
    env:
      KEY: VALUE
    ports:
      - <host-port>:<container-port>
    options: >-            # Additional docker run flags
      --health-cmd ...
      --health-interval ...
      --health-timeout ...
      --health-retries ...
```

### Health Checks — Waiting for Services to Be Ready

Databases take time to start. Without health checks, your tests might fail because they try to connect before the database is ready.

Health check options for Docker:
- `--health-cmd`: Command to test if the service is healthy. Exit 0 = healthy, non-zero = unhealthy.
- `--health-interval`: How often to run the health check
- `--health-timeout`: Maximum time for a single health check to run
- `--health-retries`: Number of consecutive failures before declaring unhealthy

GitHub Actions waits for the service to become healthy before starting job steps, so you don't need to add sleep commands.

**PostgreSQL health check:**
```yaml
options: >-
  --health-cmd pg_isready
  --health-interval 10s
  --health-timeout 5s
  --health-retries 5
```

**MySQL health check:**
```yaml
options: >-
  --health-cmd "mysqladmin ping"
  --health-interval 10s
  --health-timeout 5s
  --health-retries 10
```

**Redis health check:**
```yaml
options: >-
  --health-cmd "redis-cli ping"
  --health-interval 5s
  --health-timeout 3s
  --health-retries 5
```

### Connecting to Services from Steps

If your job steps run directly on the runner (no container job), connect via `localhost` and the mapped host port:

```yaml
- name: Test database connection
  run: |
    # The port mapping 5432:5432 makes postgres available on localhost:5432
    psql -h localhost -p 5432 -U postgres -c "SELECT 1"
  env:
    PGPASSWORD: testpassword
```

If your job steps run inside a container, use the service name as the hostname:

```yaml
- name: Test database connection
  run: |
    # In a container job, use the service name "postgres" as hostname
    psql -h postgres -p 5432 -U postgres -c "SELECT 1"
```

### Common Service Container Patterns

**PostgreSQL for integration tests:**
```yaml
services:
  postgres:
    image: postgres:15-alpine
    env:
      POSTGRES_USER: testuser
      POSTGRES_PASSWORD: testpassword
      POSTGRES_DB: testdb
    ports:
      - 5432:5432
    options: >-
      --health-cmd pg_isready
      --health-interval 10s
      --health-timeout 5s
      --health-retries 5
```

**Redis for cache testing:**
```yaml
services:
  redis:
    image: redis:7-alpine
    ports:
      - 6379:6379
    options: >-
      --health-cmd "redis-cli ping"
      --health-interval 5s
      --health-timeout 3s
      --health-retries 5
```

**MongoDB:**
```yaml
services:
  mongodb:
    image: mongo:6
    env:
      MONGO_INITDB_ROOT_USERNAME: root
      MONGO_INITDB_ROOT_PASSWORD: secret
    ports:
      - 27017:27017
```

---

## 8. Job Summaries

### What Are Job Summaries?

GitHub Actions lets you write Markdown content that appears in the Actions UI as a formatted summary. This is a powerful way to present test results, build information, coverage reports, or any data from your workflow in a human-readable format.

### Writing to the Summary

Job summaries use the `GITHUB_STEP_SUMMARY` environment variable, which points to a file. Anything you write (append) to that file appears as Markdown in the GitHub Actions summary panel.

```yaml
- name: Write summary
  run: |
    echo "## Build Results" >> $GITHUB_STEP_SUMMARY
    echo "" >> $GITHUB_STEP_SUMMARY
    echo "| Property | Value |" >> $GITHUB_STEP_SUMMARY
    echo "|----------|-------|" >> $GITHUB_STEP_SUMMARY
    echo "| Python Version | ${{ matrix.python-version }} |" >> $GITHUB_STEP_SUMMARY
    echo "| OS | ${{ matrix.os }} |" >> $GITHUB_STEP_SUMMARY
    echo "| Status | :white_check_mark: Passed |" >> $GITHUB_STEP_SUMMARY
```

### Supported Markdown in Summaries

Job summaries support a subset of GitHub-Flavored Markdown:
- Headers (# through ######)
- Bold, italic, strikethrough
- Unordered and ordered lists
- Tables
- Code blocks (inline and fenced)
- Links
- Blockquotes
- Task lists
- Emoji shortcodes (`:white_check_mark:`)

### Summary Limitations

- Maximum 1 MB per step
- Maximum 20 MB per job
- Content is stored per-job (not shared between jobs)

### Clearing the Summary

To replace (rather than append to) the summary, use `>` instead of `>>`:

```yaml
- name: Clear and rewrite summary
  run: |
    echo "# Fresh Summary" > $GITHUB_STEP_SUMMARY  # Overwrites
```

### Multi-line Summary with Heredoc

For cleaner multi-line summaries, use a heredoc:

```yaml
- name: Write detailed summary
  run: |
    cat >> $GITHUB_STEP_SUMMARY << 'EOF'
    ## Test Results

    | Suite      | Tests | Passed | Failed |
    |------------|-------|--------|--------|
    | Unit       | 45    | 45     | 0      |
    | Integration| 12    | 12     | 0      |

    All tests passed! :rocket:
    EOF
```

---

## 9. Workflow Commands

### What Are Workflow Commands?

Workflow commands are special `echo` statements that GitHub Actions intercepts to perform special actions. They follow this format:

```
::command-name param1=value1,param2=value2::message
```

### Setting Environment Variables (GITHUB_ENV)

Instead of the deprecated `set-output` and `::set-env::` commands, use the file-based approach:

```yaml
- name: Set environment variable
  run: |
    echo "MY_VAR=hello world" >> $GITHUB_ENV
    echo "TIMESTAMP=$(date -u +%Y%m%d%H%M%S)" >> $GITHUB_ENV

- name: Use the variable
  run: |
    echo "MY_VAR is: $MY_VAR"
    echo "TIMESTAMP is: $TIMESTAMP"
```

### Setting Step Outputs (GITHUB_OUTPUT)

```yaml
- name: Set step output
  id: my-step
  run: |
    echo "version=1.2.3" >> $GITHUB_OUTPUT
    echo "sha=$(git rev-parse --short HEAD)" >> $GITHUB_OUTPUT

- name: Use step output
  run: |
    echo "Version: ${{ steps.my-step.outputs.version }}"
    echo "SHA: ${{ steps.my-step.outputs.sha }}"
```

### Masking Values

Use `add-mask` to prevent a value from appearing in logs:

```yaml
- name: Mask sensitive value
  run: |
    MY_SECRET="super-secret-value"
    echo "::add-mask::$MY_SECRET"
    echo "This will be redacted: $MY_SECRET"  # Shows *** in logs
```

Any subsequent appearance of that value in logs will be replaced with `***`.

### Annotations: Notice, Warning, Error

Annotations appear in the workflow summary and in pull request file diffs:

```yaml
- name: Emit annotations
  run: |
    # Simple annotations
    echo "::notice::This is an informational notice"
    echo "::warning::This might be a problem"
    echo "::error::This is a critical error"

    # Annotations linked to a file/line
    echo "::warning file=src/app.py,line=23,col=4::Deprecated function used"
    echo "::error file=tests/test_app.py,line=45::Assertion failed"
```

**Annotation parameters:**
- `file`: The relative file path
- `line`: Starting line number
- `endLine`: Ending line number
- `col`: Starting column
- `endColumn`: Ending column
- `title`: Title for the annotation

### Adding to PATH (GITHUB_PATH)

```yaml
- name: Add to PATH
  run: |
    echo "/opt/my-tool/bin" >> $GITHUB_PATH

- name: Use the tool
  run: my-tool --version  # Works because /opt/my-tool/bin is in PATH
```

### Debug Logging

```yaml
- name: Debug output
  run: |
    echo "::debug::This only appears when debug logging is enabled"
```

Debug messages appear only when the secret `ACTIONS_STEP_DEBUG` is set to `true`.

### Grouping Log Output

```yaml
- name: Grouped output
  run: |
    echo "::group::Dependency installation"
    pip install -r requirements.txt -r requirements-dev.txt
    echo "::endgroup::"

    echo "::group::Running tests"
    pytest tests/ -v
    echo "::endgroup::"
```

This creates collapsible sections in the GitHub Actions log viewer.

---

## 10. Project Walkthrough

### Files in This Module

```
module-10-matrix-advanced/
├── README.md                    ← This file
└── project/
    └── .github/
        └── workflows/
            ├── matrix-build.yml       ← Matrix strategy demo
            ├── service-containers.yml ← Service containers demo
            └── job-summaries.yml      ← Summaries and commands demo
```

### matrix-build.yml

This workflow demonstrates the core matrix build feature:

- **Trigger**: push and pull_request to any branch
- **Matrix**: os × python-version with includes and excludes
- **Demonstrates**: fail-fast, max-parallel, matrix variable access, step summaries

Key things to observe:
1. How the `name` field uses matrix variables for clear job identification
2. The `exclude` removes the windows + Python 3.12 combination
3. The `include` adds a special property for Windows
4. How `GITHUB_STEP_SUMMARY` produces a formatted report

### service-containers.yml

This workflow demonstrates running PostgreSQL and Redis as service containers:

- **PostgreSQL**: Shows health checks, port mapping, and connection testing
- **Redis**: Shows a simpler service without health check complexity
- **Key insight**: Steps run on the runner (`localhost`), not inside a container

### job-summaries.yml

This workflow focuses on GitHub Actions communication mechanisms:

- **GITHUB_STEP_SUMMARY**: Writes a formatted Markdown report
- **Workflow commands**: Notice, warning, and error annotations
- **Masking**: Prevents sensitive values from appearing in logs
- **GITHUB_PATH**: Dynamically extends the PATH

---

## 11. Exercises

### Exercise 1: Extend the Matrix

Open `matrix-build.yml` and add a fourth dimension to the matrix: `experimental: [true, false]`. Only run the experimental=true variant on ubuntu-latest. Use `fail-fast: false` to ensure all combinations run even if the experimental ones fail.

**Hint**: Use the `include` keyword to add the `experimental` property to specific combinations.

### Exercise 2: Service Container Integration Test

Create a new workflow file `integration-tests.yml` that:
1. Spins up a PostgreSQL service container
2. Installs the `psql` client
3. Creates a table and inserts a row
4. Queries the table and verifies the result
5. Writes a test report to `GITHUB_STEP_SUMMARY`

### Exercise 3: Annotation System

Extend `job-summaries.yml` to:
1. Simulate a linting run that produces a warning for a specific file
2. Use `::warning file=src/app.py,line=10::` to annotate the file
3. Conditionally emit an `::error::` if a simulated test count is below a threshold
4. Use the `::group::` command to organize your log output

### Exercise 4: Concurrency Experiment

Create a workflow that:
1. Uses `workflow_dispatch` trigger
2. Configures concurrency with `cancel-in-progress: true`
3. Includes a `sleep 30` step (simulates long work)
4. Trigger it twice in quick succession from the GitHub UI
5. Observe that the first run is cancelled

**Learning goal**: Understand the visual feedback in the GitHub Actions UI when cancellation occurs.

### Exercise 5: Matrix with Conditional Steps

Create a matrix workflow across Ubuntu and Windows where:
1. On Ubuntu, steps use `bash` shell
2. On Windows, steps use `pwsh` shell
3. Use the `include` keyword to add a `shell` matrix variable
4. Use that variable in a `shell:` property on steps

**Hint**: You can set the `shell` for individual steps or use a default-shell approach.

---

## Key Takeaways

1. **Matrix builds** eliminate duplicated job definitions — declare once, run many times
2. **Include/exclude** give you fine-grained control over which combinations run
3. **Fail-fast** and **max-parallel** balance speed vs. completeness and resource usage
4. **Concurrency groups** prevent race conditions in deployments
5. **Container jobs** provide reproducible, isolated build environments
6. **Service containers** make database/cache integration testing easy
7. **Job summaries** create rich, readable reports directly in the GitHub Actions UI
8. **Workflow commands** are the bridge between your scripts and the GitHub Actions runtime

---

## Resources

- [GitHub Docs: Using a matrix for your jobs](https://docs.github.com/en/actions/using-jobs/using-a-matrix-for-your-jobs)
- [GitHub Docs: Using concurrency](https://docs.github.com/en/actions/using-jobs/using-concurrency)
- [GitHub Docs: Running jobs in a container](https://docs.github.com/en/actions/using-jobs/running-jobs-in-a-container)
- [GitHub Docs: About service containers](https://docs.github.com/en/actions/using-containerized-services/about-service-containers)
- [GitHub Docs: Workflow commands](https://docs.github.com/en/actions/using-workflows/workflow-commands-for-github-actions)
- [GitHub Docs: Adding a job summary](https://docs.github.com/en/actions/using-workflows/workflow-commands-for-github-actions#adding-a-job-summary)

---

*Next up: Module 11 — Reusable Workflows & Composite Actions*
