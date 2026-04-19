import React, { useState, useEffect, useRef } from 'react';
import { A2UIProvider, A2UIRenderer, useA2UIActions, ComponentRegistry } from '@a2ui/react';
import { Send, User, Bot, Loader2, BookOpen, ExternalLink } from 'lucide-react';

// Simplified Basic Catalog for v0.8 Protocol
// In v0.8, components receive { node, surfaceId } instead of direct props
const basicCatalog = {
  version: "0.8",
  components: {
    Card: ({ node }: any) => {
      const { title } = node.properties || {};
      return (
        <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-4 my-2 text-left shadow-xl w-full">
          {title && <h3 className="text-xl font-bold mb-2 text-blue-400">{title}</h3>}
          <div className="text-slate-200">{node.children}</div>
        </div>
      );
    },
    Column: ({ node }: any) => <div className="flex flex-col gap-2 w-full">{node.children}</div>,
    Text: ({ node }: any) => <p className="mb-2 text-left">{node.properties?.content || node.properties?.text}</p>,
    Heading: ({ node }: any) => {
      const { level, content } = node.properties || {};
      const Tag = (`h${level || 2}`) as keyof JSX.IntrinsicElements;
      return <Tag className="text-lg font-semibold mb-2 text-left text-white">{content}</Tag>;
    },
    Button: ({ node }: any) => {
      const { label } = node.properties || {};
      return (
        <button className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors mr-2 mb-2">
          {label}
        </button>
      );
    },
    Divider: () => <hr className="border-slate-700 my-4" />,
    List: ({ node }: any) => <ul className="list-disc pl-5 mb-2 text-left">{node.children}</ul>,
    ListItem: ({ node }: any) => <li className="mb-1 text-left">{node.properties?.content || node.properties?.text}</li>,
    DocCard: ({ node }: any) => {
      const { title, description, url, tags } = node.properties || {};
      return (
        <a 
          href={url || '#'} 
          target="_blank" 
          rel="noopener noreferrer"
          className="block bg-slate-800/80 border-l-4 border-indigo-500 p-5 my-3 rounded-r-xl shadow-lg hover:bg-slate-800 hover:border-indigo-400 hover:translate-x-1 transition-all group text-left no-underline cursor-pointer"
        >
          <div className="flex justify-between items-start mb-2">
            <div className="flex items-center gap-2">
              <div className="p-2 bg-indigo-500/20 rounded-lg text-indigo-400 group-hover:scale-110 transition-transform">
                <BookOpen size={20} />
              </div>
              <h4 className="text-lg font-bold text-white line-clamp-1">{title || 'Document'}</h4>
            </div>
            {tags && Array.isArray(tags) && (
              <div className="flex gap-1 flex-wrap justify-end">
                {tags.map((tag: string) => (
                  <span key={tag} className="text-[10px] bg-slate-700 px-2 py-0.5 rounded-full text-slate-300 uppercase tracking-tighter whitespace-nowrap">
                    {tag}
                  </span>
                ))}
              </div>
            )}
          </div>
          <p className="text-sm text-slate-400 mb-4 line-clamp-2">{description}</p>
          <div className="flex items-center gap-1 text-sm font-medium text-blue-400 group-hover:text-blue-300 transition-colors">
            Open Resource <ExternalLink size={14} />
          </div>
        </a>
      );
    }
  }
};

// Register the components in the A2UI Registry
const registry = ComponentRegistry.getInstance();
Object.entries(basicCatalog.components).forEach(([type, component]) => {
  registry.register(type, { component });
});

// Simple but robust direct A2UI JSON mapper
// This avoids fighting with the A2UI v0.8 internal binding system 
// and gracefully renders the exact JSON structure provided by the agent.
const A2UICustomRenderer = ({ data }: { data: any }) => {
  const surfaceData = data.createSurface || data;
  const rawComponents = surfaceData.components || [];

  return (
    <div className="flex flex-col gap-2 w-full">
      {rawComponents.map((comp: any, index: number) => {
        // Use basicCatalog as the source of truth for our UI library
        const Component = basicCatalog.components[comp.type as keyof typeof basicCatalog.components];
        
        if (!Component) {
          console.warn(`[A2UI] Component type "${comp.type}" not found in catalog.`);
          return null;
        }

        // We wrap the agent's props in a structure that mimics the node 
        // to maintain compatibility with our catalog component signatures.
        const mockNode = {
          properties: comp.props,
          children: comp.props?.children || null
        };

        return <Component key={`${comp.type}-${index}`} node={mockNode} />;
      })}
    </div>
  );
};

interface Message {
  role: 'user' | 'assistant';
  content: string;
  a2uiData?: any;
}

function App() {
  const [messages, setMessages] = useState<Message[]>([
    { 
      role: 'assistant', 
      content: 'Welcome! I am your Technical Onboarding Assistant. How can I help you settle in today?' 
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage = input.trim();
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:8000/onboarding_tutor/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: 'new_hire_123',
          session_id: 'onboarding_session',
          message: userMessage
        }),
      });

      if (!response.ok) throw new Error('Failed to connect to backend');

      const data = await response.json();
      const assistantResponse = data.response;

      let cleanText = assistantResponse;
      let a2uiData = null;

      // 1. Try to extract JSON using a highly flexible regex
      // This handles ```json, ```, and varied spacing.
      const a2uiRegex = /```(?:json)?\s*({[\s\S]*?createSurface[\s\S]*?})\s*```/i;
      const match = assistantResponse.match(a2uiRegex);

      if (match) {
        try {
          a2uiData = JSON.parse(match[1]);
          cleanText = assistantResponse.replace(a2uiRegex, '').trim();
        } catch (e) {
          console.error("Failed to parse A2UI JSON from markdown block", e);
        }
      } else {
        // 2. Fallback: If agent forgot backticks completely, try parsing the whole response
        try {
          const parsed = JSON.parse(assistantResponse);
          if (parsed.createSurface || parsed.components) {
            a2uiData = parsed;
            cleanText = "Here are the resources you requested:";
          }
        } catch(e) {
          // It's not raw JSON, just a text response. Do nothing.
        }
      }

      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: cleanText || (a2uiData ? 'Here is the requested information:' : ''),
        a2uiData 
      }]);
    } catch (error) {
      console.error(error);
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: 'Sorry, I encountered an error. Please make sure the backend is running.' 
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen max-h-screen bg-slate-900 text-slate-100 p-4 font-sans">
      <header className="flex items-center justify-between mb-6 pb-4 border-b border-slate-800">
        <div className="flex items-center gap-3">
          <div className="bg-blue-600 p-2 rounded-lg">
            <Bot size={24} />
          </div>
          <div>
            <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-indigo-400 bg-clip-text text-transparent">
              Onboarding Tutor
            </h1>
            <p className="text-sm text-slate-400">Powered by A2UI & ADK</p>
          </div>
        </div>
      </header>

      <main className="flex-1 overflow-hidden flex flex-col glass p-4 mb-4">
        <div className="flex-1 overflow-y-auto pr-2 space-y-4">
          {messages.map((m, i) => (
            <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`flex gap-3 max-w-[85%] ${m.role === 'user' ? 'flex-row-reverse' : ''}`}>
                <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                  m.role === 'user' ? 'bg-blue-600' : 'bg-slate-700'
                }`}>
                  {m.role === 'user' ? <User size={18} /> : <Bot size={18} />}
                </div>
                <div className={`flex flex-col ${m.role === 'user' ? 'items-end' : 'items-start'}`}>
                  {m.content && (
                    <div className={`p-4 rounded-2xl ${
                      m.role === 'user' 
                        ? 'bg-blue-600 text-white rounded-tr-none' 
                        : 'bg-slate-800 border border-slate-700 text-slate-200 rounded-tl-none'
                    }`}>
                      {m.content}
                    </div>
                  )}
                  {m.a2uiData && (
                    <div className="mt-2 w-full overflow-hidden">
                      <React.Suspense fallback={<Loader2 className="animate-spin text-blue-500" />}>
                        <A2UICustomRenderer data={m.a2uiData} />
                      </React.Suspense>
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="flex justify-start">
              <div className="flex gap-3 items-center text-slate-400">
                <div className="w-8 h-8 rounded-full bg-slate-700 flex items-center justify-center">
                  <Bot size={18} />
                </div>
                <Loader2 className="animate-spin" size={18} />
                <span className="text-sm italic text-left">Tutor is thinking...</span>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </main>

      <footer className="relative">
        <div className="flex gap-2 p-2 glass rounded-xl focus-within:ring-2 focus-within:ring-blue-500 transition-all">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            placeholder="Type your message..."
            className="flex-1 bg-transparent border-none outline-none p-2 text-slate-100 placeholder-slate-500"
          />
          <button
            onClick={handleSend}
            disabled={isLoading || !input.trim()}
            className="bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:hover:bg-blue-600 p-2 rounded-lg transition-all"
          >
            <Send size={20} />
          </button>
        </div>
      </footer>
    </div>
  );
}

export default App;
