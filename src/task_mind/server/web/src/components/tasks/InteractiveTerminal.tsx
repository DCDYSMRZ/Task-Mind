import { useEffect, useRef } from 'react';
import { Terminal } from 'xterm';
import { FitAddon } from 'xterm-addon-fit';
import 'xterm/css/xterm.css';

interface InteractiveTerminalProps {
  sessionId: string;
}

/**
 * 交互式终端组件 - 使用xterm.js连接到后端PTY
 */
export default function InteractiveTerminal({ sessionId }: InteractiveTerminalProps) {
  const terminalRef = useRef<HTMLDivElement>(null);
  const xtermRef = useRef<Terminal | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const fitAddonRef = useRef<FitAddon | null>(null);

  useEffect(() => {
    if (!terminalRef.current) return;

    // 创建xterm实例
    const term = new Terminal({
      cursorBlink: true,
      fontSize: 13,
      fontFamily: 'Menlo, Monaco, "Courier New", monospace',
      lineHeight: 1.2,
      letterSpacing: 0,
      theme: {
        background: '#1e1e1e',
        foreground: '#d4d4d4',
        cursor: '#d4d4d4',
        black: '#000000',
        red: '#cd3131',
        green: '#0dbc79',
        yellow: '#e5e510',
        blue: '#2472c8',
        magenta: '#bc3fbc',
        cyan: '#11a8cd',
        white: '#e5e5e5',
        brightBlack: '#666666',
        brightRed: '#f14c4c',
        brightGreen: '#23d18b',
        brightYellow: '#f5f543',
        brightBlue: '#3b8eea',
        brightMagenta: '#d670d6',
        brightCyan: '#29b8db',
        brightWhite: '#e5e5e5',
      },
    });

    const fitAddon = new FitAddon();
    term.loadAddon(fitAddon);
    term.open(terminalRef.current);
    fitAddon.fit();

    xtermRef.current = term;
    fitAddonRef.current = fitAddon;

    // 连接WebSocket
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/api/terminal/${sessionId}`;
    const ws = new WebSocket(wsUrl);
    // Receive PTY output as binary to avoid corrupting ANSI sequences
    ws.binaryType = 'arraybuffer';
    wsRef.current = ws;

    ws.onopen = () => {
      console.log('Terminal WebSocket connected');
      // 发送初始尺寸
      ws.send(JSON.stringify({
        type: 'resize',
        rows: term.rows,
        cols: term.cols,
      }));
    };

    ws.onmessage = (event) => {
      // Server may send:
      // - binary PTY bytes (preferred)
      // - JSON error messages
      const data = event.data as unknown;
      if (typeof data === 'string') {
        try {
          const message = JSON.parse(data) as { type?: string; message?: string };
          if (message.type === 'error') {
            term.write(`\r\n\x1b[31mError: ${message.message || 'Unknown error'}\x1b[0m\r\n`);
          }
        } catch {
          // If it's plain text, write it directly
          term.write(data);
        }
        return;
      }

      // ArrayBuffer (binaryType='arraybuffer') or Blob (browser dependent)
      if (data instanceof ArrayBuffer) {
        term.write(new Uint8Array(data));
        return;
      }
      if (data instanceof Blob) {
        data.arrayBuffer().then((buf) => term.write(new Uint8Array(buf)));
      }
    };

    ws.onerror = (error) => {
      console.error('Terminal WebSocket error:', error);
      term.write('\r\n\x1b[31mConnection error\x1b[0m\r\n');
    };

    ws.onclose = (event) => {
      console.log('Terminal WebSocket closed:', event.code, event.reason);
      term.write('\r\n\x1b[33mConnection closed\x1b[0m\r\n');
    };

    // 处理用户输入
    term.onData((data) => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({
          type: 'input',
          data: data,
        }));
      }
    });

    // 处理窗口大小变化
    const handleResize = () => {
      fitAddon.fit();
      if (ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({
          type: 'resize',
          rows: term.rows,
          cols: term.cols,
        }));
      }
    };

    window.addEventListener('resize', handleResize);

    // 清理
    return () => {
      window.removeEventListener('resize', handleResize);
      ws.close();
      term.dispose();
    };
  }, [sessionId]);

  return (
    <div 
      ref={terminalRef} 
      className="h-full w-full"
      style={{ padding: '8px' }}
    />
  );
}

