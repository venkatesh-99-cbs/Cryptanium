import React, { useState, useRef, useEffect } from 'react';
import { useSecurity } from '../context/SecurityContext';

type Message = {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
};

const SUGGESTED_PROMPTS = [
  'Explain the critical SQL injection vulnerability found in the scan.',
  'What are the top 3 security issues I should fix first?',
  'Generate a patch for the secrets exposure issue.',
  'How can I improve my repository trust score?',
  'Summarize the latest security scan results.',
];

const AIAssistant: React.FC = () => {
  const { repositories } = useSecurity();
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'assistant',
      content: "Hello! I'm Cryptanium AI, your dedicated security assistant. I can analyze your repository vulnerabilities, generate remediation plans, and answer any security questions. How can I help you today?",
      timestamp: 'Just now',
    }
  ]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [selectedRepo, setSelectedRepo] = useState(repositories[0]?.id ?? '');
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isTyping]);

  const MOCK_RESPONSES: Record<string, string> = {
    default: "I've analyzed your repositories and found several areas of concern. Based on the latest scan, I recommend prioritizing the critical vulnerabilities in your main service repository. Would you like me to generate a detailed remediation plan?",
    sql: "The SQL injection vulnerability found occurs because user input is directly concatenated into a SQL query string. Here's a patch using parameterized queries:\n\n```python\n# ❌ Vulnerable code\ncursor.execute(f\"SELECT * FROM users WHERE id={user_id}\")\n\n# ✅ Fixed code\ncursor.execute(\"SELECT * FROM users WHERE id=%s\", (user_id,))\n```\n\nThis prevents any malicious SQL from being injected into the query.",
    score: "Your current trust score of **82/100** is in the 'Good' range. To improve it:\n\n1. **Fix the 3 critical vulnerabilities** (+8 points)\n2. **Resolve the exposed AWS credentials** (+5 points)\n3. **Update 12 outdated dependencies** (+3 points)\n\nThis could bring your score to **~98/100**.",
    secrets: "I detected an **AWS Access Key** exposed in `config/aws.py`. Here's what you should do:\n\n1. **Immediately rotate the key** in your AWS Console\n2. **Add secrets to `.gitignore`**\n3. **Use environment variables** or a secrets manager (AWS Secrets Manager, HashiCorp Vault)\n4. **Audit your git history** with `git log --all -p | grep -i 'AKIA'`",
  };

  const getResponse = (msg: string): string => {
    const lower = msg.toLowerCase();
    if (lower.includes('sql') || lower.includes('injection')) return MOCK_RESPONSES.sql;
    if (lower.includes('score') || lower.includes('improve')) return MOCK_RESPONSES.score;
    if (lower.includes('secret') || lower.includes('key') || lower.includes('credential')) return MOCK_RESPONSES.secrets;
    return MOCK_RESPONSES.default;
  };

  const sendMessage = async (content: string) => {
    if (!content.trim()) return;
    const userMsg: Message = { role: 'user', content, timestamp: 'Just now' };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setIsTyping(true);

    await new Promise(res => setTimeout(res, 1200 + Math.random() * 800));

    const aiMsg: Message = {
      role: 'assistant',
      content: getResponse(content),
      timestamp: 'Just now',
    };
    setMessages(prev => [...prev, aiMsg]);
    setIsTyping(false);
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
        const code = part.replace(/```[\w]*\n/, '').replace(/```$/, '');
        return (
          <pre key={i} className="mt-sm bg-background rounded-lg p-md border border-outline-variant font-code-sm text-[12px] text-[#a8b1c9] overflow-x-auto custom-scrollbar">
            <code>{code}</code>
          </pre>
        );
      }
      return (
        <span key={i} className="whitespace-pre-wrap">
          {part.replace(/\*\*(.*?)\*\*/g, (_, m) => m)}
        </span>
      );
    });
  };

  return (
    <div className="flex-1 flex flex-col h-full max-h-[calc(100vh-120px)]">
      {/* Header */}
      <div className="mb-lg flex justify-between items-center">
        <div>
          <h2 className="text-headline-md font-headline-md font-bold text-on-background flex items-center gap-sm">
            <span className="material-symbols-outlined text-primary">smart_toy</span>
            AI Security Assistant
          </h2>
          <p className="text-on-surface-variant text-sm mt-1">Ask about vulnerabilities, get remediation plans, and generate code patches.</p>
        </div>
        <select
          className="bg-surface-container-lowest border border-outline-variant rounded-lg px-4 py-2 text-body-md text-on-background outline-none focus:border-primary text-sm"
          value={selectedRepo}
          onChange={e => setSelectedRepo(e.target.value)}
        >
          <option value="">All Repositories</option>
          {repositories.map(r => (
            <option key={r.id} value={r.id}>{r.name}</option>
          ))}
        </select>
      </div>

      {/* Chat Container */}
      <div className="flex-1 glass-card rounded-xl flex flex-col overflow-hidden">
        {/* Messages */}
        <div className="flex-1 overflow-y-auto custom-scrollbar p-lg space-y-lg">
          {messages.map((msg, i) => (
            <div key={i} className={`flex gap-md items-start ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
              {/* Avatar */}
              <div className={`w-10 h-10 rounded-full flex items-center justify-center shrink-0 border ${msg.role === 'assistant' ? 'bg-primary/10 border-primary/20' : 'bg-surface-container-highest border-outline-variant'}`}>
                <span className={`material-symbols-outlined text-[22px] ${msg.role === 'assistant' ? 'text-primary' : 'text-on-surface-variant'}`}>
                  {msg.role === 'assistant' ? 'smart_toy' : 'person'}
                </span>
              </div>

              {/* Bubble */}
              <div className={`max-w-[75%] flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'}`}>
                <div className={`px-lg py-md rounded-2xl text-body-md text-sm leading-relaxed ${
                  msg.role === 'assistant'
                    ? 'bg-surface-container-high border border-outline-variant/40 text-on-surface rounded-tl-sm'
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
                <span className="text-on-surface-variant text-sm">Analyzing your request...</span>
              </div>
            </div>
          )}
          <div ref={bottomRef} />
        </div>

        {/* Suggestions */}
        {messages.length <= 1 && (
          <div className="px-lg py-md border-t border-outline-variant bg-surface-container/30">
            <p className="text-[11px] font-label-caps text-on-surface-variant mb-sm uppercase tracking-wider">Try asking...</p>
            <div className="flex flex-wrap gap-sm">
              {SUGGESTED_PROMPTS.map(p => (
                <button
                  key={p}
                  onClick={() => sendMessage(p)}
                  className="text-sm text-on-surface-variant bg-surface-container border border-outline-variant px-3 py-1.5 rounded-lg hover:border-primary hover:text-primary transition-all"
                >
                  {p.length > 45 ? `${p.substring(0, 42)}...` : p}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Input Row */}
        <div className="px-lg py-md border-t border-outline-variant bg-surface-container/20">
          <div className="flex items-end gap-sm bg-background border border-outline-variant rounded-xl p-sm focus-within:border-primary transition-all">
            <textarea
              className="flex-1 bg-transparent text-on-background resize-none text-sm placeholder:text-outline outline-none py-1 px-2 max-h-32 custom-scrollbar"
              placeholder="Ask about a vulnerability, request a patch, or get a security recommendation..."
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
          <p className="text-[10px] text-on-surface-variant mt-sm ml-1 opacity-60">Press Enter to send, Shift+Enter for new line.</p>
        </div>
      </div>
    </div>
  );
};

export default AIAssistant;
