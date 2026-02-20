import random
from collections import defaultdict

#Ainda em teste o gerador de letras com markov 
class SimpleMarkov:
    def __init__(self):
        self.model = defaultdict(list)
        self.starts = []

    def train(self, texts):
        for t in texts:
            words = t.split()
            if len(words) < 2:
                continue
            self.starts.append(words[0])
            for i in range(len(words)-1):
                self.model[words[i]].append(words[i+1])

    def generate(self, max_words=50, seed=None):
        if seed:
            word = seed
        else:
            word = random.choice(self.starts)
        result = [word]
        for _ in range(max_words-1):
            if word not in self.model:
                break
            word = random.choice(self.model[word])
            result.append(word)
        return " ".join(result)
