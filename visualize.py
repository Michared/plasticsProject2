import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from matplotlib.colors import LinearSegmentedColormap

from agents import Cup


def visualize_model(model, save=True, show=False):
    color_map = {
        "Empty": 0,
        "HasNoCup": 1,
        "HasCup": 2,
        "Stand": 3
    }

    fig, ax = plt.subplots(1, 2, figsize=(10, 5), facecolor=(1, 1, 1), tight_layout=True)

    title_text = "Visitors with empty or full cup" + " Height= " + str(model.grid.height) + " Width= " + str(
        model.grid.width) + " t= " + str(model.schedule.steps)
    fig.suptitle(title_text)

    filename = "plot_van_PlasticProject_ABM"
    myColors = ('grey', 'green', 'red', 'blue')
    colors = LinearSegmentedColormap.from_list('Custom', myColors, len(myColors))
    ax[0].set_aspect('equal')

    grid = np.zeros((model.grid.height, model.grid.width))
    for agent in model.schedule.agents:
            if not isinstance(agent, Cup):
                grid[agent.pos] = color_map.get(agent.condition)


    ax[0] = sns.heatmap(grid, ax=ax[0], cmap=colors, linewidths=.5, linecolor='black', cbar=True)
    colorbar = ax[0].collections[0].colorbar
    colorbar.set_ticks([0, 1, 2, 3])
    colorbar.set_ticklabels(['Empty', 'Visitor without cup', 'Visitor with cup', 'Stand'])

    # results = Festival.datacollector.get_model_vars_dataframe()
    #ax[1] = sns.lineplot(data=model.cups_on_floor, ax=ax[1])
    # ax[1].set_xlabel("Steps")
    # ax[1].set_ylabel("Cups")

    if save:
        plt.savefig(filename + ".png", dpi=100, bbox_inches='tight')
    if show:
        plt.show()