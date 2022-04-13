import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from matplotlib.colors import LinearSegmentedColormap
from agents import Cup
from model import get_cup, get_cup_on_floor, get_reuse_count

def visualize_batch(data):
    '''Visualize the data from the batchrunner'''



def visualize_model(model, save=True, show=False):
    '''
    Visualize the model in a grid (left) and a line graph (right)
    '''

    color_map = {
        "Empty": 0,
        "HasNoCup": 1,
        "HasCup": 2,
        "Stand": 3
    }

    # percentage verloren cups berekenen
    lost_per_use = round(get_cup_on_floor(model) / (get_cup(model) + get_reuse_count(model)), 2) * 100

    #set up the lay-out for the grid and the graph
    fig, ax = plt.subplots(1, 2, figsize=(10, 5), facecolor=(1, 1, 1), tight_layout=True)

    #Set up the title of the image
    title_text = "1 cup is worth " + str(model.drinks_for_cup) + " drink (grid = " + str(
        model.grid.width) + " x " + str(model.grid.height) + ", N = " + str(model.num_visitors) + ", t = " \
                 + str(model.schedule.steps) + ") Cups lost per cup used " + str(lost_per_use) + "%"
    fig.suptitle(title_text)

    filename = "plot_van_PlasticProject_ABM"
    myColors = ('grey', 'green', 'red', 'blue') #Choose the colors for the different types of agents in the grid
    colors = LinearSegmentedColormap.from_list('Custom', myColors, len(myColors))
    ax[0].set_aspect('equal')

    """""Make the grid for later display"""""
    grid = np.zeros((model.grid.height, model.grid.width)) #Make a grid filled with zero's

    #Iterate trough all the agents and chance the value of their cell to their corresponding value
    for agent in model.schedule.agents:
            if not isinstance(agent, Cup):
                grid[agent.pos] = color_map.get(agent.condition)

    #Display the grid
    ax[0] = sns.heatmap(grid, ax=ax[0], cmap=colors, linewidths=.5, linecolor='black', cbar=True)
    colorbar = ax[0].collections[0].colorbar
    colorbar.set_ticks([0, 1, 2, 3])
    colorbar.set_ticklabels(['Empty cell', 'Visitor without cup', 'Visitor with cup', 'Stand'])

    model_data = model.datacollector.get_model_vars_dataframe()
    ax[1] = sns.lineplot(data=model_data, ax=ax[1])
    ax[1].set_xlabel("Steps")
    ax[1].set_ylabel("Cups")

    if save:
        plt.savefig(filename + ".png", dpi=100, bbox_inches='tight')
    if show:
        plt.show()

    return lost_per_use