# Exercise 02: Write a GitHub Actions Workflow Skeleton

You do not need to know GitHub Actions yet — this is a pure YAML exercise.
Use what you learned in Module 01 to construct the following structure.

---

## Task

Write a YAML file that represents the following workflow structure:

### Workflow Details
- **Name:** Python CI
- **Triggers:**
  - On `push` to branches: `main` and `develop`
  - On `pull_request` to branch: `main`
  - Manually, with one input:
    - Name: `debug_mode`
    - Type: boolean
    - Default: `false`
    - Description: "Enable debug output"

### Environment Variables (workflow level)
- `PYTHON_VERSION`: value `"3.14"`
- `APP_NAME`: value `my-python-app`

### Jobs
The workflow has **two jobs**:

**Job 1: `lint`**
- Runs on: `ubuntu-latest`
- Timeout: 10 minutes
- Steps:
  1. Name: `Checkout repository` — uses `actions/checkout@v4`
  2. Name: `Set up Python` — uses `actions/setup-python@v5` with input `python-version` set to the workflow-level env var value `"3.14"`
  3. Name: `Install linter` — runs shell command: `pip install flake8`
  4. Name: `Run linter` — runs shell command: `flake8 src/`

**Job 2: `test`**
- Depends on job `lint` (use the `needs:` key)
- Runs on: `ubuntu-latest`
- Steps:
  1. Name: `Checkout repository` — uses `actions/checkout@v4`
  2. Name: `Set up Python` — uses `actions/setup-python@v5` with `python-version: "3.14"`
  3. Name: `Install dependencies` — runs: `pip install -r requirements.txt`
  4. Name: `Run tests` — runs: `pytest tests/ -v`
     - This step has an environment variable: `DEBUG: ${{ inputs.debug_mode }}`
  5. Name: `Upload coverage` — uses `actions/upload-artifact@v4` with:
     - `name`: `coverage-report`
     - `path`: `coverage/`

---

## Requirements

- Use correct YAML indentation (2 spaces)
- Use `|` (literal block) for any multi-line shell commands
- Quote strings where necessary
- The file should be a valid GitHub Actions workflow

---

## Hints

- Triggers go under `on:` (a mapping of event names to their configuration)
- Jobs go under `jobs:` (a mapping of job IDs to their configuration)
- Steps is a list — each item starts with `- name:`
- `needs: lint` makes job `test` wait for job `lint`
- Access env vars with `${{ env.VAR_NAME }}`

---

## Check Your Work

Your file should parse without errors. Validate it with:
```bash
pip install yamllint
yamllint your-solution.yaml
```

Or paste it into an online YAML validator.

Compare against `exercise-02-solution.yaml` when done.
