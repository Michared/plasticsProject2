from mesa import Model
from mesa.space import MultiGrid
from mesa.time import RandomActivation
from agents import Visitor, Stand, Cup
from mesa.datacollection import DataCollector

"""Functies die de waardes van het model bijhouden."""
def get_cup_on_floor(model):
    # get the number of cups on the floor
    count = 0
    for g in model.schedule.agents:
        if isinstance(g, Cup):
            if g.on_floor == True:
                count += 1
    return count

def get_reuse_count(model):
    # get the total amount of times that cups have been recycled
    count = 0
    for g in model.schedule.agents:
        if isinstance(g, Cup):
            count += g.reuse_count

    return count


def get_cup(model):
    # get the total number of cups in the model
    count = 0
    for g in model.schedule.agents:
        if isinstance(g,Cup):
            count += 1
    return count



class Festival (Model):
    """A model with some number of agents."""

    def __init__(self, visitors=200, drinks_for_cup=1, stands=((2, 5), (8, 7), (12,12)), width=15, height=15):
        self.num_visitors = visitors
        self.pos_stands = stands
        self.schedule = RandomActivation(self)
        self.grid = MultiGrid(height, width, True)
        self.cups_returned = 0
        self.cup_id = 0
        self.cups_on_floor = 0
        self.drinks_for_cup = drinks_for_cup

        self.cups_on_floor = 0
        self.datacollector = DataCollector({"Lost cups": lambda m: get_cup_on_floor(self),
                                            "Total cups": lambda m: get_cup(self),
                                            "Reuse count": lambda m: get_reuse_count(self),
                                            })

        # Create agents
        for i in range(self.num_visitors):
            name = "v"+str(i)
            reluctance = round(max(self.random.normalvariate(1, 0.5), 0), 1) # how many drinks in return for a cup would result in this agent returning the cup
            thirst_rate = int(max(self.random.normalvariate(10, 1), 0)) # integer in range [0,100] representing how much thirstier Visitor becomes each timestep
            sip_size = int(max(self.random.normalvariate(30, 10), 0)) # integer in range [0,200] representing how much ml is consumed each sip
            a = Visitor(name, self, reluctance, thirst_rate, sip_size)
            self.schedule.add(a)

            #Add the agent to a random grid cell
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(a, (x, y))

        def place_stand(pos, name, model):
            print("placing stand "+str(name)+" at "+str(pos))
            a = Stand(name, pos, model)
            model.schedule.add(a)
            model.grid.place_agent(a, pos)

        def place_stands(*args, model):
            existing = []
            for arg in args:
                assert isinstance(arg, tuple)
                assert arg not in existing # not on top of existing stand
                name = "s"+str(len(existing) + 1) # generate id from amount of existing stands
                place_stand(arg, name, model)
                existing.append(arg) # keep track of existing stands

        place_stands(*self.pos_stands, model=self)


    def step(self):
        """Advance the model by one step."""
        self.schedule.step()
        """Verzamel de data."""
        self.datacollector.collect(self)


