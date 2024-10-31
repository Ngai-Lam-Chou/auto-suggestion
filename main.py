import keyboard
from trie import Trie, TrieNode
import re
PATTERN = r"heat\((\w*)\)"
with open("alphabet_words.txt", "r") as file:
    # Convert file content to lowercase
    FILE_CONTENT = list(map(lambda word: word.strip().lower(), file.readlines()))

if __name__ == "__main__":
    trie = Trie()
    for word in FILE_CONTENT:
        trie.insert(word)
    
    input_str = ""
    suggestions = []
    index = 0

    while True:
        event = keyboard.read_event()
        if event.event_type == keyboard.KEY_DOWN:
            key = event.name
            if len(key) == 1:
                suggestions = []  # Clear suggestions on new character input
                input_str += key.lower()

            elif key == "space":
                suggestions = []  # Clear suggestions on space
                input_str += " "

            elif key == "enter":
                if re.match(PATTERN, input_str.strip()):
                    prefix = re.search(PATTERN, input_str).group(1)
                    
                    top_n_heat_words = trie.find_top_n_highest_heat_words_with_prefix(prefix)
                    
                    print("\nTop Heated Words:")
                    print("\n".join(f"{word}: {heat}" for heat, word in top_n_heat_words))
                    
                    input_str = ""  # Clear input for next round
                    continue
                if not input_str:
                    print("\nPlease Enter A Word")
                    continue

                suggestions = trie.search_similar(input_str.lower(),increment=True)[::-1]
                if input_str not in [suggestion[0] for suggestion in suggestions]:
                    trie.insert(input_str.lower())
                    suggestions.append((input_str.lower(), 1))  # Update the heat
                    print("\nThank You For Providing A New Word!")
                
                if suggestions:
                    print("\nSuggestions:")
                    print("\n".join(f"{name}: {heat}" for name, heat in suggestions))
                else:
                    print("\nNo Suggestions Found")

                index = 0
                input_str = ""  # Clear input after processing

            elif key == "backspace":
                suggestions = []  # Clear suggestions when backspacing
                input_str = input_str[:-1]

            elif key == "tab":
                if not suggestions:  # Only fetch suggestions if none exist
                    suggestions = trie.search_similar(input_str.lower())
                    index = 0

                if suggestions:
                    input_str = suggestions[index][0]  # Update input with the suggestion
                    index = (index + 1) % len(suggestions)  # Cycle through suggestions
                else:
                    print("\nNo Suggestions")
            elif key == "esc":
                input_str = ""
            # Display current input string
            print(f"\r{' ' * 80}\rCurrent input: {input_str}", end='')
