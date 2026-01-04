# Screenshot Usage Rules (Mandatory Enforcement)

Applies to: `/task-mind.run`, `/task-mind.do`, `/task-mind.recipe`, `/task-mind.test`

## ⛔ Core Prohibition (Task Fails If Violated)

> **Do NOT use screenshots to extract webpage text content. MUST use `get-content` or recipe extraction.**

Screenshot-to-text is inefficient, error-prone, and loses structured information. This is a **hard prohibition**, not a suggestion.

## Mandatory Process After Navigation

```
1. task-mind chrome navigate <url>    ← Navigate
2. task-mind recipe list | grep xxx   ← Check if there's an existing recipe
3. task-mind chrome get-content       ← Use this command to get content when no recipe exists
4. (Optional) task-mind chrome screenshot ← Only for verifying state, NOT for reading
```

## Scenario Enforcement Table

| Scenario | ✅ MUST Do This | ⛔ DO NOT Do This |
|-----|-------------|-------------|
| Get tweet/post content | `task-mind chrome get-content` or recipe | Screenshot and ask AI to "read" |
| Get comment list | `task-mind chrome get-content` or recipe | Screenshot entire comment section |
| Get any page text | `task-mind chrome get-content` or `exec-js` | Screenshot and ask AI to "read" |
| Get DOM structure | `task-mind chrome exec-js` to extract | Screenshot entire page |

## Only Valid Uses of Screenshots

- ✅ **Verify state**: Confirm navigation success, elements loaded
- ✅ **Debug positioning**: Troubleshoot element locating failures
- ✅ **Visual backup**: Record element position (prevent reflow)

## Self-Check Question

Before using `task-mind chrome screenshot`, you MUST answer:

> "Am I planning to use this screenshot to read page content?"
> - If yes → **DO NOT screenshot**, use `task-mind chrome get-content` instead
> - If no → Screenshot is allowed

## Screenshot Commands

```bash
# Basic screenshot
task-mind chrome screenshot output.png

# Full-page screenshot
task-mind chrome screenshot output.png --full-page

# Screenshot in run context (auto-saved to screenshots/)
task-mind run screenshot "step description"
```
