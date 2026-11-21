"use client";

import { User, Bot, Copy, Check } from "lucide-react";
import { useState } from "react";

interface ChatMessageProps {
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
}

export default function ChatMessage({ role, content, timestamp }: ChatMessageProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const isUser = role === "user";

  return (
    <div
      className={`flex gap-3 animate-fade-in ${isUser ? "flex-row-reverse" : ""}`}
    >
      {/* Avatar */}
      <div
        className={`flex-shrink-0 w-9 h-9 rounded-xl flex items-center justify-center ${
          isUser
            ? "bg-primary-100 dark:bg-primary-900/50 text-primary-600 dark:text-primary-400"
            : "bg-accent-100 dark:bg-accent-900/50 text-accent-600 dark:text-accent-400"
        }`}
      >
        {isUser ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
      </div>

      {/* Message bubble */}
      <div className={`max-w-[80%] ${isUser ? "items-end" : "items-start"}`}>
        <div
          className={`relative group px-4 py-3 rounded-2xl ${
            isUser
              ? "bg-primary-600 text-white rounded-tr-md"
              : "bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-gray-100 rounded-tl-md"
          }`}
        >
          <p className="text-sm leading-relaxed whitespace-pre-wrap">{content}</p>

          {/* Copy button */}
          {!isUser && (
            <button
              onClick={handleCopy}
              className="absolute -bottom-8 right-0 opacity-0 group-hover:opacity-100 p-1.5 rounded-lg bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 transition-all duration-200"
              title="Copy response"
            >
              {copied ? (
                <Check className="w-3.5 h-3.5 text-green-500" />
              ) : (
                <Copy className="w-3.5 h-3.5 text-gray-400" />
              )}
            </button>
          )}
        </div>

        <p
          className={`mt-1.5 text-xs text-gray-400 dark:text-gray-500 ${
            isUser ? "text-right" : "text-left"
          }`}
        >
          {timestamp.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
        </p>
      </div>
    </div>
  );
}
