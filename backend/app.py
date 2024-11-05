from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
import heapq
import os

app = Flask(__name__)
CORS(app)

# Database Configuration
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'trie_search.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Initialize global trie variable
trie = None

# Database Models
class SearchTerm(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    term = db.Column(db.String(100), unique=True, nullable=False)
    heat = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'term': self.term,
            'heat': self.heat,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

# Trie Implementation
class TrieNode:
    def __init__(self):
        self.child = {}
        self.is_end_of_word = False
        self.heat = 0

class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word, heat=1):
        node = self.root
        for char in word.lower():
            if char not in node.child:
                node.child[char] = TrieNode()
            node = node.child[char]
        node.is_end_of_word = True
        node.heat = heat

    def _search_words_with_prefix(self, node, prefix, heap):
        if node.is_end_of_word:
            heapq.heappush(heap, (-node.heat, prefix))
        for char, child_node in node.child.items():
            self._search_words_with_prefix(child_node, prefix + char, heap)

    def search_similar(self, prefix, top_n=10):
        node = self.root
        prefix = prefix.lower()
        for char in prefix:
            if char not in node.child:
                return []
            node = node.child[char]
        
        heap = []
        self._search_words_with_prefix(node, prefix, heap)
        return [(word, -heat) for heat, word in heapq.nlargest(top_n, heap)]

# Initialize Trie from database
def initialize_trie():
    trie_instance = Trie()
    terms = SearchTerm.query.all()
    for term in terms:
        trie_instance.insert(term.term, term.heat)
    return trie_instance

# Create database tables and initialize trie
with app.app_context():
    db.create_all()
    
    # Add sample data if database is empty
    if not SearchTerm.query.first():
        sample_terms = [
            'react', 'redux', 'javascript', 'typescript', 'node',
            'python', 'django', 'flask', 'fastapi', 'express',
            'database', 'mongodb', 'postgresql', 'mysql', 'redis',
            'docker', 'kubernetes', 'aws', 'azure', 'google cloud'
        ]
        for term in sample_terms:
            db.session.add(SearchTerm(term=term))
        db.session.commit()
    
    # Initialize global trie
    trie = initialize_trie()

# API Routes
@app.route('/api/search', methods=['GET'])
def search():
    global trie
    query = request.args.get('q', '')
    if not query:
        return jsonify([])
    
    results = trie.search_similar(query)
    
    # Update heat in database
    for term, _ in results:
        search_term = SearchTerm.query.filter_by(term=term).first()
        if search_term:
            search_term.heat += 1
            db.session.commit()
    
    # Reinitialize trie with updated heats
    trie = initialize_trie()
    
    return jsonify(results)

@app.route('/api/terms', methods=['POST'])
def add_term():
    global trie
    data = request.get_json()
    term = data.get('term', '').lower()
    
    if not term:
        return jsonify({'error': 'Term is required'}), 400
    
    existing_term = SearchTerm.query.filter_by(term=term).first()
    if existing_term:
        existing_term.heat += 1
        db.session.commit()
    else:
        new_term = SearchTerm(term=term)
        db.session.add(new_term)
        db.session.commit()
    
    # Reinitialize trie
    trie = initialize_trie()
    
    return jsonify({'message': 'Term added successfully'})

@app.route('/api/terms', methods=['GET'])
def get_terms():
    terms = SearchTerm.query.order_by(SearchTerm.heat.desc()).all()
    return jsonify([term.to_dict() for term in terms])
@app.route('/api/interval', methods=['GET'])
def interval_search():
    query = request.args.get('q', '').lower()
    if not query:
        return jsonify([])
    
    # Get all terms
    terms = SearchTerm.query.all()
    
    # Calculate similarity for each term
    similar_terms = []
    for term in terms:
        similarity = calculate_similarity(query, term.term.lower())
        if similarity > 0.3:  # Threshold for similarity
            similar_terms.append([term.term, similarity])
    
    # Sort by similarity descending
    similar_terms.sort(key=lambda x: x[1], reverse=True)
    
    return jsonify(similar_terms[:10])  # Return top 10 similar terms

def calculate_similarity(a, b):
    from difflib import SequenceMatcher
    return SequenceMatcher(None, a, b).ratio()
if __name__ == '__main__':
    app.run(debug=True)