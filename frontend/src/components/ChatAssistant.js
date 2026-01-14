import { useState, useRef, useEffect } from "react";
import { sendChatMessage, clearChat } from "../api";
import "./ChatAssistant.css";

function ChatAssistant({ income = 0, expenses = [], goals = [] }) {
    const [isOpen, setIsOpen] = useState(false);
    const [messages, setMessages] = useState([
        { role: "assistant", content: "Hi! I'm your AI finance assistant. Ask me anything about your finances!" }
    ]);
    const [input, setInput] = useState("");
    const [loading, setLoading] = useState(false);
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const handleSend = async () => {
        if (!input.trim() || loading) return;

        const userMessage = { role: "user", content: input };
        setMessages(prev => [...prev, userMessage]);
        setInput("");
        setLoading(true);

        try {
            const context = { income, expenses, goals };
            const data = await sendChatMessage(input, context);

            const assistantMessage = {
                role: "assistant",
                content: data.response || data.error || "Sorry, something went wrong."
            };
            setMessages(prev => [...prev, assistantMessage]);
        } catch (err) {
            setMessages(prev => [...prev, {
                role: "assistant",
                content: "Sorry, I couldn't process your request. Please try again."
            }]);
        }

        setLoading(false);
    };

    const handleKeyPress = (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    const handleClear = async () => {
        try {
            await clearChat();
            setMessages([
                { role: "assistant", content: "Chat cleared! How can I help you today?" }
            ]);
        } catch (err) {
            console.error("Error clearing chat:", err);
        }
    };

    return (
        <>
            {/* Floating Chat Button */}
            <button
                className={`chat-toggle ${isOpen ? "open" : ""}`}
                onClick={() => setIsOpen(!isOpen)}
            >
                {isOpen ? "✕" : "💬"}
            </button>

            {/* Chat Window */}
            {isOpen && (
                <div className="chat-window">
                    <div className="chat-header">
                        <h3>💬 AI Finance Assistant</h3>
                        <button onClick={handleClear} className="clear-btn" title="Clear chat">
                            🗑️
                        </button>
                    </div>

                    <div className="chat-messages">
                        {messages.map((msg, i) => (
                            <div key={i} className={`message ${msg.role}`}>
                                <div className="message-content">
                                    {msg.content}
                                </div>
                            </div>
                        ))}
                        {loading && (
                            <div className="message assistant">
                                <div className="message-content typing">
                                    <span></span><span></span><span></span>
                                </div>
                            </div>
                        )}
                        <div ref={messagesEndRef} />
                    </div>

                    <div className="chat-input">
                        <textarea
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            onKeyPress={handleKeyPress}
                            placeholder="Ask about your finances..."
                            disabled={loading}
                            rows={1}
                        />
                        <button onClick={handleSend} disabled={loading || !input.trim()}>
                            ➤
                        </button>
                    </div>
                </div>
            )}
        </>
    );
}

export default ChatAssistant;
