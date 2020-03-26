import random
import string

from Users import User

class Game(object):
    """An object representing a single 'gameroom' of Set"""

    def __init__(self, name, size = 4):
        self.game_id = Game.generate_room_id()

        # create and shuffle deck
        self.generate_deck()

        # basic info for the game
        self.name = name
        self.size = 4

        # player state
        self.players = {}

        # board state
        self.board = []
        self.last_set = None

    def to_json(self):
        return {
            "name" : self.name,
            "size" : self.size,
            "players" : [player.to_json() for player in self.players.values()],
            "board" : [card.to_json() for card in self.board],
            "last_set" : self.last_set            
        }

    def add_player(self,user):
        self.players[user.uid] = user.as_player()
        
    def remove_player(self,user):
        del self.players[user.uid]

    def punish(self,user):
        self.players[user.uid].blocked = True
        
    def reward(self,user):
        self.players[user.uid].sets += 1
        
    def generate_deck(self):
        self.deck = []
        
        # iterate over each value of each attribute
        for i in range(3):
            for j in range(3):
                for k in range(3):
                    for l in range(3):
                        self.deck.append(Card(i,j,k,l))
        random.shuffle(self.deck)
        
    def draw(self):
        """Draw enough cards to get a set on the board, returns False if the deck is emptied"""

        # try to draw until 12 cards are on the board
        for i in range(0,12 - len(self.board)):
            if len(self.deck) > 0:
                self.board.append(self.deck.pop())
            else:
                return False
        
        # check if there is a set yet, otherwise try to draw 3 cards at most twice
        if not self.check_set_exists():
            for i in range(3):
                if len(self.deck) > 0:
                    self.board.append(self.deck.pop())
                else:
                    return False
                
            # check if that fixed the board, there is always a set after redrawing twice
            if not self.check_set_exists():
                for i in range(3):
                    if len(self.deck) > 0:
                        self.board.append(self.deck.pop())
                    else:
                        return False
                        
        return True

    def check_set_exists(self):
        """just brute forcing, not sure how to do much better without getting complicated"""
        for i in range(len(self.board)-2):
            for j in range(1,len(self.board)-1):
                for k in range(2,len(self.board)):
                    if Card.check_set(self.board[i],
                                      self.board[j],
                                      self.board[k]):
                        return True
        return False

    def check_set(self,selection):
        """Given a list of 3 indices, check if these indices are a set"""
        
        # make sure we selected valid cards
        for i in range(3):
            if selection[i] < 0 or selection[i] >= len(self.board):
                return False
            
        # check the match
        return Card.check_set(self.board[selection[0]], 
                              self.board[selection[1]], 
                              self.board[selection[2]])

    def remove_set(self,selection):
        """remove cards for given indices"""            

        self.last_set = []

        for i in range(3):
            # make sure we selected valid cards
            if selection[i] < 0 or selection[i] >= len(self.board):
                return False
            
            # add the card data to display
            self.last_set.append(self.board[selection[i]].to_json())


        # remove all at once using multi-index
        del self.board[selection[0],selection[1],selection[2]]

    @classmethod
    def generate_room_id(cls):
        """Generate a random room ID"""
        id_length = 5
        return ''.join(random.SystemRandom().choice(string.ascii_uppercase) for _ in range(id_length))   


class Card(object):
    COLOURS = ["red","green","blue"]
    SHADINGS = ["FULL","SHADED","EMPTY"]
    NUMBERS = ["1","2","3"]
    SHAPES = ["OVAL","DIAMOND","FLEXYBOY"]

    def __init__(self, colour, shading, number, shape):
        """Initialise a card using a quadruple of values 0,1,2"""
        self.attr = (colour, shading, number, shape)

    def to_json(self):
        return {
            "colour" : Card.COLOURS[self.attr[0]],
            "shading" : Card.SHADINGS[self.attr[1]],
            "number" : Card.NUMBERS[self.attr[2]],
            "shape" : Card.SHAPES[self.attr[3]],
        }
        
    @classmethod
    def attr_same(cls,at1,at2,at3):
        return (at1 == at2 and at2 == at3)

    @classmethod
    def attr_diff(cls,at1,at2,at3):
        return (at1 != at2 and at2 != at3 and at1 != at3)
    
    @classmethod
    def check_set(cls,a, b, c):
        correct = True
        
        # for each attribute check if it is valid
        for i in [0,1,2,3]:
            if Card.attr_same(a.attr[i],b.attr[i],c.attr[i]) or Card.attr_diff(a.attr[i],b.attr[i],c.attr[i]):
                continue
            correct = False
        return correct
