# Example 01 — Push Trigger

## What This Teaches

The `push` event is the most common GitHub Actions trigger. This example shows you how to fire a workflow when code is pushed, and how to filter that trigger so it doesn't run on every branch or every file change.

## Concepts Covered

| Concept | Key |
|---|---|
| Trigger on push | `on: push:` |
| Limit to specific branches | `branches: [main, "release/**"]` |
| Limit to specific file changes | `paths: ["src/**", "*.py"]` |
| Invert: skip specific branches | `branches-ignore:` |
| Invert: skip specific paths | `paths-ignore:` |

## How to Try It

1. Copy `.github/workflows/push-trigger.yml` into your repo at the same path.
2. Commit and push to `main`. The workflow fires.
3. Push to a branch named `scratch-anything`. The workflow does **not** fire (doesn't match the `branches` filter).
4. Edit only a `.md` file and push. The workflow does **not** fire (doesn't match the `paths` filter).
5. Edit a `.py` file and push. The workflow fires.

## Key Concepts Explained

### Branch filters

```yaml
on:
  push:
    branches:
      - main          # exact name
      - "release/**"  # wildcard: any branch starting with release/
```

`*` matches any character except `/`. `**` matches any character including `/`.

### Path filters

```yaml
    paths:
      - "src/**"      # any file inside src/
      - "*.py"        # any .py file at the repo root
```

Path filters use the same glob syntax. The workflow runs only when **at least one** changed file matches a pattern.

### `branches` vs `branches-ignore`

Use one or the other — not both at the same time.

- `branches`: allowlist — only run for these branches
- `branches-ignore`: blocklist — run for everything except these branches

The same rule applies to `paths` vs `paths-ignore`.

## Common Mistakes

**Mistake:** Forgetting that `paths` applies to the files changed in the push, not the files that exist.
If you push a commit that only changes `README.md` and your filter is `paths: ["src/**"]`, the workflow is skipped even though `src/` exists.

**Mistake:** Using `branches` and `branches-ignore` together — GitHub rejects this with a validation error.

## What's Next

Once you understand push triggers, explore [Example 02](../02-pull-request-events/) to see how pull request activity triggers work differently.
