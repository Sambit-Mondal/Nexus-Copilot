'use client';

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Message, Citation } from './types';
import { streamQuery, generateSessionId } from './api';

interface ChatInterfaceProps {
  sessionId: string;
  onError: (error: string) => void;
}

export const ChatInterface: React.FC<ChatInterfaceProps> = ({
  sessionId,
  onError,
}) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [currentResponse, setCurrentResponse] = useState('');
  const [currentCitations, setCurrentCitations] = useState<Citation[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, currentResponse, scrollToBottom]);

  const handleSubmit = useCallback(
    async (e: React.FormEvent) => {
      e.preventDefault();

      if (!inputValue.trim() || isLoading) {
        return;
      }

      const userQuery = inputValue.trim();
      setInputValue('');

      // Add user message
      const userMessage: Message = {
        id: `msg_${Date.now()}_user`,
        role: 'user',
        content: userQuery,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, userMessage]);
      setIsLoading(true);
      setCurrentResponse('');
      setCurrentCitations([]);

      // Create abort controller for streaming
      abortControllerRef.current = new AbortController();

      try {
        let finalResponse = '';
        let finalCitations: Citation[] = [];
        
        await new Promise<void>((resolve, reject) => {
          streamQuery(sessionId, userQuery, {
            onChunk: (chunk: string) => {
              finalResponse += chunk;
              setCurrentResponse((prev) => prev + chunk);
            },
            onCitation: (citations: Citation[]) => {
              finalCitations = citations;
              setCurrentCitations(citations);
            },
            onComplete: () => {
              resolve();
            },
            onError: (error: Error) => {
              reject(error);
            },
            signal: abortControllerRef.current?.signal,
          });
        });

        // Add assistant message with collected data
        const assistantMessage: Message = {
          id: `msg_${Date.now()}_assistant`,
          role: 'assistant',
          content: finalResponse,
          citations: finalCitations,
          timestamp: new Date(),
        };

        setMessages((prev) => [...prev, assistantMessage]);
      } catch (error) {
        const errorMessage =
          error instanceof Error ? error.message : 'Failed to get response';
        onError(errorMessage);
      } finally {
        setIsLoading(false);
        setCurrentResponse('');
        setCurrentCitations([]);
        abortControllerRef.current = null;
      }
    },
    [inputValue, isLoading, sessionId, onError]
  );

  const handleCancel = useCallback(() => {
    abortControllerRef.current?.abort();
    setIsLoading(false);
    setCurrentResponse('');
    setCurrentCitations([]);
  }, []);

  return (
    <div className="flex flex-col h-full bg-gradient-to-b from-[#0a0a0a] to-[#121212]">
      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        {messages.length === 0 ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <div className="text-6xl mb-6 animate-pulse-glow">💬</div>
              <p className="text-xl font-semibold text-white mb-3">Start a conversation</p>
              <p className="text-sm text-gray-400 max-w-xs">
                Ask about your documents or get financial insights powered by AI
              </p>
            </div>
          </div>
        ) : (
          <>
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex gap-3 ${
                  message.role === 'user' ? 'justify-end' : 'justify-start'
                } animate-slide-in-up`}
              >
                {/* Avatar - Assistant */}
                {message.role === 'assistant' && (
                  <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-emerald-500 to-green-600 flex items-center justify-center text-white font-bold text-sm">
                    🤖
                  </div>
                )}

                {/* Message Content */}
                <div className="flex flex-col gap-2 max-w-xs lg:max-w-md xl:max-w-lg">
                  <div
                    className={`px-4 py-3 rounded-2xl ${
                      message.role === 'user'
                        ? 'bg-gradient-to-r from-blue-600 to-emerald-600 text-white rounded-br-none shadow-lg'
                        : 'bg-[#1a1a1a] text-gray-100 rounded-bl-none border border-[rgba(255,255,255,0.08)]'
                    }`}
                  >
                    <p className="text-sm leading-relaxed">{message.content}</p>
                  </div>

                  {/* Citations at the end */}
                  {message.citations && message.citations.length > 0 && (
                    <div className="px-1 space-y-1">
                      <p className="text-xs text-gray-500 font-medium">Sources:</p>
                      <div className="flex flex-wrap gap-2">
                        {message.citations.map((citation, idx) => (
                          <div
                            key={idx}
                            className="text-xs px-2 py-1 rounded-full bg-[rgba(16,185,129,0.15)] border border-[rgba(16,185,129,0.3)] text-emerald-300 hover:bg-[rgba(16,185,129,0.25)] transition"
                            title={`Page ${citation.page_number || 'N/A'} - ${Math.round(citation.confidence * 100)}% confidence`}
                          >
                            📄 {citation.filename}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>

                {/* Avatar - User */}
                {message.role === 'user' && (
                  <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center text-white font-bold text-sm">
                    👤
                  </div>
                )}
              </div>
            ))}

            {/* Current streaming response */}
            {isLoading && currentResponse && (
              <div className="flex gap-3 justify-start animate-slide-in-up">
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-emerald-500 to-green-600 flex items-center justify-center text-white font-bold text-sm">
                  🤖
                </div>
                <div className="flex flex-col gap-2 max-w-xs lg:max-w-md xl:max-w-lg">
                  <div className="max-w-xs lg:max-w-md xl:max-w-lg px-4 py-3 rounded-2xl bg-[#1a1a1a] text-gray-100 rounded-bl-none border border-[rgba(255,255,255,0.08)]">
                    <p className="text-sm leading-relaxed">{currentResponse}</p>
                    <div className="mt-2 flex items-center space-x-1">
                      <div className="w-2 h-2 bg-emerald-400 rounded-full animate-typing-dots"></div>
                      <div className="w-2 h-2 bg-emerald-400 rounded-full animate-typing-dots delay-100"></div>
                      <div className="w-2 h-2 bg-emerald-400 rounded-full animate-typing-dots delay-200"></div>
                    </div>
                  </div>

                  {/* Citations at the end */}
                  {currentCitations && currentCitations.length > 0 && (
                    <div className="px-1 space-y-1">
                      <p className="text-xs text-gray-500 font-medium">Sources:</p>
                      <div className="flex flex-wrap gap-2">
                        {currentCitations.map((citation, idx) => (
                          <div
                            key={idx}
                            className="text-xs px-2 py-1 rounded-full bg-[rgba(16,185,129,0.15)] border border-[rgba(16,185,129,0.3)] text-emerald-300"
                          >
                            📄 {citation.filename}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}

            {isLoading && !currentResponse && (
              <div className="flex gap-3 justify-start animate-slide-in-up">
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-emerald-500 to-green-600 flex items-center justify-center text-white font-bold text-sm">
                  🤖
                </div>
                <div className="px-4 py-3 rounded-2xl bg-[#1a1a1a] text-gray-100 rounded-bl-none border border-[rgba(255,255,255,0.08)]">
                  <div className="flex space-x-2">
                    <div className="w-2 h-2 bg-emerald-400 rounded-full animate-typing-dots"></div>
                    <div className="w-2 h-2 bg-emerald-400 rounded-full animate-typing-dots delay-100"></div>
                    <div className="w-2 h-2 bg-emerald-400 rounded-full animate-typing-dots delay-200"></div>
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      {/* Input Area */}
      <div className="border-t border-[rgba(255,255,255,0.08)] p-6 bg-[#121212] backdrop-blur-sm">
        <form onSubmit={handleSubmit} className="space-y-3">
          <div className="flex gap-3">
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder="Ask a question about your documents..."
              disabled={isLoading}
              className="flex-1 px-4 py-3 bg-[#1a1a1a] border border-[rgba(255,255,255,0.12)] text-white rounded-xl focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 disabled:opacity-50 disabled:cursor-not-allowed placeholder-gray-500 transition-all"
            />
            {isLoading ? (
              <button
                type="button"
                onClick={handleCancel}
                className="px-6 py-3 bg-red-600 text-white rounded-xl hover:bg-red-700 transition font-medium shadow-lg"
              >
                Cancel
              </button>
            ) : (
              <button
                type="submit"
                disabled={!inputValue.trim()}
                className="px-6 py-3 bg-gradient-to-r from-blue-600 to-emerald-600 text-white rounded-xl hover:shadow-lg hover:shadow-emerald-500/30 transition font-medium disabled:opacity-50 disabled:cursor-not-allowed shadow-lg"
              >
                Send
              </button>
            )}
          </div>
          <p className="text-xs text-gray-500 text-center">
            Responses are powered by your documents
          </p>
        </form>
      </div>
    </div>
  );
};

export default ChatInterface;
