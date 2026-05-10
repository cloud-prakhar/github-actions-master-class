# Example 07 — Job Outputs

## What This Teaches

Jobs run in separate virtual machines, so they can't share files or environment variables directly. Job outputs are the mechanism for passing data from one job to a downstream job that `needs:` it.

## Concepts Covered

| Concept | Key |
|---|---|
| Set a step output | `echo "key=value" >> $GITHUB_OUTPUT` |
| Expose a job output | `outputs: name: ${{ steps.<id>.outputs.<key> }}` |
| Reference upstream output | `${{ needs.<job>.outputs.<name> }}` |
| Access result status | `${{ needs.<job>.result }}` |
| Step `id` is required | steps need an `id:` to be referenced |

## How to Try It

1. Copy `.github/workflows/job-outputs.yml` into your repo and push to `main`.
2. In the **Actions tab**, open the run and watch the three jobs appear in sequence:
   - `detect-version` runs first and emits a version string.
   - `build` waits for it, reads the version, and emits an artifact path.
   - `deploy` waits for both and reads from both.

## Key Concepts Explained

### The three-step pattern

**Step 1 — write the step output:**

```yaml
- name: Compute something
  id: compute               # ← id is required to reference this step
  run: echo "result=hello" >> $GITHUB_OUTPUT
```

**Step 2 — declare the job output:**

```yaml
jobs:
  my-job:
    outputs:
      my_result: ${{ steps.compute.outputs.result }}   # exposes to downstream jobs
```

**Step 3 — read it in a downstream job:**

```yaml
jobs:
  downstream:
    needs: my-job
    steps:
      - run: echo "${{ needs.my-job.outputs.my_result }}"
```

### Data flow diagram

```
detect-version job
  └─ step (id: detect) → app_version=1.4.2  →  $GITHUB_OUTPUT
     └─ job outputs.version ───────────────────────────────────┐
                                                               │
build job (needs: detect-version)                             │
  └─ reads needs.detect-version.outputs.version ◄─────────────┘
  └─ step (id: build-step) → artifact_path=dist/app.tar.gz  → $GITHUB_OUTPUT
     └─ job outputs.artifact ───────────────────────────────────┐
                                                               │
deploy job (needs: [detect-version, build])                   │
  └─ reads needs.detect-version.outputs.version               │
  └─ reads needs.build.outputs.artifact ◄──────────────────────┘
```

### Output values are strings

Job outputs are always strings. If you need to pass a list or object, encode it as JSON:

```yaml
run: echo "items=[\"a\",\"b\",\"c\"]" >> $GITHUB_OUTPUT
```

Then decode it in the downstream job using `fromJSON()`.

### Check upstream job result

```yaml
- run: echo "build result: ${{ needs.build.result }}"
# result is one of: success, failure, cancelled, skipped
```

## Common Mistakes

**Mistake:** Forgetting `id:` on the step — without it, `steps.<id>.outputs.*` has nothing to reference.

**Mistake:** Trying to share data between jobs using `$GITHUB_ENV` — that file is job-local and disappears when the job ends.

**Mistake:** Forgetting to declare `outputs:` on the job — step outputs don't automatically become job outputs.

## What's Next

See [Example 08](../08-conditional-logic/) to learn how to use `if:` conditions to control which steps and jobs actually run.
