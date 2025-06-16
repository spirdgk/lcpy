import numpy as np
import sys
import importlib
import multiprocessing
import random
import os
from collections import defaultdict


def worker(args):
    label, keys, methods, config = args

    key_list = list(config.keys())

    path = config[key_list[0]]

    if path not in sys.path:
        sys.path.insert(0, path)

    bd = importlib.import_module('bw2data')
    bc = importlib.import_module('bw2calc')
    bi = importlib.import_module('bw2io')
    ba = importlib.import_module('bw2analyzer')
    bp = importlib.import_module('bw2parameters')

    bd.projects.set_current(config[key_list[1]])

    db_calc = bd.Database(config[key_list[2]])
    my_bio = bd.Database(config[key_list[3]])
    my_ei = bd.Database(config[key_list[4]])

    if len(keys) == 0:
        pass
    else:
        # if len(mat_keys) > 1 and len(self.methods) > 1:
        activities = []
        for key in keys:
            try:
                activities.append(db_calc.get(key))
            except:
                try:
                    activities.append(my_ei.get(key))
                except:
                    activities.append('key was not found')

        first_activity = [{act: 1} for act in activities if act != 'key was not found'][0]

        scores = np.zeros((len(activities), len(methods)))

        characterization_matrixes = []

        my_lca = bc.LCA(first_activity, methods[0])
        my_lca.lci()
        my_lca.lcia()
        for meth in methods:
            my_lca.switch_method(meth)
            characterization_matrixes.append(my_lca.characterization_matrix.copy())

        for index1, act in enumerate(activities):

            if act != 'key was not found':
                my_lca.redo_lci({act: 1})

                for index2, c_mat in enumerate(characterization_matrixes):
                    char_inv = c_mat * my_lca.inventory
                    scores[index1, index2] = char_inv.sum()

    result_array = scores

    return {
        'name': label,
        'result': result_array
    }


def worker_2(args):
    label, keys, methods, config = args

    key_list = list(config.keys())

    path = config[key_list[0]]

    if path not in sys.path:
        sys.path.insert(0, path)

    bd = importlib.import_module('bw2data')
    bc = importlib.import_module('bw2calc')
    bi = importlib.import_module('bw2io')
    ba = importlib.import_module('bw2analyzer')
    bp = importlib.import_module('bw2parameters')

    bd.projects.set_current(config[key_list[1]])

    db_calc = bd.Database(config[key_list[2]])
    my_bio = bd.Database(config[key_list[3]])
    my_ei = bd.Database(config[key_list[4]])

    if len(keys) == 0:
        pass
    else:
        # if len(mat_keys) > 1 and len(self.methods) > 1:
        activities = []
        for key in keys:
            try:
                activities.append(db_calc.get(key))
            except:
                try:
                    activities.append(my_ei.get(key))
                except:
                    activities.append('key was not found')

        first_activity = [{act: 1} for act in activities if act != 'key was not found'][0]

        scores_2 = np.zeros((len(activities), len(methods)))
        characterization_matrixes = []
        inventory_per_activity = [0 for m in range(len(activities))]
        characterized_inventory_per_activity = [[0 for m in range(len(methods))] for _ in
                                                range(len(activities))]
        # biosphere_dic_per_activity = [0 for m in range(len(activities))]
        # activity_dic_per_activity = [0 for m in range(len(activities))]

        my_lca = bc.LCA(first_activity, methods[0])
        my_lca.lci()
        my_lca.lcia()
        for meth in methods:
            my_lca.switch_method(meth)
            characterization_matrixes.append(my_lca.characterization_matrix.copy())

        for index1, act in enumerate(activities):

            if act != 'key was not found':
                my_lca.redo_lci({act: 1})
                inventory_per_activity[index1] = my_lca.inventory

                # reverse_bio = {value: key for key, value in my_lca.biosphere_dict.items()}
                # reverse_techno = {value: key for key, value in my_lca.activity_dict.items()}
                #
                # bio_names = {row: my_bio.get(reverse_bio[row][1]) for row in
                #              range(len(reverse_bio))}
                #
                # techno_names = {}
                #
                # for row in range(len(reverse_techno)):
                #     try:
                #         techno_names[row] = my_ei.get(reverse_techno[row][1])
                #     except:
                #         techno_names[row] = db_calc.get(reverse_techno[row][1])
                #
                # biosphere_dic_per_activity[index1] = bio_names
                # activity_dic_per_activity[index1] = techno_names

                for index2, c_mat in enumerate(characterization_matrixes):
                    char_inv = c_mat * my_lca.inventory
                    characterized_inventory_per_activity[index1][index2] = char_inv
                    scores_2[index1, index2] = char_inv.sum()

    return {
        'name': label,
        'result': scores_2,
        'unit_inv': inventory_per_activity,
        'unit_char_inv': characterized_inventory_per_activity
        # 'biosphere': bio_dict_array,
        # 'technosphere': techno_dict_array
    }


class mpLCAer:


    def __init__(self, njobs, methods_gp, configuration: dict):

        self.configuration = configuration
        self.unit_impacts = None
        self.njobs = njobs
        self.methods = methods_gp
        self.unit_inventory = None
        self.unit_char_inventory = None
        self.biosphere_dict = {}
        self.technosphere_dict = {}
        self.bw2modules = {}


    def import_isolated_environment(self):

        keys_config = list(self.configuration.keys())

        path = self.configuration[keys_config[0]]
        if not path or not os.path.isdir(path):
            raise ValueError(f"Invalid Brightway venv path: {path}")

        if path not in sys.path:
            sys.path.insert(0, path)

        try:
            bd = importlib.import_module('bw2data')
            bc = importlib.import_module('bw2calc')
            bi = importlib.import_module('bw2io')
            ba = importlib.import_module('bw2analyzer')
            bp = importlib.import_module('bw2parameters')
            np_comp_version = importlib.import_module('numpy')

            bd.projects.set_current(self.configuration[keys_config[1]])

            self.bw2modules = {
                "bd": bd,
                "bc": bc,
                "bi": bi,
                "ba": ba,
                "bp": bp,
                "np": np_comp_version,
                "db_calc": bd.Database(self.configuration[keys_config[2]]),
                "my_bio": bd.Database(self.configuration[keys_config[3]]),
                "my_ei": bd.Database(self.configuration[keys_config[4]]),
            }

        except ImportError as e:
            raise RuntimeError("Brightway2 modules could not be imported from the provided environment.") from e


    def _ensure_initialized(self):
        if not self.bw2modules:
            raise RuntimeError("Brightway environment not initialized. Call `initialize_bw_environment()` first.")


    def run_parallel_impact_calculations(self, mapping):

        self._ensure_initialized()

        tasks = [(label, keys, self.methods, self.configuration) for label, keys in mapping.items()]

        # Create a Pool of workers.
        with multiprocessing.Pool(processes=self.njobs) as pool:
            results = pool.map(worker, tasks)

        # Reassemble the results into a dictionary.
        self.unit_impacts = {result['name']: result['result'] for result in results}

    def lca_calculations(self, mapping):

        self._ensure_initialized()

        tasks = [(label, keys, self.methods, self.configuration) for label, keys in mapping.items()]

        # Create a Pool of workers.
        with multiprocessing.Pool(processes=self.njobs) as pool:
            results = pool.map(worker_2, tasks)

        # Reassemble the results into a dictionary.
        self.unit_impacts = {result['name']: result['result'] for result in results}
        self.unit_inventory = {result['name']: result['unit_inv'] for result in results}
        self.unit_char_inventory = {result['name']: result['unit_char_inv'] for result in results}

    def derive_technosphere_and_biosphere_dictionaries(self, mapping, name, times = 2):

        self._ensure_initialized()

        db_calc = self.bw2modules["db_calc"]
        my_ei = self.bw2modules["my_ei"]
        my_bio = self.bw2modules["my_bio"]
        bc = self.bw2modules["bc"]
        bd = self.bw2modules["bd"]
        bi = self.bw2modules["bi"]
        ba = self.bw2modules["ba"]
        bp = self.bw2modules["bp"]

        temp_list = []

        for _ in range(times):
            key = random.choice(list(mapping.keys()))
            value = random.choice(mapping[key])
            temp_list.append(value)

        activities = []
        for key in temp_list:
            try:
                activities.append(db_calc.get(key))
            except:
                try:
                    activities.append(my_ei.get(key))
                except:
                    activities.append('key was not found')

        first_activity = [{act: 1} for act in activities if act != 'key was not found'][0]

        biosphere_dic_per_activity = [0 for m in range(len(activities))]
        activity_dic_per_activity = [0 for m in range(len(activities))]

        my_lca = bc.LCA(first_activity, self.methods[0])
        my_lca.lci()

        for index1, act in enumerate(activities):

            if act != 'key was not found':
                my_lca.redo_lci({act: 1})

                reverse_bio = {value: key for key, value in my_lca.biosphere_dict.items()}
                reverse_techno = {value: key for key, value in my_lca.activity_dict.items()}

                bio_names = {row: my_bio.get(reverse_bio[row][1]) for row in
                             range(len(reverse_bio))}

                techno_names = {}

                for row in range(len(reverse_techno)):
                    try:
                        techno_names[row] = my_ei.get(reverse_techno[row][1])
                    except:
                        techno_names[row] = db_calc.get(reverse_techno[row][1])

                biosphere_dic_per_activity[index1] = bio_names
                activity_dic_per_activity[index1] = techno_names

        if all(bio_dict == biosphere_dic_per_activity[0] for bio_dict in biosphere_dic_per_activity ):
            print("All biosphere dictionaries are the same")
            self.biosphere_dict[name] = biosphere_dic_per_activity[0]
        else:
            print("Biosphere dictionaries are different")

        if all(act_dict == activity_dic_per_activity[0] for act_dict in activity_dic_per_activity ):
            print("All technosphere dictionaries are the same")
            self.technosphere_dict[name] = activity_dic_per_activity[0]
        else:
            print("Technosphere dictionaries are different")


    def derive_char_matrixes_for_one_category(self):

        self._ensure_initialized()

        db_calc = self.bw2modules["db_calc"]
        my_ei = self.bw2modules["my_ei"]
        my_bio = self.bw2modules["my_bio"]
        bc = self.bw2modules["bc"]
        bd = self.bw2modules["bd"]
        bi = self.bw2modules["bi"]
        ba = self.bw2modules["ba"]
        bp = self.bw2modules["bp"]

        ia_methods = self.methods

        characterization_matrixes = []
        try:
            random_activity = db_calc.random()
        except:
            random_activity = my_ei.random()

        my_lca = bc.LCA({random_activity: 1}, ia_methods[0])
        my_lca.lci()
        my_lca.lcia()

        for meth in ia_methods:
            my_lca.switch_method(meth)
            characterization_matrixes.append(my_lca.characterization_matrix.copy())

        reverse_bio = {value: key for key, value in my_lca.biosphere_dict.items()}
        bio_names = {row: my_bio.get(reverse_bio[row][1]) for row in
                     range(len(reverse_bio))}

        return characterization_matrixes, bio_names


    def get_unit_impact(self, name):

        return self.unit_impacts.get(name)






    def top_processes(self, activities, char_inventory, my_ei):
        processes = defaultdict(list)

        for process in my_ei:
            if process.key in activities:
                processes[process].append(
                    char_inventory[:, activities[process.key]].sum()
                )

        return sorted(
            [(sum(scores), name) for name, scores in processes.items()], reverse=True
        )


    def contribution_analysis_in_technosphere(self, mat_keys, methods_gp):

        self._ensure_initialized()

        db_calc = self.bw2modules["db_calc"]
        my_ei = self.bw2modules["my_ei"]
        my_bio = self.bw2modules["my_bio"]
        bc = self.bw2modules["bc"]
        bd = self.bw2modules["bd"]
        bi = self.bw2modules["bi"]
        ba = self.bw2modules["ba"]
        bp = self.bw2modules["bp"]

        ia_methods = methods_gp

        if len(mat_keys) > 0:

            activities = []
            key_places = []
            characterization_matrixes = []

            for index, key in enumerate(mat_keys):
                try:
                    activities.append(db_calc.get(key))
                except:
                    try:
                        activities.append(my_ei.get(key))
                    except:
                        activities.append('key was not found')

            result = [[0] * len(ia_methods) for _ in range(len(activities))]

            fu1 = [{act: 1} for act in activities if act != 'key was not found'][0]

            my_lca = bc.LCA(fu1, ia_methods[0])
            my_lca.lci()
            my_lca.lcia()

            for meth in ia_methods:
                my_lca.switch_method(meth)
                characterization_matrixes.append(my_lca.characterization_matrix.copy())

            for index1, act in enumerate(activities):

                if act != 'key was not found':
                    my_lca.redo_lci({act: 1})

                    for index2, c_mat in enumerate(characterization_matrixes):
                        char_inv = c_mat * my_lca.inventory
                        result[index1][index2] = self.top_processes(my_lca.activity_dict, char_inv, my_ei)

        return result


    def top_emissions(self, bio_dict, char_inventory, my_bio):
        emissions = defaultdict(list)

        for flow in my_bio:
            if flow.key in bio_dict:
                emissions[flow].append(
                    char_inventory[bio_dict[flow.key], :].sum()
                )

        return sorted(
            [(sum(scores), name) for name, scores in emissions.items()], reverse=True
        )

    def contribution_analysis_in_biosphere(self, mat_keys, methods_gp):

        self._ensure_initialized()

        db_calc = self.bw2modules["db_calc"]
        my_ei = self.bw2modules["my_ei"]
        my_bio = self.bw2modules["my_bio"]
        bc = self.bw2modules["bc"]
        bd = self.bw2modules["bd"]
        bi = self.bw2modules["bi"]
        ba = self.bw2modules["ba"]
        bp = self.bw2modules["bp"]


        ia_methods = methods_gp

        if len(mat_keys) > 0:

            activities = []
            key_places = []
            characterization_matrixes = []

            for index, key in enumerate(mat_keys):
                try:
                    activities.append(db_calc.get(key))
                except:
                    try:
                        activities.append(my_ei.get(key))
                    except:
                        activities.append('key was not found')

            result = [[0] * len(methods_gp) for _ in range(len(activities))]

            fu1 = [{act: 1} for act in activities if act != 'key was not found'][0]

            my_lca = bc.LCA(fu1, ia_methods[0])
            my_lca.lci()
            my_lca.lcia()

            for meth in ia_methods:
                my_lca.switch_method(meth)
                characterization_matrixes.append(my_lca.characterization_matrix.copy())

            for index1, act in enumerate(activities):

                if act != 'key was not found':
                    my_lca.redo_lci({act: 1})

                    for index2, c_mat in enumerate(characterization_matrixes):
                        char_inv = c_mat * my_lca.inventory
                        result[index1][index2] = self.top_emissions(my_lca.biosphere_dict, char_inv, my_bio)

        return result






























# if __name__ == '__main__':
#     # Example mapping dictionary:
#     mapping = {
#         'no1': [
#             'de2bf523eb05925877c4a15a45a1563b_copy1',
#             'a7d3ee7569364474b95f7965300e5cdc_copy1',
#             '9c1e9d5ae9fc4746190b32d9805a9ceb_copy1',
#             '5886a5286ffe63c7a8625c793c054db3_copy1',
#             '8d3cf8074ca097a7e2d9d9aed8cad13a_copy1',
#             '7e997067d3ffeee07c338a11b8ca995b_copy1',
#             '5bfa39eda2a710103c8b0797d6285143_copy1'
#         ],
#         'no2': [
#             '7e997067d3ffeee07c338a11b8ca995b_copy1',
#             'aa9ae2198d3e4817ae26b8f05be79c4f'
#         ]
#     }
#
#     # Create a Calculator instance with the desired number of jobs.
#     calc = mpLCAer(njobs=2)
#     results_dict = calc.run_parallel_impact_calculations(mapping)
#
#     # Print the results for each label.
#     for label, result_array in results_dict.items():
#         print(f"Label: {label}")
#         print("Result Array:")
#         print(result_array)
#         print()
