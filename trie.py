class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end_of_word = False
        self.heat = 0  

class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word):
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end_of_word = True
        node.heat += 1 

    def search(self, word):
        node = self.root
        for char in word:
            if char not in node.children:
                return False, 0 
            node = node.children[char]
        if node.is_end_of_word:
            node.heat += 1 
            return True, node.heat 
        return False, 0 
