# Example 08 — Conditional Logic

## What This Teaches

The `if:` key lets you skip steps or entire jobs based on runtime conditions — the branch name, the event type, whether a previous step failed, and more. This is how you build flexible workflows that behave differently for PRs vs merges, or for main vs feature branches.

## Concepts Covered

| Concept | Key |
|---|---|
| Skip a step | `if: <expression>` on a step |
| Skip a whole job | `if: <expression>` on a job |
| Check branch name | `github.ref_name == 'main'` |
| Check event type | `github.event_name == 'push'` |
| Status: run on failure | `if: failure()` |
| Status: always run | `if: always()` |
| Status: run on cancel | `if: cancelled()` |
| Check a specific step | `if: steps.<id>.outcome == 'success'` |

## How to Try It

1. Copy `.github/workflows/conditional-logic.yml` into your repo.
2. Push to `main` — the **deploy-job** runs, the **preview-job** is skipped.
3. Push to a feature branch — the **preview-job** runs, the **deploy-job** is skipped.
4. In the **status-functions** job, watch the failure-handling steps run after the intentional failure.

## Key Concepts Explained

### The `if:` expression

```yaml
- name: Only on main
  if: github.ref_name == 'main'
  run: echo "main branch!"
```

If the condition is `false`, the step is **skipped** (shown as grey in the UI) — not failed. The job continues normally.

### Useful context values for conditions

```yaml
github.ref_name          # branch name: "main", "feature/login"
github.event_name        # "push", "pull_request", "workflow_dispatch"
github.actor             # username of who triggered the run
startsWith(github.ref_name, 'feature/')   # glob helper function
contains(github.ref_name, 'hotfix')       # substring check
```

### Status functions

| Function | Runs when... |
|---|---|
| `success()` | all previous steps succeeded (default behavior) |
| `failure()` | any previous step failed |
| `always()` | no matter what happened |
| `cancelled()` | the workflow was manually cancelled |

```yaml
- name: Cleanup (always run)
  if: always()
  run: rm -rf /tmp/build
```

### Step outcome vs conclusion

When a step has `continue-on-error: true`, a failed step still lets the job continue.

- `steps.<id>.outcome` — the raw result: `success` or `failure`
- `steps.<id>.conclusion` — the effective result: always `success` when `continue-on-error: true`

Use `outcome` when you want to know the real result. Use `conclusion` when you want to mirror how GitHub reports it.

### Combining conditions

```yaml
if: github.ref_name == 'main' && github.event_name == 'push'
if: github.ref_name != 'main' || github.event_name == 'workflow_dispatch'
```

Note: inside `if:` you don't need `${{ }}` — it's already in expression context. Both forms work:

```yaml
if: github.ref_name == 'main'            # ← preferred (cleaner)
if: ${{ github.ref_name == 'main' }}     # ← also valid
```

## Common Mistakes

**Mistake:** Using `if: failure()` without `continue-on-error: true` — if a step fails and there's no `continue-on-error`, the job stops and subsequent steps don't run at all. Add `continue-on-error: true` to the failing step, or put the cleanup in a separate job.

**Mistake:** Putting the `if:` inside `run:` as a shell `if` statement — that's valid shell scripting, but if you need to skip the step entirely (not just part of it), use `if:` at the YAML level.

## What's Next

See [Example 09](../09-matrix-builds/) to learn how to run the same job across multiple Python versions in parallel with a matrix strategy.
