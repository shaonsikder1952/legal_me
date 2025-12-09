import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Home from './pages/Home';
import Chat from './pages/Chat';
import ContractAnalysis from './pages/ContractAnalysis';
import './App.css';

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/chat" element={<Chat />} />
          <Route path="/contract" element={<ContractAnalysis />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;