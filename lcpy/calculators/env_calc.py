from ..cython_files import calc
from itertools import islice
import numpy as np


class fast_calculator:

    def __init__(self):

        self.impact_per_process = {}
        self.impact = {}
        self.total_impact = {}
        self.total_impact_contributions = {}
        self.total_impact_per_category_and_scenario = {}
        self.total_impact_per_category_and_scenario_fcf = {}

        self.total_fu = {}
        self.total_fu_per_scenario = {}

        self.total_impact_per_fu_per_category_per_scenario = {}
        self.total_impact_per_fu = {}
        self.total_impact_per_fu_per_category_per_scenario_fcf = {}

        self.cum_impact_in_time = {}
        self.cum_impact_in_time_per_fu = {}

        self.cum_fu = {}

        self.total_impact_infr = {}
        self.total_impact_contributions_infr = {}

        self.total_impact_op = {}
        self.total_impact_contributions_op = {}

        self.summed_unit_inventories = {}
        self.summed_unit_characterized_inventories = {}

        self.inventory = {}
        self.inventory_per_process = {}
        self.characterized_inventory = {}
        self.characterized_inventory_per_process = {}

        self.total_inventory = {}
        self.total_inventory_per_process = {}
        self.total_inventory_infr ={}
        self.total_inventory_contributions_infr = {}
        self.total_inventory_op = {}
        self.total_inventory_contributions_op = {}

        self.total_char_inventory = {}
        self.total_char_inventory_per_process = {}
        self.total_char_inventory_infr = {}
        self.total_char_inventory_contributions_infr = {}
        self.total_char_inventory_op = {}
        self.total_char_inventory_contributions_op = {}

        self.total_impact_fcf_per_flow = {}
        self.total_impact_fcf = {}

        self.total_impact_icf_per_flow = {}
        self.total_impact_icf= {}

        self.cum_impact_in_time_fcf ={}
        self.cum_impact_in_time_per_fu_fcf = {}

        self.total_impact_per_fu_fcf = {}




    def calculation_static_lcia(self, mapping, unit_impacts):

        if len(unit_impacts) != len(mapping):
            raise ValueError("Length of unit_impacts does not match length of mapping!")

        for (key_mapping, value_mapping), (key_unit_impact, value_unit_impact) in zip(mapping.items(), unit_impacts.items()):
            # print(key_unit_impact)
            self.impact_per_process[key_unit_impact], self.impact[key_unit_impact] = calc.impact_calculation_static_lcia(value_mapping, value_unit_impact)


    def calculation_impact_senarios(self, total_exchanges, impacts, name):

        if len(impacts) != len(total_exchanges):
            raise ValueError("Length of unit_impacts does not match length of total_exchanges!")

        list_with_impact_flows = list(impacts.values())
        self.total_impact[name], self.total_impact_contributions[name] = calc.impact_calculation_only_scenarios(total_exchanges, list_with_impact_flows)


    def emissions_calculation_in_time(self, mapping, unit_summed_inventories):

        if len(unit_summed_inventories) != len(mapping):
            raise ValueError("Length of unit inventories does not match length of mapping!")

        for (key_mapping, value_mapping), (key_unit_inv, value_unit_inv) in zip(mapping.items(), unit_summed_inventories.items()):
            self.inventory[key_unit_inv], self.inventory_per_process[key_unit_inv] = calc.emissions_calculation_in_time(value_mapping, value_unit_inv)


    def emissions_calculation_simple_lca(self, mapping, unit_summed_inventories):

        if len(unit_summed_inventories) != len(mapping):
            raise ValueError("Length of unit inventories does not match length of mapping!")

        for (key_mapping, value_mapping), (key_unit_inv, value_unit_inv) in zip(mapping.items(), unit_summed_inventories.items()):
            self.inventory[key_unit_inv], self.inventory_per_process[key_unit_inv] = calc.emissions_calculation_simple_lca(value_mapping, value_unit_inv)


    def characterized_inventory_calculation_in_time(self, mapping, unit_summed_char_inventories):

        if len(unit_summed_char_inventories) != len(mapping):
            raise ValueError("Length of unit characterized inventories does not match length of mapping!")

        for (key_mapping, value_mapping), (key_unit_inv, value_unit_inv) in zip(mapping.items(), unit_summed_char_inventories.items()):
            self.characterized_inventory[key_unit_inv], self.characterized_inventory_per_process[key_unit_inv] = calc.characterized_inventory_calculation_in_time(value_mapping, value_unit_inv)


    def characterized_inventory_calculation_simple_lca(self, mapping, unit_summed_char_inventories):

        if len(unit_summed_char_inventories) != len(mapping):
            raise ValueError("Length of unit characterized inventories does not match length of mapping!")

        for (key_mapping, value_mapping), (key_unit_inv, value_unit_inv) in zip(mapping.items(), unit_summed_char_inventories.items()):
            self.characterized_inventory[key_unit_inv], self.characterized_inventory_per_process[key_unit_inv] = (
                calc.characterized_inventory_calculation_simple_lca(value_mapping, value_unit_inv))


    def calculation_dynamic_LCIA_fcf(self, total_inventory, dyn_factors_fcf, category_name = 'GWP'):

        if total_inventory.shape[0] != dyn_factors_fcf.shape[0]:
            raise ValueError("Flows in the inventory does not match the flows in the characterization factors")

        self.total_impact_fcf_per_flow[category_name], self.total_impact_fcf[category_name] = calc.impact_calculation_dynamic_LCIA_fcf(total_inventory, dyn_factors_fcf)


    def calculation_dynamic_LCIA_icf(self, total_inventory, dyn_factors_icf, category_name = 'GWP'):

        total_inventory_expanded_for_dynamic_ia = np.pad(total_inventory, pad_width=(
        (0, 0), (0, 0), (0, dyn_factors_icf.shape[1] - total_inventory.shape[2])), mode='constant',
                                                         constant_values=0)

        self.total_impact_icf_per_flow[category_name], self.total_impact_icf[
            category_name] = calc.impact_calculation_dynamic_LCIA_icf(total_inventory_expanded_for_dynamic_ia, dyn_factors_icf)



    def sum_inventory_per_sub_sub_process(self, dict_with_inventories):

        for key, value in dict_with_inventories.items():

            temp_list = []
            length = len(value)
            # self.summed_unit_inventories[key] = value[0].sum(axis=1).A
            for i in range(length):
                temp_list.append(value[i].sum(axis=1).A)

            self.summed_unit_inventories[key] = temp_list


    def sum_characterized_inventory_per_sub_sub_process(self, dict_with_char_inventories):

        for key, value in dict_with_char_inventories.items():

            num_sps = len(value)
            num_cat = len(value[0])

            char_inventory_activity_all = [[0] * num_cat for _ in range(num_sps)]  # Dimensions (sub_sub_processes, categories)

            # temp_list = []
            # length = len(value[0])

            for i in range(num_sps):
                for j in range(num_cat):
                    char_inventory_activity_all[i][j] = value[i][j].sum(axis=1).A

            self.summed_unit_characterized_inventories[key] = char_inventory_activity_all


    def calculate_total_impact_per_category_and_scenario(self, name):

        x = calc.calculate_total_impact_per_category_and_scenario(self.total_impact[name])
        self.total_impact_per_category_and_scenario[name] = x.T


    def calculate_total_fu_per_scenario(self, total_fu, name):

        self.total_fu_per_scenario[name] = calc.calculate_total_fu_per_scenario(total_fu)
        self.total_fu[name] = total_fu


    def per_fu_per_category_per_scenario(self, name):

        self.total_impact_per_fu_per_category_per_scenario[name] = self.total_impact_per_category_and_scenario[name] / self.total_fu_per_scenario[name].reshape(-1,1)


    def calculation_of_the_in_time_impact_evolution_absolute(self, name):

        self.cum_impact_in_time[name] = calc.calculation_of_the_in_time_impact_evolution_absolute(self.total_impact[name])


    def cum_calculation_of_the_in_time_impact_evolution_per_fu_actual(self, number_con_years, name):

        self.cum_impact_in_time_per_fu = {}
        self.cum_fu = {}

        self.cum_impact_in_time_per_fu[name], self.cum_fu[name] = \
            calc.cum_calculation_of_the_in_time_impact_evolution_per_fu(self.total_impact[name], self.total_fu[name], number_con_years)


    def calculate_total_impact_per_category_and_scenario_fcf(self, category):

        temp = np.expand_dims(self.total_impact_fcf[category], axis=0)

        x = calc.calculate_total_impact_per_category_and_scenario(temp)
        self.total_impact_per_category_and_scenario_fcf[category] = x.T


    def per_fu_per_category_per_scenario_fcf(self, category, name):

        self.total_impact_per_fu_per_category_per_scenario_fcf[category] = (
                    self.total_impact_per_category_and_scenario_fcf[category] /
                    self.total_fu_per_scenario[name].reshape(-1, 1))


    def calculation_of_the_in_time_impact_evolution_absolute_fcf(self, category):

        temp = np.expand_dims(self.total_impact_fcf[category], axis=0)
        self.cum_impact_in_time_fcf[category] = calc.calculation_of_the_in_time_impact_evolution_absolute(temp)


    def cum_calculation_of_the_in_time_impact_evolution_per_fu_actual_fcf(self, category, number_con_years, name):

        self.cum_impact_in_time_per_fu_fcf = {}
        temp = {}
        temp_array = np.expand_dims(self.total_impact_fcf[category], axis=0)

        self.cum_impact_in_time_per_fu_fcf[category], temp[name] = \
            calc.cum_calculation_of_the_in_time_impact_evolution_per_fu(temp_array, self.total_fu[name],
                                                                        number_con_years)

    def total_impact_per_fu(self):
        try:
            self.total_impact_per_fu['Total'] = self.total_impact['Total']/self.total_fu['Total']
        except:
            self.total_impact_per_fu['Total'] = self.total_impact['Total'] / self.total_fu['Total'][0]


    def total_impact_per_fu_fcf(self):
        try:
            self.total_impact_per_fu_fcf['Total'] = self.total_impact_fcf['Total']/self.total_fu['Total']
        except:
            self.total_impact_per_fu_fcf['Total'] = self.total_impact_fcf['Total'] / self.total_fu['Total'][0]


    def cum_calculation_of_the_in_time_impact_evolution_per_fu(self):

        self.cum_impact_in_time_per_fu['Total'], self.cum_fu['Total'] = \
            calc.cum_calculation_of_the_in_time_impact_evolution_per_fu_no_construction(self.total_impact['Total'], self.total_fu['Total'])

        self.cum_fu['Total'] = self.cum_fu['Total'].T


    def impact_calculation_total(self, total_exchanges, impacts, number_con_proc, number_con_years, name):
        if len(impacts) != len(total_exchanges):
            raise ValueError("Length of impacts does not match length of total_exchanges!")

        if (number_con_proc != 0 and number_con_years == 0) or (number_con_proc == 0 and number_con_years != 0):
            raise ValueError("Number of construction years is 0 but number of construction processes is not 0 or"
                             "Number of construction years is not 0 but number of construction processes is 0")

        self.total_impact = {}
        self.total_impact_contributions = {}

        temp_dict_infr = dict(islice(impacts.items(), number_con_proc))
        list_with_infrastructure_impact_flows = list(temp_dict_infr.values())

        temp_dict = dict(list(impacts.items())[number_con_proc:])
        list_with_impact_flows = list(temp_dict.values())

        self.total_impact[name], self.total_impact_contributions[name],\
            self.total_impact_infr[name], self.total_impact_contributions_infr[name],\
            self.total_impact_op[name], self.total_impact_contributions_op[name] = calc.impact_calculation_total_test2_no_contrs_ability(
            total_exchanges, list_with_impact_flows, list_with_infrastructure_impact_flows, number_con_years)


    def emissions_calculation_in_time_total(self, total_exchanges, inventories, number_con_proc, number_con_years, name):

        if len(inventories) != len(total_exchanges):
            raise ValueError("Length of impacts does not match length of total_exchanges!")

        temp_dict_infr = dict(islice(inventories.items(), number_con_proc))
        list_with_infrastructure_inventories = list(temp_dict_infr.values())

        temp_dict = dict(list(inventories.items())[number_con_proc:])
        list_with_inventories = list(temp_dict.values())

        self.total_inventory[name], self.total_inventory_per_process[name],\
        self.total_inventory_infr[name], self.total_inventory_contributions_infr[name],\
        self.total_inventory_op[name], self.total_inventory_contributions_op[name] = calc.emissions_calculation_in_time_total_test2(
            total_exchanges, list_with_inventories, list_with_infrastructure_inventories, number_con_years
        )


    def emissions_calculation_total_simple_lca(self, total_exchanges, inventories, name):

        if len(inventories) != len(total_exchanges):
            raise ValueError("Length of impacts does not match length of total_exchanges!")

        temp_dict = dict(list(inventories.items()))
        list_with_inventories = list(temp_dict.values())

        self.total_inventory[name], self.total_inventory_per_process[name] = calc.emissions_calculation_total_simple_lca(
            total_exchanges, list_with_inventories)


    def characterized_inventory_calculation_total_simple_lca(self, total_exchanges, characterized_inventories, name):

        if len(characterized_inventories) != len(total_exchanges):
            raise ValueError("Length of impacts does not match length of total_exchanges!")

        temp_dict = dict(list(characterized_inventories.items()))
        list_with_char_inventories = list(temp_dict.values())

        self.total_char_inventory[name], self.total_char_inventory_per_process[name] = calc.characterized_inventory_calculation_total_simple_lca(
            total_exchanges, list_with_char_inventories)




    def characterized_inventory_calculation_in_time_total(self, total_exchanges, characterized_inventories,
                                                                number_con_proc, number_con_years, name):

        if len(characterized_inventories) != len(total_exchanges):
            raise ValueError("Length of impacts does not match length of total_exchanges!")

        temp_dict_infr = dict(islice(characterized_inventories.items(), number_con_proc))
        list_with_infrastructure_inventories = list(temp_dict_infr.values())

        temp_dict = dict(list(characterized_inventories.items())[number_con_proc:])
        list_with_inventories = list(temp_dict.values())

        self.total_char_inventory[name], self.total_char_inventory_per_process[name],\
        self.total_char_inventory_infr[name], self.total_char_inventory_contributions_infr[name],\
        self.total_char_inventory_op[name], self.total_char_inventory_contributions_op[name] = calc.characterized_inventory_calculation_in_time_total_test2(
            total_exchanges, list_with_inventories, list_with_infrastructure_inventories, number_con_years
        )



    def get_impact(self, label):
        """Return the no_keys list."""
        return self.impact.get(label)


    def get_impact_per_process(self, label):
        """Return the no_keys list."""
        return self.impact_per_process.get(label)


    def get_total_impact_contribution(self, label):
        """Return the no_keys list."""
        return self.total_impact.get(label)


    def get_total_impact(self, label):
        """Return the no_keys list."""
        return self.total_impact_contributions.get(label)



