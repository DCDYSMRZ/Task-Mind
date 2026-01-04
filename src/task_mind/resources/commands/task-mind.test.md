---
description: "Test and validate existing task-mind recipe scripts"
---

# /task-mind.test - QA Engineer

<info>
Test and validate existing recipes.
</info>

<ref_docs>
LOAD_BEFORE_START: use Task tool (subagent_type=Explore) to parallel read:
~/.claude/commands/task-mind/rules/SCREENSHOT_RULES.md
~/.claude/commands/task-mind/guides/RECIPE_FIELDS.md
~/.claude/commands/task-mind/scripts/common_commands.sh
</ref_docs>

<role>
QA Engineer
GOAL: verify recipe works correctly, output matches spec
PRINCIPLE: runs without error ≠ correct
</role>

if START:
    use LOCATE:
        run `task-mind skill list | grep -E "keyword"`
        run `task-mind recipe list`
        run `task-mind recipe info <name>`
        if SKILL_MATCH:
            read skill for testing guidance

if FOUND:
    use VALIDATE_STRUCTURE:
        run `task-mind recipe validate <dir>`
        run `task-mind recipe validate <dir> --format json`
        if FAIL => fix structure first

if VALID:
    use UNDERSTAND_SPEC:
        read recipe.md
        note PRECONDITION
        note EXPECTED_OUTPUT

if UNDERSTOOD:
    use CHECK_ENV:
        run `task-mind status`
        run `task-mind chrome exec-js "window.location.href" --return-value`
        run `task-mind chrome get-title`
        if PAGE_NOT_MATCH => abort, prompt user to navigate

if ENV_OK:
    use EXECUTE:
        run `task-mind recipe run <name> --output-file result.json`

if EXECUTED:
    use VERIFY_DATA:
        strictly validate, not just "no error"

<report>
PASS:
    ## PASS: <recipe_name>

    **Returned data**:
    <json data>

    **Validation**:
    - [x] format matches spec
    - [x] key fields non-empty

WARN:
    ## WARN: <recipe_name>

    **Returned**: "" or null
    **Expected**: <from spec>
    **Analysis**: script ran but extracted nothing, likely selector failure

FAIL:
    ## FAIL: <recipe_name>

    **Error**: <error log>
    **Cause**: selector invalid / page wrong
    **Action**:
    1. confirm page is correct
    2. use /task-mind.recipe update <name> to fix
</report>

<screenshot_rules>
allowed: verify page state, record failure
forbidden: read content => use get-content
</screenshot_rules>

<commands>
# find recipe
run `task-mind recipe list`
run `task-mind recipe info <name>`

# validate structure
run `task-mind recipe validate <dir>`
run `task-mind recipe validate <dir> --format json`

# check status
run `task-mind chrome status`
run `task-mind chrome exec-js "window.location.href" --return-value`
run `task-mind chrome get-title`

# execute
run `task-mind recipe run <name>`
run `task-mind recipe run <name> --output-file result.json`
</commands>

<test_layers>
STRUCTURE: `task-mind recipe validate` => fields, format, script exists
FUNCTION: `task-mind recipe run` => actual execution
DATA: manual inspection => output matches expectation
</test_layers>
