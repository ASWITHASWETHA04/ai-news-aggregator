"use client";

/**
 * AI Chatbot page — RAG-powered news assistant.
 */

import { useState, useRef, useEffect } from "react";
import ProtectedRoute from "@/components/ProtectedRoute";
import { chatAPI } from "@/lib/api";
import { ChatMessage } from "@/lib/types";
import { useAuth } from "@/context/AuthContext";
import toast from "react-hot-toast";
import { FiSend, FiTrash2, FiDatabase, FiUser, FiCpu } from "react-icons/fi";
import { MdOutlineNewspaper } from "react-icons/md";
import ReactMarkdown from "react-markdown";

// Suggested questions for quick start
const SUGGESTIONS = [
  "Summarize today's AI news",
  "What's happening in tech today?",
  "Give me sports highlights",
  "What are the top business stories?",
  "Explain the latest science news",
];

function MessageBubble({ message }: { message: ChatMessage }) {
  const isUser = message.role === "user";

  return (
    <div className={`flex gap-3 animate-slide-up ${isUser ? "flex-row-reverse" : ""}`}>
      {/* Avatar */}
      <div
        className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
          isUser
            ? "bg-blue-600 text-white"
            : "bg-gradient-to-br from-purple-500 to-blue-600 text-white"
        }`}
      >
        {isUser ? <FiUser className="text-sm" /> : <FiCpu className="text-sm" />}
      </div>

      {/* Bubble */}
      <div
        className={`max-w-[80%] rounded-2xl px-4 py-3 ${
          isUser
            ? "bg-blue-600 text-white rounded-tr-sm"
            : "bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-slate-100 rounded-tl-sm"
        }`}
      >
        {isUser ? (
          <p className="text-sm">{message.content}</p>
        ) : (
          <div className="text-sm prose prose-sm dark:prose-invert max-w-none">
            <ReactMarkdown>{message.content}</ReactMarkdown>
          </div>
        )}

        {/* Sources */}
        {message.sources && message.sources.length > 0 && (
          <div className="mt-2 pt-2 border-t border-slate-200 dark:border-slate-600">
            <p className="text-xs text-slate-400 mb-1">Sources:</p>
            {message.sources.slice(0, 3).map((src, i) => (
              <a
                key={i}
                href={src}
                target="_blank"
                rel="noopener noreferrer"
                className="block text-xs text-blue-400 hover:text-blue-300 truncate"
              >
                {src}
              </a>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function TypingIndicator() {
  return (
    <div className="flex gap-3 animate-fade-in">
      <div className="w-8 h-8 rounded-full bg-gradient-to-br from-purple-500 to-blue-600 flex items-center justify-center flex-shrink-0">
        <FiCpu className="text-white text-sm" />
      </div>
      <div className="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-2xl rounded-tl-sm px-4 py-3">
        <div className="flex gap-1 items-center h-5">
          {[0, 1, 2].map((i) => (
            <div
              key={i}
              className="w-2 h-2 bg-slate-400 rounded-full animate-bounce"
              style={{ animationDelay: `${i * 0.15}s` }}
            />
          ))}
        </div>
      </div>
    </div>
  );
}

export default function ChatPage() {
  const { user } = useAuth();
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      role: "assistant",
      content:
        "Hi! I'm your AI News Assistant powered by RAG technology. I can help you:\n\n- **Summarize** today's news on any topic\n- **Answer questions** about current events\n- **Recommend** articles based on your interests\n\nWhat would you like to know?",
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isIndexing, setIsIndexing] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  const sendMessage = async (text?: string) => {
    const messageText = text || input.trim();
    if (!messageText || isLoading) return;

    const userMessage: ChatMessage = {
      role: "user",
      content: messageText,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      const res = await chatAPI.sendMessage(messageText);
      const aiMessage: ChatMessage = {
        role: "assistant",
        content: res.data.answer,
        sources: res.data.sources,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, aiMessage]);
    } catch (err: any) {
      const errorMsg =
        err.response?.data?.detail || "Failed to get a response. Please try again.";
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: `❌ ${errorMsg}`, timestamp: new Date() },
      ]);
    } finally {
      setIsLoading(false);
      inputRef.current?.focus();
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const clearChat = async () => {
    try {
      await chatAPI.clearHistory();
      setMessages([
        {
          role: "assistant",
          content: "Chat history cleared. How can I help you?",
          timestamp: new Date(),
        },
      ]);
    } catch {
      toast.error("Failed to clear history.");
    }
  };

  const indexNews = async () => {
    setIsIndexing(true);
    try {
      const res = await chatAPI.indexNews();
      toast.success(res.data.message);
    } catch (err: any) {
      toast.error(err.response?.data?.detail || "Indexing failed.");
    } finally {
      setIsIndexing(false);
    }
  };

  return (
    <ProtectedRoute>
      <div className="flex flex-col h-[calc(100vh-8rem)] animate-fade-in">
        {/* Header */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-purple-500 to-blue-600 flex items-center justify-center">
              <FiCpu className="text-white text-lg" />
            </div>
            <div>
              <h1 className="font-bold text-lg text-slate-900 dark:text-slate-100">
                AI News Assistant
              </h1>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                Powered by RAG + MCP Tools
              </p>
            </div>
          </div>
          <div className="flex gap-2">
            <button
              onClick={indexNews}
              disabled={isIndexing}
              className="btn-secondary text-xs flex items-center gap-1.5 py-1.5 px-3"
              title="Index latest news into AI knowledge base"
            >
              <FiDatabase className={isIndexing ? "animate-spin" : ""} />
              {isIndexing ? "Indexing..." : "Index News"}
            </button>
            <button
              onClick={clearChat}
              className="btn-secondary text-xs flex items-center gap-1.5 py-1.5 px-3 text-red-500"
            >
              <FiTrash2 />
              Clear
            </button>
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto space-y-4 pr-2 pb-4">
          {messages.map((msg, i) => (
            <MessageBubble key={i} message={msg} />
          ))}
          {isLoading && <TypingIndicator />}
          <div ref={messagesEndRef} />
        </div>

        {/* Suggestions */}
        {messages.length <= 1 && (
          <div className="flex gap-2 overflow-x-auto pb-3 scrollbar-hide">
            {SUGGESTIONS.map((s) => (
              <button
                key={s}
                onClick={() => sendMessage(s)}
                className="whitespace-nowrap text-xs px-3 py-1.5 rounded-full bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400 hover:bg-blue-100 dark:hover:bg-blue-900/40 transition-colors border border-blue-200 dark:border-blue-800"
              >
                {s}
              </button>
            ))}
          </div>
        )}

        {/* Input */}
        <div className="flex gap-3 items-end">
          <div className="flex-1 relative">
            <textarea
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask about today's news... (Enter to send)"
              rows={1}
              className="input-field resize-none pr-12 min-h-[44px] max-h-32"
              style={{ height: "auto" }}
              onInput={(e) => {
                const target = e.target as HTMLTextAreaElement;
                target.style.height = "auto";
                target.style.height = Math.min(target.scrollHeight, 128) + "px";
              }}
            />
          </div>
          <button
            onClick={() => sendMessage()}
            disabled={!input.trim() || isLoading}
            className="btn-primary p-3 rounded-xl flex-shrink-0"
            aria-label="Send message"
          >
            <FiSend className="text-lg" />
          </button>
        </div>
      </div>
    </ProtectedRoute>
  );
}
