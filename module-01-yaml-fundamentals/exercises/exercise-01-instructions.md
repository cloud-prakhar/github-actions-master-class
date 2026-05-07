# Exercise 01: Fix the Broken YAML

Each snippet below has one or more YAML syntax errors. Identify the problem and fix it.
Write your corrected YAML in a file called `exercise-01-my-solution.yaml`.

Compare your answer against `exercise-01-solution.yaml` when done.

---

## Snippet 1 — The Missing Space

```yaml
name:GitHub Actions Course
version:2.0
active:true
```

**What is wrong?** Find and fix it.

---

## Snippet 2 — The Tab Problem

```yaml
course:
	title: YAML Fundamentals
	level: beginner
	duration: 3
```

**Hint:** Open this in VS Code — look for the red underline.

---

## Snippet 3 — The Boolean Trap

```yaml
settings:
  notifications: on
  country: no
  feature_toggle: yes
  env_type: null
```

**Task:** You want ALL of these to be **strings**, not booleans/null. Fix them.

---

## Snippet 4 — Bad Indentation

```yaml
jobs:
  build:
  runs-on: ubuntu-latest
  steps:
    - name: Checkout
      uses: actions/checkout@v4
```

**What is wrong with the structure?**

---

## Snippet 5 — Colon in Value

```yaml
message: Hello: World
website: http://example.com
path: C:\Users\alice
```

**Task:** Fix all three values so they are proper strings.

---

## Snippet 6 — Wrong List Syntax

```yaml
languages:
  Python
  JavaScript
  Go

ports: -80 -443 -8080
```

**Task:** Rewrite both as correct YAML lists.

---

## Snippet 7 — Mixed Tabs and Spaces (the worst kind)

```yaml
config:
  host: localhost
	port: 5432
  database: mydb
```

**Hint:** One line uses a tab, others use spaces. Find it and fix it.

---

Good luck! Check `exercise-01-solution.yaml` when ready.
