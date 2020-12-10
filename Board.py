import random
class Board:
    def __init__(self, dim):
        self.dim = dim
        self.turn = random.choice([0,1])
        print(str(self.turn))
        f = open("word_lists/sounds", "r")
        words = f.read()
        wordList = words.split("\n")
        random.shuffle(wordList)
        wordValues = [self.turn]*8 + [(self.turn+1)%2]*7 + [-1] * (dim*dim-16) + [-2]
        random.shuffle(wordValues)
        self.board = [([0] * dim) for rows in range(dim)]

        for x in range(dim):
            for y in range(dim):
                self.board[x][y] = Word(wordList[x*dim+y], wordValues[x*dim+y])
    def copy(self):
        b = Board(self.dim)
        b.turn = self.turn
        for i in range(b.dim):
            for j in range(b.dim):
                b.board[i][j]=self.board[i][j].copy()
        return b


class Word:
    #should color be an int instead?
    def __init__(self, word, color):
        self.word = word
        self.color = color
        self.selected = False
    def copy(self):
        w = Word(self.word,self.color)
        w.selected = self.selected
        return w