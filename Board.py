import random
class Board:
    def __init__(self, dim):
        self.dim = dim
        self.turn = random.choice([0,1])
        f = open("word_lists/sounds", "r")
        words = f.read()
        wordList = words.split("\n")
        random.shuffle(wordList)
        wordValues = [self.turn]*8 + [(self.turn+1)%1]*7 +[-2]*2 + [-1]*(dim*dim-17)
        random.shuffle(wordValues)
        self.board = [[]]*dim

        for x in range(dim):
            for y in range(dim):
                self.board[x].append(Word(wordList[x*y+y], wordValues[x*y+y]))
                print(self.board[x][y])


class Word:
    #should color be an int instead?
    def __init__(self, word, color):
        self.word = word
        self.color = color
        self.selected = False
