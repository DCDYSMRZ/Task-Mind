import { useEffect, useRef, useState } from 'react';
import { X, Maximize2, Minimize2 } from 'lucide-react';
import InteractiveTerminal from './InteractiveTerminal';

interface FloatingTerminalProps {
  sessionId: string;
  onClose: () => void;
}

export default function FloatingTerminal({ sessionId, onClose }: FloatingTerminalProps) {
  const [position, setPosition] = useState({ x: 100, y: 100 });
  const [size, setSize] = useState({ width: 800, height: 600 });
  const [isMaximized, setIsMaximized] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  const [isResizing, setIsResizing] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
  const [resizeStart, setResizeStart] = useState({ x: 0, y: 0, width: 0, height: 0 });
  const windowRef = useRef<HTMLDivElement>(null);

  const handleMouseDown = (e: React.MouseEvent) => {
    if (isMaximized) return;
    setIsDragging(true);
    setDragStart({ x: e.clientX - position.x, y: e.clientY - position.y });
  };

  const handleResizeMouseDown = (e: React.MouseEvent) => {
    if (isMaximized) return;
    e.stopPropagation();
    setIsResizing(true);
    setResizeStart({ x: e.clientX, y: e.clientY, width: size.width, height: size.height });
  };

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (isDragging) {
        setPosition({ x: e.clientX - dragStart.x, y: e.clientY - dragStart.y });
      } else if (isResizing) {
        const newWidth = Math.max(400, resizeStart.width + (e.clientX - resizeStart.x));
        const newHeight = Math.max(300, resizeStart.height + (e.clientY - resizeStart.y));
        setSize({ width: newWidth, height: newHeight });
      }
    };

    const handleMouseUp = () => {
      setIsDragging(false);
      setIsResizing(false);
    };

    if (isDragging || isResizing) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
      return () => {
        document.removeEventListener('mousemove', handleMouseMove);
        document.removeEventListener('mouseup', handleMouseUp);
      };
    }
  }, [isDragging, isResizing, dragStart, resizeStart]);

  const toggleMaximize = () => {
    setIsMaximized(!isMaximized);
  };

  const windowStyle = isMaximized
    ? { top: 0, left: 0, width: '100vw', height: '100vh' }
    : { top: position.y, left: position.x, width: size.width, height: size.height };

  return (
    <div
      ref={windowRef}
      className="fixed bg-[#1e1e1e] border border-[#3e3e3e] shadow-2xl flex flex-col z-50"
      style={windowStyle}
    >
      {/* Title bar */}
      <div
        className="flex items-center justify-between px-4 py-2 bg-[#2d2d2d] border-b border-[#3e3e3e] cursor-move select-none"
        onMouseDown={handleMouseDown}
      >
        <span className="text-sm text-[#d4d4d4]">Live PTY - {sessionId.slice(0, 8)}</span>
        <div className="flex items-center gap-2">
          <button
            className="p-1 hover:bg-[#3e3e3e] rounded"
            onClick={toggleMaximize}
          >
            {isMaximized ? (
              <Minimize2 className="w-4 h-4 text-[#d4d4d4]" />
            ) : (
              <Maximize2 className="w-4 h-4 text-[#d4d4d4]" />
            )}
          </button>
          <button
            className="p-1 hover:bg-[#e81123] rounded"
            onClick={onClose}
          >
            <X className="w-4 h-4 text-[#d4d4d4]" />
          </button>
        </div>
      </div>

      {/* Terminal content */}
      <div className="flex-1 overflow-hidden bg-[#1e1e1e]">
        <InteractiveTerminal sessionId={sessionId} />
      </div>

      {/* Resize handle */}
      {!isMaximized && (
        <div
          className="absolute bottom-0 right-0 w-4 h-4 cursor-se-resize"
          onMouseDown={handleResizeMouseDown}
          style={{
            background: 'linear-gradient(135deg, transparent 50%, #666 50%)',
          }}
        />
      )}
    </div>
  );
}

