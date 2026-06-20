import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, ArcElement, PointElement, LineElement } from 'chart.js';
import { Bar, Pie, Line } from 'react-chartjs-2';
import './ChatInterface.css';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, ArcElement, PointElement, LineElement);

const ChatInterface = () => {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const sendMessage = async () => {
        if (!input.trim()) return;

        const userMsg = { role: 'user', content: input };
        setMessages(prev => [...prev, userMsg]);
        setInput('');
        setLoading(true);

        try {
            const response = await axios.post('http://localhost:8080/api/chat', { message: input });
            const botMsg = { role: 'bot', ...response.data };
            setMessages(prev => [...prev, botMsg]);
        } catch (error) {
            console.error(error);
            setMessages(prev => [...prev, { role: 'bot', type: 'TEXT', data: 'Error: Failed to fetch response. Ensure backend is running.' }]);
        } finally {
            setLoading(false);
        }
    };

    const handleKeyPress = (e) => {
        if (e.key === 'Enter') sendMessage();
    };

    const renderContent = (msg) => {
        if (msg.role === 'user') return <div className="text-content">{msg.content}</div>;

        // Bot response
        return (
            <div className="bot-response">
                {msg.explanation && <div className="explanation">{msg.explanation}</div>}
                {renderData(msg)}
            </div>
        );
    };

    const renderData = (msg) => {
        if (!msg.data) return null;

        if (msg.type === 'TEXT') {
            return <div className="text-content">{typeof msg.data === 'string' ? msg.data : JSON.stringify(msg.data)}</div>;
        }
        if (msg.type === 'CHART' && msg.chart) {
            return renderChart(msg);
        }
        if (msg.type === 'TABLE') {
            // Basic table rendering
            if (!Array.isArray(msg.data) || msg.data.length === 0) return <div className="no-data">No data found</div>;
            // Collect all unique keys from all objects to handle heterogeneous data (if any)
            const allKeys = new Set();
            msg.data.forEach(row => Object.keys(row).forEach(k => allKeys.add(k)));
            const headers = Array.from(allKeys);

            return (
                <div className="table-container">
                    <table>
                        <thead>
                            <tr>{headers.map(h => <th key={h}>{h}</th>)}</tr>
                        </thead>
                        <tbody>
                            {msg.data.map((row, i) => (
                                <tr key={i}>{headers.map(h => <td key={h}>{typeof row[h] === 'object' ? JSON.stringify(row[h]) : row[h]}</td>)}</tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            );
        }
        return null; // fallback
    };

    const renderChart = (msg) => {
        if (!Array.isArray(msg.data) || msg.data.length === 0) return <div className="no-data">No data for chart</div>;

        const labels = msg.data.map(d => d[msg.chart.x] || 'Unknown');
        const values = msg.data.map(d => Number(d[msg.chart.y]) || 0);

        const data = {
            labels,
            datasets: [{
                label: msg.chart.y,
                data: values,
                backgroundColor: [
                    'rgba(255, 99, 132, 0.6)',
                    'rgba(54, 162, 235, 0.6)',
                    'rgba(255, 206, 86, 0.6)',
                    'rgba(75, 192, 192, 0.6)',
                    'rgba(153, 102, 255, 0.6)',
                ],
                borderColor: [
                    'rgba(255, 99, 132, 1)',
                    'rgba(54, 162, 235, 1)',
                    'rgba(255, 206, 86, 1)',
                    'rgba(75, 192, 192, 1)',
                    'rgba(153, 102, 255, 1)',
                ],
                borderWidth: 1
            }]
        };

        const options = {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { labels: { color: '#cbd5e1' } },
                title: { display: true, text: `Chart: ${msg.chart.type}`, color: '#cbd5e1' }
            },
            scales: {
                x: { ticks: { color: '#94a3b8' }, grid: { color: '#334155' } },
                y: { ticks: { color: '#94a3b8' }, grid: { color: '#334155' } }
            }
        };

        // Pie charts don't use x/y scales the same way, but ChartJS handles it gracefully mostly.
        // For Pie, we usually hide scales.
        const pieOptions = {
            ...options,
            scales: {}
        };

        if (msg.chart.type === 'bar') return <div className="chart-wrapper"><Bar data={data} options={options} /></div>;
        if (msg.chart.type === 'pie') return <div className="chart-wrapper"><Pie data={data} options={pieOptions} /></div>;
        if (msg.chart.type === 'line') return <div className="chart-wrapper"><Line data={data} options={options} /></div>;

        return <div>Unsupported chart type: {msg.chart.type}</div>;
    };

    return (
        <div className="chat-interface">
            <div className="messages-area">
                {messages.map((msg, idx) => (
                    <div key={idx} className={`message ${msg.role}`}>
                        <div className={`message-bubble glass ${msg.role === 'user' ? 'user-bubble' : 'bot-bubble'}`}>
                            {renderContent(msg)}
                        </div>
                    </div>
                ))}
                {loading && <div className="message bot"><div className="message-bubble glass bot-bubble">Processing...</div></div>}
                <div ref={messagesEndRef} />
            </div>
            <div className="input-area glass">
                <input
                    type="text"
                    value={input}
                    onChange={e => setInput(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="Ask something about your data..."
                    disabled={loading}
                    className="chat-input"
                />
                <button onClick={sendMessage} disabled={loading} className="send-btn">
                    Send
                </button>
            </div>
        </div>
    );
};

export default ChatInterface;
