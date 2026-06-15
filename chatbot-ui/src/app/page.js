'use client';

import { useState, useRef, useEffect } from 'react';
import styles from './page.module.css';

export default function Home() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage = { role: 'user', content: input.trim() };
    const newMessages = [...messages, userMessage];
    
    setMessages(newMessages);
    setInput('');
    setIsLoading(true);

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ messages: newMessages }),
      });

      if (!response.ok) {
        throw new Error('Failed to generate response');
      }

      const data = await response.json();
      setMessages([...newMessages, { role: 'assistant', content: data.text }]);
    } catch (error) {
      console.error('Error:', error);
      setMessages([...newMessages, { role: 'assistant', content: "ERR: SYSTEM HALT" }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={styles.container}>
      <header className={styles.header}>
        <h1 className={styles.title}>THE_ORACLE</h1>
        <p className={styles.subtitle}>// DIRECT INTERFACE</p>
      </header>

      <main className={styles.chatArea}>
        {messages.length === 0 && (
          <div className={styles.emptyState}>
            <p>&gt; INPUT REQUIRED TO INITIATE SEQUENCE</p>
          </div>
        )}
        
        {messages.map((msg, idx) => (
          <div 
            key={idx} 
            className={`${styles.messageWrapper} ${msg.role === 'user' ? styles.messageWrapperUser : styles.messageWrapperBot}`}
          >
            <div className={`${styles.message} ${msg.role === 'user' ? styles.messageUser : styles.messageBot}`}>
              {msg.content}
            </div>
          </div>
        ))}
        
        {isLoading && (
          <div className={`${styles.messageWrapper} ${styles.messageWrapperBot}`}>
            <div className={styles.typingIndicator}>
              PROCESSING...
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </main>

      <div className={styles.inputContainer}>
        <form onSubmit={handleSubmit} className={styles.inputArea}>
          <input
            type="text"
            className={styles.input}
            placeholder="TYPE COMMAND HERE"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={isLoading}
            autoComplete="off"
          />
          <button 
            type="submit" 
            className={styles.sendButton}
            disabled={!input.trim() || isLoading}
          >
            SEND
          </button>
        </form>
      </div>
    </div>
  );
}
