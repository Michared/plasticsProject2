from visualize import visualize_model
from model import Festival

# Run (press the green button in the gutter to run the script)
if __name__ == '__main__':
    model = Festival(drinks_for_cup=1)
    for i in range(200):
        model.step()
    visualize_model(model)