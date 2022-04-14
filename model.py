from mesa import Model
from mesa.space import MultiGrid
from mesa.time import RandomActivation
from agents import Visitor, Stand, Cup
from mesa.datacollection import DataCollector


def get_cup_on_floor(model):
    '''Return the number of cups on the floor'''

    count = 0
    for g in model.schedule.agents:
        if isinstance(g, Cup):
            if g.on_floor == True:
                count += 1
    return count

def get_reuse_count(model):
    '''Return total amount of times that cups have been reused'''

    count = 0
    for g in model.schedule.agents:
        if isinstance(g, Cup):
            count += g.reuse_count

    return count


def get_cup(model):
    '''Return total number of cups in the model'''

    count = 0
    for g in model.schedule.agents:
        if isinstance(g,Cup):
            count += 1
    return count



class Festival (Model):
    """A model that represents a festival terrain, in which Visitor agents move around and interact with Stands and Cups.
    The model is designed to analyze cup recycling behavior"""

    def __init__(self, drinks_for_cup=1, reluctance_avg=0.5, awareness=0.05, stands=((2, 5), (8, 7), (12, 12)), visitors=200, width=15, height=15, name='Base case', verbose=False):
        super().__init__()
        self.name = name
        self.verbose = verbose
        self.num_visitors = visitors
        self.pos_stands = stands
        self.schedule = RandomActivation(self)
        self.grid = MultiGrid(height, width, True)
        self.cups_returned = 0
        self.cup_id = 0
        self.cups_on_floor = 0
        self.drinks_for_cup = drinks_for_cup
        self.awareness = awareness
        self.reluctance_avg = reluctance_avg

        self.cups_on_floor = 0
        self.datacollector = DataCollector({"Lost cups": lambda m: get_cup_on_floor(self),
                                            "Total cups": lambda m: get_cup(self),
                                            "Reuse count": lambda m: get_reuse_count(self),
                                            # "% lost": lambda m: round(get_cup_on_floor(self) / (get_cup(self) + get_reuse_count(self)), 2) * 100
                                            })

        # Create agents
        for i in range(self.num_visitors):
            name = "v"+str(i)
            reluctance = round(max(self.random.normalvariate(self.reluctance_avg, 0.5), 0), 1) # how many drinks in return for a cup would result in this agent returning the cup
            thirst_rate = int(max(self.random.normalvariate(10, 1), 0)) # integer in range [0,100] representing how much thirstier Visitor becomes each timestep
            sip_size = int(max(self.random.normalvariate(30, 10), 0)) # integer in range [0,200] representing how much ml is consumed each sip
            a = Visitor(name, self, reluctance, thirst_rate, sip_size)
            self.schedule.add(a)

            #Add the agent to a random grid cell
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(a, (x, y))

        def place_stand(pos, name, model):
            '''
            Place a single stand at indicated coordinate
            '''

            print("placing stand "+str(name)+" at "+str(pos))
            a = Stand(name, pos, model)
            model.schedule.add(a)
            model.grid.place_agent(a, pos)

        def place_stands(*args, model):
            '''
            Place multiple stands at the indicated coordinates
            '''

            existing = []
            for arg in args:
                assert isinstance(arg, tuple)
                assert arg not in existing # not on top of existing stand
                name = "s"+str(len(existing) + 1) # generate id from amount of existing stands
                place_stand(arg, name, model)
                existing.append(arg) # keep track of existing stands

        place_stands(*self.pos_stands, model=self)


    def step(self):
        """Advance the model by one step and collect data"""

        self.schedule.step()

        # collect data
        self.datacollector.collect(self)


