import { useEffect, useRef, useState } from 'react';
import { Terminal } from 'lucide-react';

interface TerminalViewProps {
  steps: Array<{
    timestamp: string;
    type: string;
    content: string;
    tool_name: string | null;
  }>;
  sessionId?: string;
}

/**
 * 完整终端视图 - 显示所有步骤的原始输出，不折叠
 * 如果提供sessionId，会实时tail日志文件
 */
export default function TerminalView({ steps, sessionId }: TerminalViewProps) {
  const terminalRef = useRef<HTMLDivElement>(null);
  const [rawLog, setRawLog] = useState<string>('');
  const [useRawLog, setUseRawLog] = useState(false);

  // 自动滚动到底部
  useEffect(() => {
    if (terminalRef.current) {
      terminalRef.current.scrollTop = terminalRef.current.scrollHeight;
    }
  }, [steps, rawLog]);

  // 实时tail日志文件
  useEffect(() => {
    if (!sessionId || !useRawLog) return;

    const controller = new AbortController();
    const fetchLog = async () => {
      try {
        const response = await fetch(`/api/logs/agent/${sessionId}/stream`, {
          signal: controller.signal,
        });
        
        if (!response.ok) {
          console.error('Failed to fetch log stream');
          return;
        }

        const reader = response.body?.getReader();
        const decoder = new TextDecoder();
        
        if (!reader) return;

        let accumulated = '';
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          
          const chunk = decoder.decode(value, { stream: true });
          accumulated += chunk;
          setRawLog(accumulated);
        }
      } catch (error) {
        if (error instanceof Error && error.name !== 'AbortError') {
          console.error('Error streaming log:', error);
        }
      }
    };

    fetchLog();

    return () => {
      controller.abort();
    };
  }, [sessionId, useRawLog]);

  if (!steps || steps.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-full text-[var(--text-muted)]">
        <Terminal className="icon-scaled-lg mb-scaled-2 opacity-50" />
        <p>No terminal output yet</p>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col">
      {/* 切换按钮 */}
      {sessionId && (
        <div className="flex gap-scaled-2 mb-scaled-2 shrink-0">
          <button
            className={`px-scaled-2 py-scaled-1 text-scaled-xs rounded ${
              !useRawLog ? 'bg-[var(--accent-primary)] text-white' : 'bg-[var(--bg-secondary)] text-[var(--text-muted)]'
            }`}
            onClick={() => setUseRawLog(false)}
          >
            Structured
          </button>
          <button
            className={`px-scaled-2 py-scaled-1 text-scaled-xs rounded ${
              useRawLog ? 'bg-[var(--accent-primary)] text-white' : 'bg-[var(--bg-secondary)] text-[var(--text-muted)]'
            }`}
            onClick={() => setUseRawLog(true)}
          >
            Raw Log (Real-time)
          </button>
        </div>
      )}

      {/* 终端内容 */}
      <div
        ref={terminalRef}
        className="flex-1 overflow-y-auto bg-[var(--bg-elevated)] rounded p-scaled-3 font-mono text-scaled-xs"
        style={{ fontFamily: 'var(--font-geist-mono)' }}
      >
        {useRawLog && rawLog ? (
          <pre className="whitespace-pre-wrap break-words text-[var(--text-primary)]">
            {rawLog}
          </pre>
        ) : (
          steps.map((step, index) => (
            <div key={index} className="mb-scaled-2 border-b border-[var(--border-subtle)] pb-scaled-2">
              <div className="text-[var(--text-muted)] mb-scaled-1">
                [{new Date(step.timestamp).toLocaleTimeString()}] {step.type}
                {step.tool_name && ` - ${step.tool_name}`}
              </div>
              <pre className="whitespace-pre-wrap break-words text-[var(--text-primary)]">
                {step.content}
              </pre>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

