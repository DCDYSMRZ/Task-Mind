# task-mind Common Resources Index

This directory contains rules, guides, and script examples shared by all `/task-mind.dev.*` commands.

## Prerequisites

**This document assumes task-mind has been installed as a global command via `uv tool install task-mind-cli`.**

All examples use the `task-mind <command>` format. If you get `command not found`:

```bash
uv tool install task-mind-cli
```

---

## Command Quick Reference

| Command | Purpose | Documentation |
|------|------|------|
| `/task-mind.run` | Exploration & research (before Recipe creation) | [task-mind.dev.run.md](../task-mind.dev.run.md) |
| `/task-mind.do` | One-time task execution | [task-mind.dev.do.md](../task-mind.dev.do.md) |
| `/task-mind.recipe` | Recipe creation/update | [task-mind.dev.recipe.md](../task-mind.dev.recipe.md) |
| `/task-mind.test` | Recipe testing & validation | [task-mind.dev.test.md](../task-mind.dev.test.md) |
| `task-mind view` | Content viewer (presentations/docs) | See "Content Viewing" section below |

---

## Rules Documentation (rules/)

Core rules, **failure if violated**.

| Document | Applicable Commands | Description |
|------|---------|------|
| [EXECUTION_PRINCIPLES.md](rules/EXECUTION_PRINCIPLES.md) | run, do | Execution principles (intent understanding, tool-driven, trial & error recording) |
| [SCREENSHOT_RULES.md](rules/SCREENSHOT_RULES.md) | All | Screenshot usage rules (use screenshots less, use get-content more) |
| [NAVIGATION_RULES.md](rules/NAVIGATION_RULES.md) | run, do | Prohibition of hallucinated navigation (strictly forbid guessing URLs) |
| [TOOL_PRIORITY.md](rules/TOOL_PRIORITY.md) | run, do | Tool priority (Recipe > task-mind > system commands) |
| [WORKSPACE_RULES.md](rules/WORKSPACE_RULES.md) | run, do | Workspace management (isolation, exclusivity, no cd) |

---

## Guide Documentation (guides/)

Detailed usage guides and best practices.

| Document | Applicable Commands | Description |
|------|---------|------|
| [LOGGING_GUIDE.md](guides/LOGGING_GUIDE.md) | run, do | Logging system (auto/manual, 6 execution_methods) |
| [SELECTOR_PRIORITY.md](guides/SELECTOR_PRIORITY.md) | recipe | Selector priority (ARIA > ID > class) |

---

## Script Examples (scripts/)

Executable workflow examples.

| Script | Applicable Commands | Description |
|------|---------|------|
| [common_commands.sh](scripts/common_commands.sh) | All | Common command quick reference |
| [run_workflow.sh](scripts/run_workflow.sh) | run | Research workflow example |
| [do_workflow.sh](scripts/do_workflow.sh) | do | Task execution workflow example |
| [recipe_workflow.sh](scripts/recipe_workflow.sh) | recipe | Recipe creation workflow example |

---

## Quick Start

### 1. Discover Resources

```bash
task-mind recipe list              # List recipes
task-mind recipe info <name>       # Recipe details
task-mind --help                   # All commands
```

### 2. Browser Operations

```bash
task-mind chrome start             # Start Chrome
task-mind chrome navigate <url>    # Navigate
task-mind chrome click <selector>  # Click
task-mind chrome exec-js <expr> --return-value  # Execute JS
task-mind chrome get-content       # Get content
task-mind chrome screenshot output.png  # Screenshot
```

### 3. Project Management

```bash
task-mind run init "task desc"     # Create project
task-mind run set-context <id>     # Set context
task-mind run release              # Release context
```

### 4. Execute Recipes

```bash
task-mind recipe run <name>
task-mind recipe run <name> --params '{}' --output-file result.json
```

### 5. Content Viewing

```bash
task-mind view slides.md             # Auto-detect mode
task-mind view slides.md --present   # Force presentation mode (reveal.js)
task-mind view README.md --doc       # Force document mode
task-mind view report.pdf            # View PDF
task-mind view config.json           # Format JSON
```

---

## Content Viewing (task-mind view)

Universal content viewer based on pywebview, embedded with reveal.js / PDF.js / highlight.js, **fully offline usable**.

### Two Modes

| Mode | Trigger Condition | Engine | Purpose |
|------|---------|------|------|
| **Presentation mode** | File contains `---` separator, or `--present` | reveal.js | Slideshow presentation |
| **Document mode** | Default, or `--doc` | HTML + highlight.js | Scrollable document |

### Supported Formats

| Format | Presentation Mode | Document Mode |
|------|---------|---------|
| `.md` | reveal.js slides (`---` pagination) | Markdown rendering |
| `.html` | Direct display | Direct rendering |
| `.pdf` | ❌ | PDF.js rendering |
| `.json` | ❌ | Formatting + syntax highlighting |
| `.py/.js/.ts/...` | ❌ | Syntax highlighting |

---

### Presentation Document Specification (Important)

#### File Structure

```markdown
# Presentation Title

First page content (title page)

---

## Second Page Title

Body content, supports all Markdown syntax:

- List item 1
- List item 2

---

## Code Display

​```python
def hello():
    print("syntax highlighting")
​```

---

## Vertical Slide Group

This is the main slide

--

### Sub-slide 1

Press ↓ key to navigate here

--

### Sub-slide 2

Continue downward

---

# Ending Page

Thank you for watching!
```

#### Separator Rules

| Separator | Effect | Navigation Keys |
|--------|------|--------|
| `---` | Horizontal separation (new page) | ← → |
| `--` | Vertical separation (sub-page) | ↑ ↓ |

**Note**: Separators must have blank lines before and after!

```markdown
Content...

---

Next page...
```

#### Supported Markdown Syntax

| Syntax | Example |
|------|------|
| Headings | `# H1` `## H2` `### H3` |
| Lists | `- item` `1. item` |
| Code blocks | ` ```python ` |
| Inline code | `` `code` `` |
| Bold/Italic | `**bold**` `*italic*` |
| Links | `[text](url)` |
| Images | `![alt](path)` |
| Tables | Standard Markdown tables |
| Quotes | `> quote` |

#### Keyboard Shortcuts (During Presentation)

| Key | Function |
|------|------|
| `→` `Space` `N` | Next page |
| `←` `P` | Previous page |
| `↑` `↓` | Vertical navigation |
| `F` | Fullscreen |
| `S` | Speaker notes |
| `O` | Slide overview |
| `B` | Black screen pause |
| `Esc` | Exit fullscreen/overview |
| `/` | Search |

---

### Available Themes

**Dark**: `black`(default), `night`, `moon`, `dracula`, `blood`, `league`

**Light**: `white`, `beige`, `serif`, `simple`, `sky`, `solarized`

```bash
task-mind view slides.md --theme dracula
task-mind view slides.md --theme white --fullscreen
```

---

### Command Options

```bash
task-mind view <file>                    # Auto-detect mode
task-mind view <file> --present          # Force presentation mode
task-mind view <file> --doc              # Force document mode
task-mind view <file> --theme <name>     # Specify theme
task-mind view <file> --fullscreen       # Start fullscreen
task-mind view <file> -w 1920 -h 1080    # Specify window size
task-mind view --stdin                   # Read from stdin
task-mind view -c "# Hello"              # Pass content directly
```

| Option | Short | Description |
|------|--------|------|
| `--present` | `-p` | Force presentation mode |
| `--doc` | `-d` | Force document mode |
| `--theme` | `-t` | Theme name |
| `--fullscreen` | `-f` | Start fullscreen |
| `--width` | `-w` | Window width (default 1280) |
| `--height` | `-h` | Window height (default 800) |
| `--title` | | Window title |
| `--stdin` | | Read from stdin |
| `--content` | `-c` | Pass content string directly |

---

### Auto-Mode Detection Logic

1. `.pdf` file → Document mode
2. `.md` file contains `\n---\n` or `\n--\n` → Presentation mode
3. `.html` file contains `class="reveal"` → Presentation mode
4. Other → Document mode

---

### Complete Presentation Template

```markdown
# Project Name

Subtitle or introduction

Author / Date

---

## Table of Contents

1. Background
2. Core Features
3. Technical Implementation
4. Demo
5. Summary

---

## 1. Background

### Problem Description

- Pain point 1
- Pain point 2

### Solution

Our solution is...

---

## 2. Core Features

### Feature A

Detailed explanation...

--

### Feature B

Detailed explanation...

--

### Feature C

Detailed explanation...

---

## 3. Technical Implementation

​```python
# Core code example
class MyClass:
    def __init__(self):
        pass
​```

---

## 4. Demo

> Screenshots or explanations can go here

---

## 5. Summary

- Key point 1
- Key point 2
- Key point 3

---

# Q&A

Thank you for watching!

Contact info / Links
```

---

## Directory Structure

```
.claude/commands/
├── task-mind.dev.run.md       # Exploration & research command
├── task-mind.dev.do.md        # Task execution command
├── task-mind.dev.recipe.md    # Recipe creation command
├── task-mind.dev.test.md      # Recipe testing command
└── task-mind/
    ├── COMMON.md          # This index document
    ├── rules/             # Core rules
    │   ├── EXECUTION_PRINCIPLES.md
    │   ├── SCREENSHOT_RULES.md
    │   ├── NAVIGATION_RULES.md
    │   ├── TOOL_PRIORITY.md
    │   └── WORKSPACE_RULES.md
    ├── guides/            # Usage guides
    │   ├── LOGGING_GUIDE.md
    │   └── SELECTOR_PRIORITY.md
    └── scripts/           # Script examples
        ├── common_commands.sh
        ├── run_workflow.sh
        ├── do_workflow.sh
        └── recipe_workflow.sh
```
