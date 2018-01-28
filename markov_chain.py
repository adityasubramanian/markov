import random, re, argparse, _pickle, pickle

class MarkovChain(object):
    def __init__(self,n):
        self.states = {} # empty states
        self.state_counts = {}
        self.n = n
    def train(self,state,next):
        if state not in self.states:
            self.states[state] = {}
        state_dict = self.states[state]
        state_dict[next] = state_dict.get(next,0) + 1 # Counts for the next block of markov chain
        self.state_counts[state] = self.state_counts.get(state,0) + 1 # Counts for current state
    def next(self,state):
        state_dict = self.states[state]
        choice = random.randint(0,self.state_counts[state])
        sum = 0
        for word, count in state_dict.items():
            if sum+count >= choice:
                return word
            sum += count
        return random.choice(list(self.states.keys()))
    def train_words(self,words):
        words = list(words)
        for i in range(len(words) - int(self.n) - 1):
            state = tuple(words[i:i+int(self.n)])
            next = words[i+int(self.n)]
            self.train(state,next)
    def generate(self,count,start=None):
        if start is None:
            start = random.choice(list(self.states))
            return Generator(self, start, count)
        elif start not in self.states:
            print("{} not in word list".format(start))
            return
    def sentence(self):
        candidate_starts = [s for s in self.states.keys() if s[0] == '.']
        start = random.choice(candidate_starts)
        sentence = list(start[1:])
        for word in self.generate(None, start = start):
            if word != '.':
                sentence.append(word)
            else:
                break
        string = ' '.join(sentence)
        return string[0].upper() + string[1:] + '.'
class Generator(object):
    def __init__(self, markov_chain, start, count):
        self.markov = markov_chain
        self.previous = start
        self.count = count
    def __iter__(self):
        return self
    def __next__(self):
        if self.count is not None and self.count <= 0:
            raise StopIteration()
        return_value = self.markov.next(self.previous)
        self.previous = self.previous[1:]+(return_value,)
        if self.count is not None:
            self.count -= 1
        return return_value
def words(file_):
    with open(file_, 'r') as file:
        for line in file.readlines():
            for word in re.findall(r"[A-Za-z'-]+|\.",line):
                word = word.strip("'-")
                if word:
                    yield word.lower()
def main():
    arg_parse = argparse.ArgumentParser()
    arg_parse.add_argument("--input_file", help = 'The input file to the Markov Chain', default = None)
    arg_parse.add_argument("--output_file", help = 'The output file for the Markov Chain', default = None)
    arg_parse.add_argument("--train_file", help='The file to train Markov Chain on', default = None)
    arg_parse.add_argument("--save_to_file", help = 'Boolean, save text to output file?', default = True)
    arg_parse.add_argument("--n", help ='Number of words in state', default = 1)
    args = arg_parse.parse_args()
    if args.input_file is not None:
        markov = pickle.load(open(args.input_file, 'rb'))
        open(args.input_file).close()
    else:
        markov = MarkovChain(n=args.n)
    if args.train_file is not None:
        markov.train_words(words(args.train_file))
    if args.save_to_file:
        print(markov.sentence())
    if args.output_file is not None:
        with open(args.output_file, 'wb') as pickle_file:
            _pickle.dump(markov, pickle_file)

if __name__ == "__main__":
    main()