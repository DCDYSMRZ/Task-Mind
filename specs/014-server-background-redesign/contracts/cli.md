# CLI Contract: Server Command Group

**Feature**: 014-server-background-redesign

## Command Structure

```
task-mind server [SUBCOMMAND]
```

## Subcommands

### `task-mind server` (default: start)

Start the web service in background mode.

**Options**:
| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--debug` | flag | false | Run in foreground with verbose logging |

**Behavior**:
- Without `--debug`: Spawns daemon process, returns to prompt within 3 seconds
- With `--debug`: Runs in foreground, blocks terminal, shows live logs

**Exit codes**:
| Code | Meaning |
|------|---------|
| 0 | Server started successfully |
| 1 | Server already running |
| 2 | Port 8093 unavailable |

**Output examples**:

```bash
# Success (background)
$ task-mind server
Task-Mind server started on http://127.0.0.1:8093 (PID: 12345)

# Already running
$ task-mind server
Task-Mind server is already running (PID: 12345)

# Port conflict
$ task-mind server
Error: Port 8093 is in use by chrome (PID: 54321)

# Debug mode
$ task-mind server --debug
  Task-Mind Web Service (Debug Mode)
  ─────────────────────────────────
  Local:   http://127.0.0.1:8093
  API:     http://127.0.0.1:8093/api/docs

  Press Ctrl+C to stop

[2025-12-23 10:30:00] INFO: Uvicorn running...
```

### `task-mind server stop`

Stop the running web service.

**Exit codes**:
| Code | Meaning |
|------|---------|
| 0 | Server stopped successfully |
| 1 | Server not running |

**Output examples**:

```bash
# Success
$ task-mind server stop
Task-Mind server stopped (PID: 12345)

# Not running
$ task-mind server stop
Task-Mind server is not running
```

### `task-mind server status`

Check if the web service is running.

**Exit codes**:
| Code | Meaning |
|------|---------|
| 0 | Server is running |
| 1 | Server is not running |

**Output examples**:

```bash
# Running
$ task-mind server status
Task-Mind server is running
  PID:     12345
  URL:     http://127.0.0.1:8093
  Uptime:  2h 30m

# Not running
$ task-mind server status
Task-Mind server is not running
```

## Files

| File | Purpose |
|------|---------|
| `~/.task-mind/server.pid` | Stores PID of running server |
| `~/.task-mind/server.log` | Server log output (background mode) |

## Deprecation

The existing `task-mind serve` command will be deprecated in favor of `task-mind server`. During transition:
- `task-mind serve` continues to work but shows deprecation warning
- Future version will remove `task-mind serve`
