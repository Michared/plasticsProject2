# This is a  Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

# Imports
from mesa.visualization.ModularVisualization import ModularServer
import mesa

from visualize import visualize_model
from model import Festival

# Run (press the green button in the gutter to run the script)
if __name__ == '__main__':
    model = Festival()
    for i in range(200):
        model.step()
    visualize_model(model)