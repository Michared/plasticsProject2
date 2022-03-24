import random

from mesa import Model
from mesa.space import MultiGrid
from mesa.time import RandomActivation
from agents import Visitor, Stand


class Festival (Model):
    """A model with some number of agents."""

    def __init__(self, visitors=20, drinks_for_cup=0.5, stands=((2, 5), (8, 7), (12,12)), width=15, height=15):
        self.num_visitors = visitors
        self.pos_stands = stands
        self.schedule = RandomActivation(self)
        self.grid = MultiGrid(height, width, True)
        self.cups_returned = 0
        self.cup_id = 0
        self.cups_on_floor = 0
        self.drinks_for_cup = drinks_for_cup


        # Create agents
        for i in range(self.num_visitors):
            name = "v"+str(i)
            reluctance = round(max(self.random.normalvariate(0.5, 0.5), 0), 1) # how many drinks in return for a cup would result in this agent returning the cup
            a = Visitor(name, self, reluctance)
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

        # self.datacollector = DataCollector(
        #     {"Cups": lambda m: m.schedule.get_type_count(Cup)})

    def step(self):
        """Advance the model by one step."""
        self.schedule.step()
        # collect data
        # self.datacollector.collect(self)

