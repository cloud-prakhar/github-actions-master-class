# Module 11: Reusable Workflows & Composite Actions
## Project 9: Shared Workflow Library

---

## Overview

As organizations scale their use of GitHub Actions, a common pain point emerges: teams copy-paste the same workflow patterns across dozens of repositories. When a security best practice changes or a build process is updated, the change must be applied to every copy. This is the antithesis of good software engineering.

Module 11 addresses this with two powerful features: **reusable workflows** and **composite actions**. Together, they let you build a shared library of CI/CD building blocks that can be maintained centrally and consumed across all your repositories.

---

## Learning Objectives

By the end of this module, you will be able to:

1. **Create reusable workflows** using the `workflow_call` trigger
2. **Define inputs, outputs, and secrets** for reusable workflows
3. **Call reusable workflows** from both the same and external repositories
4. **Create composite actions** that encapsulate multi-step logic
5. **Choose between** reusable workflows and composite actions for different scenarios
6. **Understand the limitations** and constraints of each approach
7. **Apply best practices** for versioning, documentation, and security

---

## Table of Contents

1. [Why Reusable Workflows?](#1-why-reusable-workflows)
2. [Creating Reusable Workflows (workflow_call)](#2-creating-reusable-workflows-workflow_call)
3. [Inputs, Outputs, and Secrets](#3-inputs-outputs-and-secrets)
4. [Calling Reusable Workflows](#4-calling-reusable-workflows)
5. [Secrets in Reusable Workflows](#5-secrets-in-reusable-workflows)
6. [Composite Actions](#6-composite-actions)
7. [JavaScript Actions (Introduction)](#7-javascript-actions-introduction)
8. [Docker Actions (Introduction)](#8-docker-actions-introduction)
9. [Publishing Actions to the Marketplace](#9-publishing-actions-to-the-marketplace)
10. [Best Practices](#10-best-practices)
11. [Project Walkthrough](#11-project-walkthrough)
12. [Exercises](#12-exercises)

---

## 1. Why Reusable Workflows?

### The DRY Principle in CI/CD

DRY — "Don't Repeat Yourself" — is a fundamental software engineering principle. In CI/CD, violations of DRY look like:

- Copying `.github/workflows/ci.yml` from one repository to another
- Maintaining 15 copies of "build and push Docker image" workflow logic
- Updating the same Python version in 40 workflow files when support ends

Each copy is a liability. Copies drift apart over time. Security fixes must be applied everywhere. New developers don't know which copy is "the right one."

### Centralized Pipeline Logic

Reusable workflows and composite actions let you centralize your CI/CD logic in one place:

```
org/shared-workflows repository
├── .github/
│   └── workflows/
│       ├── build-and-test.yml      ← Reusable: build + test any Python app
│       ├── docker-publish.yml      ← Reusable: build and push Docker image
│       └── deploy-to-kubernetes.yml ← Reusable: deploy to k8s cluster
└── .github/
    └── actions/
        ├── setup-python-cached/    ← Composite: setup Python with pip caching
        ├── notify-slack/           ← Composite: send Slack notification
        └── git-tag-release/        ← Composite: create and push a release tag
```

Any repository in the organization can reference these:

```yaml
# In any-service/repo/.github/workflows/ci.yml
jobs:
  build:
    uses: org/shared-workflows/.github/workflows/build-and-test.yml@main
    with:
      python-version: '3.14'
```

### Team-Wide Standards Enforcement

When pipelines are centralized, you get:

- **Security**: All repos use the same security scanning — no repo accidentally skips it
- **Consistency**: Every service deploys the same way — no snowflake deployments
- **Upgrades**: Update the runner version once, all repos benefit
- **Compliance**: Audit requirements can be enforced in shared workflows

### Version Control Your Pipelines

Just as you version your application code, reusable workflows are versioned via Git. Reference specific versions:

```yaml
uses: org/shared-workflows/.github/workflows/build.yml@v2.1.0
```

Pin to a stable version, upgrade deliberately. Test pipeline changes in isolation before rolling them out organization-wide.

---

## 2. Creating Reusable Workflows (workflow_call)

### The `workflow_call` Trigger

A reusable workflow is any workflow file that includes `workflow_call` as one of its `on:` triggers:

```yaml
# File: .github/workflows/reusable-build.yml
on:
  workflow_call:
    # Define inputs, outputs, and secrets here
```

That's the only requirement. The `workflow_call` event is triggered when another workflow calls this one using the `uses:` keyword.

### Structure of a Reusable Workflow

```yaml
name: Reusable Build and Test

on:
  workflow_call:
    inputs:
      python-version:
        description: 'Python version to use'
        type: string
        default: '3.14'
        required: false
    outputs:
      artifact-name:
        description: 'Name of the uploaded build artifact'
        value: ${{ jobs.build.outputs.artifact }}
    secrets:
      PYPI_TOKEN:
        description: 'PyPI token for publishing packages'
        required: false

jobs:
  build:
    runs-on: ubuntu-latest
    outputs:
      artifact: ${{ steps.set-artifact.outputs.name }}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ inputs.python-version }}  # Use the input
          cache: pip
      - run: pip install -r requirements.txt -r requirements-dev.txt
      - run: pytest tests/
        env:
          PYTHONPATH: src
```

### Key Differences from Regular Workflows

| Feature | Regular Workflow | Reusable Workflow |
|---------|-----------------|-------------------|
| Trigger | `on: push`, `on: pull_request`, etc. | `on: workflow_call:` |
| How called | Triggered by events | Called from another workflow |
| Context | `github.event.*` from the trigger | Gets the caller's `github` context |
| Inputs | N/A (uses env vars) | Typed inputs with defaults |
| Outputs | Artifacts only | Typed outputs via `outputs:` |

### Accessing Inputs in the Reusable Workflow

Use `${{ inputs.input-name }}` syntax (NOT `github.event.inputs`):

```yaml
steps:
  - uses: actions/setup-python@v5
    with:
      python-version: ${{ inputs.python-version }}
```

---

## 3. Inputs, Outputs, and Secrets

### Input Types

Reusable workflow inputs support four types:

| Type | Description | Example Values |
|------|-------------|----------------|
| `string` | Text value | `'ubuntu-latest'`, `'20'` |
| `number` | Numeric value | `20`, `3.14` |
  | `boolean` | True/false | `true`, `false` |
| `choice` | Enum (one of several values) | `'dev'`, `'staging'`, `'production'` |

```yaml
on:
  workflow_call:
    inputs:
      python-version:
        type: string
        default: '3.14'
        required: false
        description: 'Python version (e.g. 3.12, 3.13, 3.14)'

      run-lint:
        type: boolean
        default: true
        required: false
        description: 'Whether to run the linter'

      environment:
        type: choice
        options:
          - dev
          - staging
          - production
        default: dev
        required: true
        description: 'Target deployment environment'

      max-parallel:
        type: number
        default: 4
        required: false
        description: 'Maximum parallel test runners'
```

### Outputs

Reusable workflow outputs let caller workflows receive data back:

```yaml
on:
  workflow_call:
    outputs:
      version:
        description: 'The semantic version of the build'
        value: ${{ jobs.build.outputs.version }}
      test-result:
        description: 'Overall test result: pass or fail'
        value: ${{ jobs.test.outputs.result }}
```

Outputs reference job outputs, which reference step outputs:

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    outputs:
      version: ${{ steps.get-version.outputs.version }}  # job → step
    steps:
      - name: Get version
        id: get-version
        run: |
          echo "version=$(python -c 'import src.app; print(src.app.__version__)')" >> $GITHUB_OUTPUT
        env:
          PYTHONPATH: src
```

The caller can then access `${{ needs.build-job.outputs.version }}`.

### Secrets

Reusable workflows can declare required or optional secrets:

```yaml
on:
  workflow_call:
    secrets:
      PYPI_TOKEN:
        required: false
        description: 'Token for publishing to PyPI'
      CODECOV_TOKEN:
        required: true
        description: 'Token for uploading coverage to Codecov'
```

Access them in jobs with `${{ secrets.PYPI_TOKEN }}` — the same syntax as regular secrets.

---

## 4. Calling Reusable Workflows

### Same Repository

To call a reusable workflow in the same repository:

```yaml
jobs:
  call-build:
    uses: ./.github/workflows/reusable-build.yml
    with:
      python-version: '3.14'
      run-lint: true
      environment: staging
    secrets:
      PYPI_TOKEN: ${{ secrets.PYPI_TOKEN }}
```

The path `./.github/workflows/reusable-build.yml` is relative to the repository root.

### Different Repository

```yaml
jobs:
  call-build:
    uses: my-org/shared-workflows/.github/workflows/build.yml@main
    with:
      python-version: '3.14'
    secrets:
      PYPI_TOKEN: ${{ secrets.PYPI_TOKEN }}
```

The format is `owner/repo/.github/workflows/file.yml@ref` where `ref` can be:
- A branch name: `@main`, `@develop`
- A tag: `@v2.0.0`
- A commit SHA: `@abc1234`

**Best practice**: Pin to a specific tag or commit SHA for stability in production.

### Jobs After Reusable Workflows

Add jobs that run after a reusable workflow using `needs`:

```yaml
jobs:
  build-and-test:
    uses: ./.github/workflows/reusable-build.yml
    with:
      python-version: '3.14'

  deploy:
    needs: build-and-test   # Wait for the reusable workflow
    runs-on: ubuntu-latest
    steps:
      - name: "Use output from reusable workflow"
        run: |
          echo "Version: ${{ needs.build-and-test.outputs.version }}"
```

### Limitations

- Maximum **4 levels of nesting**: A → B → C → D (no deeper)
- A workflow calling a reusable workflow **cannot also define other jobs** in the same file as the `uses:` job... wait, actually it can. But each `uses:` job must ONLY use the `uses:` keyword — no `steps:` alongside `uses:`.
- Reusable workflows CANNOT call other reusable workflows with `env:` context variables from the caller
- Environment protection rules apply to the reusable workflow's jobs, not the caller's

---

## 5. Secrets in Reusable Workflows

### Explicit Secret Passing

The most secure approach — only pass the secrets the reusable workflow needs:

```yaml
# Caller
jobs:
  call-build:
    uses: ./.github/workflows/reusable-build.yml
    secrets:
      PYPI_TOKEN: ${{ secrets.PYPI_TOKEN }}
      CODECOV_TOKEN: ${{ secrets.CODECOV_TOKEN }}
```

The reusable workflow only receives these two secrets, not all secrets available in the caller.

### Secrets Inheritance (`secrets: inherit`)

Pass ALL secrets from the caller context to the reusable workflow:

```yaml
# Caller
jobs:
  call-build:
    uses: ./.github/workflows/reusable-build.yml
    secrets: inherit
```

The reusable workflow can access any secret available to the caller. This is convenient but less secure — the reusable workflow gains access to secrets it might not need.

### When to Use Each

| Approach | Use When |
|----------|----------|
| Explicit passing | Reusable workflow is in a different (public or shared) repo |
| `secrets: inherit` | Trusted internal workflow, easier to maintain |

### Security Consideration

Reusable workflows run in the context of the CALLER's repository, not the repository where the workflow file lives. This means:
- Permissions are determined by the caller's `permissions:` configuration
- Environment protection rules from the caller apply
- Secrets are from the caller's secrets store

---

## 6. Composite Actions

### What Is a Composite Action?

A composite action is a custom GitHub Action defined in an `action.yml` file that chains together multiple steps — including both `uses:` steps (other actions) and `run:` steps (shell commands). Think of it as a reusable "step group" rather than a reusable "job group."

### Action Structure

```
.github/actions/setup-my-app/
└── action.yml
```

The `action.yml` file is the action's definition:

```yaml
name: 'Setup My Application'
description: 'Installs Python and application dependencies with pip caching'

inputs:
  python-version:
    description: 'Python version to use'
    default: '3.14'
    required: false

outputs:
  cache-hit:
    description: 'Whether the dependency cache was restored'
    value: ${{ steps.cache-deps.outputs.cache-hit }}

runs:
  using: composite   # This declares it as a composite action
  steps:
    - name: Setup Python
      uses: actions/setup-python@v5
      with:
        python-version: ${{ inputs.python-version }}
        cache: 'pip'

    - name: Install dependencies
      shell: bash    # Required for 'run' steps in composite actions
      run: pip install -r requirements.txt -r requirements-dev.txt

    - name: Check cache status
      id: cache-deps
      shell: bash
      run: |
        echo "cache-hit=false" >> $GITHUB_OUTPUT
```

### Key Rules for Composite Actions

1. **`runs.using: composite`** — required to declare it as composite
2. **`shell:` is required** on every `run:` step — composite actions don't inherit a default shell
3. **Can use `uses:` and `run:`** steps, just like a regular workflow job
4. Outputs reference step outputs using `${{ steps.step-id.outputs.key }}`

### Using a Composite Action

Reference it like any other action, using the path to the directory containing `action.yml`:

```yaml
# In any workflow
steps:
  - uses: ./.github/actions/setup-my-app  # Same repo
    with:
      python-version: '3.14'

  # OR from another repo
  - uses: my-org/shared-actions/setup-my-app@v1
    with:
      python-version: '3.14'
```

### Composite Action vs Reusable Workflow

This is the most common source of confusion. Here's when to use each:

| Feature | Composite Action | Reusable Workflow |
|---------|-----------------|-------------------|
| Unit of reuse | A set of steps (part of a job) | An entire job (or multiple jobs) |
| Can have multiple jobs | No — runs within a job | Yes — can define multiple jobs |
| Runs on | Caller's runner | Its own runner(s) |
| Can use matrix | No | Yes |
| Can use services | No (uses caller's services) | Yes |
| Inputs | Yes | Yes |
| Outputs | Yes | Yes |
| Secrets | Accesses caller's secrets | Declared secrets or inherit |
| File location | `action.yml` in a directory | `.github/workflows/*.yml` |

**Rule of thumb**:
- Use a **composite action** when you want to share a group of steps that run as part of a job
- Use a **reusable workflow** when you want to share an entire job or set of jobs

---

## 7. JavaScript Actions (Introduction)

### When to Use JavaScript Actions

JavaScript actions run directly on the runner using Node.js. Use them when:
- You need complex logic that's awkward in shell scripts
- You want to use npm packages (e.g., for GitHub API calls via Octokit)
- You need OS-independent behavior (JavaScript is cross-platform)
- Performance matters — no container startup overhead

### Structure

```
my-action/
├── action.yml
├── index.js     (or index.ts compiled to dist/index.js)
└── package.json
```

```yaml
# action.yml
name: 'My JavaScript Action'
runs:
  using: 'node20'   # Specifies the Node.js version to use
  main: 'dist/index.js'
  post: 'dist/cleanup.js'  # Optional: runs after all steps complete
```

```javascript
// index.js
const core = require('@actions/core');
const github = require('@actions/github');

async function run() {
  try {
    const inputValue = core.getInput('my-input');
    core.setOutput('my-output', `processed: ${inputValue}`);
    core.info('Action completed successfully');
  } catch (error) {
    core.setFailed(error.message);
  }
}

run();
```

### Key packages

- `@actions/core` — inputs, outputs, logging, masking
- `@actions/github` — authenticated GitHub API client
- `@actions/exec` — run commands
- `@actions/io` — file system utilities
- `@actions/tool-cache` — download and cache tools

---

## 8. Docker Actions (Introduction)

### When to Use Docker Actions

Docker actions run in a container. Use them when:
- Your action requires specific OS tools or libraries not in Node.js
- You write in a language other than JavaScript (Python, Go, Ruby)
- You need full control over the execution environment
- The action is computationally intensive and benefits from a custom image

### Structure

```
my-docker-action/
├── action.yml
├── Dockerfile
└── entrypoint.sh
```

```yaml
# action.yml
name: 'My Docker Action'
runs:
  using: 'docker'
  image: 'Dockerfile'
  args:
    - ${{ inputs.my-input }}
```

```dockerfile
FROM alpine:3.18
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
```

### Trade-offs

- Slower than JavaScript actions (container build/pull time)
- Only works on Linux runners (not Windows or macOS)
- More flexible for complex tooling requirements

---

## 9. Publishing Actions to the Marketplace

### Repository Requirements

To publish an action to the GitHub Actions Marketplace:

1. **Public repository** — the action must be in a public repo
2. **`action.yml` in the root** — not in a subdirectory
3. **README.md** — explains usage, inputs, outputs, examples
4. **Semantic versioning tags** — `v1.0.0`, `v1.0.1`, `v2.0.0`

### action.yml Metadata for Marketplace

```yaml
name: 'My Awesome Action'
description: 'One-line description shown in the Marketplace'
author: 'Your Name or Organization'

branding:
  icon: 'rocket'        # Feather icon name
  color: 'blue'         # blue, green, orange, purple, red, white, yellow, gray-dark

inputs:
  my-input:
    description: 'Explain what this input does'
    required: true

outputs:
  my-output:
    description: 'Explain what this output contains'

runs:
  using: 'node20'
  main: 'dist/index.js'
```

### Versioning Strategy

GitHub recommends the "moving major tag" pattern:
- Tag `v1.0.0` for each exact release
- Move a `v1` tag to always point to the latest v1.x.x release

This lets users choose their stability preference:
```yaml
uses: my-org/my-action@v1         # Latest v1 (gets patches automatically)
uses: my-org/my-action@v1.2.0     # Exact version (frozen)
uses: my-org/my-action@abc1234    # Commit SHA (most stable)
```

---

## 10. Best Practices

### Version Pinning

Always pin external actions to a specific version:

```yaml
# BAD — @main can break at any time
uses: actions/checkout@main

# BETTER — pinned to major version
uses: actions/checkout@v4

# BEST — pinned to commit SHA (cannot be changed retroactively)
uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683
```

For internal shared workflows, use at minimum a tag (`@v2`), preferably a SHA for security-critical workflows.

### Documentation Standards

Every reusable workflow and composite action should have:

1. **Clear `description`** in `action.yml` or workflow comments
2. **Input/output documentation** — every input and output has a `description`
3. **Usage example** — show exactly how to call it
4. **Required permissions** — document what GitHub token permissions are needed

### Testing Your Actions

Test composite actions and reusable workflows like any other code:

```yaml
# test-my-action.yml — tests the composite action
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: ./.github/actions/my-action
        id: test-run
        with:
          my-input: 'test-value'
      - name: Verify output
        run: |
          if [[ "${{ steps.test-run.outputs.my-output }}" != "expected-value" ]]; then
            echo "::error::Output did not match expected value"
            exit 1
          fi
```

### Security Considerations

1. **Principle of least privilege**: Declare minimum permissions needed
2. **Avoid `secrets: inherit`** for external reusable workflows
3. **Pin third-party actions** to commit SHAs in security-sensitive workflows
4. **Validate inputs** in your actions — don't trust inputs blindly
5. **Never log secrets** — use `add-mask` for dynamic sensitive values

---

## 11. Project Walkthrough

### Files in This Module

```
module-11-reusable-workflows/
├── README.md                      ← This file
└── project/
    └── .github/
        ├── workflows/
        │   ├── reusable-build-test.yml  ← The reusable workflow
        │   └── caller-main.yml          ← Calls the reusable workflow
        └── actions/
            └── setup-project/
                └── action.yml           ← Composite action
```

### reusable-build-test.yml

This is the reusable workflow. Key things to observe:
1. `on: workflow_call:` — the only trigger
2. Typed inputs with defaults and descriptions
3. Conditional jobs using `if: inputs.run-lint == true`
4. Job outputs that aggregate step outputs
5. Workflow-level outputs that reference job outputs

### caller-main.yml

This calls the reusable workflow. Key things to observe:
1. `uses:` pointing to the local reusable workflow
2. `with:` for inputs, `secrets:` for secrets
3. A subsequent job that `needs:` the reusable workflow job
4. Accessing `needs.<job-id>.outputs.<output-name>`

### setup-project/action.yml

This composite action encapsulates the "setup Python and install deps" logic. Key things to observe:
1. `runs.using: composite`
2. `shell: bash` on every `run:` step
3. Inputs and outputs
4. References to other actions within the composite action

---

## 12. Exercises

### Exercise 1: Add a New Input

Add a `test-command` string input to `reusable-build-test.yml` that lets the caller specify what command to run for tests (default: `pytest tests/`). Update the test job to use this input.

### Exercise 2: Cross-Repository Caller

Create a new file `caller-external.yml` that calls `reusable-build-test.yml` as if it were in an external repo. Use `secrets: inherit`. Add a comment explaining when you would prefer `secrets: inherit` vs explicit passing.

### Exercise 3: Enhance the Composite Action

Extend `setup-project/action.yml` to:
1. Accept an `extras` string input (e.g., `pytest-cov flake8`) for additional pip packages
2. Install `requirements.txt` plus the extra packages
3. Output the number of installed packages (get it from `pip list | wc -l`)

### Exercise 4: Create a Notify Action

Create a new composite action `.github/actions/notify-status/action.yml` that:
1. Accepts `status` (success/failure), `workflow-name`, and `message` inputs
2. Prints a formatted status report to `GITHUB_STEP_SUMMARY`
3. Emits a `::notice::` or `::error::` annotation based on status

### Exercise 5: JavaScript Action (Bonus)

Create a minimal JavaScript action `.github/actions/parse-version/action.yml` that:
1. Uses `runs: using: node20`
2. Reads a `version-string` input (e.g., `v1.2.3`)
3. Parses and outputs `major`, `minor`, `patch` separately
4. Does NOT use npm packages (just Node.js built-ins)

---

## Key Takeaways

1. **Reusable workflows** share entire jobs/multi-job pipelines; **composite actions** share step groups
2. `workflow_call` is the trigger that makes a workflow reusable
3. Inputs support four types: string, number, boolean, choice
4. Outputs flow: step output → job output → workflow output → caller's `needs` context
5. Secrets can be passed explicitly or with `inherit`
6. Composite actions require `runs: using: composite` and `shell:` on every `run:` step
7. Pin external actions to SHAs for maximum security and reproducibility

---

## Resources

- [GitHub Docs: Reusing workflows](https://docs.github.com/en/actions/using-workflows/reusing-workflows)
- [GitHub Docs: Creating a composite action](https://docs.github.com/en/actions/creating-actions/creating-a-composite-action)
- [GitHub Docs: Creating a JavaScript action](https://docs.github.com/en/actions/creating-actions/creating-a-javascript-action)
- [GitHub Docs: Metadata syntax for GitHub Actions](https://docs.github.com/en/actions/creating-actions/metadata-syntax-for-github-actions)
- [GitHub Actions Toolkit](https://github.com/actions/toolkit)
- [GitHub Actions Marketplace](https://github.com/marketplace?type=actions)

---

*Next up: Module 12 — Real-World Full-Stack CI/CD Pipeline*
