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
        await new Promise<void>((resolve, reject) => {
          streamQuery(sessionId, userQuery, {
            onChunk: (chunk: string) => {
              setCurrentResponse((prev) => prev + chunk);
            },
            onCitation: (citations: Citation[]) => {
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

        // Add assistant message
        const assistantMessage: Message = {
          id: `msg_${Date.now()}_assistant`,
          role: 'assistant',
          content: currentResponse,
          citations: currentCitations,
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
    [inputValue, isLoading, sessionId, currentResponse, currentCitations, onError]
  );

  const handleCancel = useCallback(() => {
    abortControllerRef.current?.abort();
    setIsLoading(false);
    setCurrentResponse('');
    setCurrentCitations([]);
  }, []);

  return (
    <div className="flex flex-col h-full bg-white">
      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        {messages.length === 0 ? (
          <div className="flex items-center justify-center h-full text-gray-400">
            <div className="text-center">
              <div className="text-4xl mb-4">💬</div>
              <p className="text-lg font-medium">Start a conversation</p>
              <p className="text-sm mt-2">
                Ask about your documents or get financial insights
              </p>
            </div>
          </div>
        ) : (
          <>
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${
                  message.role === 'user' ? 'justify-end' : 'justify-start'
                }`}
              >
                <div
                  className={`max-w-xs lg:max-w-md xl:max-w-lg px-4 py-3 rounded-lg ${
                    message.role === 'user'
                      ? 'bg-blue-500 text-white rounded-br-none'
                      : 'bg-gray-100 text-gray-900 rounded-bl-none'
                  }`}
                >
                  <p className="text-sm leading-relaxed">{message.content}</p>
                  {message.citations && message.citations.length > 0 && (
                    <div className="mt-2 pt-2 border-t border-opacity-20 border-gray-500">
                      <div className="text-xs opacity-75 space-y-1">
                        {message.citations.map((citation, idx) => (
                          <div
                            key={idx}
                            className="inline-block bg-opacity-20 bg-gray-700 px-2 py-1 rounded mr-1 mb-1"
                          >
                            📄 {citation.filename}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ))}

            {/* Current streaming response */}
            {isLoading && currentResponse && (
              <div className="flex justify-start">
                <div className="max-w-xs lg:max-w-md xl:max-w-lg px-4 py-3 rounded-lg bg-gray-100 text-gray-900 rounded-bl-none">
                  <p className="text-sm leading-relaxed">{currentResponse}</p>
                  <div className="mt-2 flex items-center space-x-1">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-100"></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-200"></div>
                  </div>
                  {currentCitations && currentCitations.length > 0 && (
                    <div className="mt-2 pt-2 border-t border-opacity-20 border-gray-500">
                      <div className="text-xs opacity-75 space-y-1">
                        {currentCitations.map((citation, idx) => (
                          <div
                            key={idx}
                            className="inline-block bg-opacity-20 bg-gray-700 px-2 py-1 rounded mr-1 mb-1"
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
              <div className="flex justify-start">
                <div className="px-4 py-3 rounded-lg bg-gray-100 text-gray-900 rounded-bl-none">
                  <div className="flex space-x-2">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-100"></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-200"></div>
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      {/* Input Area */}
      <div className="border-t border-gray-200 p-6 bg-white">
        <form onSubmit={handleSubmit} className="space-y-3">
          <div className="flex gap-3">
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder="Ask a question about your documents..."
              disabled={isLoading}
              className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
            />
            {isLoading ? (
              <button
                type="button"
                onClick={handleCancel}
                className="px-6 py-3 bg-red-500 text-white rounded-lg hover:bg-red-600 transition font-medium"
              >
                Cancel
              </button>
            ) : (
              <button
                type="submit"
                disabled={!inputValue.trim()}
                className="px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition font-medium disabled:bg-gray-300 disabled:cursor-not-allowed"
              >
                Send
              </button>
            )}
          </div>
          <p className="text-xs text-gray-500">
            Responses are generated in real-time using your documents as context
          </p>
        </form>
      </div>
    </div>
  );
};

export default ChatInterface;
