from mesa import Model
from mesa.space import MultiGrid
from mesa.time import RandomActivation
from agents import Visitor, Stand


class Festival (Model):
    """A model with some number of agents."""

    def __init__(self, visitors=8, stands=((0, 6), (9, 4)), width=10, height=10):
        self.num_visitors = visitors
        self.pos_stands = stands
        self.schedule = RandomActivation(self)
        self.grid = MultiGrid(height, width, True)
        self.cups_returned = 0
        self.cup_id = 0

        # Create agents
        for i in range(self.num_visitors):
            name = "v"+str(i)
            a = Visitor(name, self)
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

#Poging tot visualisatie
'''''
hmap = hv.HoloMap()
for i in range(10):
    data = np.array([[value(c) for c in row] for row in Festival.grid.grid])
    data = np.transpose(data)
    data = np.flip(data, axis=0)
    bounds = (0, 0, 5, 5)
    hmap[i] = hv.Image(data, vdims=[hv.Dimension('a', range=(0, 21))], bounds=bounds).relabel('Grid').opts(cmap='bwr', xticks=[0], yticks=[0])
'''''
#Andere manier visualisatie
'''''
server = ModularServer(model,
                       [model.grid],
                       "Festival")
server.port = 8521  # The default
server.launch()


def agent_portrayal(agent):
    portrayal = {"Shape": "circle",
                 "Filled": "true",
                 "Layer": 0,
                 "Color": "red",
                 "r": 0.5}
    return portrayal
'''''