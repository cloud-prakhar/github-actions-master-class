# Example 06 — Environment Variables

## What This Teaches

Environment variables in GitHub Actions exist at three scopes — workflow, job, and step. Inner scopes override outer scopes. This example also covers GitHub's built-in `$GITHUB_*` variables and the secure pattern for injecting secrets.

## Concepts Covered

| Concept | Key |
|---|---|
| Workflow-level env | top-level `env:` |
| Job-level env | `env:` inside a job |
| Step-level env | `env:` inside a step |
| Inner overrides outer | same key at a deeper scope wins |
| GitHub built-in variables | `$GITHUB_WORKSPACE`, `$GITHUB_SHA`, etc. |
| Dynamic variables | `echo "KEY=VALUE" >> $GITHUB_ENV` |
| Secure secret injection | `env: MY_SECRET: ${{ secrets.MY_SECRET }}` |

## How to Try It

1. Copy `.github/workflows/environment-variables.yml` into your repo and push to `main`.
2. Watch the **Variable Scopes Demo** job — notice `LOG_LEVEL` changes value at each scope.
3. Watch the **Dynamic Variables** job — values computed at runtime are available in later steps.
4. To test secret injection: add a secret named `MY_API_KEY` in **Settings → Secrets and variables → Actions**.

## Key Concepts Explained

### Scope hierarchy

```
Workflow env    ← available everywhere
  └── Job env  ← overrides workflow for this job's steps
        └── Step env  ← overrides job for this single step only
```

```yaml
env:              # workflow level
  LOG_LEVEL: info

jobs:
  example:
    env:
      LOG_LEVEL: debug   # overrides "info" for all steps in this job
    steps:
      - run: echo $LOG_LEVEL   # prints: debug
        env:
          LOG_LEVEL: warning   # overrides "debug" for this step only
```

### Dynamic variables (`$GITHUB_ENV`)

Write `KEY=VALUE` to the `$GITHUB_ENV` file to share a variable with **subsequent steps** in the same job:

```yaml
- name: Set value
  run: echo "BUILD_ID=abc123" >> $GITHUB_ENV

- name: Use value
  run: echo $BUILD_ID   # prints: abc123
```

This does **not** work across jobs — use job outputs for that (see Example 07).

### Secret injection pattern

```yaml
# CORRECT: inject as env var, reference $VAR_NAME in shell
- name: Call API
  env:
    API_KEY: ${{ secrets.MY_API_KEY }}   # injected here
  run: curl -H "Authorization: Bearer $API_KEY" https://api.example.com

# WRONG: inline in run — logged in the YAML, harder to mask
- run: curl -H "Authorization: Bearer ${{ secrets.MY_API_KEY }}" ...
```

### GitHub built-in variables

| Variable | Value example |
|---|---|
| `$GITHUB_WORKSPACE` | `/home/runner/work/my-repo` |
| `$GITHUB_SHA` | Full commit SHA |
| `$GITHUB_REF_NAME` | `main` |
| `$GITHUB_ACTOR` | `octocat` |
| `$GITHUB_RUN_NUMBER` | `42` |
| `$GITHUB_OUTPUT` | Path to write step outputs |
| `$GITHUB_ENV` | Path to write env vars for later steps |

## Common Mistakes

**Mistake:** Expecting a step-level env var to be visible in the next step — step env vars are **only** visible within that step.

**Mistake:** Writing `$GITHUB_ENV` in one job and expecting it to work in another — `$GITHUB_ENV` is job-scoped, not workflow-scoped.

## What's Next

See [Example 07](../07-job-outputs/) to learn how to pass data **between jobs** using outputs.
