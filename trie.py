ASCII_A = ord('a')

class TrieNode:
    def __init__(self):
        self.child = [None] * 26  
        self.word_end = False 

class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, key):
        node = self.root
        for c in key:
            index = ord(c) - ASCII_A
            if not node.child[index]:
                node.child[index] = TrieNode()
            node = node.child[index]
        node.word_end = True

    def search(self, key):
        node = self.root
        for c in key:
            index = ord(c) - ASCII_A
            if not node.child[index]:
                return False
            node = node.child[index]
        return node.word_end
    
    def _find_words_with_prefix(self, node, prefix, results):
        if node.word_end:
            results.append(prefix)
        for i in range(26):
            if node.child[i]:
                self._find_words_with_prefix(node.child[i], prefix + chr(i + ASCII_A), results)

    def find_similar(self, prefix):
        node = self.root
        for c in prefix:
            index = ord(c) - ASCII_A
            if not node.child[index]:
                return []
            node = node.child[index]
        results = []
        self._find_words_with_prefix(node, prefix, results) 
        return results  