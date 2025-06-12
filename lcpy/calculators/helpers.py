import pandas as pd
import os
import numpy as np


class ListHolder:

    def __init__(self):
        """Initialize empty lists."""
        self.no_names_dict = {}
        self.no_keys_dict = {}


    def create_lca_lists(self, label, keys_no):
        no_names = []
        no_keys = []

        for name, key in keys_no.items():
            no_names.append(name)
            no_keys.append(key)

        self.no_names_dict[label] = no_names
        self.no_keys_dict[label] = no_keys


    def get_names(self, label):
        """Return the no_names list."""
        return self.no_names_dict.get(label)

    def get_keys(self, label):
        """Return the no_keys list."""
        return self.no_keys_dict.get(label)


class ExchangeHolder:

    def __init__(self, methods_gp):
        self.exchanges_dict = {}
        self.methods_gp = methods_gp


    def create_exchange_arrays(self, mapping_exchanges):

        for name, key in mapping_exchanges.items():
            self.exchanges_dict[name] = np.tile(key, (len(self.methods_gp), 1)).T


    def get_exchanges(self, label):
        """Return the no_keys list."""
        return self.exchanges_dict.get(label)


class ImpactCalculator:

    def __init__(self):
        self.simple_impacts = {}


    def impact_calculation_simple(self, unit_impacts, exchanges):

        if len(unit_impacts) != len(exchanges):
            raise ValueError("Unit Impacts do not have same length as Exchanges")

        for (key_unit_impact, value_unit_impact), (key_exchange, value_exchange) in zip(unit_impacts.items(), exchanges.items()):
            self.simple_impacts[key_unit_impact] = np.multiply(value_unit_impact, value_exchange)

    def get_simple_impact(self, label):
        """Return the no_keys list."""
        return self.simple_impacts.get(label)


class ImpactHandler:

    def __init__(self, names):

        self.names = names
        self.total_impact_arrays = {}
        self.df_impacts ={}
        self.df_contributions = {}
        self.total_unit_impact = {}
        self.contribution_per_sub_sub_process = {}


    def create_dataframes(self, impacts_dict, names_dict):

        if len(impacts_dict) != len(names_dict):
            raise ValueError("Unit Impacts do not have same length as Exchanges")


        for (key_impact, value_impact), (key_name, value_name) in zip(impacts_dict.items(), names_dict.items()):

            temp1 = value_impact.sum(axis=0)
            self.total_impact_arrays[key_impact] = temp1
            temp = np.vstack([value_impact, temp1])

            df_temp = pd.DataFrame(temp, index=value_name + ['Sum'], columns=self.names )
            self.df_impacts[key_impact] = df_temp

            temp_perc = (value_impact / temp1)*100
            df_temp1 = pd.DataFrame(temp_perc, index=value_name, columns=self.names )
            self.df_contributions[key_name] = df_temp1


    def calculate_total_unit_impact(self, my_dict, name):

        self.total_unit_impact[name] = np.vstack(list(my_dict.values()))


    def contribution_to_total_impact_per_sub_sub_processes(self, dict_with_total_impacts, dict_with_contributions, list_with_unique_names, name = '', save = 'True', target_dir = ''):

        temp = 0.0
        temp_dict = {}
        temp_list = []

        for cat in self.names:

            test = dict_with_total_impacts['Total'][cat]

            for act in list_with_unique_names:
                for (item, df) in zip(dict_with_contributions.keys(), dict_with_contributions.values()):

                    if item != 'Total':
                        x = df[cat]
                        try:
                            temp += x[act] / 100 * test[item]
                        except:
                            pass

                temp_dict[act] = temp
                temp = 0.0


            cleaned_data = {k: (0.0 if pd.isna(v) else v) for k, v in temp_dict.items()}
            sorted_items = sorted(cleaned_data.items(), key=lambda x: x[1], reverse=True)
            my_df = pd.DataFrame(sorted_items, columns=["Key", "Value"]).set_index("Key")

            temp_list.append(my_df)
            temp_dict = {}

        self.contribution_per_sub_sub_process = dict(zip(self.names, temp_list))

        if save:
            filepath = os.path.join(target_dir, 'Sub_sub_process_contributions_{name}.xlsx')

            with pd.ExcelWriter(filepath, engine='xlsxwriter') as writer:
                for sheet_name, df in self.contribution_per_sub_sub_process.items():
                    df.to_excel(writer, sheet_name=sheet_name, index=True)


    def get_total_impact_arrays(self, label):
        """Return the no_keys list."""
        return self.total_impact_arrays.get(label)


    def get_df_impacts(self, label):
        """Return the no_keys list."""
        return self.df_impacts.get(label)


    def get_df_contributions(self, label):
        """Return the no_keys list."""
        return self.df_contributions.get(label)

