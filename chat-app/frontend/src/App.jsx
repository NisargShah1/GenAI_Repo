import React from 'react';
import ChatInterface from './components/ChatInterface';
import './App.css';

function App() {
  return (
    <div className="app-container">
      <header className="app-header">
        <h1 className="logo gradient-text">MongoChat AI</h1>
        <div className="subtitle">Powered by Vertex AI</div>
      </header>

      <main className="main-content glass">
        <ChatInterface />
      </main>
    </div>
  );
}

export default App;
