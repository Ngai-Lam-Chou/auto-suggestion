import heapq

ASCII_A = ord('a')


class TrieNode:
    def __init__(self):
        self.child = {}
        self.is_end_of_word = False
        self.heat = 0


class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word):
        node = self.root
        for char in word:
            if char not in node.child:
                node.child[char] = TrieNode()
            node = node.child[char]
        node.is_end_of_word = True
        node.heat += 1

    def search(self, word):
        node = self.root
        for char in word:
            if char not in node.child:
                return False, 0
            node = node.child[char]
        if node.is_end_of_word:
            node.heat += 1
            return True, node.heat
        return False, 0

    def _search_words_with_prefix(self, node, prefix, heap):
        if node.is_end_of_word:
            heapq.heappush(heap, (-node.heat, prefix))
        for char, child_node in node.child.items():
            self._search_words_with_prefix(child_node, prefix + char, heap)

    def search_similar(self, prefix, top_n=10, increment = False):
        words = prefix.split()
        node = self.root
        for word in words:
            for char in prefix:
                if char not in node.child:
                    return []
                node = node.child[char]

        heap = []

        self._search_words_with_prefix(node, prefix, heap)
        
        top_words = heapq.nlargest(top_n, heap)

        results = []
        for heat, word in top_words:
            search_node = self.root
            for char in word:
                search_node = search_node.child[char]
            if increment == True:
                search_node.heat += 1
            results.append((word, search_node.heat))

        return results

    def find_top_n_highest_heat_words_with_prefix(self, prefix="", top_n=10):
        node = self.root
        # Step 1: Navigate to the prefix node
        for char in prefix:
            if char not in node.child:
                return []  
            node = node.child[char]

        min_heap = []

        def dfs(current_node, current_word):
            if current_node.is_end_of_word:
                if len(min_heap) < top_n:
                    heapq.heappush(min_heap, (current_node.heat, current_word))
                else:
                    heapq.heappushpop(min_heap, (current_node.heat, current_word))

            for char, child_node in current_node.child.items():
                dfs(child_node, current_word + char)

        dfs(node, prefix)
        
        results = sorted(min_heap, key=lambda x: (-x[0], x[1]))

        return results
