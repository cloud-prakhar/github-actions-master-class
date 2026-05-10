# Example 04 — Manual Dispatch

## What This Teaches

`workflow_dispatch` adds a "Run workflow" button to your workflow in the GitHub Actions UI. You can define input parameters that appear as a form — making it easy to run parameterised workflows without editing YAML.

## Concepts Covered

| Concept | Key |
|---|---|
| Add "Run workflow" button | `on: workflow_dispatch:` |
| Free-text input | `type: string` |
| Dropdown input | `type: choice` with `options:` |
| Checkbox input | `type: boolean` |
| Read input values | `${{ github.event.inputs.<name> }}` |
| Conditional job on input value | `if: github.event.inputs.run_tests == 'true'` |

## How to Try It

1. Copy `.github/workflows/manual-dispatch.yml` into your repo and push to `main`.
2. Go to **Actions tab** → select **"04 - Manual Dispatch"** → click **"Run workflow"**.
3. Fill in the form:
   - `target_environment`: type `production`
   - `log_level`: pick `debug` from the dropdown
   - `run_tests`: uncheck it
4. Click **"Run workflow"** and watch the deploy job skip the test step.

## Key Concepts Explained

### Input types

```yaml
inputs:
  name:                         # input ID — used in ${{ github.event.inputs.name }}
    description: "Shown in UI"  # label above the field
    type: string                # free-text box
    required: true              # can't leave blank
    default: "staging"          # pre-filled value

  level:
    type: choice                # dropdown
    options: [info, debug, warning]

  run_tests:
    type: boolean               # checkbox
    default: true
```

### Reading inputs

```yaml
run: echo "Target: ${{ github.event.inputs.target_environment }}"
```

You can also use `${{ inputs.target_environment }}` (shorthand in newer GitHub Actions syntax).

### Boolean inputs are strings

Boolean inputs arrive as the **string** `"true"` or `"false"`, not real booleans. Always compare against the string:

```yaml
# CORRECT
if: github.event.inputs.run_tests == 'true'

# WRONG — this doesn't work as expected
if: github.event.inputs.run_tests == true
```

### Also triggerable from the CLI

```bash
gh workflow run manual-dispatch.yml \
  --field target_environment=staging \
  --field log_level=debug \
  --field run_tests=true
```

## Common Mistakes

**Mistake:** Using `workflow_dispatch` on a feature branch and expecting the "Run workflow" button to appear — it only shows for the **default branch**.

**Mistake:** Comparing boolean inputs to `true` (real boolean) instead of `'true'` (string).

## What's Next

See [Example 05](../05-concurrency-control/) to learn how to prevent duplicate workflow runs from trampling each other.
