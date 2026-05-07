# Module 07: Dependent Jobs & Artifacts

**Difficulty:** Intermediate | **Time:** 2-3 hours | **Prev:** [Module 06](../module-06-secrets-variables/README.md) | **Next:** [Module 08 — CI Pipeline](../module-08-ci-pipeline/README.md)

## Project 5: Build-Test-Deploy Pipeline with Job Dependencies

---

## Learning Objectives

By the end of this module you will:
- Create ordered job pipelines with `needs:`
- Pass data between jobs using job outputs
- Upload and download artifacts to share files between jobs
- Implement fan-out (parallel jobs from one trigger) and fan-in (converging jobs) patterns
- Control job execution based on upstream job results

---

## 1. Why Job Dependencies?

By default all jobs run in parallel — they start simultaneously and race to finish. This is great for independent checks (lint, test, security scan) but wrong for ordered pipelines.

You need `needs:` when:
- Job B requires files produced by Job A
- Deploying only after tests pass
- Building a Docker image only after the app builds successfully
- Running cleanup only after all other jobs finish

```yaml
# WITHOUT needs: — all 3 jobs start at the same time
jobs:
  build:    # starts immediately
  test:     # starts immediately (but tests need the build!)
  deploy:   # starts immediately (but deploy needs tests to pass!)

# WITH needs: — ordered execution
jobs:
  build:    # starts immediately
  test:
    needs: build    # waits for build to succeed
  deploy:
    needs: test     # waits for test to succeed
```

---

## 2. The `needs:` Key

### Single Dependency
```yaml
test:
  needs: build       # string — single dependency
```

### Multiple Dependencies
```yaml
deploy:
  needs: [build, test, security-scan]   # list — ALL must succeed
```

### Accessing Upstream Status
```yaml
notify:
  needs: [build, test, deploy]
  if: always()
  steps:
    - run: |
        echo "Build:  ${{ needs.build.result }}"
        echo "Test:   ${{ needs.test.result }}"
        echo "Deploy: ${{ needs.deploy.result }}"
```

Possible values for `needs.<job>.result`:
- `success` — job completed successfully
- `failure` — job failed
- `cancelled` — job was cancelled
- `skipped` — job was skipped (its `if:` condition was false)

---

## 3. Job Outputs

Jobs can produce named values for downstream jobs. Two-step process:

### Step 1: Define outputs at the job level
```yaml
jobs:
  build:
    outputs:
      version: ${{ steps.get-ver.outputs.value }}
      image-tag: ${{ steps.tag.outputs.tag }}
```

### Step 2: Set values from steps
```yaml
    steps:
      - id: get-ver
        run: echo "value=1.2.3" >> $GITHUB_OUTPUT

      - id: tag
        run: echo "tag=my-app:${{ github.sha }}" >> $GITHUB_OUTPUT
```

### Step 3: Consume in downstream jobs
```yaml
  deploy:
    needs: build
    steps:
      - run: |
          echo "Deploying version ${{ needs.build.outputs.version }}"
          echo "Image: ${{ needs.build.outputs.image-tag }}"
```

---

## 4. Artifacts

Artifacts are files produced during a workflow run. They solve a different problem than job outputs:
- **Job outputs:** Small values (strings, numbers, booleans)
- **Artifacts:** Files (test reports, binaries, Docker tarballs, coverage HTML)

### Uploading an Artifact
```yaml
- uses: actions/upload-artifact@v4
  with:
    name: coverage-report        # artifact name (unique per run)
    path: htmlcov/               # what to upload
    retention-days: 30           # how long to keep (1-90 days)
    if-no-files-found: error     # error | warn | ignore
```

### Downloading in a Later Job
```yaml
- uses: actions/download-artifact@v4
  with:
    name: coverage-report        # must match the upload name
    path: ./coverage             # where to put the files (optional)
```

### Key Artifact Rules
- Artifacts are scoped to the **workflow run** — available to any job in the same run
- A later job can download what an earlier job uploaded
- Artifacts are also available for **manual download** from the Actions UI
- Default retention: 90 days (public), 90 days (private)
- Paid storage starts after the free 500 MB limit

---

## 5. Pipeline Patterns

### Sequential Pipeline (A → B → C)
```yaml
jobs:
  lint:  {}           # starts first
  build:
    needs: lint       # waits for lint
  test:
    needs: build      # waits for build
  deploy:
    needs: test       # waits for test
```

```
lint → build → test → deploy
```

### Fan-Out (One triggers many parallel)
```yaml
jobs:
  setup:  {}          # runs first

  test-unit:
    needs: setup      # all three start after setup
  test-integration:
    needs: setup
  test-e2e:
    needs: setup
```

```
         ┌→ test-unit
setup ───┼→ test-integration
         └→ test-e2e
```

### Fan-In (Many converge into one)
```yaml
jobs:
  test-unit:  {}
  test-integration: {}
  test-e2e: {}

  report:
    needs: [test-unit, test-integration, test-e2e]   # waits for all three
```

```
test-unit ────────┐
test-integration ─┼→ report
test-e2e ─────────┘
```

### Diamond (Fan-Out then Fan-In)
```yaml
jobs:
  setup:  {}
  test-unit:
    needs: setup
  test-integration:
    needs: setup
  deploy:
    needs: [test-unit, test-integration]
```

```
         ┌→ test-unit ────┐
setup ───┤                ├→ deploy
         └→ test-integration ─┘
```

---

## 6. Conditional Jobs with `needs`

```yaml
# Only deploy if tests passed
deploy:
  needs: test
  if: needs.test.result == 'success' && github.ref == 'refs/heads/main'

# Always run notification, regardless of other jobs
notify:
  needs: [build, test, deploy]
  if: always()
  steps:
    - run: |
        if [[ "${{ needs.test.result }}" == "failure" ]]; then
          echo "Tests failed — sending failure notification"
        else
          echo "Pipeline succeeded — sending success notification"
        fi
```

---

## Project Files

| File | What it teaches |
|---|---|
| [dependent-jobs.yml](./project/.github/workflows/dependent-jobs.yml) | Sequential pipeline, job outputs, needs: |
| [fan-out-fan-in.yml](./project/.github/workflows/fan-out-fan-in.yml) | Fan-out and fan-in patterns |
| [artifacts-demo.yml](./project/.github/workflows/artifacts-demo.yml) | Upload and download artifacts |

---

## References

- 🔗 **Using Jobs in a Workflow** (`needs:`) — [docs.github.com/en/actions/using-jobs/using-jobs-in-a-workflow](https://docs.github.com/en/actions/using-jobs/using-jobs-in-a-workflow)
- 📦 **Storing Workflow Data as Artifacts** — [docs.github.com/en/actions/using-workflows/storing-workflow-data-as-artifacts](https://docs.github.com/en/actions/using-workflows/storing-workflow-data-as-artifacts)
- 📤 **actions/upload-artifact** — [github.com/actions/upload-artifact](https://github.com/actions/upload-artifact)
- 📥 **actions/download-artifact** — [github.com/actions/download-artifact](https://github.com/actions/download-artifact)
- 📋 **Defining Outputs for Jobs** — [docs.github.com/en/actions/using-jobs/defining-outputs-for-jobs](https://docs.github.com/en/actions/using-jobs/defining-outputs-for-jobs)

---

## Next Module

**[Module 08 — Continuous Integration (CI)](../module-08-ci-pipeline/README.md)**
