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
        #if visitor.cup is not None:
        for cup in visitor.collected_cups:

            print('Cup gets returned')
            self.model.schedule.remove(cup)  # Return current cup
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
            if random.randint(1,5) == 1 and self.dirty < 1:
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

        super().__init__(unique_id, model)
        self.thirst = 20 # initial thirst is 20%
        self.cup = None
        self.collected_cups = []
        self.condition = "HasNoCup"
        self.buying_drink = False
        self.reluctance = reluctance
        self.thirst_rate = thirst_rate
        self.sip_size = sip_size

        if self.unique_id == "v1" and self.model.verbose:
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
        if self.unique_id == "v1" and self.model.verbose:
            if self.cup is not None:
                report_contents = "and my cup contains " + str(self.cup.full) + " / 200 ml"
            else:
                report_contents = "and I have no cup"
            print(self.unique_id, "moving to", next_move, "my thirst is", self.thirst, '%', report_contents)

    def move_towards(self, pos):
        '''
        Move towards specific coordinate
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
        if self.unique_id == "v1" and self.model.verbose:
            print(self.unique_id, 'current position is ' + str(self.pos), "my thirst is", self.thirst, "%")
        self.model.grid.move_agent(self, tuple(new))
        if self.unique_id == "v1" and self.model.verbose:
            print(self.unique_id,'new position is ' + str(self.pos))

    def find_stand(self):
        ''''
        Find the nearest Stand and return the nearest
        '''

        options = [a for a in self.model.schedule.agents if isinstance(a, Stand)]
        nearest = min(options, key=lambda x: math.dist(x.pos, self.pos))

        return nearest

    def drop_cup(self):
        '''
        Look at surrounding trash and possibly drop cup on the ground
        '''

        # compute odds that Visitor drops cup depending on surrounding trash
        trash = 0
        for neighbor in self.model.grid.neighbor_iter(self.pos):
            if isinstance(neighbor, Cup):
                if neighbor.on_floor == True:
                    trash += 1

        odds = min(0.1 + trash/5, 1)

        # drop cup
        if random.random() < odds:
            self.cup.on_floor = True
            self.model.cups_on_floor += 1
            print("t =", str(self.model.schedule.time), ", 1 cup dropped (", self.model.cups_on_floor, ")")
            self.cup.pos = self.pos
            self.condition = "HasNoCup"
            self.model.grid.place_agent(self.cup,self.cup.pos) # place the Cup agent in the grid
            self.cup = None

            # log if verbose
            if self.unique_id == "v1" and self.model.verbose:
                print(self.unique_id, 'DROPPING CUP!')
                print(self.model.cups_on_floor)

    def collect_cup(self):
        '''If trash is around, possibly collect a cup. Odds are based on the model attribute awareness'''

        # Assess whether trash is around
        possible = False
        for neighbor in self.model.grid.neighbor_iter(self.pos):
            if isinstance(neighbor, Cup):
                if neighbor.on_floor == True and neighbor.dirty < 0.7:
                    possible = True
                    cup_to_pick = neighbor

        # Possible
        if possible:
            if random.random() < self.model.awareness:
                self.collected_cups.append(cup_to_pick)
                cup_to_pick.on_floor = False
                self.model.cups_on_floor -= 1
                print("t =", str(self.model.schedule.time),", 1 cup collected (", self.model.cups_on_floor, ")")
                self.condition = "HasCup"
                self.model.grid.remove_agent(cup_to_pick)  #remove the agent from the grid

                # log if verbose
                if self.unique_id == "v1" and self.model.verbose:
                    print(self.unique_id, 'DROPPING CUP!')
                    print(self.model.cups_on_floor)


    def buy_drink(self, stand):
        '''Buy drink from stand. Return cup if carrying one. Stand will return a used cup if possible,
        otherwise a new Cup agent is created.'''

        self.buying_drink = False # finished

        # If Visitor already has a cup, this cup is returned.
        if self.cup is not None:
            if self.unique_id == "v1" and self.model.verbose:
                print(self.unique_id,'RETURNING CUP!')
            self.cup.condition = "returned"
            stand.cups.append(self.cup)
            self.model.cups_returned += 1
            if self.unique_id == "v1" and self.model.verbose:
                print(stand.unique_id, "Cups that have been returned: ", self.model.cups_returned)

        # reuse if used cups in inventory
        if len(stand.cups) > 0:
            recycled_cup = stand.cups[-1] # last returned cup
            recycled_cup.fill() # fill cup
            recycled_cup.reuse_count += 1 # register recycle count
            self.cup = recycled_cup # give cup to agent
            stand.cups.pop() # remove cup from stand

        # create new cup agent if no reusables in inventory
        else:
            a = Cup(self.model)
            self.model.schedule.add(a)
            self.cup = a
            self.condition = "HasCup"

        # log if verbose
        if self.unique_id == "v1" and self.model.verbose:
            print(self.unique_id,'I bought a new drink, back to partying')

    def get_drink(self):
        ''''''

        if self.thirst < 80: # not thirsty enough
            self.random_move()
            return
        self.buying_drink = True
        goal = self.find_stand()
        if self.pos == goal.pos:
            self.buy_drink(goal)
        else:
            if self.unique_id == "v1" and self.model.verbose:
                print(self.unique_id, "Getting a drink")
            self.move_towards(goal.pos)

    def reduce_thirst(self):

        if self.cup is not None and self.cup.full > 0:
                # Take sip from cup
                if self.unique_id == "v1" and self.model.verbose:
                    print(self.unique_id, "my thirst is", self.thirst, '%. Drinking...')
                self.cup.full -= min(self.cup.full,
                                     self.sip_size)  # sip size of 20ml or whatever amount under 20ml is remaining
                self.thirst -= min(self.thirst,
                                   20)  # thirst reduction of 20% or whatever amount of thirst is remaining
                # Now move
                self.random_move()
                return

    def step(self):

        # if the agent was already on their way to a stand, they continue
        if self.buying_drink:
            self.get_drink()

        # otherwise it assesses its thirst, whether to take a sip, or get a drink if no cup is present
        elif self.thirst > 50: # threshold to take a sip if currently a cup
            if self.cup is None:
                self.get_drink() # function has internal threshold >80% thirst, so agent may not actually get drink
            elif self.cup.full > 0:
                self.reduce_thirst()
            else:
                self.get_drink() # function has internal threshold >80% thirst, so agent may not actually get drink
        else:
            self.random_move()

        # if in possession of empty cup, decide what to do with it (drop, collect more cups)
        if self.cup is not None and self.cup.full <= 0:
            if self.reluctance > self.model.drinks_for_cup:
                self.drop_cup()
            else:
                self.collect_cup()

        # at the end of every step an agent gets more thirsty
        max_increase = 100 - self.thirst
        self.thirst += min(self.thirst_rate, max_increase)
