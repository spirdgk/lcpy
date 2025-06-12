import numpy as np
from ..cython_files import calc


class FastTeaCalculator:

    def __init__(self, number_of_infrastructure_processes: int,
                 construction_years: int,  scenarios: int ,
                 discount_rate: float):

        self.number_of_infrastructure_processes = number_of_infrastructure_processes
        self.construction_years = construction_years
        self.scenarios = scenarios
        self.discount_rate_simple_value = discount_rate

        self.cost_per_process = {}
        self.cost = {}
        self.revenue = {}
        self.revenue_per_process = {}

        self.non_cum_cost = {}
        self.non_cum_cost_per_process = {}
        self.cum_cost = {}
        self.cum_cost_per_process = {}

        self.non_cum_revenue = {}
        self.non_cum_revenue_per_process = {}
        self.cum_revenue = {}
        self.cum_revenue_per_process = {}

        self.non_cum_cost_infr= {}
        self.non_cum_cost_per_process_infr = {}
        self.cum_cost_infr = {}
        self.cum_cost_per_process_infr = {}

        self.npv = {}
        self.total_costs = {}
        self.operational_costs = {}
        self.total_revenue = {}

        self.lcoe = {}
        self.lcoe_in_time = {}

        self.annualized_capex = {}
        self.annualized_opex = {}
        self.annualized_cost = {}

        self.total_product_costs = {}
        self.tax_cost = {}
        self.loan_cost = {}

        self.msp = {}
        self.msp_in_time = {}


    def cost_calculation(self, mapping, discount_rate, num = -1, infrastructure = False):

        for (key_mapping, value_mapping) in mapping.items():

            self.cost_per_process[key_mapping], self.cost[key_mapping] = calc.cost_calculation_time_series(value_mapping, discount_rate, num, infrastructure)


    def revenue_calculation(self, mapping, discount_rate, num = 1, infrastructure = False):

        for (key_mapping, value_mapping) in mapping.items():

            self.revenue_per_process[key_mapping], self.revenue[key_mapping] = calc.cost_calculation_time_series(value_mapping, discount_rate, num, infrastructure)


    def total_cost_calculation(self, discount_rate, name, num = 1, add_disc = True, excl_sub_processes = []):

        list_with_cost_flows = [value for (key, value) in self.cost.items() if
                                key not in excl_sub_processes][:-self.number_of_infrastructure_processes]
        if add_disc:
            disc_construction = self.construction_years
        else:
            disc_construction = 0

        (self.non_cum_cost[name], self.non_cum_cost_per_process[name],
         self.cum_cost[name], self.cum_cost_per_process[name]) = calc.total_cost_per_time_step(list_with_cost_flows, discount_rate, num, disc_construction)


    def total_revenue_calculation(self, discount_rate, name, num = -1, add_disc = True, excl_sub_processes = []):

        list_with_revenue_flows = [value for (key, value) in self.revenue.items() if
                                key not in excl_sub_processes][:]

        if add_disc:
            disc_construction = self.construction_years
        else:
            disc_construction = 0

        (self.non_cum_revenue[name], self.non_cum_revenue_per_process[name],
         self.cum_revenue[name], self.cum_revenue_per_process[name]) = calc.total_cost_per_time_step(list_with_revenue_flows, discount_rate, num, disc_construction)


    def total_cost_calculation_including_infrastructure(self, discount_rate, name,  excl_sub_processes = []):

        list_with_cost_flows = [value for (key, value) in self.cost.items() if
                                key not in excl_sub_processes][:-self.number_of_infrastructure_processes]

        list_with_infrastructure_cost_flows = [value for (key, value) in self.cost.items() if
                                               key not in excl_sub_processes][
                                              -self.number_of_infrastructure_processes:]

        (self.non_cum_cost_infr[name], self.non_cum_cost_per_process_infr[name], self.cum_cost_infr[name],
         self.cum_cost_per_process_infr[name]) = calc.total_cost_per_time_step_time_infrastructure_included(list_with_cost_flows, list_with_infrastructure_cost_flows, discount_rate)


    def refine_revenue_dicts(self, name,  excl_sub_processes = []):

        columns_to_add = np.zeros((self.scenarios, self.construction_years))

        third_dim =  len([value for (key, value) in self.revenue.items() if
                                   key not in excl_sub_processes][:])

        zeros_to_add = np.zeros((self.scenarios, self.construction_years, third_dim))

        self.non_cum_revenue[name] = np.hstack((columns_to_add, self.non_cum_revenue[name]))
        self.cum_revenue[name] = np.hstack((columns_to_add, self.cum_revenue[name]))

        self.non_cum_revenue_per_process[name] = np.concatenate((zeros_to_add, self.non_cum_revenue_per_process[name]), axis=1)
        self.cum_revenue_per_process[name] = np.concatenate((zeros_to_add, self.cum_revenue_per_process[name]), axis=1)


    def npv_calculation(self, discount_rate, name, excl_sub_processes = []):

        list_with_cost_flows = [value for (key, value) in self.cost.items() if
                                key not in excl_sub_processes][:-self.number_of_infrastructure_processes]

        list_with_infrastructure_cost_flows = [value for (key, value) in self.cost.items() if
                                               key not in excl_sub_processes][
                                              -self.number_of_infrastructure_processes:]

        list_with_revenue_flows = [value for (key, value) in self.revenue.items() if
                                   key not in excl_sub_processes][:]

        (self.npv[name], self.total_costs[name],
         self.operational_costs[name], self.total_revenue[name]) = calc.npv_calculation(list_with_cost_flows, list_with_revenue_flows,
                                                                                        list_with_infrastructure_cost_flows,
                                                                                        self.construction_years, discount_rate)

    def msp_calculation(self, discount_rate, name, quantity, excl_sub_processes = []):

        list_with_cost_flows = [value for (key, value) in self.cost.items() if
                                key not in excl_sub_processes][:-self.number_of_infrastructure_processes]

        list_with_infrastructure_cost_flows = [value for (key, value) in self.cost.items() if
                                               key not in excl_sub_processes][
                                              -self.number_of_infrastructure_processes:]

        list_with_revenue_flows = [value for (key, value) in self.revenue.items() if
                                   key not in excl_sub_processes][:]

        self.msp[name] = calc.msp_calculation(list_with_cost_flows, list_with_revenue_flows,
                                              list_with_infrastructure_cost_flows, self.construction_years,
                                              discount_rate, quantity)

    def sum_sub_process(self, sub_process_list):

        if type(sub_process_list[0]) is list:
            return calc.process_to_sub_process_one_ssp(sub_process_list)
        elif type(sub_process_list[0]) is np.ndarray:
            return calc.process_to_sub_process(sub_process_list)





    def npv_calculation_depreciation(self, discount_rate, name, tax_rate, loan_percentage, loan_years, loan_rate, depreciation_years, excl_sub_processes = []):

        list_with_cost_flows = [value for (key, value) in self.cost.items() if
                                key not in excl_sub_processes][:-self.number_of_infrastructure_processes]

        list_with_infrastructure_cost_flows = [value for (key, value) in self.cost.items() if
                                               key not in excl_sub_processes][
                                              -self.number_of_infrastructure_processes:]

        list_with_revenue_flows = [value for (key, value) in self.revenue.items() if
                                   key not in excl_sub_processes][:]

        (self.npv[name], self.total_product_costs[name],
         self.operational_costs[name], self.total_revenue[name],
         self.tax_cost[name], self.loan_cost[name]) = calc.npv_calculation_depreciation(list_with_cost_flows, list_with_revenue_flows,
                                                                                        list_with_infrastructure_cost_flows, self.construction_years,
                                                                                        discount_rate, tax_rate,
                                                                                        loan_percentage, loan_years, loan_rate, depreciation_years)



    def lcoe_calculation(self, quantity, discount_rate, name):

        self.lcoe[name] = calc.lcoe_calculation(quantity, self.total_costs[name], discount_rate, self.construction_years)
        self.lcoe_in_time[name] = calc.lcoe_calculation_in_time(quantity, self.cum_cost_infr[name], discount_rate, self.construction_years)


    def annualized_cost_calculation(self, name, excl_sub_processes = []):

        list_with_cost_flows = [value for (key, value) in self.cost.items() if
                                key not in excl_sub_processes][:-self.number_of_infrastructure_processes]

        list_with_infrastructure_cost_flows = [value for (key, value) in self.cost.items() if
                                               key not in excl_sub_processes][
                                              -self.number_of_infrastructure_processes:]

        list_with_revenue_flows = [value for (key, value) in self.revenue.items() if
                                   key not in excl_sub_processes][:]

        self.annualized_capex[name], self.annualized_opex[name], self.annualized_cost[name] = (
            calc.annualized_cost(list_with_cost_flows, list_with_revenue_flows, list_with_infrastructure_cost_flows,
                                 self.construction_years, self.discount_rate_simple_value))