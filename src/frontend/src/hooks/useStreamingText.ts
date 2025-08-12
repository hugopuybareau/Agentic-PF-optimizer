// frontend/src/hooks/useStreamingText.ts

import { useState, useRef, useCallback } from 'react';

interface StreamingChunk {
    type: 'metadata' | 'token' | 'complete' | 'error';
    content?: string;
    index?: number;
    is_final?: boolean;
    error?: string;
    [key: string]: any;
}

interface UseStreamingTextOptions {
    onComplete?: (fullText: string, metadata: any, aiMessageId: string) => void;
    onError?: (error: string, aiMessageId: string) => void;
    onStart?: () => void;
}

export const useStreamingText = (options: UseStreamingTextOptions = {}) => {
    const [streamedText, setStreamedText] = useState('');
    const [isStreaming, setIsStreaming] = useState(false);
    const [isThinking, setIsThinking] = useState(false);
    const [metadata, setMetadata] = useState<any>(null);
    const [error, setError] = useState<string | null>(null);
    
    const abortControllerRef = useRef<AbortController | null>(null);
    const fullTextRef = useRef('');
    const metadataRef = useRef<any>(null);

    const startStreaming = useCallback(async (url: string, requestBody: any, aiMessageId: string) => {
        // Cancel any existing stream
        if (abortControllerRef.current) {
            abortControllerRef.current.abort();
        }

        // Reset state
        setStreamedText('');
        setError(null);
        setMetadata(null);
        setIsThinking(true);
        setIsStreaming(true);
        fullTextRef.current = '';
        metadataRef.current = null;
        
        options.onStart?.();

        // Create new abort controller
        abortControllerRef.current = new AbortController();

        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestBody),
                signal: abortControllerRef.current.signal,
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const reader = response.body?.getReader();
            if (!reader) {
                throw new Error('No response body reader available');
            }

            const decoder = new TextDecoder();
            let buffer = '';

            while (true) {
                const { done, value } = await reader.read();
                
                if (done || abortControllerRef.current?.signal.aborted) {
                    break;
                }

                // Decode the chunk and add to buffer
                buffer += decoder.decode(value, { stream: true });
                
                // Process complete lines
                const lines = buffer.split('\n');
                buffer = lines.pop() || ''; // Keep incomplete line in buffer

                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        try {
                            const chunk: StreamingChunk = JSON.parse(line.slice(6));
                            
                            switch (chunk.type) {
                                case 'metadata':
                                    metadataRef.current = chunk;
                                    setMetadata(chunk);
                                    setIsThinking(false); // First chunk received
                                    break;
                                    
                                case 'token':
                                    setIsThinking(false);
                                    if (chunk.content) {
                                        fullTextRef.current += chunk.content;
                                        setStreamedText(fullTextRef.current);
                                    }
                                    break;
                                    
                                case 'complete':
                                    setIsStreaming(false);
                                    options.onComplete?.(fullTextRef.current, metadataRef.current, aiMessageId);
                                    break;
                                    
                                case 'error':
                                    setError(chunk.error || 'Unknown streaming error');
                                    setIsStreaming(false);
                                    setIsThinking(false);
                                    options.onError?.(chunk.error || 'Unknown streaming error', chunk.aiMessageId);
                                    break;
                            }
                        } catch (parseError) {
                            console.warn('Failed to parse SSE chunk:', line, parseError);
                        }
                    }
                }
            }
        } catch (err: any) {
            if (err.name === 'AbortError') {
                // Stream was cancelled, this is expected
                return;
            }
            
            console.error('Streaming error:', err);
            setError(err.message || 'Streaming failed');
            setIsStreaming(false);
            setIsThinking(false);
            options.onError?.(err.message || 'Streaming failed', err.aiMessageId || null);
        }
    }, [options]);

    const cancelStream = useCallback(() => {
        if (abortControllerRef.current) {
            abortControllerRef.current.abort();
        }
        setIsStreaming(false);
        setIsThinking(false);
    }, []);

    const reset = useCallback(() => {
        setStreamedText('');
        setError(null);
        setMetadata(null);
        setIsThinking(false);
        setIsStreaming(false);
        fullTextRef.current = '';
    }, []);

    return {
        streamedText,
        isStreaming,
        isThinking,
        metadata,
        error,
        startStreaming,
        cancelStream,
        reset,
    };
};