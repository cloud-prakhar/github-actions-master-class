# Module 05: Jobs & Steps Deep Dive

**Difficulty:** Intermediate | **Time:** 2-3 hours | **Prev:** [Module 04](../module-04-workflow-triggers/README.md) | **Next:** [Module 06 — Secrets & Variables](../module-06-secrets-variables/README.md)

## Project 3: Multi-Job Pipeline

---

## Learning Objectives

By the end of this module you will:
- Understand all job-level configuration options
- Know every type of step and when to use each
- Set and consume step outputs via `$GITHUB_OUTPUT`
- Write conditional steps using `if:` with status functions
- Use environment variables at workflow, job, and step levels
- Configure multiple shells (bash, python, shell)
- Handle failures gracefully with `continue-on-error` and `always()`

---

## 1. Job Anatomy

```yaml
jobs:
  my-job:                          # Job ID (unique, hyphens OK)
    name: Human-readable Name     # optional display name
    runs-on: ubuntu-latest        # REQUIRED: which runner
    needs: [previous-job]         # optional: dependencies
    if: github.ref == 'refs/heads/main'  # optional: condition
    timeout-minutes: 30           # optional: max runtime
    continue-on-error: false      # optional: allow failure?
    concurrency:                  # optional: job-level concurrency
      group: deploy-${{ github.ref }}
      cancel-in-progress: false
    env:                          # optional: job-level env vars
      APP_ENV: production
    outputs:                      # optional: values to pass downstream
      version: ${{ steps.ver.outputs.value }}
    steps:
      - ...
```

### Runner Options

| `runs-on` value | OS | Architecture | Notes |
|---|---|---|---|
| `ubuntu-latest` | Ubuntu Linux | x64 | Fastest, cheapest, most common |
| `ubuntu-24.04` | Ubuntu 24.04 | x64 | Specific LTS version |
| `ubuntu-22.04` | Ubuntu 22.04 | x64 | Previous LTS |
| `windows-latest` | Windows Server | x64 | Slower startup |
| `macos-latest` | macOS | arm64 (M-series) | Most expensive |
| `macos-13` | macOS 13 | x64 | Intel Mac |
| `self-hosted` | Your machine | Any | You manage the runner |

---

## 2. Step Types

### Type A: Action Step (`uses:`)

Runs a pre-built action. The action can be from:
- GitHub Marketplace: `actions/checkout@v4`
- Same repo: `./.github/actions/my-action`
- Another repo: `owner/repo@v2`

```yaml
- name: Checkout
  uses: actions/checkout@v4
  with:               # inputs to the action (from the action's README)
    fetch-depth: 0
    token: ${{ secrets.GITHUB_TOKEN }}
```

### Type B: Shell Command (`run:`)

Executes shell commands directly on the runner.

```yaml
# Single command
- name: Install packages
  run: pip install -r requirements.txt

# Multi-line script (use | literal block scalar)
- name: Build and test
  run: |
    pip install -r requirements.txt
    python -m flake8 src/
    pytest tests/ -v

# Specific shell (override the default)
- name: Python script
  shell: python
  run: |
    import sys
    import os
    print(f"Python {sys.version}")
    print(f"Platform: {sys.platform}")
```

### Shell Options

| `shell` value | Interpreter | OS |
|---|---|---|
| `bash` (default on Linux/macOS) | Bash | Linux, macOS |
| `sh` | POSIX sh | Linux, macOS |
| `python` | Python | Any (if installed) |
| `pwsh` | PowerShell Core | Any |
| `powershell` | Windows PowerShell | Windows only |
| `cmd` | Command Prompt | Windows only |

---

## 3. Step Configuration Keys

```yaml
steps:
  - name: My Step              # display name (optional but helpful)
    id: my-step                # reference ID (optional, needed for outputs)
    uses: some/action@v1       # action (OR use run:, not both)
    run: echo "hello"          # shell command (OR use uses:, not both)
    with:                      # action inputs (only with uses:)
      key: value
    env:                       # step-level environment variables
      MY_VAR: my-value
    if: success()              # condition (optional)
    continue-on-error: false   # don't fail job if step fails (optional)
    timeout-minutes: 5         # max time for this step (optional)
    working-directory: ./src   # run from this path (optional)
    shell: bash                # override default shell (optional)
```

---

## 4. Step Outputs

Steps can produce named outputs that later steps (in the same job) can reference.

### Setting an Output

The mechanism: write `key=value` to the special `$GITHUB_OUTPUT` file.

```yaml
- name: Get version
  id: version          # id is REQUIRED to reference this step's outputs
  run: |
    # Get version from pyproject.toml or any source
    VERSION=$(python -c "import tomllib; print(tomllib.loads(open('pyproject.toml').read())['project']['version'])")
    echo "tag=$VERSION" >> $GITHUB_OUTPUT
    echo "Set version output: $VERSION"
```

### Reading an Output

```yaml
- name: Use the version
  run: |
    echo "Version is: ${{ steps.version.outputs.tag }}"
    echo "Building image: my-app:${{ steps.version.outputs.tag }}"
```

### Multiple Outputs from One Step

```yaml
- id: build-info
  run: |
    echo "timestamp=$(date -u +%Y%m%d%H%M%S)" >> $GITHUB_OUTPUT
    echo "sha=${GITHUB_SHA:0:7}" >> $GITHUB_OUTPUT
    echo "branch=${{ github.ref_name }}" >> $GITHUB_OUTPUT
```

---

## 5. Conditional Steps (`if:`)

The `if:` key on a step (or job) controls whether it runs.

### Common Conditions

```yaml
# Branch conditions
if: github.ref == 'refs/heads/main'
if: github.ref_name == 'main'
if: startsWith(github.ref, 'refs/tags/v')

# Event conditions
if: github.event_name == 'push'
if: github.event_name == 'pull_request'
if: github.event_name != 'schedule'

# Status functions — check the state of the current job
if: success()           # only if all previous steps succeeded (default)
if: failure()           # only if a previous step failed
if: cancelled()         # only if the workflow was cancelled
if: always()            # always run, regardless of previous failures

# Combining conditions
if: github.ref == 'refs/heads/main' && github.event_name == 'push'
if: failure() && github.ref == 'refs/heads/main'

# Input conditions (workflow_dispatch)
if: inputs.environment == 'production'

# Skip CI pattern
if: "!contains(github.event.head_commit.message, '[skip ci]')"

# Check if a previous step succeeded or failed
if: steps.my-step.outcome == 'success'
if: steps.my-step.outcome == 'failure'
```

### Status Functions Explained

| Function | When it's true |
|---|---|
| `success()` | All previous steps succeeded. This is the DEFAULT — steps without `if:` use this implicitly |
| `failure()` | At least one previous step failed |
| `cancelled()` | The workflow was cancelled |
| `always()` | Every situation — success, failure, and cancelled. Use for cleanup steps |

---

## 6. Environment Variables — Precedence

Three levels, each overriding the level above:

```yaml
env:
  COLOR: blue        # Workflow level — available everywhere

jobs:
  build:
    env:
      COLOR: green   # Job level — overrides workflow level for this job

    steps:
      - run: echo $COLOR   # prints: green

      - env:
          COLOR: red       # Step level — overrides job level for this step only
        run: echo $COLOR   # prints: red

      - run: echo $COLOR   # prints: green again (step level expired)
```

### Setting Dynamic Environment Variables

Write to `$GITHUB_ENV` to set variables for **subsequent steps**:

```yaml
- name: Compute values
  run: |
    BUILD_TIME=$(date -u +%Y-%m-%dT%H:%M:%SZ)
    GIT_SHORT_SHA=${GITHUB_SHA:0:7}

    echo "BUILD_TIME=$BUILD_TIME" >> $GITHUB_ENV
    echo "GIT_SHORT_SHA=$GIT_SHORT_SHA" >> $GITHUB_ENV

- name: Use the dynamic values
  run: |
    echo "Built at: $BUILD_TIME"
    echo "Short SHA: $GIT_SHORT_SHA"
```

### Built-in GitHub Environment Variables

| Variable | Value |
|---|---|
| `GITHUB_REPOSITORY` | `owner/repo-name` |
| `GITHUB_SHA` | Full commit SHA |
| `GITHUB_REF` | `refs/heads/main` |
| `GITHUB_REF_NAME` | `main` (branch name) |
| `GITHUB_ACTOR` | Username who triggered |
| `GITHUB_WORKFLOW` | Workflow name |
| `GITHUB_RUN_NUMBER` | Sequential run number |
| `GITHUB_RUN_ID` | Globally unique run ID |
| `GITHUB_WORKSPACE` | `/home/runner/work/repo/repo` |
| `GITHUB_TOKEN` | Auto-created token |
| `RUNNER_OS` | `Linux`, `Windows`, `macOS` |

---

## 7. Handling Failures

### `continue-on-error: true`

Allow a step (or job) to fail without failing the whole job:

```yaml
- name: Optional security scan
  continue-on-error: true    # don't fail the job if this fails
  run: |
    pip install safety
    safety check -r requirements.txt
```

### `if: always()` for Cleanup

Run a step regardless of whether previous steps failed:

```yaml
- name: Run tests
  run: pytest tests/         # might fail

- name: Upload test results
  if: always()               # upload even when tests fail (so we can see what failed)
  uses: actions/upload-artifact@v4
  with:
    name: test-results
    path: test-results.xml

- name: Cleanup temp files
  if: always()               # always clean up
  run: rm -rf /tmp/test-*
```

---

## Project Files

| File | What it teaches |
|---|---|
| [multi-job-pipeline.yml](./project/.github/workflows/multi-job-pipeline.yml) | Parallel jobs, job structure |
| [step-outputs-demo.yml](./project/.github/workflows/step-outputs-demo.yml) | `$GITHUB_OUTPUT`, reading outputs |
| [conditional-steps.yml](./project/.github/workflows/conditional-steps.yml) | `if:` conditions, status functions |

---

## References

- **Workflow syntax: jobs** — search "Workflow syntax jobs GitHub Actions"
- **Workflow syntax: steps** — search "Workflow syntax steps GitHub Actions"
- **Environment variables** — search "Environment variables GitHub Actions"
- **Contexts** — search "Contexts GitHub Actions"

---

## Next Module

**[Module 06 — Secrets, Variables & Environments](../module-06-secrets-variables/README.md)**
