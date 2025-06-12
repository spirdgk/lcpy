import sys
import importlib
import numpy as np
from collections import defaultdict
# from parameters import bw_project, bw_database, bw_biosphere, bw_ecoinvent


sys.path.insert(0, "C:\\Users\\sgkousis\\Desktop\\bright\\.venv\\Lib\\site-packages")

bd = importlib.import_module('bw2data')
bc = importlib.import_module('bw2calc')
bi = importlib.import_module('bw2io')
ba = importlib.import_module('bw2analyzer')
bp = importlib.import_module('bw2parameters')
np_comp_version = importlib.import_module('numpy')

bd.projects.set_current(bw_project)
db_calc = bd.Database(bw_database)
my_bio = bd.Database(bw_biosphere)
my_ei = bd.Database(bw_ecoinvent)


def top_processes(activities, char_inventory):
    processes = defaultdict(list)

    for process in my_ei:
        if process.key in activities:
            processes[process].append(
                char_inventory[:, activities[process.key]].sum()
            )

    return sorted(
        [(sum(scores), name) for name, scores in processes.items()], reverse=True
    )


def contribution_analysis_in_technosphere(mat_keys, methods_gp):
    ia_methods = methods_gp

    if len(mat_keys) > 0:

        activities = []
        key_places = []
        characterization_matrixes = []

        for index, key in enumerate(mat_keys):
            try:
                activities.append(db_calc.get(key))
                key_places.append(index)
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
                    result[index1][index2] = top_processes(my_lca.activity_dict, char_inv)

    return result


def top_emissions(bio_dict, char_inventory):
    emissions = defaultdict(list)

    for flow in my_bio:
        if flow.key in bio_dict:
            emissions[flow].append(
                char_inventory[bio_dict[flow.key], :].sum()
            )

    return sorted(
        [ (sum(scores), name) for name, scores in emissions.items()], reverse = True
    )


def contribution_analysis_in_biosphere(mat_keys, methods_gp):
    ia_methods = methods_gp

    if len(mat_keys) > 0:

        activities = []
        key_places = []
        characterization_matrixes = []

        for index, key in enumerate(mat_keys):
            try:
                activities.append(db_calc.get(key))
                key_places.append(index)
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
                    result[index1][index2] = top_emissions(my_lca.biosphere_dict, char_inv)

    return result



class LCAer:

    def __init__(self, methods):

        sys.path.insert(0, "C:\\Users\\sgkousis\\Desktop\\bright\\.venv\\Lib\\site-packages")

        self.methods = methods
        self.unit_impacts = {}


    def impact_calculation(self, name, mat_keys):

        if len(mat_keys) == 0:
            pass
        else:
            # if len(mat_keys) > 1 and len(self.methods) > 1:
            activities = []
            for key in mat_keys:
                try:
                    activities.append(db_calc.get(key))
                except:
                    activities.append('key was not found')

            first_activity = [{act: 1} for act in activities if act != 'key was not found'][0]

            scores = np.zeros((len(activities), len(self.methods)))
            characterization_matrixes = []

            my_lca = bc.LCA(first_activity, self.methods[0])
            my_lca.lci()
            my_lca.lcia()
            for meth in self.methods:
                my_lca.switch_method(meth)
                characterization_matrixes.append(my_lca.characterization_matrix.copy())

            for index1, act in enumerate(activities):

                if act != 'key was not found':
                    my_lca.redo_lci({act: 1})

                    for index2, c_mat in enumerate(characterization_matrixes):
                        char_inv = c_mat * my_lca.inventory
                        scores[index1, index2] = char_inv.sum()

            self.unit_impacts[name] = scores


    def get_unit_impact(self, label):
        """Return the no_keys list."""
        return self.unit_impacts.get(label)

