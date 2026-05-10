# Example 05 — Concurrency Control

## What This Teaches

Without concurrency control, pushing 3 commits quickly starts 3 workflow runs simultaneously. They waste compute and can produce confusing results. The `concurrency` key prevents this by ensuring only one run occupies a named "slot" at a time.

## Concepts Covered

| Concept | Key |
|---|---|
| Concurrency at workflow level | top-level `concurrency:` |
| Concurrency at job level | `concurrency:` inside a job |
| Cancel old run on new push | `cancel-in-progress: true` |
| Queue new run until old finishes | `cancel-in-progress: false` |
| Scope per branch | `group: ${{ github.workflow }}-${{ github.ref }}` |
| Scope per PR | `group: pr-${{ github.event.pull_request.number }}` |

## How to Try It

1. Copy `.github/workflows/concurrency-control.yml` into your repo.
2. Push a commit — watch the workflow start (it takes ~10 seconds).
3. Immediately push another commit before the first finishes.
4. In the **Actions tab**, watch the first run get **cancelled** automatically and the second run take over.

## Key Concepts Explained

### Concurrency group

```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```

The `group` string is the slot name. Any two runs with the **same group value** cannot run simultaneously. Using `${{ github.ref }}` means each branch has its own slot — pushing to `main` doesn't cancel a run for `feature/login`.

### `cancel-in-progress: true` (for CI)

```
Push commit A → run A starts
Push commit B → run A is CANCELLED, run B starts
```

Best for **feature branch CI** — you only care about the latest commit.

### `cancel-in-progress: false` (for deploys)

```
Deploy run 1 starts
Deploy run 2 arrives → it QUEUES and waits
Run 1 finishes → run 2 starts
```

Best for **deployments** — you want every version deployed in order.

### Per-job concurrency (advanced)

```yaml
jobs:
  build:
    concurrency:
      group: build-${{ github.ref }}
      cancel-in-progress: true    # fast CI: always test latest

  deploy:
    concurrency:
      group: deploy-production
      cancel-in-progress: false   # ordered deploys: never skip
```

This is a common production pattern: cancel duplicate builds, queue deploys.

### ASCII diagram

```
Branch: feature/x
──────────────────────────────────────────────────
Push 1  →  [Run A starts]
Push 2  →  [Run A CANCELLED]  [Run B starts]
Push 3  →                     [Run B CANCELLED]  [Run C starts]
                                                 [Run C completes ✓]
```

## Common Mistakes

**Mistake:** Setting `cancel-in-progress: false` for CI — this queues every commit and you wait for them all to finish, which defeats the purpose.

**Mistake:** Using a global group without `${{ github.ref }}` — pushes to different branches would cancel each other.

## What's Next

See [Example 06](../06-environment-variables/) to master the three scopes of environment variables.
