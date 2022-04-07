from visualize import visualize_model
from model import Festival

# Run (press the green button in the gutter to run the script)
if __name__ == '__main__':
    model = Festival(drinks_for_cup=0, awareness=0.2, reluctance_avg = 0.8)
    for i in range(200):
        model.step()
    visualize_model(model)