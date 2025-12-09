import React from 'react';
import { useNavigate } from 'react-router-dom';
import { MessageSquare, FileUp, Home, Briefcase, FileText, Calculator } from 'lucide-react';

const HomePage = () => {
  const navigate = useNavigate();

  const topics = [
    {
      id: 'rental',
      name: 'Rental Law',
      image: 'https://images.unsplash.com/photo-1649646861831-8225fa368f86?q=80&w=800&auto=format&fit=crop',
      icon: Home
    },
    {
      id: 'job',
      name: 'Employment Law',
      image: 'https://images.unsplash.com/photo-1760236963218-424a715d1816?q=80&w=800&auto=format&fit=crop',
      icon: Briefcase
    },
    {
      id: 'tax',
      name: 'Tax Law',
      image: 'https://images.unsplash.com/photo-1649209979970-f01d950cc5ed?q=80&w=800&auto=format&fit=crop',
      icon: Calculator
    },
    {
      id: 'subscription',
      name: 'Subscription Law',
      image: 'https://images.unsplash.com/photo-1651641049161-5051c910241d?q=80&w=800&auto=format&fit=crop',
      icon: FileText
    }
  ];

  return (
    <div className="min-h-screen bg-stone-50">
      <div className="grid grid-cols-1 md:grid-cols-12 gap-6 p-6 md:p-12 max-w-7xl mx-auto">
        {/* Hero Section */}
        <div 
          className="col-span-1 md:col-span-8 row-span-2 bg-stone-900 text-stone-50 rounded-3xl p-8 md:p-12 flex flex-col justify-between relative overflow-hidden"
          style={{
            backgroundImage: 'url(https://images.unsplash.com/photo-1760597371592-09e901b7317d?q=80&w=2000&auto=format&fit=crop)',
            backgroundSize: 'cover',
            backgroundPosition: 'center'
          }}
          data-testid="hero-section"
        >
          <div className="absolute inset-0 bg-gradient-to-br from-stone-900/95 via-stone-900/90 to-stone-900/80"></div>
          <div className="relative z-10">
            <h1 className="font-serif text-4xl md:text-6xl tracking-tight leading-tight mb-4">
              LegalMe
            </h1>
            <p className="text-lg md:text-xl text-stone-300 max-w-2xl leading-relaxed">
              Your friendly AI assistant for understanding German legal documents and contracts.
              Get instant clarity on rental agreements, employment contracts, and more.
            </p>
          </div>
          <div className="relative z-10 mt-8">
            <p className="text-sm uppercase tracking-wide text-stone-400 mb-2">Powered by AI</p>
            <div className="flex gap-2">
              <div className="h-1 w-16 bg-orange-600 rounded"></div>
              <div className="h-1 w-8 bg-orange-400 rounded"></div>
              <div className="h-1 w-4 bg-orange-300 rounded"></div>
            </div>
          </div>
        </div>

        {/* Start Chat Card */}
        <div 
          onClick={() => navigate('/chat')}
          className="col-span-1 md:col-span-4 bg-white border border-stone-200 rounded-3xl p-8 hover:shadow-xl hover:border-orange-200 hover:ring-1 hover:ring-orange-200 cursor-pointer group"
          data-testid="start-chat-button"
        >
          <div className="flex flex-col h-full justify-between">
            <div>
              <div className="w-14 h-14 bg-orange-100 rounded-2xl flex items-center justify-center mb-4 group-hover:bg-orange-200">
                <MessageSquare className="w-7 h-7 text-orange-700" strokeWidth={1.5} />
              </div>
              <h2 className="font-serif text-3xl md:text-4xl mb-3 text-stone-900">Start Chat</h2>
              <p className="text-stone-600 leading-relaxed">
                Ask legal questions and get instant AI-powered answers with references to German law.
              </p>
            </div>
            <div className="mt-6">
              <span className="inline-flex items-center text-orange-700 font-medium group-hover:translate-x-1">
                Ask a question →
              </span>
            </div>
          </div>
        </div>

        {/* Upload Contract Card */}
        <div 
          onClick={() => navigate('/contract')}
          className="col-span-1 md:col-span-4 bg-white border border-stone-200 rounded-3xl p-8 hover:shadow-xl hover:border-orange-200 hover:ring-1 hover:ring-orange-200 cursor-pointer group"
          data-testid="upload-contract-button"
        >
          <div className="flex flex-col h-full justify-between">
            <div>
              <div className="w-14 h-14 bg-orange-100 rounded-2xl flex items-center justify-center mb-4 group-hover:bg-orange-200">
                <FileUp className="w-7 h-7 text-orange-700" strokeWidth={1.5} />
              </div>
              <h2 className="font-serif text-3xl md:text-4xl mb-3 text-stone-900">Upload Document</h2>
              <p className="text-stone-600 leading-relaxed">
                Analyze any legal document for risky clauses and legal violations.
              </p>
            </div>
            <div className="mt-6">
              <span className="inline-flex items-center text-orange-700 font-medium group-hover:translate-x-1">
                Upload document →
              </span>
            </div>
          </div>
        </div>

        {/* Topic Cards */}
        {topics.map((topic) => {
          const Icon = topic.icon;
          return (
            <div
              key={topic.id}
              onClick={() => navigate('/chat', { state: { initialTopic: topic.name } })}
              className="col-span-1 md:col-span-3 h-48 relative rounded-2xl overflow-hidden group cursor-pointer"
              style={{
                backgroundImage: `url(${topic.image})`,
                backgroundSize: 'cover',
                backgroundPosition: 'center'
              }}
              data-testid={`topic-${topic.id}`}
            >
              <div className="absolute inset-0 bg-gradient-to-t from-stone-900/90 via-stone-900/50 to-transparent group-hover:from-stone-900/95"></div>
              <div className="absolute inset-0 p-6 flex flex-col justify-end">
                <Icon className="w-8 h-8 text-white mb-2" strokeWidth={1.5} />
                <h3 className="font-serif text-2xl text-white">{topic.name}</h3>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default HomePage;