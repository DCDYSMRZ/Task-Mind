"""Windows Registry Run key autostart management."""

import shutil
import sys
from pathlib import Path

from .base import AutostartManager


class WindowsAutostartManager(AutostartManager):
    """Manage autostart via Windows Registry Run key.

    Adds an entry to HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Run
    that runs 'task-mind server start' at user login.
    """

    REGISTRY_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
    VALUE_NAME = "FragoServer"

    @property
    def platform_name(self) -> str:
        return "Windows Registry"

    @property
    def config_path(self) -> Path:
        # Registry doesn't have a file path, return a pseudo-path for display
        return Path(f"HKEY_CURRENT_USER\\{self.REGISTRY_KEY}\\{self.VALUE_NAME}")

    def _get_task_mind_path(self) -> str:
        """Get the full path to the task-mind executable."""
        task_mind_path = shutil.which("task-mind")
        if task_mind_path:
            return task_mind_path
        # Try to find task-mind.exe in Python Scripts directory
        scripts_dir = Path(sys.executable).parent / "Scripts"
        task_mind_exe = scripts_dir / "task-mind.exe"
        if task_mind_exe.exists():
            return str(task_mind_exe)
        return "task-mind"  # Hope it's in PATH at login

    def _build_command(self) -> str:
        """Build the autostart command with proper PATH setup."""
        task_mind_path = self._get_task_mind_path()
        # Quote path if it contains spaces
        if " " in task_mind_path:
            task_mind_cmd = f'"{task_mind_path}"'
        else:
            task_mind_cmd = task_mind_path

        # Collect extra paths that may not be in system PATH
        extra_paths = self._collect_environment_path()
        if extra_paths:
            # Use cmd /c to set PATH before running task-mind
            # %PATH% preserves existing PATH, extra_paths adds node/claude locations
            return f'cmd /c "set PATH={extra_paths};%PATH% && {task_mind_cmd} server start"'
        else:
            return f"{task_mind_cmd} server start"

    def enable(self) -> tuple[bool, str]:
        """Enable autostart by adding Registry Run key."""
        try:
            import winreg

            command = self._build_command()

            # Open the Run key
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                self.REGISTRY_KEY,
                0,
                winreg.KEY_SET_VALUE,
            )

            try:
                winreg.SetValueEx(
                    key,
                    self.VALUE_NAME,
                    0,
                    winreg.REG_SZ,
                    command,
                )
            finally:
                winreg.CloseKey(key)

            return True, f"Autostart enabled ({self.platform_name})"

        except ImportError:
            return False, "winreg module not available (not running on Windows?)"
        except PermissionError:
            return False, "Permission denied accessing registry"
        except Exception as e:
            return False, f"Failed to enable autostart: {e}"

    def disable(self) -> tuple[bool, str]:
        """Disable autostart by removing Registry Run key."""
        try:
            import winreg

            # Open the Run key
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                self.REGISTRY_KEY,
                0,
                winreg.KEY_SET_VALUE,
            )

            try:
                winreg.DeleteValue(key, self.VALUE_NAME)
            except FileNotFoundError:
                # Value doesn't exist, that's fine
                return True, "Autostart was not enabled"
            finally:
                winreg.CloseKey(key)

            return True, "Autostart disabled"

        except ImportError:
            return False, "winreg module not available (not running on Windows?)"
        except PermissionError:
            return False, "Permission denied accessing registry"
        except Exception as e:
            return False, f"Failed to disable autostart: {e}"

    def is_enabled(self) -> bool:
        """Check if Registry Run key exists."""
        try:
            import winreg

            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                self.REGISTRY_KEY,
                0,
                winreg.KEY_READ,
            )

            try:
                winreg.QueryValueEx(key, self.VALUE_NAME)
                return True
            except FileNotFoundError:
                return False
            finally:
                winreg.CloseKey(key)

        except ImportError:
            return False
        except Exception:
            return False
