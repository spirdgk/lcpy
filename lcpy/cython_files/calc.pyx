import numpy as np # katevazoume nunmpy
cimport numpy as cnp # katevazoume c-level API to numpy pou afinei na kanoume define types np.arrays

def impact_calculation_static_lcia(list exchange_amounts, cnp.ndarray[cnp.float64_t, ndim=2] unit_impacts):

    cdef int num_processes = len(exchange_amounts) # Processes gia ypologismo (sub-sub-processes stin sub-process) i unit_impacts.shape[0]
    cdef int scenarios = exchange_amounts[0].shape[0] # Scenaria
    cdef int time_steps = exchange_amounts[0].shape[1] # time steps
    cdef int num_impacts = unit_impacts.shape[1] # impact categories


    cdef cnp.ndarray[cnp.float64_t, ndim=4] result_groups = np.zeros((num_processes, num_impacts, scenarios, time_steps), dtype = np.float64)

    cdef cnp.ndarray[cnp.float64_t, ndim=3] final_result = np.zeros((num_impacts, scenarios, time_steps), dtype = np.float64)


    cdef int k, i, j, t

    cdef cnp.ndarray[cnp.float64_t, ndim=2] amount_array
    cdef cnp.float64_t temp

    for k in range(num_processes): # gia kathe sub-sub-process sto sub-process
        amount_array = exchange_amounts[k] #Travaw ton np.array me ta amounts of exchanges gia kathe scenario kai se kathe time-step

        for i in range(num_impacts): # gia kathe impact category
            temp = unit_impacts[k, i]
            for j in range(scenarios): # gia kathe scenario
                for t in range(time_steps): # kai se kathe time-step
                    result_groups[k,i,j,t] = temp * amount_array[j,t] #pollaplasiazoume to unit_impact gia tin katigoria me to exchange amount se kathe time-step kai scenario

    #twra pame na summaroume ana process
    for k in range(num_processes):
        for i in range(num_impacts):
                for j in range(scenarios):
                    for t in range(time_steps):
                        final_result[i,j,t] += result_groups[k,i,j,t]


    return result_groups, final_result


def impact_calculation_only_scenarios(list exchange_amounts, list unit_impacts):
    cdef int num_p = len(unit_impacts)  # number of operational sub-processes
    cdef int scenarios = unit_impacts[0].shape[1]  #senaria
    cdef int time_steps = unit_impacts[0].shape[2]  # xronia
    cdef int categories = unit_impacts[0].shape[0]  # impact categories

    cdef cnp.ndarray[cnp.float64_t, ndim=3] sum_array = np.zeros((categories, scenarios, time_steps), dtype=np.float64)
    cdef cnp.ndarray[cnp.float64_t, ndim=4] contributions_array = np.zeros(
        (num_p, categories, scenarios, time_steps), dtype=np.float64)

    cdef int n, c, s, t
    cdef double product
    cdef cnp.ndarray[cnp.float64_t, ndim = 2] exchange_amount
    cdef cnp.ndarray[cnp.float64_t, ndim = 3] unit_impact


    for n in range(num_p):  # gia kathe infrastructural sub-process (e.g., 1-5)
        exchange_amount = exchange_amounts[n]  # travaw ta scales tis infrastructural sub-process. Dim: (scenarios, construction_years)
        unit_impact = unit_impacts[n]  # travaw ta unit impacts ths infrastructural sub-process. Dim (impact categories, scenarios, construction_years)

        for c in range(categories):
            for s in range(scenarios):
                for t in range(time_steps):
                    product = unit_impact[c, s, t] * exchange_amount[s, t]  #ypologizw to impact stin catigoria c pou skaei sto

                    sum_array[c, s, t] += product  # apothikevw to impact se kathe catigoria kai kathe construction_year kai senario

                    contributions_array[n, c, s, t] = product  # apothikevw per infrastructural sub-process


    return sum_array, contributions_array


def impact_calculation_total_test2(list exchange_amounts, list unit_impacts, list unit_impacts_infr, cnp.int con_years):

    cdef int num_p = len(unit_impacts) # number of operational sub-processes
    cdef int scenarios = unit_impacts[0].shape[1] #senaria
    cdef int time_steps = unit_impacts[0].shape[2] # xronia
    cdef int categories = unit_impacts[0].shape[0] # impact categories

    cdef int num_p_infr = len(unit_impacts_infr) # number of infrastructural sub-processes, should be same with construction years

    cdef int total_years = con_years + time_steps
    cdef int total_processes = num_p + num_p_infr

    cdef cnp.ndarray[cnp.float64_t, ndim=3] sum_array = np.zeros((categories, scenarios, total_years), dtype = np.float64)
    cdef cnp.ndarray[cnp.float64_t, ndim=4] contributions_array = np.zeros((total_processes, categories, scenarios, total_years), dtype = np.float64)

    cdef cnp.ndarray[cnp.float64_t, ndim=3] sum_array_infr = np.zeros((categories, scenarios, con_years), dtype=np.float64)
    cdef cnp.ndarray[cnp.float64_t, ndim=4] contributions_array_infr = np.zeros((num_p_infr, categories, scenarios, con_years), dtype=np.float64)

    cdef cnp.ndarray[cnp.float64_t, ndim=3] sum_array_op = np.zeros((categories, scenarios, time_steps), dtype=np.float64)
    cdef cnp.ndarray[cnp.float64_t, ndim=4] contributions_array_op = np.zeros((num_p, categories, scenarios, time_steps), dtype=np.float64)

    cdef int n, c, s, t
    cdef double product
    cdef cnp.ndarray[cnp.float64_t, ndim = 2] exchange_amount
    cdef cnp.ndarray[cnp.float64_t, ndim = 3] unit_impact


    for n in range(num_p_infr): 
        exchange_amount = exchange_amounts[n]
        unit_impact = unit_impacts_infr[n] 

        for c in range(categories):
            for s in range(scenarios):
                for t in range(con_years):
                    product = unit_impact[c, s, t] * exchange_amount[s, t]
  
                    sum_array[c, s, t] += product 
  
                    contributions_array[n, c, s, t] = product
                    #kane to idio kai gia tous infrastructure specific pinakes
                    sum_array_infr[c, s, t] += product
                    contributions_array_infr[n, c, s, t] = product

    # sinexizoume gia tis operational sub-processes num_p me tin idia logiki opws panw
    for n in range(num_p_infr, total_processes):
        exchange_amount = exchange_amounts[n]
        unit_impact = unit_impacts[n - num_p_infr]

        for c in range(categories):
            for s in range(scenarios):
                for t in range(con_years, total_years):

                    product = unit_impact[c,s,t - con_years] * exchange_amount[s,t - con_years]
                    sum_array[c,s,t] += product
                    contributions_array[n,c,s,t] = product
                    sum_array_op[c, s, t - con_years] += product
                    contributions_array_op[n - num_p_infr, c, s, t - con_years] = product

    return sum_array, contributions_array, sum_array_infr, contributions_array_infr, sum_array_op, contributions_array_op


def calculate_total_impact_per_category_and_scenario(cnp.ndarray[cnp.float64_t, ndim=3] total_impacts):

    cdef int num_cat = total_impacts.shape[0] # categories
    cdef int num_scen = total_impacts.shape[1] # senaria
    cdef int num_time = total_impacts.shape[2] # time_steps

    cdef cnp.ndarray[cnp.float64_t, ndim=2] result_groups = np.zeros((num_cat, num_scen), dtype=np.float64)

    cdef int i, j, k

    cdef cnp.float64_t temp = 0.0

    for k in range(num_cat):
        for j in range(num_scen):
            temp = 0.0
            for i in range(num_time):
                temp += total_impacts[k,j,i]

            result_groups[k,j] = temp

    return result_groups


def calculate_total_fu_per_scenario(list total_fu):

    cdef int num_scen = total_fu[0].shape[0] # senaria
    cdef int num_time = total_fu[0].shape[1] # time_steps

    cdef cnp.ndarray[cnp.float64_t, ndim=1] result_groups = np.zeros(( num_scen), dtype=np.float64)

    cdef int i, j, k

    cdef cnp.float64_t temp = 0.0

    cdef cnp.ndarray[cnp.float64_t, ndim=2] fus

    fus = total_fu[0]

    for j in range(num_scen):
        temp = 0.0
        for i in range(num_time):
            temp += fus[j,i]
        result_groups[j] = temp

    return result_groups


def cost_calculation_time_series(list exchange_costs, cnp.ndarray[cnp.float64_t, ndim=1] discount_rates, cnp.float64_t sign, infrastructure = False):

    cdef int num_processes = len(exchange_costs) # Processes gia ypologismo
    cdef int scenarios = exchange_costs[0].shape[0] # Scenaria
    cdef int time_steps = exchange_costs[0].shape[1] # time steps


    cdef cnp.ndarray[cnp.float64_t, ndim=3] result_groups = np.zeros((num_processes, scenarios, time_steps), dtype = np.float64)

    cdef cnp.ndarray[cnp.float64_t, ndim=2] final_result = np.zeros((scenarios, time_steps), dtype = np.float64)


    cdef int k, i, j, t

    cdef cnp.ndarray[cnp.float64_t, ndim=2] amount_array

    if infrastructure:
        for k in range(num_processes):  # gia kathe process

            amount_array = exchange_costs[k]  #Travaw ton np.array me ta amounts of exchanges tou sub-sub-process gia kathe scenario kai se kathe time-step

            for j in range(scenarios):  # gia kathe scenario
                for t in range(time_steps):  # kai se kathe time-step
                    result_groups[k, j, t] = amount_array[j, t] * sign
    else:
        for k in range(num_processes): # gia kathe process

            amount_array = exchange_costs[k] #Travaw ton np.array me ta amounts of exchanges tou sub-sub-process gia kathe scenario kai se kathe time-step

            for j in range(scenarios): # gia kathe scenario
                for t in range(time_steps): # kai se kathe time-step
                    result_groups[k,j,t] = discount_rates[t] * amount_array[j,t] * sign #pollaplasiazoume to cost gia tin katigoria me to exchange amount


    #twra pame na summaroume ana process
    for j in range(scenarios):
        for t in range(time_steps):
            for k in range(num_processes):
                final_result[j, t] += result_groups[k, j, t] #vazeis k, j ,t tis loopes etsi wste na diavazesi mnimi sinexomena

    return result_groups, final_result


def npv_calculation(list processes_costs, list processes_revenues, list infrastructure_cost, cnp.int con_years, cnp.ndarray[cnp.float64_t, ndim = 1] discount_rates):

    cdef int num_processes = len(processes_costs)  # Operational processes kostous
    cdef int scenarios = processes_costs[0].shape[0]  # Scenaria
    cdef int time_steps = processes_costs[0].shape[1]  # time steps
    cdef int num_rev_processes = len(processes_revenues) # Operational processes revenues

    cdef int num_con_years = infrastructure_cost[0].shape[1] # xronia kataskevis
    cdef int num_processes_infr = len(infrastructure_cost) # processes kataskavis


    cdef cnp.ndarray[cnp.float64_t, ndim = 1] operational_costs = np.zeros((scenarios), dtype = np.float64)
    cdef cnp.ndarray[cnp.float64_t, ndim = 1] infr_costs = np.zeros((scenarios), dtype=np.float64)
    cdef cnp.ndarray[cnp.float64_t, ndim = 1] total_costs = np.zeros((scenarios), dtype=np.float64)
    cdef cnp.ndarray[cnp.float64_t, ndim = 1] total_revenue = np.zeros((scenarios), dtype=np.float64)
    cdef cnp.ndarray[cnp.float64_t, ndim = 1] npv = np.zeros((scenarios), dtype=np.float64)


    cdef cnp.ndarray[cnp.float64_t, ndim=2] cost_amount_array
    cdef cnp.ndarray[cnp.float64_t, ndim=2] infr_cost_amount_array
    cdef cnp.ndarray[cnp.float64_t, ndim=2] rev_amount_array
    cdef int k, i, j, t
    cdef cnp.float64_t rate = discount_rates[con_years]
    cdef cnp.float64_t temp

    for k in range(num_processes):
        cost_amount_array = processes_costs[k]

        for j in range(scenarios):
            for i in range(time_steps):
                operational_costs[j] += cost_amount_array[j,i] * rate

    for k in range(num_processes_infr):
        infr_cost_amount_array = infrastructure_cost[k]

        for j in range(scenarios):
            for i in range(num_con_years):
                infr_costs[j] += infr_cost_amount_array[j,i] * discount_rates[i]

    for t in range(num_rev_processes):
        rev_amount_array = processes_revenues[t]

        for j in range(scenarios):
            for i in range(time_steps):
                total_revenue[j] += rev_amount_array[j,i] * rate

    for j in range(scenarios):
        total_costs[j] = operational_costs[j] + infr_costs[j]
        npv[j] = total_revenue[j] + total_costs[j]

    return npv, total_costs, operational_costs, total_revenue


def total_cost_per_time_step(list cost_list, cnp.ndarray[cnp.float64_t, ndim=1] discount_rates, cnp.float64_t sign, cnp.int add_disc):

    cdef int num_processes = len(cost_list)
    cdef int scenarios = cost_list[0].shape[0]
    cdef int time_steps = cost_list[0].shape[1]


    cdef cnp.ndarray[cnp.float64_t, ndim=2] non_cumulative_sum = np.zeros((scenarios, time_steps), dtype=np.float64)
    cdef cnp.ndarray[cnp.float64_t, ndim=3] non_cumulative_sum_per_process = np.zeros((scenarios, time_steps, num_processes), dtype=np.float64)
    cdef cnp.ndarray[cnp.float64_t, ndim=2] cumulative_sum = np.zeros((scenarios, time_steps), dtype=np.float64)
    cdef cnp.ndarray[cnp.float64_t, ndim=3] cumulative_sum_per_process = np.zeros((scenarios, time_steps, num_processes), dtype=np.float64)

    cdef int i, j, k
    cdef cnp.ndarray[cnp.float64_t, ndim=2] no_k_cost
    cdef cnp.float64_t cost_value
    cdef cnp.float64_t cost_to_add
    cdef cnp.float64_t rate = discount_rates[add_disc]

    if add_disc == 0:

        for k in range(num_processes):
            no_k_cost = cost_list[k]
            for i in range(scenarios):
                for j in range(time_steps):
                    cost_value = no_k_cost[i, j]
                    cost_to_add = - cost_value * sign
                    non_cumulative_sum[i, j] += cost_to_add
                    non_cumulative_sum_per_process[i, j, k] = cost_to_add
    else:

        for k in range(num_processes):
            no_k_cost = cost_list[k]
            for i in range(scenarios):
                for j in range(time_steps):
                    cost_value = no_k_cost[i, j]
                    cost_to_add = - cost_value * sign * rate
                    non_cumulative_sum[i, j] += cost_to_add
                    non_cumulative_sum_per_process[i, j, k] = cost_to_add


    for i in range(scenarios):
        cumulative_sum[i,0] = non_cumulative_sum[i,0]
        for j in range(1,time_steps):
            cumulative_sum[i, j] = cumulative_sum[i, j - 1] + non_cumulative_sum[i, j]


    for k in range(num_processes):
        for i in range(scenarios):
            cumulative_sum_per_process[i, 0, k] = non_cumulative_sum_per_process[i, 0, k]
            for j in range(1, time_steps):
                cumulative_sum_per_process[i, j, k] = cumulative_sum_per_process[i, j - 1, k] + non_cumulative_sum_per_process[i, j, k]

    return non_cumulative_sum, non_cumulative_sum_per_process, cumulative_sum, cumulative_sum_per_process


def total_cost_per_time_step_time_infrastructure_included(list cost_list, list infr_cost_list, cnp.ndarray[cnp.float64_t, ndim=1] discount_rates):

    cdef int num_processes = len(cost_list)
    cdef int scenarios = cost_list[0].shape[0]
    cdef int time_steps = cost_list[0].shape[1]


    cdef int num_con_processes = len(infr_cost_list)
    cdef int num_con_years = infr_cost_list[0].shape[1]


    cdef int total_years = num_con_years + time_steps
    cdef int total_processes = num_processes + num_con_processes


    cdef cnp.ndarray[cnp.float64_t, ndim=2] non_cumulative_sum = np.zeros((scenarios, total_years), dtype=np.float64)
    cdef cnp.ndarray[cnp.float64_t, ndim=3] non_cumulative_sum_per_process = np.zeros((scenarios, total_years, total_processes),
                                                                                      dtype=np.float64)
    cdef cnp.ndarray[cnp.float64_t, ndim=2] cumulative_sum = np.zeros((scenarios, total_years), dtype=np.float64)
    cdef cnp.ndarray[cnp.float64_t, ndim=3] cumulative_sum_per_process = np.zeros((scenarios, total_years, total_processes),
                                                                                  dtype=np.float64)

    cdef int i, j, k
    cdef cnp.ndarray[cnp.float64_t, ndim=2] no_k_cost
    cdef cnp.ndarray[cnp.float64_t, ndim=2] step0_cost
    cdef cnp.float64_t cost_value


    for k in range(num_con_processes):
        step0_cost = infr_cost_list[k]
        for i in range(scenarios):
            for j in range(num_con_years):
                cost_value = -step0_cost[i,j] * discount_rates[j]
                non_cumulative_sum[i, j] += cost_value
                non_cumulative_sum_per_process[i, j, k] = cost_value


    for k in range(num_processes):
        no_k_cost = cost_list[k]
        for i in range(scenarios):
            for j in range(num_con_years, total_years):
                cost_value = -no_k_cost[i, j - num_con_years] * discount_rates[num_con_years]
                non_cumulative_sum[i, j] += cost_value
                non_cumulative_sum_per_process[i, j, num_con_processes + k] = cost_value


    for i in range(scenarios):
        cumulative_sum[i,0] = non_cumulative_sum[i,0]
        for j in range(1,total_years):
            cumulative_sum[i, j] = cumulative_sum[i, j - 1] + non_cumulative_sum[i, j]


    for k in range(total_processes):
        for i in range(scenarios):
            cumulative_sum_per_process[i, 0, k] = non_cumulative_sum_per_process[i, 0, k]
            for j in range(1, time_steps):
                cumulative_sum_per_process[i, j, k] = cumulative_sum_per_process[i, j - 1, k] + non_cumulative_sum_per_process[i, j, k]


    return non_cumulative_sum, non_cumulative_sum_per_process, cumulative_sum, cumulative_sum_per_process



def lcoe_calculation(list amounts_lists, cnp.ndarray[cnp.float64_t, ndim=1] cumulative_costs, cnp.ndarray[cnp.float64_t, ndim = 1] discount_rate, cnp.int con_years):

    cdef int scenarios = amounts_lists[0].shape[0]
    cdef int time_steps = amounts_lists[0].shape[1]

    # Define output arrays with appropriate shapes and types
    cdef cnp.ndarray[cnp.float64_t, ndim=1] lcoe = np.zeros((scenarios), dtype=np.float64)
    cdef cnp.ndarray[cnp.float64_t, ndim=1] denominator = np.zeros((scenarios), dtype=np.float64)

    cdef int i, j, k
    cdef cnp.ndarray[cnp.float64_t, ndim=2] amounts = amounts_lists[0] #assuming only one product
    cdef cnp.ndarray[cnp.float64_t, ndim=1] cumulative_costs_mv = cumulative_costs
    cdef cnp.float64_t rate = discount_rate[con_years]


    for i in range(scenarios):
        for j in range(time_steps):
            denominator[i] += amounts[i,j]*discount_rate[j]

        denominator[i] *= rate

        lcoe[i] = -cumulative_costs_mv[i]/denominator[i]

    return lcoe



def lcoe_calculation_in_time(list amounts_lists, cnp.ndarray[cnp.float64_t, ndim=2] cumulative_costs, cnp.ndarray[cnp.float64_t, ndim = 1] discount_rate, cnp.int con_years):

    cdef int scenarios = amounts_lists[0].shape[0]
    cdef int time_steps = amounts_lists[0].shape[1]
    cdef int total_years = time_steps + con_years

    # Define output arrays with appropriate shapes and types
    cdef cnp.ndarray[cnp.float64_t, ndim=2] lcoe_in_time = np.zeros((scenarios, total_years), dtype=np.float64)
    cdef cnp.ndarray[cnp.float64_t, ndim=2] denominator = np.zeros((scenarios, total_years), dtype=np.float64)

    cdef int i, j, k
    cdef cnp.ndarray[cnp.float64_t, ndim=2] amounts = amounts_lists[0]
    cdef cnp.ndarray[cnp.float64_t, ndim=2] cumulative_costs_mv = cumulative_costs
    cdef cnp.float64_t rate = discount_rate[con_years]
    cdef cnp.float64_t accumulated_discounted_amount_at_year = 0
    cdef cnp.float64_t discounted_amount_at_year = 0

    for i in range(scenarios):

        accumulated_discounted_amount_at_year = 0

        for j in range(construction_years, total_years):

            discounted_amount_at_year = amounts[i,j - construction_years]*discount_rate_np[j - construction_years]
            accumulated_discounted_amount_at_year += discounted_amount_at_year
            accumulated_discounted_amount_at_year_discounted_at_first_year = accumulated_discounted_amount_at_year*rate
            lcoe_in_time[i,j] = cumulative_costs_mv[i,j]/accumulated_discounted_amount_at_year_discounted_at_first_year

        # denominator[i, con_years] = amounts[i, 0] * rate
        # lcoe_in_time[i, con_years] = cumulative_costs_mv[i, con_years] / denominator[i, con_years]

        # for j in range(con_years, total_years):
        #     denominator[i,j] = (amounts[i,j - con_years]*discount_rate[j - con_years] + denominator[i,j-1])*rate
        #     lcoe_in_time[i,j] = cumulative_costs_mv[i,j]/denominator[i,j]

    return lcoe_in_time


def calculation_of_the_in_time_impact_evolution_absolute(cnp.ndarray[cnp.float64_t, ndim=3] impact):

    cdef int ncat = impact.shape[0]
    cdef int nscen = impact.shape[1]
    cdef int ntime = impact.shape[2]

    cdef cnp.ndarray[cnp.float64_t, ndim=3] cumulative_impact = np.zeros((ncat, nscen, ntime), dtype=np.float64)

    cdef int k, j, i

    for k in range(ncat):
        for j in range(nscen):

            cumulative_impact[k,j,0] = impact[k,j,0]

            for i in range(1, ntime):
                cumulative_impact[k, j, i] =  impact[k,j,i] + cumulative_impact[k, j, i - 1]

    return cumulative_impact


def cum_calculation_of_the_in_time_impact_evolution_per_fu(cnp.ndarray[cnp.float64_t, ndim=3] impact,
                                                           list fuss,
                                                           cnp.int con_years):

    cdef int ncat = impact.shape[0]
    cdef int nscen = impact.shape[1]
    cdef int ntime = impact.shape[2]

    cdef cnp.ndarray[cnp.float64_t, ndim = 2] fu = fuss[0]

    cdef cnp.ndarray[cnp.float64_t, ndim=3] cumulative_impact_per_fu = np.zeros((ncat, nscen, ntime), dtype=np.float64)
    cdef cnp.ndarray[cnp.float64_t, ndim=2] cumulative_fu = np.zeros((nscen, ntime), dtype=np.float64)

    cdef cnp.ndarray[cnp.float64_t, ndim=3] temp_impact = np.zeros((ncat, nscen, ntime), dtype=np.float64)

    cdef int k, j, i

    # return cumulative_impact_per_fu, cumulative_fu


    for k in range(ncat):
        for j in range(nscen):

            cumulative_impact_per_fu[k,j,0] = impact[k,j,0]

            for i in range(1, con_years):
                cumulative_impact_per_fu[k, j, i] =  impact[k,j,i] + cumulative_impact_per_fu[k, j, i - 1]

    for k in range(ncat):
        for j in range(nscen):

            cumulative_fu[j, con_years] = fu[j, 0]
            temp_impact[k,j,con_years] = cumulative_impact_per_fu[k, j, con_years-1] + impact[k, j, con_years]
            cumulative_impact_per_fu[k, j, con_years] = (impact[k, j, con_years] + cumulative_impact_per_fu[k, j, con_years - 1]) / cumulative_fu[j, con_years]

            for i in range(con_years+1, ntime):
                cumulative_fu[j,i] = fu[j,i - con_years] + cumulative_fu[j,i -1]
                temp_impact[k, j, i] = impact[k,j,i] + temp_impact[k,j,i-1]
                cumulative_impact_per_fu[k, j, i] =  temp_impact[k,j,i]/cumulative_fu[j,i]

    return cumulative_impact_per_fu, cumulative_fu


def emissions_calculation_in_time(list exchange_amounts, list emission_amounts):

    cdef int num_processes = len(exchange_amounts) # Processes gia ypologismo (sub-sub-processes stin sub-process) i unit_impacts.shape[0]
    cdef int scenarios = exchange_amounts[0].shape[0] # Scenaria
    cdef int time_steps = exchange_amounts[0].shape[1] # time steps
    cdef int num_flows = emission_amounts[0].shape[0] # flows


    cdef cnp.ndarray[cnp.float64_t, ndim=4] result_groups = np.zeros((num_processes, num_flows, scenarios, time_steps), dtype = np.float64)

    cdef cnp.ndarray[cnp.float64_t, ndim=3] final_result = np.zeros((num_flows, scenarios, time_steps), dtype = np.float64)


    cdef int k, i, j, t

    cdef cnp.ndarray[cnp.float64_t, ndim=2] amount_array
    cdef cnp.ndarray[cnp.float64_t, ndim=2] amount_flows
    cdef cnp.float64_t temp

    for k in range(num_processes): # gia kathe sub-sub-process sto sub-process
        amount_array = exchange_amounts[k] #Travaw ton np.array me ta amounts of exchanges gia kathe scenario kai se kathe time-step
        amount_flows = emission_amounts[k]

        for i in range(num_flows): # gia kathe impact category
            temp = amount_flows[i,0]
            for j in range(scenarios): # gia kathe scenario
                for t in range(time_steps): # kai se kathe time-step
                    result_groups[k,i,j,t] = temp * amount_array[j,t] #pollaplasiazoume to unit_impact gia tin katigoria me to exchange amount se kathe time-step kai scenario


    for k in range(num_processes):
        for i in range(num_flows):
                for j in range(scenarios):
                    for t in range(time_steps):
                        final_result[i,j,t] += result_groups[k,i,j,t]


    return final_result, result_groups


def characterized_inventory_calculation_in_time(list exchange_amounts, list emission_amounts):

    cdef int num_processes = len(exchange_amounts) # Processes gia ypologismo (sub-sub-processes stin sub-process) i len(emission_amounts)
    cdef int scenarios = exchange_amounts[0].shape[0] # Scenaria
    cdef int time_steps = exchange_amounts[0].shape[1] # time steps
    cdef int num_cat = len(emission_amounts[0]) # categories
    cdef int num_flows = emission_amounts[0][0].shape[0]


    cdef cnp.ndarray[cnp.float64_t, ndim=5] result_groups = np.zeros((num_processes, num_cat, num_flows, scenarios, time_steps), dtype = np.float64)

    cdef cnp.ndarray[cnp.float64_t, ndim=4] final_result = np.zeros((num_cat, num_flows, scenarios, time_steps), dtype = np.float64)

    # Ypologismos ana process
    cdef int c, k, i, j, t
    # cdef list unit_list
    cdef cnp.ndarray[cnp.float64_t, ndim=2] amount_array
    cdef cnp.ndarray[cnp.float64_t, ndim=2] amount_flows
    cdef cnp.float64_t temp

    for k in range(num_processes): # gia kathe sub-sub-process sto sub-process
        for c in range(num_cat):

            amount_array = exchange_amounts[k] #Travaw ton np.array me ta amounts of exchanges gia kathe scenario kai se kathe time-step
            amount_flows = emission_amounts[k][c]

            for i in range(num_flows): # gia kathe impact category
                temp = amount_flows[i,0]
                for j in range(scenarios): # gia kathe scenario
                    for t in range(time_steps): # kai se kathe time-step
                        result_groups[k,c,i,j,t] = temp * amount_array[j,t] #pollaplasiazoume to unit_impact gia tin katigoria me to exchange amount se kathe time-step kai scenario


    for k in range(num_processes):
        for c in range(num_cat):
            for i in range(num_flows):
                    for j in range(scenarios):
                        for t in range(time_steps):
                            final_result[c,i,j,t] += result_groups[k,c,i,j,t]


    return final_result, result_groups


def emissions_calculation_in_time_total_test2(list exchange_amounts, list unit_impacts, list unit_impacts_infr, cnp.int con_years):

    cdef int num_p = len(unit_impacts) # number of operational sub-processes
    cdef int num_p_infr = len(unit_impacts_infr)  # number of infrastructural sub-processes, should be same with construction years
    cdef int flows = unit_impacts[0].shape[0] # impact categories
    cdef int scenarios = unit_impacts[0].shape[1] #senaria
    cdef int time_steps = unit_impacts[0].shape[2] # operational xronia

    cdef int total_years = con_years + time_steps
    cdef int total_processes = num_p + num_p_infr

    cdef cnp.ndarray[cnp.float64_t, ndim=3] sum_array = np.zeros((flows, scenarios, total_years), dtype = np.float64)
    cdef cnp.ndarray[cnp.float64_t, ndim=4] contributions_array = np.zeros((total_processes, flows, scenarios, total_years), dtype = np.float64)

    cdef cnp.ndarray[cnp.float64_t, ndim=3] sum_array_infr = np.zeros((flows, scenarios, con_years), dtype=np.float64)
    cdef cnp.ndarray[cnp.float64_t, ndim=4] contributions_array_infr = np.zeros((num_p_infr, flows, scenarios, con_years), dtype=np.float64)

    cdef cnp.ndarray[cnp.float64_t, ndim=3] sum_array_op = np.zeros((flows, scenarios, time_steps), dtype=np.float64)
    cdef cnp.ndarray[cnp.float64_t, ndim=4] contributions_array_op = np.zeros((num_p, flows, scenarios, time_steps), dtype=np.float64)

    cdef int n, c, s, t
    cdef double product
    cdef cnp.ndarray[cnp.float64_t, ndim = 2] exchange_amount
    cdef cnp.ndarray[cnp.float64_t, ndim = 3] unit_impact


    for n in range(num_p_infr): # gia kathe infrastructural sub-process (e.g., 1-5)
        exchange_amount = exchange_amounts[n] # travaw ta scales tis infrastructural sub-process. Dim: (scenarios, construction_years)
        unit_impact = unit_impacts_infr[n] # travaw ta unit impacts ths infrastructural sub-process. Dim (flows, scenarios, construction_years)

        for c in range(flows):
            for s in range(scenarios):
                for t in range(con_years):
                    product = unit_impact[c, s, t] * exchange_amount[s, t]

                    sum_array[c, s, t] += product 

                    contributions_array[n, c, s, t] = product 

                    sum_array_infr[c, s, t] += product
                    contributions_array_infr[n, c, s, t] = product


    for n in range(num_p_infr, total_processes):
        exchange_amount = exchange_amounts[n]
        unit_impact = unit_impacts[n - num_p_infr]

        for c in range(flows):
            for s in range(scenarios):
                for t in range(con_years, total_years):

                    product = unit_impact[c,s,t - con_years] * exchange_amount[s,t - con_years]
                    sum_array[c,s,t] += product
                    contributions_array[n,c,s,t] = product
                    sum_array_op[c, s, t - con_years] += product
                    contributions_array_op[n - num_p_infr, c, s, t - con_years] = product

    return sum_array, contributions_array, sum_array_infr, contributions_array_infr, sum_array_op, contributions_array_op


def characterized_inventory_calculation_in_time_total_test2(list exchange_amounts, list unit_char_inv,
                                                            list unit_char_inv_infr, cnp.int con_years):

    cdef int num_p = len(unit_char_inv)  # number of operational sub-processes
    cdef int num_p_infr = len(unit_char_inv_infr)  # number of infrastructural sub-processes, should be same with construction years
    cdef int num_cat = unit_char_inv[0].shape[0]  # impact categories
    cdef int flows = unit_char_inv[0].shape[1]  # flows
    cdef int scenarios = unit_char_inv[0].shape[2]  # senarios
    cdef int time_steps = unit_char_inv[0].shape[3]  # operational xronia

    cdef int total_years = con_years + time_steps
    cdef int total_processes = num_p + num_p_infr

    cdef cnp.ndarray[cnp.float64_t, ndim=4] sum_array = np.zeros((num_cat, flows, scenarios, total_years), dtype=np.float64)
    cdef cnp.ndarray[cnp.float64_t, ndim=5] contributions_array = np.zeros((total_processes, num_cat, flows, scenarios, total_years), dtype=np.float64)

    cdef cnp.ndarray[cnp.float64_t, ndim=4] sum_array_infr = np.zeros((num_cat, flows, scenarios, con_years), dtype=np.float64)
    cdef cnp.ndarray[cnp.float64_t, ndim=5] contributions_array_infr = np.zeros((num_p_infr, num_cat, flows, scenarios, con_years), dtype=np.float64)

    cdef cnp.ndarray[cnp.float64_t, ndim=4] sum_array_op = np.zeros((num_cat, flows, scenarios, time_steps), dtype=np.float64)
    cdef cnp.ndarray[cnp.float64_t, ndim=5] contributions_array_op = np.zeros((num_p, num_cat, flows, scenarios, time_steps), dtype=np.float64)

    cdef int n, c, s, t, f
    cdef double product
    cdef cnp.ndarray[cnp.float64_t, ndim = 2] exchange_amount
    cdef cnp.ndarray[cnp.float64_t, ndim = 4] unit_c_inv


    for n in range(num_p_infr):  # gia kathe infrastructural sub-process (e.g., 1-5)

        exchange_amount = exchange_amounts[n]  # travaw ta scales tis infrastructural sub-process. Dim: (scenarios, construction_years)
        unit_c_inv = unit_char_inv_infr[n]  # travaw ta unit impacts ths infrastructural sub-process. Dim (flows, scenarios, construction_years)
        for c in range(num_cat):

            for f in range(flows):
                for s in range(scenarios):
                    for t in range(con_years):
                        product = unit_c_inv[c, f, s, t] * exchange_amount[s, t]  

                        sum_array[c, f, s, t] += product  
     
                        contributions_array[n, c, f, s, t] = product  
 
                        sum_array_infr[c, f, s, t] += product
                        contributions_array_infr[n, c, f, s, t] = product

    for n in range(num_p_infr, total_processes):
        exchange_amount = exchange_amounts[n]
        unit_c_inv = unit_char_inv[n - num_p_infr]

        for c in range(num_cat):

            for f in range(flows):
                for s in range(scenarios):
                    for t in range(con_years, total_years):
                        product = unit_c_inv[c, f, s, t - con_years] * exchange_amount[s, t - con_years]
                        sum_array[c, f, s, t] += product
                        contributions_array[n, c, f, s, t] = product
                        sum_array_op[c, f, s, t - con_years] += product
                        contributions_array_op[n - num_p_infr, c, f, s, t - con_years] = product


    return sum_array, contributions_array, sum_array_infr, contributions_array_infr, sum_array_op, contributions_array_op


def impact_calculation_dynamic_LCIA_fcf(cnp.ndarray[cnp.float64_t, ndim=3] inventory_per_scenario_and_year,
                                        cnp.ndarray[cnp.float64_t, ndim=2] factors):

    cdef int num_flows = inventory_per_scenario_and_year.shape[0] # Or factors.shape[0] # = 2420
    cdef int num_scen = inventory_per_scenario_and_year.shape[1]  # = 2
    cdef int num_years = inventory_per_scenario_and_year.shape[2] # = 11
    cdef int time_horizon = factors.shape[1] # = 100

    cdef int f, s, y, t

    cdef cnp.ndarray[cnp.float64_t, ndim=3] result_per_flow = np.zeros((num_flows, num_scen, num_years), dtype=np.float64)
    cdef cnp.ndarray[cnp.float64_t, ndim=2] result_total = np.zeros((num_scen, num_years), dtype=np.float64)

    # Ta fcf_{f,t} kanoun model poso impact skaei to f apo otan ekpempetai kai gia t years. Aftos o pinakas exei sto column 0 ton prwto CF kai sto column TH-1 to teleftaio
    # Ara ena emission pou ekpempetai to year X prepei na matsaristei me to FCF[f][TH-X-1] to opoio dinei to CF gia osa xronia einai eksw
    # Afto twra isxyei gia ta flows pou exoun dynamic impact assessment methods. Gia ta ypoloipa gia ta opoia den exoume dynamic IA alla static IA
    # o pinakas FCF exei gemistei me ton static CF. Ara gia ena emission pou simvainei sto year X kai pou exei static CF to impact tou ginetai evaluate gia X+TH years.
    # Ara exoume time boundaries incosistency gia afta opws sto semi-dynamic.
    # Afto to impact ginetai allocate sto year X (diafora me to paper mou edw).
    # Gia afta pou exoume dynami IA oi FCF lynoun to time boundaries inconsistency problem
    cdef double product
    for f in range(num_flows):
        for s in range(num_scen):
            for y in range(num_years):
                product = inventory_per_scenario_and_year[f, s, y] * factors[f, time_horizon - y - 1]
                result_per_flow[f, s, y] = product
                result_total[s,y] += product


    return result_per_flow, result_total


# inventory_per_scenario_and_year: (flows, scenarios, total_years)
# factors (flows, time_horizon)
# to impact pou skaei kathe xrono apo to etos pou ginetai emmit to substance. Gia substances me mideniko impact afineis ta factors 0.
# H_{j,τ} = ∑^τ_{t=0}(Gj,t*ICFj,τ− t+1). me τ Ε [0,ΤΗ] kai t E [0,total_years]
# total_impact_ICF_GWP100_per_flow, total_impact_ICF_GWP100 = impact_calculation_dynamic_LCIA_icf(total_inventory, dyn_factors_gwp_100_icf)

def impact_calculation_dynamic_LCIA_icf(cnp.ndarray[cnp.float64_t, ndim=3] inventory_per_scenario_and_year,
                                        cnp.ndarray[cnp.float64_t, ndim=2] factors):
    cdef int num_flows = inventory_per_scenario_and_year.shape[0]  # Or factors.shape[0] = 2420
    cdef int num_scen = inventory_per_scenario_and_year.shape[1] # = 2
    cdef int num_years = inventory_per_scenario_and_year.shape[2] # = 100
    cdef int time_horizon = factors.shape[1] # = 100

    cdef int f, s, y, t

    cdef cnp.ndarray[cnp.float64_t, ndim=3] result_per_flow = np.zeros((num_flows, num_scen, time_horizon), dtype=np.float64)
    cdef cnp.ndarray[cnp.float64_t, ndim=2] result_total = np.zeros((num_scen, time_horizon), dtype=np.float64)

    cdef double product = 0.0
    cdef double intermediate_sum = 0.0

    # To ICF[f,taf] kanei model to impact pou skaei to flow f taf years after its emission. Aftos o pinakas exei sto column 0 to ICF gia to year of emission
    # sto column -1 (e.g., 100) exei to ICF gia TH years after the emission. Note that TH = index[column[-1]] + 1

    # H_{j,τ} = ∑^τ_{t=0}(Gj,t*ICFj,τ− t+1). me τ Ε [0,ΤΗ] kai t E [0,total_years]
    for f in range(num_flows): # gia kathe flow
        for s in range(num_scen): # kai se kathe scenario
            for y in range(time_horizon): # gia kathe etos tou time horizon (0-99), pame na ypologisoume to impact pou skaei afto to etos apo ola ta emisisons pou exoun proklithei
                y_star = y + 1

                if factors[f,-1] == 20598:
                    product = inventory_per_scenario_and_year[f,s,y]*factors[f,0]
                    intermediate_sum += product
                else:
                    # gia kathe year tou time horizon 0, 1, 2, 3, ..., TH
                    # prepei na summaroume to impact pou skane ta emissions pou
                    # ginontai emit afto to etos (y), mazi me to impact pou skane afto to etos (y) ta emissions
                    # pou exoun ekpempfthei ta proigoumena xronia (0:y)
                    # Afto gia ta flows pou exw dynamic CFs
                    # Gia afta pou den exw dynamic CFs kai exw mono static CFs. Exw kanei to eksis ston pinaka me ta ICFS:
                    # Exw valei sto year 0 to static CF, kai sto year TH (index = -1) exw valei 20061996
                    # Opote (opws velpeis panw) an eimaste se tetoia periptwsi tote to impact ginetai evaluate with the static CF, dimiourgontas to time boundaries
                    # inconsistency problem gia afto to flow kai to impact ginetai assigned sto year of emission (diafora me to paper mou edw!)
                    for t in range(y_star):
                        product = inventory_per_scenario_and_year[f,s,t]*factors[f,y-t]
                        intermediate_sum += product

                result_per_flow[f,s,y] = intermediate_sum
                result_total[s,y] += intermediate_sum
                intermediate_sum = 0.0

    return result_per_flow, result_total



def cum_calculation_of_the_in_time_impact_evolution_per_fu_no_construction(cnp.ndarray[cnp.float64_t, ndim=3] impact,
                                                           list fuss):

    cdef int ncat = impact.shape[0]
    cdef int nscen = impact.shape[1]
    cdef int ntime = impact.shape[2]

    cdef cnp.ndarray[cnp.float64_t, ndim = 2] fu = fuss[0]

    cdef cnp.ndarray[cnp.float64_t, ndim=3] cumulative_impact_per_fu = np.zeros((ncat, nscen, ntime), dtype=np.float64)
    cdef cnp.ndarray[cnp.float64_t, ndim=2] cumulative_fu = np.zeros((nscen, ntime), dtype=np.float64)

    cdef cnp.ndarray[cnp.float64_t, ndim=3] temp_impact = np.zeros((ncat, nscen, ntime), dtype=np.float64)

    cdef int k, j, i

    for k in range(ncat):
        for j in range(nscen):

            cumulative_fu[j, 0] = fu[j, 0]
            temp_impact[k, j, 0] = impact[k, j, 0]
            cumulative_impact_per_fu[k, j, 0] = temp_impact[k, j, 0]/fu[j, 0]

            for i in range(1, ntime):
                cumulative_fu[j,i] = fu[j,i] + cumulative_fu[j,i-1]
                temp_impact[k,j,i] = impact[k,j,i] + temp_impact[k,j,i-1]
                cumulative_impact_per_fu[k, j, i] =  temp_impact[k,j,i]/cumulative_fu[j,i]

    return cumulative_impact_per_fu, cumulative_fu


def impact_calculation_total_test2_no_contrs_ability(list exchange_amounts, list unit_impacts, list unit_impacts_infr, cnp.int con_years):

    cdef int num_p = len(unit_impacts) # number of operational sub-processes
    cdef int scenarios = unit_impacts[0].shape[1] #senaria
    cdef int time_steps = unit_impacts[0].shape[2] # xronia
    cdef int categories = unit_impacts[0].shape[0] # impact categories

    cdef int num_p_infr = len(unit_impacts_infr) # number of infrastructural sub-processes, should be same with construction years

    cdef int total_years = con_years + time_steps
    cdef int total_processes = num_p + num_p_infr


    cdef cnp.ndarray[cnp.float64_t, ndim=3] sum_array = np.zeros((categories, scenarios, total_years), dtype = np.float64)
    cdef cnp.ndarray[cnp.float64_t, ndim=4] contributions_array = np.zeros((total_processes, categories, scenarios, total_years), dtype = np.float64)

    cdef cnp.ndarray[cnp.float64_t, ndim=3] sum_array_infr = np.zeros((categories, scenarios, max(con_years,1)), dtype=np.float64)
    cdef cnp.ndarray[cnp.float64_t, ndim=4] contributions_array_infr = np.zeros((max(num_p_infr,1), categories, scenarios, con_years), dtype=np.float64)

    cdef cnp.ndarray[cnp.float64_t, ndim=3] sum_array_op = np.zeros((categories, scenarios, time_steps),  dtype=np.float64)
    cdef cnp.ndarray[cnp.float64_t, ndim=4] contributions_array_op = np.zeros( (num_p, categories, scenarios, time_steps), dtype=np.float64)

    cdef int n, c, s, t
    cdef double product
    cdef cnp.ndarray[cnp.float64_t, ndim = 2] exchange_amount
    cdef cnp.ndarray[cnp.float64_t, ndim = 3] unit_impact

    if con_years != 0  and len(unit_impacts_infr) != 0:

        for n in range(num_p_infr):
            exchange_amount = exchange_amounts[n] 
            unit_impact = unit_impacts_infr[n] 

            for c in range(categories):
                for s in range(scenarios):
                    for t in range(con_years):
                        product = unit_impact[c, s, t] * exchange_amount[s, t] 

                        sum_array[c, s, t] += product

                        contributions_array[n, c, s, t] = product
                        #kane to idio kai gia tous infrastructure specific pinakes
                        sum_array_infr[c, s, t] += product
                        contributions_array_infr[n, c, s, t] = product


        for n in range(num_p_infr, total_processes):
            exchange_amount = exchange_amounts[n]
            unit_impact = unit_impacts[n - num_p_infr]

            for c in range(categories):
                for s in range(scenarios):
                    for t in range(con_years, total_years):

                        product = unit_impact[c,s,t - con_years] * exchange_amount[s,t - con_years]
                        sum_array[c,s,t] += product
                        contributions_array[n,c,s,t] = product
                        sum_array_op[c, s, t - con_years] += product
                        contributions_array_op[n - num_p_infr, c, s, t - con_years] = product
    else:


        for n in range(num_p_infr, total_processes):
            exchange_amount = exchange_amounts[n]
            unit_impact = unit_impacts[n - num_p_infr]

            for c in range(categories):
                for s in range(scenarios):
                    for t in range(con_years, total_years):
                        product = unit_impact[c, s, t - con_years] * exchange_amount[s, t - con_years]
                        sum_array[c, s, t] += product
                        contributions_array[n, c, s, t] = product

    return sum_array, contributions_array, sum_array_infr, contributions_array_infr, sum_array_op, contributions_array_op


def annualized_cost(list processes_costs, list processes_revenues, list infrastructure_cost, cnp.int con_years, cnp.float64_t discount_rate):

    cdef int num_processes = len(processes_costs)  # Operational processes kostous
    cdef int scenarios = processes_costs[0].shape[0]  # Scenaria
    cdef int time_steps = processes_costs[0].shape[1]  # time steps
    cdef int num_rev_processes = len(processes_revenues)  # Operational processes revenues

    cdef int num_con_years = infrastructure_cost[0].shape[1]  # xronia kataskevis
    cdef int num_processes_infr = len(infrastructure_cost)  # processes kataskavis

    # Pinakes me results
    cdef cnp.ndarray[cnp.float64_t, ndim = 1] operational_costs = np.zeros((scenarios), dtype=np.float64)
    cdef cnp.ndarray[cnp.float64_t, ndim = 1] infr_costs = np.zeros((scenarios), dtype=np.float64)
    cdef cnp.ndarray[cnp.float64_t, ndim = 1] total_costs = np.zeros((scenarios), dtype=np.float64)
    cdef cnp.ndarray[cnp.float64_t, ndim = 1] total_revenue = np.zeros((scenarios), dtype=np.float64)
    cdef cnp.ndarray[cnp.float64_t, ndim = 1] npv = np.zeros((scenarios), dtype=np.float64)
    cdef cnp.ndarray[cnp.float64_t, ndim = 1] capex_projected_at_last_construction_year = np.zeros((scenarios), dtype=np.float64)
    cdef cnp.ndarray[cnp.float64_t, ndim = 1] temp_array = np.zeros((scenarios), dtype=np.float64)

    #Intermediate pinakes kai integers
    cdef cnp.ndarray[cnp.float64_t, ndim=2] cost_amount_array
    cdef cnp.ndarray[cnp.float64_t, ndim=2] infr_cost_amount_array
    cdef cnp.ndarray[cnp.float64_t, ndim=2] rev_amount_array
    cdef int k, i, j, t, j2
    cdef cnp.float64_t rate = discount_rate
    cdef cnp.float64_t temp

    # Pinakes me results
    cdef cnp.ndarray[cnp.float64_t, ndim = 2] annualized_capex = np.zeros((scenarios, time_steps), dtype = np.float64)
    cdef cnp.ndarray[cnp.float64_t, ndim = 2] annualized_opex = np.zeros((scenarios, time_steps), dtype = np.float64)
    cdef cnp.ndarray[cnp.float64_t, ndim = 2] annualized_cost = np.zeros((scenarios, time_steps), dtype = np.float64)

    for k in range(num_processes_infr):
        infr_cost_amount_array = infrastructure_cost[k]

        for j in range(scenarios):
            for j2 in range(con_years):
                 temp += infr_cost_amount_array[j, j2] * (1+rate)**(con_years-1-j2)

            capex_projected_at_last_construction_year[j] = temp
            temp = 0.0

            for i in range(time_steps):
                annualized_capex[j, i] += capex_projected_at_last_construction_year[j] * (rate*(1+rate)**(time_steps))/((1+rate)**(time_steps) - 1)


    for k in range(num_processes):
        cost_amount_array = processes_costs[k]
        temp_array = cost_amount_array.sum(axis=1)
        for j in range(scenarios):

            for i in range(time_steps):
                annualized_opex[j, i] += temp_array[j] * (rate*(1+rate)**(time_steps))/((1+rate)**(time_steps) - 1)

    for j in range(scenarios):
        for i in range(time_steps):
            annualized_cost[j,i] = annualized_capex[j,i] + annualized_opex[j,i]


    return annualized_capex, annualized_opex, annualized_cost


def npv_calculation_depreciation(list processes_costs, list processes_revenues,
                    list infrastructure_cost, cnp.int con_years, cnp.ndarray[cnp.float64_t, ndim = 1] discount_rates, cnp.float64_t tax_rate,
                                 cnp.float64_t loan_percentage, cnp.int loan_years, cnp.float64_t loan_rate,
                                 cnp.int depreciation_years):

    cdef int num_processes = len(processes_costs)  # Operational processes kostous
    cdef int scenarios = processes_costs[0].shape[0]  # Scenaria
    cdef int time_steps = processes_costs[0].shape[1]  # time steps
    cdef int num_rev_processes = len(processes_revenues) # Operational processes revenues

    cdef int num_con_years = infrastructure_cost[0].shape[1] # xronia kataskevis
    cdef int num_processes_infr = len(infrastructure_cost) # processes kataskavis

    # Pinakes me results
    cdef cnp.ndarray[cnp.float64_t, ndim = 1] operational_costs = np.zeros((scenarios), dtype = np.float64)
    cdef cnp.ndarray[cnp.float64_t, ndim = 1] infr_costs = np.zeros((scenarios), dtype=np.float64)
    cdef cnp.ndarray[cnp.float64_t, ndim = 1] total_costs = np.zeros((scenarios), dtype=np.float64)
    cdef cnp.ndarray[cnp.float64_t, ndim = 1] total_revenue = np.zeros((scenarios), dtype=np.float64)
    cdef cnp.ndarray[cnp.float64_t, ndim = 1] npv = np.zeros((scenarios), dtype=np.float64)

    cdef cnp.ndarray[cnp.float64_t, ndim = 2] depreciation = np.zeros((scenarios, time_steps), dtype=np.float64)
    cdef cnp.ndarray[cnp.float64_t, ndim = 1] total_depreciation = np.zeros((scenarios), dtype=np.float64)
    cdef cnp.ndarray[cnp.float64_t, ndim = 2] loan_amount = np.zeros((scenarios, con_years), dtype=np.float64)
    cdef cnp.ndarray[cnp.float64_t, ndim = 2] loan_payment = np.zeros((scenarios, time_steps), dtype=np.float64)
    cdef cnp.ndarray[cnp.float64_t, ndim = 2] loan_interest = np.zeros((scenarios, time_steps), dtype=np.float64)
    cdef cnp.ndarray[cnp.float64_t, ndim = 1] loan_total = np.zeros((scenarios), dtype=np.float64)
    cdef cnp.ndarray[cnp.float64_t, ndim = 2] loan_remaining = np.zeros((scenarios, time_steps), dtype=np.float64)
    cdef cnp.ndarray[cnp.float64_t, ndim = 2] loan_principal = np.zeros((scenarios, time_steps), dtype=np.float64)

    cdef cnp.ndarray[cnp.float64_t, ndim = 2] net_revenues = np.zeros((scenarios, time_steps), dtype=np.float64)
    cdef cnp.ndarray[cnp.float64_t, ndim = 2] total_revenue_undisc = np.zeros((scenarios, time_steps), dtype=np.float64)
    cdef cnp.ndarray[cnp.float64_t, ndim = 2] total_operational_cost_undisc = np.zeros((scenarios, time_steps), dtype=np.float64)

    cdef cnp.ndarray[cnp.float64_t, ndim = 2] before_tax = np.zeros((scenarios, time_steps), dtype=np.float64)
    cdef cnp.ndarray[cnp.float64_t, ndim = 2] tax = np.zeros((scenarios, time_steps), dtype=np.float64)

    cdef cnp.ndarray[cnp.float64_t, ndim = 1] tax_disc = np.zeros((scenarios), dtype=np.float64)
    cdef cnp.ndarray[cnp.float64_t, ndim = 1] loan_payment_disc = np.zeros((scenarios), dtype=np.float64)
    cdef cnp.ndarray[cnp.float64_t, ndim = 1] total_product_costs = np.zeros((scenarios), dtype=np.float64)


    #Intermediate pinakes kai integers
    cdef cnp.ndarray[cnp.float64_t, ndim=2] cost_amount_array
    cdef cnp.ndarray[cnp.float64_t, ndim=2] infr_cost_amount_array
    cdef cnp.ndarray[cnp.float64_t, ndim=2] rev_amount_array
    cdef int k, i, j, t
    cdef cnp.float64_t rate = discount_rates[con_years]
    cdef cnp.float64_t temp
    cdef cnp.float64_t temp2
    cdef cnp.float64_t loan_factor


    # Depreciation
    for k in range(num_processes_infr):
        infr_cost_amount_array = infrastructure_cost[k]
        temp2 = 0.0
        for j in range(scenarios):
            for i in range(num_con_years):
                temp2 += infr_cost_amount_array[j,i]

            # Discounted sto prwto operational year
            for dep_year in range(depreciation_years):
                depreciation[j,i] += (temp2/depreciation_years * discount_rates[dep_year]*(-1)) # Thetiko prosimo
            temp2 = 0.0

    temp2 = 0.0
    # Loan
    for k in range(num_processes_infr):
        infr_cost_amount_array = infrastructure_cost[k]
        temp2 = 0.0
        for j in range(scenarios):
            for i in range(num_con_years):
                loan_amount[j,i] += (infr_cost_amount_array[j,i]*loan_percentage *(-1)) # Thetiko prosimo

    temp2 = 0.0
    # Loan payments Discounted sto prwto operational year

    loan_factor = (loan_rate*(1+loan_rate)**loan_years) / ((1+loan_rate)**loan_years - 1)

    for j in range(scenarios):
        for i in range(num_con_years):
            loan_total[j] += loan_amount[j,i]

        for i in range(loan_years):
            loan_payment[j, i] = loan_total[j] * loan_factor

        loan_remaining[j, 0] = loan_total[j]
        loan_interest[j, 0] = loan_remaining[j, 0] * loan_rate
        loan_principal[j,0] = loan_payment[j, 0] - loan_interest[j, 0]

        for i in range(1, loan_years):

            loan_remaining[j, i] = loan_remaining[j, i-1] - loan_principal[j,i-1]
            loan_interest[j,i] = loan_remaining[j, i] * loan_rate
            loan_principal[j,i] = loan_payment[j, i] - loan_interest[j, i]


    for j in range(scenarios):
        for i in range(loan_years):
            loan_payment[j, i] *= -discount_rates[i]
            loan_remaining[j, i] *= -discount_rates[i]
            loan_interest[j, i] *= -discount_rates[i]
            loan_principal[j, i] *= -discount_rates[i]


    # Calculation of taxes, discounted sto prwto operaitonal year

    for t in range(num_rev_processes):
        rev_amount_array = processes_revenues[t]
        for j in range(scenarios):
            for i in range(time_steps):
                total_revenue_undisc[j, i] += rev_amount_array[j,i]

    for k in range(num_processes):
        cost_amount_array = processes_costs[k]

        for j in range(scenarios):
            for i in range(time_steps):
                total_operational_cost_undisc[j,i] += cost_amount_array[j, i]

    for j in range(scenarios):
        for i in range(time_steps):
            before_tax[j,i] = total_revenue_undisc[j, i] + total_operational_cost_undisc[j,i] - depreciation[j,i] + loan_interest[j,i]
            if before_tax[j,i] > 0:
                tax[j,i] = - before_tax[j,i] * tax_rate

    # Calculation of cash flows discounted sto year 0

    # Discounted sto year 0
    for k in range(num_processes):
        cost_amount_array = processes_costs[k]

        for j in range(scenarios):
            for i in range(time_steps):
                operational_costs[j] += cost_amount_array[j,i] * rate

    # Discounted sto year 0
    for t in range(num_rev_processes):
        rev_amount_array = processes_revenues[t]

        for j in range(scenarios):
            for i in range(time_steps):
                total_revenue[j] += rev_amount_array[j, i] * rate

    for j in range(scenarios):
        for i in range(time_steps):
            tax_disc[j] += tax[j, i] * rate
            loan_payment_disc[j] += loan_payment[j, i] * rate

    for k in range(num_processes_infr):
        infr_cost_amount_array = infrastructure_cost[k]

        for j in range(scenarios):
            for i in range(num_con_years):
                infr_costs[j] += infr_cost_amount_array[j,i]

    for j in range(scenarios):
        for i in range(num_con_years):
            infr_costs[j] -= loan_total[j]

    # Discounted sto year 0
    for j in range(scenarios):
        total_product_costs[j] = operational_costs[j] + infr_costs[j]
        npv[j] = total_revenue[j] + total_product_costs[j] + loan_payment_disc[j] + tax_disc[j]

    return npv, total_product_costs, operational_costs, total_revenue, tax_disc, loan_payment_disc


def msp_calculation(list processes_costs, list processes_revenues,
                    list infrastructure_cost, cnp.int con_years, cnp.ndarray[cnp.float64_t, ndim = 1] discount_rates, list amounts_lists):

    cdef int num_processes = len(processes_costs)  # Operational processes kostous
    cdef int scenarios = processes_costs[0].shape[0]  # Scenaria
    cdef int time_steps = processes_costs[0].shape[1]  # time steps
    cdef int num_rev_processes = len(processes_revenues)  # Operational processes revenues

    cdef int num_con_years = infrastructure_cost[0].shape[1]  # xronia kataskevis
    cdef int num_processes_infr = len(infrastructure_cost)  # processes kataskevis

    # Pinakes me results
    cdef cnp.ndarray[cnp.float64_t, ndim = 1] operational_costs = np.zeros((scenarios), dtype=np.float64)
    cdef cnp.ndarray[cnp.float64_t, ndim = 1] infr_costs = np.zeros((scenarios), dtype=np.float64)
    cdef cnp.ndarray[cnp.float64_t, ndim = 1] nominator = np.zeros((scenarios), dtype=np.float64)
    cdef cnp.ndarray[cnp.float64_t, ndim = 1] total_revenue = np.zeros((scenarios), dtype=np.float64)
    cdef cnp.ndarray[cnp.float64_t, ndim=1] msp = np.zeros((scenarios), dtype=np.float64)
    cdef cnp.ndarray[cnp.float64_t, ndim=1] denominator = np.zeros((scenarios), dtype=np.float64)

    #Intermediate pinakes kai integers
    cdef cnp.ndarray[cnp.float64_t, ndim=2] cost_amount_array
    cdef cnp.ndarray[cnp.float64_t, ndim=2] infr_cost_amount_array
    cdef cnp.ndarray[cnp.float64_t, ndim=2] rev_amount_array
    cdef int k, i, j, t
    cdef cnp.float64_t rate = discount_rates[con_years]
    cdef cnp.ndarray[cnp.float64_t, ndim=2] amounts = amounts_lists[0]  #assuming only one product

    for k in range(num_processes):
        cost_amount_array = processes_costs[k]

        for j in range(scenarios):
            for i in range(time_steps):
                operational_costs[j] += cost_amount_array[j, i] * rate

    for k in range(num_processes_infr):
        infr_cost_amount_array = infrastructure_cost[k]

        for j in range(scenarios):
            for i in range(num_con_years):
                infr_costs[j] += infr_cost_amount_array[j, i] * discount_rates[i]

    for t in range(num_rev_processes):
        rev_amount_array = processes_revenues[t]

        for j in range(scenarios):
            for i in range(time_steps):
                total_revenue[j] += rev_amount_array[j, i] * rate

    for i in range(scenarios):
        for j in range(time_steps):
            denominator[i] += amounts[i, j] * discount_rates[j]

        denominator[i] *= rate

    for j in range(scenarios):
        nominator[j] = -operational_costs[j] - infr_costs[j] - total_revenue[j]
        msp[j] = nominator[j]/denominator[j]

    return msp


def process_to_sub_process(list exchanges):

    cdef int num_processes = len(exchanges)  # Operational processes kostous

    cdef int scenarios = exchanges[0].shape[0]  # Scenaria
    cdef int time_steps = exchanges[0].shape[1]  # time steps

    cdef cnp.ndarray[cnp.float64_t, ndim=2] result = np.zeros((scenarios, time_steps), dtype=np.float64)
    cdef cnp.ndarray[cnp.float64_t, ndim=2] current_array

    cdef int k, i, j

    for k in range(num_processes):
        current_array = exchanges[k]
        for i in range(scenarios):
            for j in range(time_steps):
                result[i,j] += current_array[i,j]

    return result


def process_to_sub_process_one_ssp(list list_with_exchanges):

    cdef int num_sub_sub_processes = len(list_with_exchanges)
    cdef int scenarios =  list_with_exchanges[0][0].shape[0]
    cdef int time_steps = list_with_exchanges[0][0].shape[1]

    cdef cnp.ndarray[cnp.float64_t, ndim=2] result = np.zeros((scenarios, time_steps), dtype=np.float64)
    cdef cnp.ndarray[cnp.float64_t, ndim=2] temp_array
    cdef cnp.ndarray[cnp.float64_t, ndim=2] current_array

    cdef int i, j, k, l
    cdef int len_temp_list

    for k in range(num_sub_sub_processes):

        temp_list = list_with_exchanges[k]
        temp_array = np.zeros((scenarios, time_steps), dtype=np.float64) #ksanathetoume 0 ton temp_array se kathe loopa
        len_temp_list = len(temp_list)

        for l in range(len_temp_list): # Afto stin ousia einai i loupa stin panw function kai gia kathe sub_sub_process dimiourgeis ton temp_array
                                       # (stin proigoumeni functions afto itan to result pou ekanes return)

            current_array = temp_list[l]
            for i in range(scenarios):
                for j in range(time_steps):
                    temp_array[i, j] += current_array[i, j]

            # kai twra pairneis ton kathe dimiourgimeno temp_array kai ton prostheteis sto result pou einai na gyriseis.

        for i in range(scenarios):
            for j in range(time_steps):
                result[i, j] += temp_array[i, j]

    return result


def emissions_calculation_simple_lca(list exchange_amounts, list emission_amounts):

    cdef int num_processes = len(exchange_amounts) # Processes gia ypologismo (sub-sub-processes stin sub-process) i unit_impacts.shape[0]
    cdef int num_flows = emission_amounts[0].shape[0] # flows


    cdef cnp.ndarray[cnp.float64_t, ndim=2] result_groups = np.zeros((num_processes, num_flows), dtype = np.float64)

    cdef cnp.ndarray[cnp.float64_t, ndim=1] final_result = np.zeros((num_flows), dtype = np.float64)


    cdef int k, i
    cdef cnp.float64_t temp, amount_array
    cdef cnp.ndarray[cnp.float64_t, ndim=2] amount_flows

    for k in range(num_processes): # gia kathe sub-sub-process sto sub-process
        amount_array = exchange_amounts[k] #Travaw ton np.array me ta amounts of exchanges gia kathe scenario kai se kathe time-step
        amount_flows = emission_amounts[k]

        for i in range(num_flows): # gia kathe impact category
            temp = amount_flows[i,0]
            result_groups[k,i] = temp * amount_array #pollaplasiazoume to unit_impact gia tin katigoria me to exchange amount se kathe time-step kai scenario


    for k in range(num_processes):
        for i in range(num_flows):
            final_result[i] += result_groups[k,i]

    return final_result, result_groups


def characterized_inventory_calculation_simple_lca(list exchange_amounts, list emission_amounts):

    cdef int num_processes = len(exchange_amounts) # Processes gia ypologismo (sub-sub-processes stin sub-process) i len(emission_amounts)
    cdef int num_cat = len(emission_amounts[0]) # categories
    cdef int num_flows = emission_amounts[0][0].shape[0]

    cdef cnp.ndarray[cnp.float64_t, ndim=3] result_groups = np.zeros((num_processes, num_cat, num_flows), dtype = np.float64)

    cdef cnp.ndarray[cnp.float64_t, ndim=2] final_result = np.zeros((num_cat, num_flows), dtype = np.float64)


    cdef int c, k, i

    cdef cnp.ndarray[cnp.float64_t, ndim=2] amount_flows
    cdef cnp.float64_t temp, amount_array

    for k in range(num_processes): # gia kathe sub-sub-process sto sub-process
        for c in range(num_cat):

            amount_array = exchange_amounts[k] #Travaw ton np.array me ta amounts of exchanges gia kathe scenario kai se kathe time-step
            amount_flows = emission_amounts[k][c]

            for i in range(num_flows): # gia kathe impact category
                temp = amount_flows[i,0]
                result_groups[k,c,i] = temp * amount_array #pollaplasiazoume to unit_impact gia tin katigoria me to exchange amount se kathe time-step kai scenario

    for k in range(num_processes):
        for c in range(num_cat):
            for i in range(num_flows):
                final_result[c,i] += result_groups[k,c,i]

    return final_result, result_groups


def emissions_calculation_total_simple_lca(list exchange_amounts, list unit_impacts):

    cdef int num_p = len(unit_impacts) # number of operational sub-processes
    cdef int flows = unit_impacts[0].shape[0] # impact categories

    cdef int total_processes = num_p

    cdef cnp.ndarray[cnp.float64_t, ndim=1] sum_array = np.zeros((flows), dtype = np.float64)
    cdef cnp.ndarray[cnp.float64_t, ndim=2] contributions_array = np.zeros((total_processes, flows), dtype = np.float64)

    cdef int n, c
    cdef double product, exchange_amount
    cdef cnp.ndarray[cnp.float64_t, ndim = 1] unit_impact


    for n in range(total_processes):
        exchange_amount = exchange_amounts[n]
        unit_impact = unit_impacts[n]
        for c in range(flows):
            product = unit_impact[c] * exchange_amount
            sum_array[c] += product
            contributions_array[n,c] = product

    return sum_array, contributions_array


def characterized_inventory_calculation_total_simple_lca(list exchange_amounts, list unit_char_inv):

    cdef int num_p = len(unit_char_inv)  # number of operational sub-processes
    cdef int num_cat = unit_char_inv[0].shape[0]  # impact categories
    cdef int flows = unit_char_inv[0].shape[1]  # flows

    cdef int total_processes = num_p

    cdef cnp.ndarray[cnp.float64_t, ndim=2] sum_array = np.zeros((num_cat, flows), dtype=np.float64)
    cdef cnp.ndarray[cnp.float64_t, ndim=3] contributions_array = np.zeros((total_processes, num_cat, flows), dtype=np.float64)

    cdef int n, c, f
    cdef double product, exchange_amount
    cdef cnp.ndarray[cnp.float64_t, ndim = 2] unit_c_inv

    for n in range(total_processes):
        exchange_amount = exchange_amounts[n]
        unit_c_inv = unit_char_inv[n]
        for c in range(num_cat):
            for f in range(flows):
                product = unit_c_inv[c, f] * exchange_amount
                sum_array[c, f] += product
                contributions_array[n, c, f] = product

    return sum_array, contributions_array



















