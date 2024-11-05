import React, { useState, useEffect } from 'react';
import { Search, Loader2, Plus } from 'lucide-react';

const API_BASE_URL = 'http://localhost:5000/api';

const TrieSearchUI = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [suggestions, setSuggestions] = useState([]);
  const [intervalSuggestions, setIntervalSuggestions] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(-1);
  const [message, setMessage] = useState('');

  useEffect(() => {
    const debounce = setTimeout(() => {
      if (searchTerm.trim()) {
        fetchSuggestions(searchTerm);
        fetchIntervalSuggestions(searchTerm);
      } else {
        setSuggestions([]);
        setIntervalSuggestions([]);
      }
    }, 300);

    return () => clearTimeout(debounce);
  }, [searchTerm]);

  const fetchSuggestions = async (term) => {
    setIsLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/search?q=${encodeURIComponent(term)}`);
      const data = await response.json();
      setSuggestions(data.map(([term, heat]) => ({ term, heat })));
    } catch (error) {
      console.error('Suggestion fetch failed:', error);
      setSuggestions([]);
    } finally {
      setIsLoading(false);
    }
  };

  const fetchIntervalSuggestions = async (term) => {
    try {
      const response = await fetch(`${API_BASE_URL}/interval?q=${encodeURIComponent(term)}`);
      const data = await response.json();
      setIntervalSuggestions(data.map(([term, similarity]) => ({ term, similarity })));
    } catch (error) {
      console.error('Interval suggestion fetch failed:', error);
      setIntervalSuggestions([]);
    }
  };

  const addNewTerm = async (term) => {
    try {
      const response = await fetch(`${API_BASE_URL}/terms`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ term }),
      });
      const data = await response.json();
      setMessage('Term added successfully!');
      setTimeout(() => setMessage(''), 3000);
      fetchSuggestions(term);
      fetchIntervalSuggestions(term);
    } catch (error) {
      console.error('Failed to add term:', error);
      setMessage('Failed to add term');
      setTimeout(() => setMessage(''), 3000);
    }
  };

  const handleKeyDown = (e) => {
    const totalSuggestions = [...suggestions, ...intervalSuggestions];
    if (totalSuggestions.length === 0) return;

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setSelectedIndex(prev => 
          prev < totalSuggestions.length - 1 ? prev + 1 : prev
        );
        break;
      case 'ArrowUp':
        e.preventDefault();
        setSelectedIndex(prev => prev > -1 ? prev - 1 : prev);
        break;
      case 'Enter':
        if (selectedIndex >= 0) {
          const selected = totalSuggestions[selectedIndex];
          handleSuggestionClick(selected.term);
        }
        break;
      case 'Escape':
        setSuggestions([]);
        setIntervalSuggestions([]);
        setSelectedIndex(-1);
        break;
    }
  };

  const handleSuggestionClick = (term) => {
    setSearchTerm(term);
    setSuggestions([]);
    setIntervalSuggestions([]);
    setSelectedIndex(-1);
  };

  const renderSuggestionItem = (item, index, type) => (
    <div
      key={`${type}-${index}`}
      onClick={() => handleSuggestionClick(item.term)}
      className={`px-4 py-2 cursor-pointer flex justify-between items-center ${
        index === selectedIndex ? 'bg-blue-50' : 'hover:bg-gray-50'
      }`}
    >
      <span>{item.term}</span>
      <div className="flex items-center space-x-2">
        {type === 'exact' ? (
          <span className="text-sm text-gray-500">Heat: {item.heat}</span>
        ) : (
          <span className="text-sm text-gray-500">
            Similarity: {Math.round(item.similarity * 100)}%
          </span>
        )}
      </div>
    </div>
  );

  return (
    <div className="w-full max-w-lg mx-auto p-4 bg-white shadow-lg rounded-lg">
      <h2 className="text-2xl font-bold text-center mb-4">Smart Search</h2>
      
      <div className="relative">
        <div className="relative">
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type to search..."
            className="w-full pl-10 pr-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            disabled={isLoading}
          />
          <div className="absolute inset-y-0 left-3 flex items-center pointer-events-none">
            {isLoading ? (
              <Loader2 className="h-5 w-5 text-gray-400 animate-spin" />
            ) : (
              <Search className="h-5 w-5 text-gray-400" />
            )}
          </div>
        </div>

        {message && (
          <div className="mt-2 text-center text-green-600 text-sm">
            {message}
          </div>
        )}

        {(suggestions.length > 0 || intervalSuggestions.length > 0) && (
          <div className="absolute mt-1 w-full bg-white border rounded-lg shadow-lg z-10 max-h-96 overflow-y-auto">
            {suggestions.length > 0 && (
              <div>
                <div className="px-4 py-2 bg-gray-50 font-semibold text-sm text-gray-700">
                  Exact Matches
                </div>
                {suggestions.map((item, index) => renderSuggestionItem(item, index, 'exact'))}
              </div>
            )}
            
            {intervalSuggestions.length > 0 && (
              <div>
                <div className="px-4 py-2 bg-gray-50 font-semibold text-sm text-gray-700">
                  Similar Terms
                </div>
                {intervalSuggestions.map((item, index) => 
                  renderSuggestionItem(item, suggestions.length + index, 'interval')
                )}
              </div>
            )}
          </div>
        )}
        
        {searchTerm && suggestions.length === 0 && intervalSuggestions.length === 0 && !isLoading && (
          <div className="mt-2">
            <div className="text-center text-gray-500 mb-2">
              No results found for "{searchTerm}"
            </div>
            <button
              onClick={() => addNewTerm(searchTerm)}
              className="w-full flex items-center justify-center space-x-2 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
            >
              <Plus className="h-4 w-4" />
              <span>Add "{searchTerm}" to database</span>
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default TrieSearchUI;