class Board:
    def __init__(self, dim):
        self.dim = dim

        # todo find way to choose the words
        self.board = [['a'] * dim] * dim

        class Word:
            #should color be an int instead?
            def __init__(self, word, color):
                self.word = word
                self.color = color
                self.selected = False
