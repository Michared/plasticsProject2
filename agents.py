import math
import random
from mesa import Agent


class Stand(Agent):
    '''
    Stand located on grid. Can create or remove Cup agents from the model whenever meeting a Visitor agent.
    '''

    def __init__(self, unique_id, pos, model):
        '''
        Creates a new BeerStand

        Args:
            pos: (coordinate) location of the stand on the grid
        '''

        super().__init__(unique_id, model)
        self.pos = pos
        self.condition = "Stand"

    def sell_drink(self, Visitor):
        if Visitor.cup is not None:
            print('Cup gets returned')
            self.model.schedule.remove(Visitor.cup)  # Return current cup
            self.model.cups_returned += 1
            print(self.model.cups_returned)
        a = Cup(self.model)
        self.model.schedule.add(a)
        Visitor.cup = a
        Visitor.condition = "HasCup"
        print('Selling cup')


class Cup(Agent):
    '''
    Is created as full by Beerstand, moves with Visitor until it is either returned or dropped.
    Can also be collected and damaged.
    '''

    def __init__(self, model):
        '''
        Creates a new Visitor

        Args:
            pos: (coordinate) location of the Visitor on the grid
        '''

        model.cup_id += 1

        id = model.cup_id

        super().__init__(id, model)
        self.full = 1.0
        self.dirty = 0.0
        self.damaged = 0.0
        self.on_floor = False


    def step(self):
        if self.on_floor == True:
            if random.randint(1,10) == 1 and self.dirty < 1:
                self.dirty += 0.1



class Visitor(Agent):
    '''
    Walks around on grid, buys drinks, takes sips from, drops or collects and returns cups.
    The function random_move was adopted from the RandomWalker agent from WolfSheep model from the course SYSMOD 3
    '''

    grid = None
    x = None
    y = None
    moore = True

    def __init__(self, unique_id, model, willingness):
        '''
        Creates a new Visitor

        Args:
        pos: (coordinate) location of the Visitor on the grid
            x: The agent's current x coordinate
            y: The agent's current y coordinate
        grid: The MultiGrid object in which the agent lives.
        moore: If True, may move in all 8 directions.
                Otherwise, only up, down, left, right.
        '''

        super().__init__(unique_id, model)
        self.thirst = 0
        self.cup = None
        self.condition = "HasNoCup"
        self.buying_drink = False
        self.reluctance = willingness
        if self.unique_id == "v1":
            print(self.unique_id, "has a reluctance of", self.reluctance)

    def random_move(self):
        '''
        Step one cell in any allowable direction.
        '''
        # Pick the next cell from the adjacent cells.
        next_moves = self.model.grid.get_neighborhood(self.pos, self.moore, True)
        next_move = self.random.choice(next_moves)
        # Now move:
        self.model.grid.move_agent(self, next_move)
        if self.unique_id == "v1":
            print(self.unique_id, "moving to", next_move, "my thirst is", self.thirst)

    def move_towards(self, pos):
        '''
        Moves towards specific coordinate
        '''

        # Find new position after moving towards pos
        new = [0, 0]
        for i in [0, 1]:
            if self.pos[i] > pos[i]:
                new[i] = self.pos[i] - 1
            elif self.pos[i] < pos[i]:
                new[i] = self.pos[i] + 1
            else:
                new[i] = self.pos[i]

        # Now move
        if self.unique_id == "v1":
            print(self.unique_id, 'current position is ' + str(self.pos), "my thirst is", self.thirst)
        self.model.grid.move_agent(self, tuple(new))
        if self.unique_id == "v1":
            print(self.unique_id,'new position is ' + str(self.pos))

    def find_stand(self):
        ''''
        Find the nearest Stand
        '''

        options = [pos for pos in self.model.pos_stands]
        nearest = min(options, key=lambda x: math.dist(x, self.pos))

        return nearest

    def drop_cup(self):
        '''
        Drop cup on the ground
        '''
        
        self.cup.on_floor = True
        self.model.cups_on_floor += 1
        self.cup.pos = self.pos
        self.condition = "HasNoCup"
        if self.unique_id == "v1":
            print(self.unique_id, 'DROPPING CUP!')
            print(self.model.cups_on_floor)
        self.cup = None


    def buy_drink(self):
        #Buy new drink. If Visitor already has a cup, this cup is returned.
        self.buying_drink = False
        if self.unique_id == "v1":
            print(self.unique_id, "I'm done with getting a drink")
        if self.cup is not None:
            if self.unique_id == "v1":
                print(self.unique_id,'RETURNING CUP!')
            self.model.schedule.remove(self.cup) # Return current cup
            self.model.cups_returned += 1
            if self.unique_id == "v1":
                print("cups that have been returned: ", self.model.cups_returned)

        a = Cup(self.model) # doesn't work yet
        self.model.schedule.add(a)
        self.cup = a
        self.condition = "HasCup"
        if self.unique_id == "v1":
            print(self.unique_id,'Buying cup')


    def get_drink(self):
        goal = self.find_stand()
        self.buying_drink = True
        if self.unique_id == "v1":
            print(self.unique_id, "I am now getting a drink")
        if self.pos == goal:
            self.buy_drink()
        else:
            self.move_towards(goal)

    def reduce_thirst(self):

        if self.cup is not None and self.cup.full > 0.0:
                #if random.randint(self.th)
                # Take sip from cup
                self.cup.full -= 0.5
                self.thirst -= 5
                if self.unique_id == "v1":
                    print(self.unique_id, "my thirst is", self.thirst,'Drinking...')
                # Now move
                self.random_move()
                return

    def step(self):
        if self.buying_drink:
            self.get_drink()
        #the more thirsty you are the more likely you are to take a sip
        elif self.thirst >= 5 and not self.buying_drink:
            if self.cup is None:
                if random.randint(1, 4) == 1:
                    self.get_drink()
                else:
                    self.random_move()
            else:
                if self.cup.full > 0:
                    self.reduce_thirst()  # Decide and act to reduce thirst
                else:
                    #empty cup decide whether to trow the cup away or get a drink
                    trash = 0

                    for neighbor in self.model.grid.neighbor_iter(self.pos):
                        if isinstance(neighbor, Cup):
                            if neighbor.on_floor == True:
                                trash += 1
                                print('Trash on the ground', trash)

                    if trash > 2:  # Visitor critizes the cups on the ground
                        self.drop_cup()

                    else:
                        self.get_drink()

        else:
            self.random_move()

        if self.cup is not None:
            if self.reluctance > self.model.drinks_for_cup and self.cup.full <= 0:
                self.drop_cup()

        if self.thirst < 10:
            self.thirst += 0.5

        # The agent's step will go here.
        # For demonstration purposes we will print the agent's unique_id
        # print("Hi, I am agent " + str(self.unique_id) + ". I am at position " + str(self.pos) + " and I have " +str(self.thirst) + " thirst.")
