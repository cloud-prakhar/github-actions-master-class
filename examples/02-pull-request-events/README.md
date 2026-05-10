# Example 02 — Pull Request Events

## What This Teaches

The `pull_request` event covers the full lifecycle of a PR: created, updated, labeled, merged, and closed. This example shows you how to react to each activity type and read PR metadata.

## Concepts Covered

| Concept | Key |
|---|---|
| Trigger on PR activity | `on: pull_request:` |
| Filter by activity type | `types: [opened, synchronize, closed, labeled]` |
| Read PR metadata | `github.event.pull_request.*` |
| Detect a merge (vs close) | `github.event.pull_request.merged == true` |
| Run checks only on new code | `if: github.event.action == 'opened' \|\| ...` |

## How to Try It

1. Copy `.github/workflows/pull-request-events.yml` into your repo.
2. Open a PR targeting `main` — the `pr-checks` job runs.
3. Push a new commit to your PR branch — `pr-checks` runs again (synchronize).
4. Add a label to the PR — the `on-labeled` job runs.
5. Merge the PR — the `on-merged` job runs.
6. Abandon (close without merging) — `on-merged` does NOT run (merged = false).

## Key Concepts Explained

### Activity types

```yaml
on:
  pull_request:
    types:
      - opened       # PR was just created
      - synchronize  # new commit was pushed to the PR branch
      - closed       # PR was merged or dismissed
      - labeled      # a label was added
```

Without `types:`, the default is `[opened, synchronize, reopened]`.

### Detecting merge vs close

A PR `closed` event fires whether the PR was merged OR abandoned. Check `merged` to distinguish:

```yaml
if: github.event.action == 'closed' && github.event.pull_request.merged == true
```

### Reading PR metadata

```yaml
${{ github.event.pull_request.number }}        # PR number
${{ github.event.pull_request.title }}         # PR title
${{ github.event.pull_request.user.login }}    # author
${{ github.head_ref }}                         # source branch
${{ github.base_ref }}                         # target branch
${{ github.event.pull_request.additions }}     # lines added
${{ github.event.pull_request.changed_files }} # file count
```

### `pull_request` vs `pull_request_target`

`pull_request` runs in the context of the **PR branch** — it has read access to the base repo but no secrets for PRs from forks (for security). `pull_request_target` runs in the context of the **target branch** and does have access to secrets — use it carefully.

## Common Mistakes

**Mistake:** Expecting `closed` to mean "merged". Always check `.merged == true`.

**Mistake:** Putting heavy jobs (test suite, build) on `labeled` or `closed` events — those events have no new code to test.

## What's Next

See [Example 03](../03-scheduled-cron/) to learn how to run workflows on a time-based schedule without any push or PR.
