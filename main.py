import keyboard
from trie import Trie, TrieNode

with open("alphabet_words.txt", "r") as file:
    FILE_CONTENT = list(map(lambda word: word.strip(), file.readlines()))

if __name__ == "__main__":
    heatmap = {}
    trie = Trie()
    for word in FILE_CONTENT:
        trie.insert(word)
    
