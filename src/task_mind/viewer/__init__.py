"""Task-Mind Viewer - Universal content viewer with presentation and document modes.

This module provides a Chrome-based viewer for displaying various content types:
- Presentation mode: reveal.js-powered slideshows
- Document mode: scrollable documents (Markdown, HTML, PDF, code)

Content is served via the task-mind server and displayed in Chrome browser.
"""

from task_mind.viewer.chrome import ChromeViewer, show_content

__all__ = ["ChromeViewer", "show_content"]
