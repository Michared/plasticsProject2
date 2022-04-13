from visualize import visualize_model, visualize_batch
from mesa.batchrunner import FixedBatchRunner
from model import Festival


# Run (shift + F10)
if __name__ == '__main__':

    manual_run = False # run one scenario, fast
    batch_experiment = True # compare scenarios, more computation

    if manual_run:
        model = Festival()
        for i in range(200):
            model.step()
        visualize_model(model)

    if batch_experiment:
        batch_size = 1
        steps = 200

        # define the base case and variable names that will be varied
        variable_names = ['name', 'drinks_for_cup', 'reluctance_avg', 'awareness', 'stands'] # these vars will be varied
        base_case = ['Base case', 0, 0.5, 0.05, ((2, 5), (8, 7), (12, 12))] # these are the default values
        base_case_dict = dict(zip(variable_names, base_case))

        # define the six variations to the base case
        varied_values = [{'reluctance_avg': 0.2},
                      {'reluctance_avg': 0.8},
                      {'awareness': 0.02},
                      {'awareness': 0.08},
                      {'stands': ((2, 5), ( 8, 7))},
                      {'stands': ((2, 5), (3, 4), (8, 7), (12, 12))}]

        # name the six variations
        scenario_names = ['Variation ' + str(n) for n in range(1, 7)]
        for d, name in zip(varied_values, scenario_names):
            d['name'] = name

        # copy the base case dict six times into the list of dicts that will be used for the batchrunner
        param_set = [base_case_dict.copy() for i in range(6)] # Copying is necessary to make the dicts unique objects

        # insert the varied values into corresponding dicts
        for d, to_insert in zip(param_set, varied_values):
            for key, value in to_insert.items():
                d[key] = value

        # insert the base case
        param_set.insert(0, base_case_dict)

        # execute batch run
        all_scenarios = FixedBatchRunner(Festival, parameters_list=param_set, iterations=batch_size, display_progress=True, max_steps=steps)
        all_scenarios.run_all()
        data = all_scenarios.get_collector_model()
        print(data)

        visualize_batch(data)