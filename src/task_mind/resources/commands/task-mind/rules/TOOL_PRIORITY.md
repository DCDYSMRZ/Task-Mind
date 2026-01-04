# Tool Priority

Applies to: `/task-mind.run`, `/task-mind.do`

## Priority Order

```
1. Existing Recipe            ← Highest priority
2. task-mind commands              ← Universal across agents
3. System or third-party commands ← Powerful functionality
4. Claude Code built-in tools  ← Last resort
```

## ⚠️ CRITICAL: WebSearch Prohibition Rule

**WebSearch causes system crash in desktop environments!**

```
if GUI_AVAILABLE (desktop mode):
    WebSearch => FORBIDDEN (causes system crash!)
    MUST USE: task-mind chrome navigate "https://google.com/search?q=..."

if HEADLESS (no GUI):
    WebSearch => allowed as fallback
```

## Scenario Comparison

- **Search info**: ❌ `WebSearch` (crashes in desktop!) → ✅ `task-mind chrome navigate "https://google.com/search?q=..."`
- **View webpage**: ❌ `Fetch` → ✅ `task-mind chrome navigate <url>` + `get-content`
- **Extract data**: ❌ Hand-write JS → ✅ Check `task-mind recipe list` first
- **File operations**: ❌ Manual creation → ✅ Use Claude Code's Write/Edit tools

## Why This Design

### 1. Recipe Has Highest Priority

- **Reusable**: Verified automation workflows
- **Stable**: Contains error handling and fallback selectors
- **Documented**: Has usage instructions and preconditions

### 2. task-mind Commands Come Second

- **Universal across agents**: Can be used in run/do/recipe/test
- **Auto logging**: CDP commands automatically logged to execution.jsonl
- **Unified interface**: Consistent `task-mind <command>` format

### 3. System Commands

- **Powerful**: `jq` for JSON processing, `ffmpeg` for video
- **Flexible composition**: Shell features like pipes, redirects

### 4. Claude Code Tools as Fallback

- **File operations**: Read/Write/Edit/Glob/Grep
- **Auxiliary functions**: AskUserQuestion, TodoWrite
- Use only when above tools cannot satisfy requirements

## Discovering Existing Recipes

```bash
# List all Recipes
task-mind recipe list

# AI format (JSON)
task-mind recipe list --format json

# View specific Recipe details
task-mind recipe info <recipe_name>

# Search related Recipes
task-mind recipe list | grep "keyword"
```

## Command Help

```bash
# View all task-mind commands
task-mind --help

# View specific command usage
task-mind <command> --help
```
