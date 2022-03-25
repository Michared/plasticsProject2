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
        self.cups = []

    def sell_drink(self, visitor):
        if visitor.cup is not None:
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
    Is created as full by Stand, moves with Visitor until it is either returned or dropped.
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
        self.full = 200 #given out with 200 ml of content
        self.dirty = 0.0
        self.damaged = 0.0
        self.on_floor = False
        self.reuse_count = 0
        self.condition = ""

    def fill(self):
        ''''
        Fill cup
        '''

        self.full = 200

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

    def __init__(self, unique_id, model, reluctance, thirst_rate, sip_size):
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
        self.thirst = 20 # initial thirst is 20%
        self.cup = None
        self.condition = "HasNoCup"
        self.buying_drink = False
        self.reluctance = reluctance
        self.thirst_rate = thirst_rate
        self.sip_size = sip_size

        if self.unique_id == "v1":
            print(self.unique_id, "I have a reluctance of", self.reluctance, ", a thirst rate of", self.thirst_rate, "% and a sip size of", self.sip_size, "ml")

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
            if self.cup is not None:
                report_contents = "and my cup contains " + str(self.cup.full) + " / 200 ml"
            else:
                report_contents = "and I have no cup"
            print(self.unique_id, "moving to", next_move, "my thirst is", self.thirst, '%', report_contents)

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
            print(self.unique_id, 'current position is ' + str(self.pos), "my thirst is", self.thirst, "%")
        self.model.grid.move_agent(self, tuple(new))
        if self.unique_id == "v1":
            print(self.unique_id,'new position is ' + str(self.pos))

    def find_stand(self):
        ''''
        Find the nearest Stand
        '''

        options = [a for a in self.model.schedule.agents if isinstance(a, Stand)]
        nearest = min(options, key=lambda x: math.dist(x.pos, self.pos))

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
        self.model.grid.place_agent(self.cup,self.cup.pos)
        self.cup = None


    def buy_drink(self, stand):
        #Buy new drink. If Visitor already has a cup, this cup is returned.
        self.buying_drink = False
        if self.cup is not None:
            if self.unique_id == "v1":
                print(self.unique_id,'RETURNING CUP!')
            self.cup.condition = "returned"
            stand.cups.append(self.cup)
            # self.model.schedule.remove(self.cup) # Return current cup
            self.model.cups_returned += 1
            if self.unique_id == "v1":
                print(stand.unique_id, "Cups that have been returned: ", self.model.cups_returned)
        if len(stand.cups) > 0:
            recycled_cup = stand.cups[-1] # last returned cup
            recycled_cup.fill() # fill cup
            recycled_cup.reuse_count += 1 # register recycle count
            self.cup = recycled_cup # give cup to agent
            stand.cups.pop() # remove cup from stand
        else:
            a = Cup(self.model)
            self.model.schedule.add(a)
            self.cup = a
            self.condition = "HasCup"

        if self.unique_id == "v1":
            print(self.unique_id,'I bought a new drink, back to partying')

    def get_drink(self):
        if self.thirst < 80: # not thirsty enough
            self.random_move()
            return
        self.buying_drink = True
        goal = self.find_stand()
        if self.pos == goal.pos:
            self.buy_drink(goal)
        else:
            if self.unique_id == "v1":
                print(self.unique_id, "Getting a drink")
            self.move_towards(goal.pos)

    def reduce_thirst(self):

        if self.cup is not None and self.cup.full > 0:
                #if random.randint(self.th)
                # Take sip from cup
                if self.unique_id == "v1":
                    print(self.unique_id, "my thirst is", self.thirst,'%. Drinking...')
                self.cup.full -= min(self.cup.full,
                                     self.sip_size)  # sip size of 20ml or whatever amount under 20ml is remaining
                self.thirst -= min(self.thirst,
                                   20)  # thirst reduction of 20% or whatever amount of thirst is remaining
                # Now move
                self.random_move()
                return

    def step(self):
        if self.buying_drink:
            self.get_drink()
        elif self.thirst > 50: # threshold to take a sip if currently a cup
            if self.cup is None:
                self.get_drink() # this function has a threshold higher than 50% thirst
            elif self.cup.full > 0:
                self.reduce_thirst()
            else:
                self.get_drink() # this function has a threshold higher than 50% thirst
        else:
            self.random_move()

        if self.cup is not None:
            if self.reluctance > self.model.drinks_for_cup and self.cup.full <= 0:
                self.drop_cup()

        max_increase = 100 - self.thirst
        self.thirst += min(self.thirst_rate, max_increase)

        # The agent's step will go here.
        # For demonstration purposes we will print the agent's unique_id
        # print("Hi, I am agent " + str(self.unique_id) + ". I am at position " + str(self.pos) + " and I have " +str(self.thirst) + " thirst.")
