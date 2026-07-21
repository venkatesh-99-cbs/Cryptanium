import React, { useState, useRef, useEffect } from 'react';
import { useSecurity } from '../context/SecurityContext';
import { apiClient } from '../services/api';

type Message = {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  isError?: boolean;
};

const SUGGESTED_PROMPTS = [
  'What are the top 3 security issues I should fix first?',
  'Explain the most critical vulnerability found in the scan.',
  'How can I improve my repository trust score?',
  'Summarize the latest security scan results.',
  'What is SQL injection and how do I prevent it?',
  'How do I safely handle secrets and API keys in code?',
];

const AIAssistant: React.FC = () => {
  const { scans } = useSecurity();

  const [messages, setMessages] = useState<Message[]>(() => {
    try { return JSON.parse(localStorage.getItem('cryptanium_ai_messages') || '[]'); } catch { return []; }
  });
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [selectedScanId, setSelectedScanId] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);

  // Auto-select most recent completed scan
  useEffect(() => {
    const completed = scans.find(s => s.status === 'completed' || s.status === 'success');
    if (completed) setSelectedScanId(completed.scan_id);
  }, [scans]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isTyping]);

  // Keep the conversation when the user changes modules or refreshes the page.
  useEffect(() => {
    localStorage.setItem('cryptanium_ai_messages', JSON.stringify(messages.slice(-50)));
  }, [messages]);

  const addMessage = (msg: Message) => setMessages(prev => [...prev, msg]);

  const sendMessage = async (content: string) => {
    if (!content.trim() || isTyping) return;

    const userMsg: Message = {
      role: 'user',
      content,
      timestamp: new Date().toLocaleTimeString(),
    };
    addMessage(userMsg);
    setInput('');
    setIsTyping(true);
    setError(null);

    try {
      const result = await apiClient.aiChat(content, selectedScanId);
      addMessage({
        role: 'assistant',
        content: result.response,
        timestamp: new Date().toLocaleTimeString(),
      });
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'AI request failed';
      setError(msg);
      addMessage({
        role: 'assistant',
        content: `⚠️ Error: ${msg}\n\nPlease check that the backend is running and OPENROUTER_API_KEY is configured in your .env file.`,
        timestamp: new Date().toLocaleTimeString(),
        isError: true,
      });
    } finally {
      setIsTyping(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage(input);
    }
  };

  const renderContent = (content: string) => {
    const parts = content.split(/(```[\w]*\n[\s\S]*?```)/g);
    return parts.map((part, i) => {
      if (part.startsWith('```')) {
        const langMatch = part.match(/^```([\w]*)\n/);
        const lang = langMatch?.[1] || '';
        const code = part.replace(/^```[\w]*\n/, '').replace(/```$/, '');
        return (
          <div key={i} className="mt-sm">
            {lang && (
              <div className="bg-surface-container-highest px-3 py-1 rounded-t-lg text-[10px] font-label-caps text-outline-variant border border-outline-variant border-b-0 flex items-center justify-between">
                <span>{lang}</span>
                <button
                  onClick={() => navigator.clipboard.writeText(code)}
                  className="hover:text-primary transition-colors text-[10px]"
                >
                  Copy
                </button>
              </div>
            )}
            <pre className={`bg-background ${lang ? 'rounded-t-none' : ''} rounded-lg p-md border border-outline-variant font-code-sm text-[12px] text-[#a8b1c9] overflow-x-auto custom-scrollbar`}>
              <code>{code}</code>
            </pre>
          </div>
        );
      }

      // Render **bold** text
      const rendered = part.split(/(\*\*.*?\*\*)/g).map((segment, j) => {
        if (segment.startsWith('**') && segment.endsWith('**')) {
          return <strong key={j} className="font-bold text-on-background">{segment.slice(2, -2)}</strong>;
        }
        return <span key={j} className="whitespace-pre-wrap">{segment}</span>;
      });

      return <span key={i}>{rendered}</span>;
    });
  };

  const selectedScan = scans.find(s => s.scan_id === selectedScanId);

  return (
    <div className="flex-1 flex flex-col h-full max-h-[calc(100vh-120px)]">
      {/* Header */}
      <div className="mb-lg flex justify-between items-start flex-wrap gap-md">
        <div>
          <h2 className="text-headline-md font-headline-md font-bold text-on-background flex items-center gap-sm">
            <span className="material-symbols-outlined text-primary">smart_toy</span>
            AI Security Assistant
          </h2>
          <p className="text-on-surface-variant text-sm mt-1">
            Powered by <code className="font-code-sm text-primary text-xs">nvidia/nemotron-4-340b-instruct</code> via OpenRouter
          </p>
        </div>
        <div className="flex flex-col gap-1">
          <label className="text-[10px] font-label-caps text-on-surface-variant uppercase">Scan Context</label>
          <select
            className="bg-surface-container-lowest border border-outline-variant rounded-lg px-4 py-2 text-body-md text-on-background outline-none focus:border-primary text-sm"
            value={selectedScanId ?? ''}
            onChange={e => setSelectedScanId(e.target.value ? Number(e.target.value) : null)}
          >
            <option value="">No context (general)</option>
            {scans.map(s => (
              <option key={s.scan_id} value={s.scan_id}>
                {s.repository_name} — Score {s.trust_score}/100
              </option>
            ))}
          </select>
          {selectedScan && (
            <p className="text-[10px] text-on-surface-variant">
              {selectedScan.findings_count} findings · Trust Score {selectedScan.trust_score}/100
            </p>
          )}
        </div>
      </div>

      {/* Chat Container */}
      <div className="flex-1 glass-card rounded-xl flex flex-col overflow-hidden">
        {/* Messages */}
        <div className="flex-1 overflow-y-auto custom-scrollbar p-lg space-y-lg">

          {/* Welcome state (empty) */}
          {messages.length === 0 && (
            <div className="flex flex-col items-center justify-center h-full text-center py-xl">
              <div className="w-20 h-20 rounded-full bg-primary/10 border border-primary/20 flex items-center justify-center mb-lg">
                <span className="material-symbols-outlined text-[48px] text-primary">smart_toy</span>
              </div>
              <h3 className="text-headline-md font-bold text-on-background mb-sm">
                Cryptanium AI Ready
              </h3>
              <p className="text-on-surface-variant text-sm max-w-md">
                Ask about your security findings, request remediation guidance, or get AI-powered code fixes.
                {selectedScanId
                  ? ' I have context from your selected scan.'
                  : ' Select a scan above to give me context.'}
              </p>
            </div>
          )}

          {messages.map((msg, i) => (
            <div key={i} className={`flex gap-md items-start ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
              {/* Avatar */}
              <div className={`w-10 h-10 rounded-full flex items-center justify-center shrink-0 border ${
                msg.role === 'assistant'
                  ? msg.isError ? 'bg-error/10 border-error/20' : 'bg-primary/10 border-primary/20'
                  : 'bg-surface-container-highest border-outline-variant'
              }`}>
                <span className={`material-symbols-outlined text-[22px] ${
                  msg.role === 'assistant'
                    ? msg.isError ? 'text-error' : 'text-primary'
                    : 'text-on-surface-variant'
                }`}>
                  {msg.role === 'assistant' ? (msg.isError ? 'error' : 'smart_toy') : 'person'}
                </span>
              </div>

              {/* Bubble */}
              <div className={`max-w-[80%] flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'}`}>
                <div className={`px-lg py-md rounded-2xl text-body-md text-sm leading-relaxed ${
                  msg.role === 'assistant'
                    ? msg.isError
                      ? 'bg-error/10 border border-error/20 text-on-surface rounded-tl-sm'
                      : 'bg-surface-container-high border border-outline-variant/40 text-on-surface rounded-tl-sm'
                    : 'bg-[#7B61FF] text-white rounded-tr-sm'
                }`}>
                  {renderContent(msg.content)}
                </div>
                <span className="text-[10px] text-on-surface-variant mt-1 px-1">{msg.timestamp}</span>
              </div>
            </div>
          ))}

          {/* Typing Indicator */}
          {isTyping && (
            <div className="flex gap-md items-start">
              <div className="w-10 h-10 rounded-full flex items-center justify-center shrink-0 border bg-primary/10 border-primary/20">
                <span className="material-symbols-outlined text-[22px] text-primary">smart_toy</span>
              </div>
              <div className="px-lg py-md rounded-2xl rounded-tl-sm bg-surface-container-high border border-outline-variant/40 flex items-center gap-sm">
                <div className="flex gap-1 items-center">
                  <span className="w-2 h-2 rounded-full bg-primary animate-bounce" style={{ animationDelay: '0ms' }} />
                  <span className="w-2 h-2 rounded-full bg-primary animate-bounce" style={{ animationDelay: '150ms' }} />
                  <span className="w-2 h-2 rounded-full bg-primary animate-bounce" style={{ animationDelay: '300ms' }} />
                </div>
                <span className="text-on-surface-variant text-sm">Analyzing with Nemotron AI...</span>
              </div>
            </div>
          )}

          <div ref={bottomRef} />
        </div>

        {/* Suggestions (shown until first message) */}
        {messages.length === 0 && (
          <div className="px-lg py-md border-t border-outline-variant bg-surface-container/30">
            <p className="text-[11px] font-label-caps text-on-surface-variant mb-sm uppercase tracking-wider">Try asking...</p>
            <div className="flex flex-wrap gap-sm">
              {SUGGESTED_PROMPTS.map(p => (
                <button
                  key={p}
                  onClick={() => sendMessage(p)}
                  disabled={isTyping}
                  className="text-sm text-on-surface-variant bg-surface-container border border-outline-variant px-3 py-1.5 rounded-lg hover:border-primary hover:text-primary transition-all disabled:opacity-40"
                >
                  {p.length > 50 ? `${p.substring(0, 47)}...` : p}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Input Row */}
        <div className="px-lg py-md border-t border-outline-variant bg-surface-container/20">
          {error && (
            <div className="mb-sm text-xs text-error flex items-center gap-xs">
              <span className="material-symbols-outlined text-[14px]">error</span>
              {error}
            </div>
          )}
          <div className="flex items-end gap-sm bg-background border border-outline-variant rounded-xl p-sm focus-within:border-primary transition-all">
            <textarea
              className="flex-1 bg-transparent text-on-background resize-none text-sm placeholder:text-outline outline-none py-1 px-2 max-h-32 custom-scrollbar"
              placeholder="Ask about vulnerabilities, request a patch, or get security recommendations..."
              rows={1}
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              onInput={e => {
                const el = e.target as HTMLTextAreaElement;
                el.style.height = 'auto';
                el.style.height = `${Math.min(el.scrollHeight, 128)}px`;
              }}
            />
            <button
              onClick={() => sendMessage(input)}
              disabled={!input.trim() || isTyping}
              className="w-10 h-10 bg-[#7B61FF] hover:bg-[#9D83FF] text-white rounded-lg flex items-center justify-center transition-all disabled:opacity-40 disabled:cursor-not-allowed shrink-0"
            >
              <span className="material-symbols-outlined text-[20px]">send</span>
            </button>
          </div>
          <p className="text-[10px] text-on-surface-variant mt-sm ml-1 opacity-60">
            Press Enter to send · Shift+Enter for new line · Model: nvidia/nemotron-4-340b-instruct
          </p>
        </div>
      </div>
    </div>
  );
};

export default AIAssistant;
