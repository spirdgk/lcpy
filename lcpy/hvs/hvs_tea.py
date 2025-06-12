import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import patches
import matplotlib.cm as cm
import os
import seaborn as sns


def save_barchart_dataframes(df_list, names_list, sheet_names_list, file_name, target_dir):


    # for df, names in zip(df_list, names_list):
    #     df['RowName'] = names

    excel_file_path_2 = os.path.join(target_dir, file_name)

    # Save DataFrames to Excel in separate sheets
    with pd.ExcelWriter(excel_file_path_2, engine='xlsxwriter') as writer:
        for df, sheet_name in zip(df_list, sheet_names_list):
            df.to_excel(writer, sheet_name=sheet_name, index=True)

    print(f"Excel file saved as {excel_file_path_2}")


def save_barchart_dataframe(df, names, sheet_name, file_name):

    # df['RowName'] = names
    # Save DataFrames to Excel in separate sheets
    with pd.ExcelWriter(file_name, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name=sheet_name, index=True)

    print(f"Excel file saved as {file_name}")


def visualize_barcharts(percentages_df, no_names, ia_headers, my_name, target_dir, rev, y_label, rel=''):
    plt.figure(figsize=(10, 6))

    # Use Seaborn's color palette instead of cm.get_cmap
    colors = sns.color_palette("cividis", len(no_names))

    bar_width = 0.3
    x_positions = np.arange(len(ia_headers))

    for i, row_label in enumerate(no_names):
        plt.bar(
            x_positions,
            percentages_df.loc[row_label].values.flatten(),
            label=row_label,
            bottom=percentages_df.loc[no_names[:i]].sum(axis=0).values.flatten() if i > 0 else 0,
            color=colors[i],
            width=bar_width
        )

    # Place legend outside the plot to avoid overlap
    plt.legend(loc="upper left", bbox_to_anchor=(1, 1))

    plt.xlabel(my_name)
    plt.ylabel(y_label)

    plt.xlim(x_positions[0] - bar_width, x_positions[-1] + bar_width * 1.2)
    plt.xticks(x_positions, ia_headers)

    # Adjust layout to prevent cropping of legend
    plt.tight_layout(rect=[0, 0, 0.85, 1])

    file_path = os.path.join(target_dir, f'barchart_{my_name}_{rel}_{rev}.png')
    plt.savefig(file_path, bbox_inches='tight')  # Ensure the entire figure (including the legend) is saved
    plt.close()


def visualize_barcharts_wrapper(list_with_dfs, lists_with_names_list, ia_headers, total_names, target_dir, rev, ylabel, rel = ' '):

    for index in range(len(list_with_dfs)):
        visualize_barcharts(list_with_dfs[index], lists_with_names_list[index], ia_headers, total_names[index], target_dir, rev, ylabel, rel)


def create_df_tea_1(no_impact, no_names, ia_headers):

    no_sum = no_impact.sum(axis=0)
    no_impact_with_sums = np.append(no_impact, [no_sum])
    # df_no2 = pd.DataFrame(no_impact_with_sums, index=no_names + ['Sum'], columns=ia_headers)
    df_no = pd.DataFrame(no_impact, index=no_names, columns=ia_headers)
    percentages = (no_impact / no_sum) * 100
    percentages_df = pd.DataFrame(percentages, index=no_names, columns=ia_headers)

    return [df_no, percentages_df]


def calculate_undiscounted_cost_contributions_per_process(names_op, names_infr, exch_op, exch_infr, header, total_names_dict,
                                                          target_dir, file_name_total = 'cost_breakdown.xlsx',
                                                          file_name_contributions= 'cost_total.xlsx', rev = '', scen = 0, year =0):
    try:
        names = [list(inner_dict.keys()) for inner_dict in names_infr.values()]
        names += [list(inner_dict.keys()) for inner_dict in names_op.values()]
    except:
        names = [list(names_infr.values())]
        names += list(names_op.values())

    exchanges = [inner_list for inner_list in exch_infr.values()]
    exchanges += [inner_list for inner_list in exch_op.values()]

    total_names_for_visualization = list(total_names_dict.values())[0]
    sheet_names = list(total_names_dict.values())[0]

    df_perc_list = []
    df_list = []

    for i in range(len(names)):
        res = create_df_tea_1(np.array(exchanges[i])[:, scen, year], names[i], header)
        df_perc_list.append(res[1])
        df_list.append(res[0])

    visualize_barcharts_wrapper(df_perc_list, names, header, total_names_for_visualization, target_dir, rev, f"Contribution", 'rel')
    save_barchart_dataframes(df_perc_list, names, sheet_names, f"scen_{scen}_year_{year}_{rev}_{file_name_total}", target_dir)

    visualize_barcharts_wrapper(df_list, names, header, total_names_for_visualization, target_dir, rev, f"Absolute", 'tot')
    save_barchart_dataframes(df_list, names, sheet_names, f"scen_{scen}_year_{year}_{rev}_{file_name_contributions}", target_dir)


def calculate_undiscounted_cost_contributions_electricity_and_personnel(names_elec, names_pers, exch_elec, exch_pers, header, total_names_dict,
                                                          target_dir, file_name_total = 'elec_and_pers_cost_breakdown.xlsx',
                                                          file_name_contributions= 'elec_and_pers_cost_total.xlsx', scen = 0, year =0):

    names = [names_elec] + [names_pers]
    exchanges = [exch_elec] + [exch_pers]

    total_names_for_visualization = list(total_names_dict.values())[0]
    sheet_names = list(total_names_dict.values())[0]

    df_perc_list = []
    df_list = []

    for i in range(len(names)):
        res = create_df_tea_1(np.array(exchanges[i])[:,scen,year], names[i], header)
        df_perc_list.append(res[1])
        df_list.append(res[0])

    visualize_barcharts_wrapper(df_perc_list, names, header, total_names_for_visualization, target_dir, f"contributions_scen_{scen}_year_{year}", 'rel')
    save_barchart_dataframes(df_perc_list, names, sheet_names, f"scen_{scen}_year_{year}_{file_name_total}", target_dir)

    visualize_barcharts_wrapper(df_list, names, header, total_names_for_visualization, target_dir, f"total_scen_{scen}_year_{year}", 'tot')
    save_barchart_dataframes(df_list, names, sheet_names, f"scen_{scen}_year_{year}_{file_name_contributions}", target_dir)


def visualize_dataframes_time_series(dataframes, impacts, scenarios, xlabel, ylabel, title, filepath, fig_size = (6,3), dpi = 300, offset = 0):

    for i, (df, category) in enumerate(zip(dataframes, impacts)):
        plt.figure(figsize=fig_size, dpi = dpi)
        df[scenarios][offset:].plot(ax=plt.gca(), title=title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.legend(title="Scenarios")

        if type(scenarios) == str:
            plt.savefig(f"{filepath}_{scenarios}.png")
        else:
            plt.savefig(f"{filepath}_all_scenarios.png")
        plt.close()


def visualize_npv_in_time(df_rev, df_cost, scen_names, filepath, fig_size = (5,3), dpi = 300):

    npv_scen = pd.DataFrame()
    plt.figure(figsize= fig_size, dpi = dpi)
    for scen in scen_names:

        npv_scen[scen] = df_rev[0][scen] - df_cost[0][scen]
        npv_scen[scen].plot(ax=plt.gca())

    plt.title("Net Present Value")
    plt.xlabel("Years")
    plt.ylabel("EUR")
    plt.legend(title="Scenarios")
    plt.savefig(filepath)
    plt.close()


def visualize_stacked_barchart_time_series(df, step, total_names, filepath, ylabel, xlabel, title):

    # pare ta onomata, valta indexes
    # df = df.set_index(df.columns[0])

    # pare kathe column pou thes me vasi to step
    cols_to_vis = df.columns[::step]
    df_with_cols_to_vis = df[cols_to_vis]

    # travikse total
    total = df_with_cols_to_vis.sum(axis=0)

    # Contributions
    df_percentage = df_with_cols_to_vis.div(total, axis=1) * 100

    # color_map = cm.get_cmap('cividis', len(total_names))  # Human-friendly color palette
    # colors = color_map(np.linspace(0, 1, len(total_names)))

    #Ftiakse diagramma
    ax = df_percentage.T.plot(
        kind='bar',
        stacked=True,
        figsize=(10, 6),
        cmap='cividis',
        edgecolor='black'
    )

    # Add labels and legend
    ax.set_ylabel(ylabel)
    ax.set_xlabel(xlabel)
    ax.set_title(title)
    ax.legend(title='Barchart', labels= total_names, bbox_to_anchor=(1.05, 1), loc='upper left')

    # Adjust layout for better visibility
    plt.tight_layout()
    plt.savefig(filepath)
    plt.close()


def visualize_stacked_barcharts(mapping_test, cost_arrays, names_scen, step_for_vis, excel_file_path, scen_to_visualize, yaxis_label, xaxis_label, rel):

    my_list = list(mapping_test.keys())
    my_dict_test = {names_scen[i]: pd.DataFrame(cost_arrays[i, :, :].T, index=list(mapping_test.keys())) for i in range(len(names_scen))}

    visualize_stacked_barchart_time_series(my_dict_test[scen_to_visualize], step_for_vis, my_list, excel_file_path, yaxis_label, xaxis_label, rel)


def npv_results_storage_and_vis(list_values, list_names, target_dir, file_name = 'boxplot_results.xlsx'):

    excel_file_path = os.path.join(target_dir, file_name)
    npv_results = {}

    for value, name in zip(list_values, list_names):
        npv_results[name] = value

    df = pd.DataFrame(npv_results)
    df.to_excel(excel_file_path, index=True)
    describe_path = os.path.join(target_dir, f"scenarios_describe_costs.xlsx")
    df.describe().to_excel(describe_path)

    for column in df.columns:
        plt.figure(figsize=(6, 4))
        plt.boxplot(df[column], vert=True)
        plt.title(f"Boxplot of {column}")
        excel_file_path = os.path.join(target_dir, f"boxplot_{column}.png")
        plt.savefig(excel_file_path)
        plt.close()


def create_dictionary_with_dfs(mapping_dict, cost_dict, scenario_index, name):
    dict_with_dfs = {}
    dict_with_dfs_contributions = {}

    for process, subprocesses in mapping_dict.items():
        # Get the corresponding cost array for the process
        cost_array = cost_dict.get(process)

        if cost_array is None:
            continue  # Skip if process not in cost_per_process (just in case)

        # Sum over time_steps (axis=2) for the specified scenario (axis=1)
        subprocess_costs = cost_array[:, scenario_index, :].sum(axis=1)

        total_cost = subprocess_costs.sum()

        if total_cost == 0:
            contributions = np.zeros_like(subprocess_costs)  # Avoid division by zero
        else:
            contributions = subprocess_costs / total_cost

        # Create a DataFrame with subprocess names as index and cost as column
        df = pd.DataFrame({
            name: subprocess_costs
        }, index=subprocesses)

        df_contributions = pd.DataFrame({
            name: contributions
        }, index=subprocesses)

        # Add the 'Total' row
        df.loc['Total'] = df[name].sum()

        # Store in the result dictionary
        dict_with_dfs[process] = df
        dict_with_dfs_contributions[process] = df_contributions

    return dict_with_dfs, dict_with_dfs_contributions


def contribution_per_sub_sub_processes(dict_with_total_impacts, dict_with_contributions,
                                       list_with_unique_names, header, sign = -1, name = '', save = 'True', target_dir = ''):

    temp = 0.0
    temp_dict = {}
    temp_list = []

    for cat in header:

        for act in list_with_unique_names:
            for (item, df) in zip(dict_with_contributions.keys(), dict_with_contributions.values()):

                if item != 'Total':
                    x = df[cat]
                    try:
                        temp += x[act] * dict_with_total_impacts[item].loc['Total', header[0]]
                    except:
                        pass

            temp_dict[act] = temp*sign
            temp = 0.0


        cleaned_data = {k: (0.0 if pd.isna(v) else v) for k, v in temp_dict.items()}
        sorted_items = sorted(cleaned_data.items(), key=lambda x: x[1], reverse=True)
        my_df = pd.DataFrame(sorted_items, columns=["Key", "Value"]).set_index("Key")

        temp_list.append(my_df)
        temp_dict = {}

    contribution_per_sub_sub_process = dict(zip(header, temp_list))

    if save:
        filepath = os.path.join(target_dir, f'Sub_sub_process_contributions_{name}.xlsx')

        with pd.ExcelWriter(filepath, engine='xlsxwriter') as writer:
            for sheet_name, df in contribution_per_sub_sub_process.items():
                df.to_excel(writer, sheet_name=sheet_name, index=True)

    return contribution_per_sub_sub_process