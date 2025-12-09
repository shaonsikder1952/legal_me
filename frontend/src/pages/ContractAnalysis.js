import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeRaw from 'rehype-raw';
import { ArrowLeft, Upload, FileText, Loader2, AlertTriangle, CheckCircle, AlertCircle, Download, Send, MessageCircle } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Dynamic Next Steps based on document type
const NEXT_STEPS_CONFIG = {
  rental: {
    authority: {
      text: 'Get tenant protection help',
      link: 'https://www.mieterschutzbund.de',
      linkText: 'Tenant Protection Association'
    },
    alternative: {
      text: 'View safer rental options',
      link: 'https://www.immobilienscout24.de',
      linkText: 'Browse fair rental listings'
    }
  },
  employment: {
    authority: {
      text: 'Contact employment agency',
      link: 'https://www.arbeitsagentur.de',
      linkText: 'Federal Employment Agency'
    },
    alternative: {
      text: 'Get employment rights guidance',
      link: 'https://www.dgb.de',
      linkText: 'Labor union resources'
    }
  },
  immigration: {
    authority: {
      text: 'Contact immigration office',
      link: 'https://service.berlin.de/dienstleistung/324284/',
      linkText: 'Immigration Office Berlin'
    },
    alternative: {
      text: 'Get visa guidance',
      link: 'https://www.bamf.de',
      linkText: 'Federal Migration Office'
    }
  },
  subscription: {
    authority: {
      text: 'Report subscription issue',
      link: 'https://www.verbraucherzentrale.de/beschwerde',
      linkText: 'Consumer protection complaint'
    },
    alternative: {
      text: 'Learn proper cancellation',
      link: 'https://www.verbraucherzentrale.de/wissen/vertraege-reklamation/kundenrechte/so-kuendigen-sie-richtig-6892',
      linkText: 'Cancellation guide'
    }
  },
  tax: {
    authority: {
      text: 'Get tax consultation',
      link: 'https://www.finanzamt.de',
      linkText: 'German Tax Office'
    },
    alternative: {
      text: 'Use tax declaration portal',
      link: 'https://www.elster.de',
      linkText: 'ELSTER tax portal'
    }
  },
  general: {
    authority: {
      text: 'Get legal advice',
      link: 'https://www.verbraucherzentrale.de',
      linkText: 'Consumer Protection Center'
    },
    alternative: {
      text: 'Find legal help',
      link: 'https://www.anwaltauskunft.de',
      linkText: 'Lawyer directory'
    }
  }
};

const ContractAnalysis = () => {
  const navigate = useNavigate();
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [analysis, setAnalysis] = useState(null);
  const [chatMessages, setChatMessages] = useState([]);
  const [chatInput, setChatInput] = useState('');
  const [chatLoading, setChatLoading] = useState(false);
  const [showChat, setShowChat] = useState(false);
  const [chatSessionId] = useState(() => `contract_chat_${Date.now()}`);
  const chatEndRef = useRef(null);

  const getNextStepText = (docType, stepType) => {
    const config = NEXT_STEPS_CONFIG[docType] || NEXT_STEPS_CONFIG.general;
    return config[stepType]?.text || NEXT_STEPS_CONFIG.general[stepType].text;
  };

  const getNextStepLink = (docType, stepType) => {
    const config = NEXT_STEPS_CONFIG[docType] || NEXT_STEPS_CONFIG.general;
    return config[stepType]?.link || NEXT_STEPS_CONFIG.general[stepType].link;
  };

  const getNextStepLinkText = (docType, stepType) => {
    const config = NEXT_STEPS_CONFIG[docType] || NEXT_STEPS_CONFIG.general;
    return config[stepType]?.linkText || NEXT_STEPS_CONFIG.general[stepType].linkText;
  };

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile && selectedFile.type === 'application/pdf') {
      setFile(selectedFile);
    } else {
      alert('Please select a PDF file');
    }
  };

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatMessages]);

  const handleUpload = async () => {
    if (!file) return;

    setUploading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post(`${API}/contract/analyze`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setAnalysis(response.data);
    } catch (error) {
      console.error('Upload error:', error);
      alert('Error analyzing contract. Please try again.');
    } finally {
      setUploading(false);
    }
  };

  const handleChatSubmit = async (e) => {
    e.preventDefault();
    if (!chatInput.trim() || !analysis) return;

    const userMessage = chatInput;
    setChatMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setChatInput('');
    setChatLoading(true);

    try {
      const response = await axios.post(`${API}/contract/${analysis.id}/chat`, {
        session_id: chatSessionId,
        message: userMessage
      });

      setChatMessages(prev => [...prev, { role: 'assistant', content: response.data.response }]);
    } catch (error) {
      console.error('Chat error:', error);
      setChatMessages(prev => [
        ...prev,
        { role: 'assistant', content: 'Sorry, I encountered an error. Please try again.' }
      ]);
    } finally {
      setChatLoading(false);
    }
  };

  const handleDownloadPDF = async () => {
    try {
      const response = await axios.get(`${API}/contract/${analysis.id}/download`, {
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `LegalMe_Report_${analysis.id.substring(0, 8)}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      console.error('Download error:', error);
      alert('Error downloading PDF. Please try again.');
    }
  };

  const getRiskIcon = (level) => {
    switch (level) {
      case 'high':
        return <AlertTriangle className="w-6 h-6 text-red-700" />;
      case 'medium':
        return <AlertCircle className="w-6 h-6 text-yellow-700" />;
      default:
        return <CheckCircle className="w-6 h-6 text-green-700" />;
    }
  };

  const getRiskBadge = (level) => {
    const styles = {
      high: 'bg-red-50 text-red-700 border-red-200',
      medium: 'bg-yellow-50 text-yellow-700 border-yellow-200',
      low: 'bg-green-50 text-green-700 border-green-200'
    };
    const labels = { high: '🔴 High Risk', medium: '🟡 Medium Risk', low: '🟢 Low Risk' };
    return (
      <span className={`px-4 py-2 rounded-full text-sm font-medium border ${styles[level]}`}>
        {labels[level]}
      </span>
    );
  };

  if (!analysis) {
    return (
      <div className="min-h-screen bg-stone-50">
        <div className="max-w-4xl mx-auto p-6 md:p-12">
          {/* Header */}
          <div className="mb-8">
            <button
              onClick={() => navigate('/')}
              className="flex items-center gap-2 text-stone-600 hover:text-stone-900 mb-4"
              data-testid="back-button"
            >
              <ArrowLeft className="w-5 h-5" />
              <span>Back to Home</span>
            </button>
            <h1 className="font-serif text-4xl md:text-5xl text-stone-900 mb-3">Contract Analysis</h1>
            <p className="text-lg text-stone-600">Upload a contract to analyze for risky clauses and legal violations</p>
          </div>

          {/* Upload Section */}
          <div className="bg-white border-2 border-dashed border-stone-300 rounded-3xl p-12 text-center hover:border-orange-400">
            <div className="max-w-md mx-auto">
              <div className="w-20 h-20 bg-orange-100 rounded-full flex items-center justify-center mx-auto mb-6">
                <Upload className="w-10 h-10 text-orange-700" strokeWidth={1.5} />
              </div>
              
              <h2 className="font-serif text-2xl text-stone-900 mb-3">Upload Your Contract</h2>
              <p className="text-stone-600 mb-6">PDF files only, max 10MB</p>

              <input
                type="file"
                accept="application/pdf"
                onChange={handleFileChange}
                className="hidden"
                id="file-upload"
                data-testid="file-input"
              />
              
              <label
                htmlFor="file-upload"
                className="inline-flex items-center gap-2 bg-stone-900 text-white hover:bg-stone-800 h-12 px-8 rounded-full font-medium cursor-pointer"
              >
                <FileText className="w-5 h-5" />
                Choose File
              </label>

              {file && (
                <div className="mt-6 p-4 bg-stone-50 rounded-2xl">
                  <p className="text-sm text-stone-600 mb-2">Selected file:</p>
                  <p className="font-medium text-stone-900" data-testid="selected-filename">{file.name}</p>
                  <button
                    onClick={handleUpload}
                    disabled={uploading}
                    className="mt-4 bg-orange-700 text-white hover:bg-orange-800 h-12 px-8 rounded-full font-medium shadow-lg shadow-orange-900/20 disabled:opacity-50 disabled:cursor-not-allowed inline-flex items-center gap-2"
                    data-testid="analyze-button"
                  >
                    {uploading ? (
                      <>
                        <Loader2 className="w-5 h-5 animate-spin" />
                        Analyzing...
                      </>
                    ) : (
                      <>
                        Analyze Contract
                      </>
                    )}
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-stone-50">
      <div className="max-w-6xl mx-auto p-6 md:p-12">
        {/* Header */}
        <div className="mb-8">
          <button
            onClick={() => {
              setAnalysis(null);
              setFile(null);
            }}
            className="flex items-center gap-2 text-stone-600 hover:text-stone-900 mb-4"
            data-testid="back-to-upload"
          >
            <ArrowLeft className="w-5 h-5" />
            <span>Analyze Another</span>
          </button>
        </div>

        {/* Chat Toggle Button */}
        <button
          onClick={() => setShowChat(!showChat)}
          className="fixed bottom-6 right-6 w-16 h-16 bg-orange-700 text-white rounded-full shadow-lg hover:bg-orange-800 flex items-center justify-center z-50"
          data-testid="toggle-contract-chat"
        >
          <MessageCircle className="w-7 h-7" />
        </button>

        {/* Chat Panel */}
        {showChat && (
          <div className="fixed bottom-24 right-6 w-96 h-[500px] bg-white rounded-2xl shadow-2xl border border-stone-200 flex flex-col z-50">
            <div className="p-4 border-b border-stone-100 flex items-center justify-between">
              <h3 className="font-serif text-lg text-stone-900">Ask about this contract</h3>
              <button onClick={() => setShowChat(false)} className="text-stone-500 hover:text-stone-900">
                ×
              </button>
            </div>

            <div className="flex-1 overflow-y-auto p-4 space-y-4" data-testid="contract-chat-messages">
              {chatMessages.length === 0 ? (
                <div className="text-center py-8 text-stone-500">
                  <p className="text-sm">Ask any question about this contract</p>
                </div>
              ) : (
                chatMessages.map((msg, idx) => (
                  <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                    {msg.role === 'user' ? (
                      <div className="bg-stone-100 text-stone-900 rounded-xl px-4 py-2 max-w-[80%]">
                        {msg.content}
                      </div>
                    ) : (
                      <div className="bg-orange-50 border border-orange-100 text-stone-800 rounded-xl px-4 py-3 max-w-[85%] prose prose-sm">
                        <ReactMarkdown remarkPlugins={[remarkGfm]} rehypePlugins={[rehypeRaw]}>
                          {msg.content}
                        </ReactMarkdown>
                      </div>
                    )}
                  </div>
                ))
              )}
              {chatLoading && (
                <div className="flex justify-start">
                  <div className="bg-orange-50 rounded-xl px-4 py-2">
                    <Loader2 className="w-4 h-4 text-orange-600 animate-spin" />
                  </div>
                </div>
              )}
              <div ref={chatEndRef} />
            </div>

            <form onSubmit={handleChatSubmit} className="p-4 border-t border-stone-100">
              <div className="flex gap-2">
                <input
                  type="text"
                  value={chatInput}
                  onChange={(e) => setChatInput(e.target.value)}
                  placeholder="Ask a question..."
                  className="flex-1 bg-stone-50 border-stone-200 focus:border-orange-500 focus:ring-orange-500/20 rounded-lg h-10 px-3 focus:outline-none focus:ring-2 text-sm"
                  disabled={chatLoading}
                  data-testid="contract-chat-input"
                />
                <button
                  type="submit"
                  disabled={chatLoading || !chatInput.trim()}
                  className="bg-orange-700 text-white hover:bg-orange-800 h-10 w-10 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
                  data-testid="contract-chat-send"
                >
                  <Send className="w-4 h-4" />
                </button>
              </div>
            </form>
          </div>
        )}

        {/* Report */}
        <div className="bg-white rounded-3xl shadow-lg border border-stone-100 p-8 md:p-12" data-testid="analysis-report">
          {/* Title */}
          <div className="mb-8 flex items-start justify-between">
            <div>
              <h1 className="font-serif text-4xl md:text-5xl text-stone-900 mb-4">LegalMe Contract Review Report</h1>
              <div className="h-1 w-24 bg-orange-600 rounded mb-6"></div>
            </div>
            <button
              onClick={handleDownloadPDF}
              className="flex items-center gap-2 bg-orange-700 text-white hover:bg-orange-800 h-12 px-6 rounded-full font-medium shadow-lg"
              data-testid="download-pdf-button"
            >
              <Download className="w-5 h-5" />
              Download PDF
            </button>
          </div>

          {/* Overview */}
          <section className="mb-10">
            <h2 className="font-serif text-3xl text-stone-900 mb-4">1. Document Overview</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="p-4 bg-stone-50 rounded-xl">
                <p className="text-sm text-stone-500 mb-1">Type</p>
                <p className="font-medium text-stone-900 capitalize">{analysis.document_type}</p>
              </div>
              <div className="p-4 bg-stone-50 rounded-xl">
                <p className="text-sm text-stone-500 mb-1">Risk Level</p>
                <div className="mt-2">{getRiskBadge(analysis.risk_level)}</div>
              </div>
              <div className="p-4 bg-stone-50 rounded-xl">
                <p className="text-sm text-stone-500 mb-1">Filename</p>
                <p className="font-medium text-stone-900">{analysis.filename}</p>
              </div>
              <div className="p-4 bg-stone-50 rounded-xl">
                <p className="text-sm text-stone-500 mb-1">Date Reviewed</p>
                <p className="font-medium text-stone-900">{new Date(analysis.timestamp).toLocaleDateString()}</p>
              </div>
            </div>
          </section>

          {/* Summary */}
          <section className="mb-10">
            <h2 className="font-serif text-3xl text-stone-900 mb-4">2. Summary</h2>
            <p className="text-stone-700 leading-relaxed">{analysis.summary}</p>
          </section>

          {/* Safe Clauses */}
          {analysis.clauses_safe.length > 0 && (
            <section className="mb-10">
              <h2 className="font-serif text-3xl text-stone-900 mb-4 flex items-center gap-3">
                <span className="text-2xl">🟢</span>
                3. Clauses That Are Acceptable
              </h2>
              <div className="space-y-4">
                {analysis.clauses_safe.map((clause, idx) => (
                  <div key={idx} className="p-6 bg-green-50 border border-green-200 rounded-2xl">
                    <p className="font-medium text-stone-900 mb-2">{clause.explanation}</p>
                    <p className="text-sm text-stone-600 mb-3 italic">&quot;...{clause.clause}...&quot;</p>
                    <a
                      href={clause.law_link}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-sm text-orange-700 hover:underline font-medium"
                    >
                      Reference: {clause.law} →
                    </a>
                  </div>
                ))}
              </div>
            </section>
          )}

          {/* Attention Clauses */}
          {analysis.clauses_attention.length > 0 && (
            <section className="mb-10">
              <h2 className="font-serif text-3xl text-stone-900 mb-4 flex items-center gap-3">
                <span className="text-2xl">🟡</span>
                4. Clauses That May Be Problematic
              </h2>
              <div className="space-y-4">
                {analysis.clauses_attention.map((clause, idx) => (
                  <div key={idx} className="p-6 bg-yellow-50 border border-yellow-200 rounded-2xl">
                    <p className="font-medium text-stone-900 mb-2">{clause.explanation}</p>
                    <p className="text-sm text-stone-600 mb-3 italic">&quot;...{clause.clause}...&quot;</p>
                    <a
                      href={clause.law_link}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-sm text-orange-700 hover:underline font-medium"
                    >
                      Reference: {clause.law} →
                    </a>
                  </div>
                ))}
              </div>
            </section>
          )}

          {/* Violates Clauses */}
          {analysis.clauses_violates.length > 0 && (
            <section className="mb-10">
              <h2 className="font-serif text-3xl text-stone-900 mb-4 flex items-center gap-3">
                <span className="text-2xl">🔴</span>
                5. Clauses That Violate German Law
              </h2>
              <div className="space-y-4">
                {analysis.clauses_violates.map((clause, idx) => (
                  <div key={idx} className="p-6 bg-red-50 border border-red-200 rounded-2xl">
                    <p className="font-medium text-stone-900 mb-2">{clause.explanation}</p>
                    <p className="text-sm text-stone-600 mb-3 italic">&quot;...{clause.clause}...&quot;</p>
                    <a
                      href={clause.law_link}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-sm text-orange-700 hover:underline font-medium"
                    >
                      Reference: {clause.law} →
                    </a>
                  </div>
                ))}
              </div>
            </section>
          )}

          {/* Recommendations */}
          <section className="mb-10">
            <h2 className="font-serif text-3xl text-stone-900 mb-4">6. Recommendations</h2>
            <p className="text-stone-700 leading-relaxed">{analysis.recommendations}</p>
          </section>

          {/* Divider */}
          <hr className="my-10 border-stone-200" />

          {/* Next Steps */}
          <section>
            <h2 className="font-serif text-3xl text-stone-900 mb-6">Next Steps</h2>
            <div className="space-y-4">
              <div className="flex items-start gap-4 p-4 bg-stone-50 rounded-xl hover:bg-stone-100">
                <span className="font-bold text-orange-700">1.</span>
                <div>
                  <p className="text-stone-900">
                    {getNextStepText(analysis.document_type, 'authority')}:{' '}
                    <a
                      href={getNextStepLink(analysis.document_type, 'authority')}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-orange-700 hover:underline font-medium"
                    >
                      {getNextStepLinkText(analysis.document_type, 'authority')} →
                    </a>
                  </p>
                </div>
              </div>
              <div className="flex items-start gap-4 p-4 bg-stone-50 rounded-xl hover:bg-stone-100">
                <span className="font-bold text-orange-700">2.</span>
                <div>
                  <p className="text-stone-900">
                    {getNextStepText(analysis.document_type, 'alternative')}:{' '}
                    <a
                      href={getNextStepLink(analysis.document_type, 'alternative')}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-orange-700 hover:underline font-medium"
                    >
                      {getNextStepLinkText(analysis.document_type, 'alternative')} →
                    </a>
                  </p>
                </div>
              </div>
              <div className="flex items-start gap-4 p-4 bg-stone-50 rounded-xl hover:bg-stone-100">
                <span className="font-bold text-orange-700">3.</span>
                <div>
                  <p className="text-stone-900">
                    Check another document:{' '}
                    <button
                      onClick={() => {
                        setAnalysis(null);
                        setFile(null);
                      }}
                      className="text-orange-700 hover:underline font-medium"
                    >
                      Upload another file →
                    </button>
                  </p>
                </div>
              </div>
            </div>
          </section>
        </div>
      </div>
    </div>
  );
};

export default ContractAnalysis;
