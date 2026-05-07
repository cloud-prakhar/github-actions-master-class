# Module 01: YAML Fundamentals

**Difficulty:** Beginner | **Time:** 2-3 hours | **Prev:** [Module 00](../module-00-prerequisites/README.md) | **Next:** [Module 02 — Git Fundamentals](../module-02-git-fundamentals/README.md)

---

## Learning Objectives

By the end of this module you will:
- Understand YAML syntax rules and structure
- Know all YAML data types (strings, numbers, booleans, null, dates)
- Write lists (sequences) and dictionaries (mappings)
- Use multi-line strings with `|` and `>`
- Use anchors and aliases to avoid repetition
- Recognize how YAML maps to GitHub Actions workflow structure
- Fix common YAML syntax errors

---

## Why YAML?

GitHub Actions workflows are written in **YAML** (YAML Ain't Markup Language). Before you can write a single workflow, you need to understand YAML — its syntax, its quirks, and its data types.

YAML is also used in: Docker Compose, Kubernetes, Ansible, CircleCI, Azure Pipelines, and many other tools. Learning it once pays dividends everywhere.

---

## 1. What is YAML?

YAML is a **human-readable data serialization format**. "Serialization" means converting data structures (like a Python dictionary or JavaScript object) into a text format that can be stored in a file or sent over a network.

Think of YAML as an alternative to JSON that is:
- Easier to read (no braces, fewer quotes)
- Supports comments (JSON does not)
- More expressive (multi-line strings, anchors)

**JSON vs YAML — same data:**
```json
{
  "name": "Alice",
  "age": 30,
  "languages": ["Python", "JavaScript"],
  "active": true
}
```

```yaml
name: Alice
age: 30
languages:
  - Python
  - JavaScript
active: true
```

YAML is a superset of JSON — valid JSON is also valid YAML.

---

## 2. Basic Syntax Rules

### Rule 1: Indentation with Spaces (Never Tabs)

YAML uses **spaces** for indentation. **Tabs are forbidden** and will cause a parse error. The convention is 2 spaces per level.

```yaml
# CORRECT
person:
  name: Alice       # 2-space indent
  address:
    city: London    # 4-space indent (2 levels)

# WRONG — tab character used
person:
	name: Alice     # tab indent — PARSE ERROR
```

### Rule 2: Comments with `#`

Anything after `#` on a line is a comment and is ignored.

```yaml
name: Alice    # this is a comment
# this whole line is a comment
```

### Rule 3: Key-Value Pairs

The basic unit is `key: value`. There must be a space after the colon.

```yaml
name: Alice       # CORRECT
name:Alice        # WRONG — no space after colon
```

### Rule 4: Case Sensitivity

Keys and values are case-sensitive.

```yaml
Name: Alice
name: Bob         # different key from "Name"
```

### Rule 5: Special Characters That Need Quoting

Some characters have special meaning in YAML. If your value contains them, wrap in quotes:

```yaml
# Characters requiring quotes: : { } [ ] , & * # ? | - < > = ! % @ `
message: "Hello: World"       # colon in value — needs quotes
path: "C:\\Users\\Alice"      # backslash
version: "1.0"                # prevent interpretation as float
yes_value: "yes"              # prevent interpretation as boolean true
```

---

## 3. YAML Data Types

YAML automatically infers types. This is convenient but can surprise you.

### Strings

```yaml
# Unquoted string — most common
name: Alice

# Single-quoted — no escape sequences, literal
message: 'Hello\nWorld'   # literally: Hello\nWorld (not a newline)

# Double-quoted — escape sequences work
message: "Hello\nWorld"   # has a real newline

# YAML auto-converts these to booleans — quote to keep as strings!
flag1: "true"    # string "true"
flag2: "yes"     # string "yes"
flag3: "on"      # string "on"
flag4: "null"    # string "null"
flag5: "1.0"     # string "1.0" (not a float)
```

### Numbers

```yaml
integer: 42
negative: -7
float: 3.14
scientific: 1.5e10
octal: 0o17          # octal 17 = decimal 15
hex: 0xFF            # hexadecimal
```

### Booleans

```yaml
# All of these are boolean TRUE:
active: true
active: True
active: TRUE
active: yes
active: Yes
active: on
active: On

# All of these are boolean FALSE:
active: false
active: False
active: FALSE
active: no
active: No
active: off
active: Off
```

> **Warning for GitHub Actions:** `on` is a YAML boolean AND a reserved GitHub Actions key. This is why GitHub Actions files always quote it: `"on"` — or just use it unquoted at the top level where YAML knows it's a key.

### Null

```yaml
nothing: null
nothing: ~
nothing:          # empty value is also null
```

### Dates

```yaml
date: 2024-01-15            # ISO 8601 date
datetime: 2024-01-15T10:30:00Z
```

---

## 4. Collections

### Block Sequences (Lists)

```yaml
# Block sequence — uses dash-space (- )
fruits:
  - apple
  - banana
  - cherry

# Inline sequence (flow style)
fruits: [apple, banana, cherry]

# List of numbers
ports:
  - 80
  - 443
  - 8080
```

### Block Mappings (Dictionaries / Objects)

```yaml
# Block mapping
person:
  name: Alice
  age: 30
  city: London

# Inline mapping (flow style)
person: {name: Alice, age: 30, city: London}
```

### Nested Structures

```yaml
# List of mappings — VERY common in GitHub Actions (list of steps)
steps:
  - name: Checkout
    uses: actions/checkout@v4
  - name: Run tests
    run: pytest tests/
    env:
      APP_ENV: test

# Mapping with list values
config:
  allowed_branches:
    - main
    - develop
  excluded_paths:
    - __pycache__
    - dist
```

### Deeply Nested Example

```yaml
workflow:
  name: CI Pipeline
  jobs:
    build:
      runs-on: ubuntu-latest
      steps:
        - name: Checkout
          uses: actions/checkout@v4
        - name: Build
          run: pip install -r requirements.txt
          env:
            APP_ENV: production
```

---

## 5. Multi-line Strings

This is critical for GitHub Actions because `run:` steps often contain multi-line shell scripts.

### Literal Block Scalar `|` — Preserves Newlines

Each newline in the YAML becomes a real `\n` in the string.

```yaml
script: |
  echo "Line 1"
  echo "Line 2"
  echo "Line 3"
# Result: "echo \"Line 1\"\necho \"Line 2\"\necho \"Line 3\"\n"
# Each line is separate when executed as a shell script
```

### Folded Block Scalar `>` — Folds to Spaces

Newlines become spaces (useful for long single-line strings you want to wrap for readability).

```yaml
description: >
  This is a very long description that
  wraps across multiple lines but will
  be treated as a single line.
# Result: "This is a very long description that wraps across multiple lines but will be treated as a single line.\n"
```

### Chomping Indicators

```yaml
# Default: keeps one trailing newline
script: |
  echo "hello"

# Strip (|-): removes ALL trailing newlines
script: |-
  echo "hello"

# Keep (|+): keeps ALL trailing newlines
script: |+
  echo "hello"

```

### In GitHub Actions Context

The `run:` key uses `|` to write multi-line shell scripts:

```yaml
steps:
  - name: Multi-step script
    run: |
      echo "Step 1: Install"
      pip install -r requirements.txt -r requirements-dev.txt
      echo "Step 2: Lint"
      flake8 src/ tests/
      echo "Step 3: Test"
      pytest tests/ -v
```

---

## 6. Anchors and Aliases

Anchors (`&name`) and aliases (`*name`) let you reuse values without repeating them. The `<<:` merge key combines mappings.

```yaml
# Define an anchor
defaults: &defaults
  retries: 3
  timeout: 30
  notify: true

# Reuse with alias
job1:
  <<: *defaults        # merges defaults into job1
  name: build

job2:
  <<: *defaults        # merges defaults into job2
  name: test
  timeout: 60          # override one value

# Result:
# job1: {retries: 3, timeout: 30, notify: true, name: build}
# job2: {retries: 3, timeout: 60, notify: true, name: test}
```

> **Note:** GitHub Actions does NOT support YAML anchors in workflow files. They are useful in other YAML contexts (Docker Compose, etc.) and worth knowing — but don't use them in `.github/workflows/*.yml`.

---

## 7. YAML in GitHub Actions Context

Here is how every YAML concept maps to GitHub Actions:

```yaml
# KEY-VALUE PAIR
name: My Workflow          # workflow name is a string value

# MAPPING (dictionary)
on:                        # "on" key contains a mapping of events
  push:                    # push event
    branches: [main]       # inline list of branch names

# SEQUENCE OF MAPPINGS (list of steps)
steps:
  - name: Checkout         # each item is a mapping
    uses: actions/checkout@v4

  - name: Run tests
    run: pytest tests/     # string value
    env:                   # nested mapping
      APP_ENV: test

# MULTI-LINE STRING
  - name: Install and test
    run: |                 # literal block scalar — each line is a shell command
      pip install -r requirements.txt
      pytest tests/ -v

# BOOLEAN
  - name: Deploy
    if: true               # boolean condition (usually an expression though)

# NUMBER
    timeout-minutes: 10    # integer value

# NULL — a job key with no value means use defaults
    container:             # null — no container specified
```

---

## 8. Common YAML Mistakes

### Mistake 1: Wrong Indentation

```yaml
# WRONG
steps:
- name: Checkout       # should be indented 2 more spaces
  uses: actions/checkout@v4

# CORRECT
steps:
  - name: Checkout
    uses: actions/checkout@v4
```

### Mistake 2: Missing Space After Colon

```yaml
# WRONG
name:My Workflow

# CORRECT
name: My Workflow
```

### Mistake 3: Using Tabs

```yaml
# WRONG (tab character before "name")
steps:
	- name: Checkout

# CORRECT (two spaces)
steps:
  - name: Checkout
```

### Mistake 4: Unquoted Values That Look Like Booleans

```yaml
# WRONG — "on" is a boolean in YAML (= true)
toggle: on

# CORRECT — quote it if you want the string "on"
toggle: "on"
```

### Mistake 5: Mixing Indentation Levels

```yaml
# WRONG — inconsistent indentation
jobs:
  build:
    runs-on: ubuntu-latest
      steps:          # extra indent — this creates a nested mapping, not a sibling key

# CORRECT
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - run: echo "hello"
```

### Mistake 6: Colon Inside an Unquoted String

```yaml
# WRONG — YAML interprets "http:" as a key
url: http://example.com

# CORRECT
url: "http://example.com"
```

---

## 9. YAML Validation Tools

Before pushing a workflow, validate the YAML:

**Online:**
- Search "YAML Lint online" — paste and validate

**CLI:**
```bash
pip install yamllint
yamllint .github/workflows/my-workflow.yml
```

**VS Code:**
- Install "YAML" extension by Red Hat
- It validates YAML in real-time with red underlines

**GitHub's own validator:**
- The GitHub Actions workflow editor (in the GitHub UI → Actions → New workflow) validates YAML and suggests fixes.

---

## Exercises

### Exercise 1 — Fix the Broken YAML
See: [exercises/exercise-01-instructions.md](./exercises/exercise-01-instructions.md)

### Exercise 2 — Write a Workflow Skeleton
See: [exercises/exercise-02-instructions.md](./exercises/exercise-02-instructions.md)

---

## Example Files

Study these before doing the exercises:

- [01-basic-syntax.yaml](./examples/01-basic-syntax.yaml) — Comments, key-value pairs, indentation
- [02-data-types.yaml](./examples/02-data-types.yaml) — All scalar types
- [03-lists-and-dicts.yaml](./examples/03-lists-and-dicts.yaml) — Collections
- [04-multiline-strings.yaml](./examples/04-multiline-strings.yaml) — `|` and `>` operators
- [05-anchors-and-aliases.yaml](./examples/05-anchors-and-aliases.yaml) — Anchors, aliases, merge
- [06-github-actions-yaml.yaml](./examples/06-github-actions-yaml.yaml) — Full annotated workflow

---

## Key Takeaways

| Concept | Remember |
|---|---|
| Indentation | Always 2 spaces, never tabs |
| Strings | Quote values containing `:`, `{`, `[`, `#`, `yes`, `no`, `true`, `false` |
| Lists | Use `- ` prefix for each item |
| Dicts | Use `key: value` pairs |
| Multi-line | Use `\|` for shell scripts, `>` for long single lines |
| Anchors | Useful but NOT supported in GitHub Actions workflows |
| Comments | Start with `#` |

---

## References

- 📄 **YAML 1.2 Specification** — [yaml.org/spec/1.2.2](https://yaml.org/spec/1.2.2/)
- 📘 **Learn YAML in Y Minutes** — [learnxinyminutes.com/docs/yaml](https://learnxinyminutes.com/docs/yaml/)
- ⚙️ **GitHub Actions Workflow Syntax** — [docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)
- 🔧 **yamllint** (CLI linter) — [yamllint.readthedocs.io](https://yamllint.readthedocs.io/en/stable/)
- 🛠️ **YAML Extension for VS Code** (Red Hat) — [marketplace.visualstudio.com](https://marketplace.visualstudio.com/items?itemName=redhat.vscode-yaml)

---

## Next Module

**[Module 02 — Git Fundamentals](../module-02-git-fundamentals/README.md)**
