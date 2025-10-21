import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
import os


def create_dataframe_dict(df_list, names_list):


    if len(df_list) != len(names_list):
        raise ValueError("The length of df_list and names_list must be the same.")

    return {name: df for name, df in zip(names_list, df_list)}


def save_dataframes_to_excel(df_dict, file_path):
    """
        Saves multiple DataFrames into an Excel workbook with each DataFrame on a separate sheet.

        Parameters:
            dataframes_dict (dict): A dictionary where keys are sheet names and values are pandas DataFrames.
            file_name (str): The name of the Excel file to save.

        Returns:
            None
        """
    with pd.ExcelWriter(file_path, engine='xlsxwriter') as writer:
        for sheet_name, df in df_dict.items():

            sheet_name_actual = sheet_name[:30]
            df.to_excel(writer, sheet_name = sheet_name_actual, index = True)

    print(f"Excel file '{file_path}' saved successfully.")


def create_name_dictionaries(mapping_dict, key_list):

    return dict(zip(list(mapping_dict.keys()), [list(dictionary.keys()) for dictionary in key_list]))


def plot_stacked_percentage_barchart_seaborn(df, filepath, figsize, dpi,
                                             label_size = 14,
                                             tick_size = 14,
                                             legend_size = 12,
                                             verbose = 'True', tab = "tab10", 
                                             xlabel="Categories", ylabel="Contribution (%)"):
    """
    Plots a stacked percentage bar chart using Seaborn where each column sums to 100%.

    Parameters:
        df (pd.DataFrame): DataFrame where columns represent different categories and rows represent data groups.
        title (str, optional): Title of the plot. Default is "Stacked Percentage Bar Chart".
        xlabel (str, optional): Label for the x-axis. Default is "Categories".
        ylabel (str, optional): Label for the y-axis. Default is "Percentage".

    Returns:
        None
    """
    # Normalize each column to percentages (column-wise sum to 100%)
    df_percent = df.div(df.sum(axis=0), axis=1) * 100

    # Define colors
    num_categories = len(df.index)
    colors = sns.color_palette(tab, num_categories)  # Uses Seaborn's color palette

    # Plot stacked bar chart
    fig, ax = plt.subplots(figsize= figsize, dpi=dpi)
    bottom = np.zeros(len(df.columns))  # Initialize bottom at zero for stacking

    for (row_label, row_values), color in zip(df_percent.iterrows(), colors):
        ax.bar(df.columns, row_values, bottom=bottom, label=row_label, color=color, edgecolor="black")
        bottom += row_values  # Update bottom position for stacking

    # Labels and Formatting
    # ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel, fontsize=label_size)
    ax.grid(False)
    ax.tick_params(axis='both', labelsize=tick_size)
    ax.set_ylim(0, 100)  # Ensures each bar sums to 100%
    ax.legend(bbox_to_anchor=(1.05, 1.05), loc="upper left", fontsize = legend_size)  # Move legend outside
    plt.xticks()  # Rotate labels for readability

    # Show the plot
    plt.savefig(filepath, bbox_inches='tight')
    if verbose:
        plt.show()
    plt.close()


def create_dataframes_for_holistic_contribution_analysis(data):

    names = [str(tup[1]) for tup in data]
    values = [tup[0] for tup in data]

    return pd.DataFrame({"Name": names, "Value": values})


def store_scenario_results(df, target_dir, impact_categories_units, figsize, dpi,
                           label_size = 14, tick_size = 12, figure_type = 'png',
                           name = ""):
    df_path = os.path.join(target_dir, "scenarios_dataframe.xlsx")
    df.to_excel(df_path, index=True)

    describe_path = os.path.join(target_dir, f"scenarios_describe_{name}.xlsx")
    df.describe().to_excel(describe_path)

    for i, column in enumerate(df.columns):
        plt.figure(figsize=figsize, dpi=dpi)
        df.boxplot(column=column)

        # Set y-axis label
        y_label = impact_categories_units[i] if i < len(impact_categories_units) else "Values"
        plt.ylabel(y_label, fontsize=label_size)
        plt.tick_params(axis ='both', labelsize=tick_size)

        boxplot_path = os.path.join(target_dir, f"boxplot_{column}_{name}.{figure_type}")
        plt.savefig(boxplot_path, bbox_inches='tight')
        plt.close()


def save_scenario_dataframes(scenario_dfs, selected_keys, output_dir, name, per_fu = "", infr_op = ''):

    excel_path = os.path.join(output_dir, f"impact_{name}_{per_fu}_{infr_op}.xlsx")

    # Write selected DataFrames to an Excel workbook
    with pd.ExcelWriter(excel_path, engine='xlsxwriter') as writer:
        for key in selected_keys:
            if key in scenario_dfs:
                scenario_dfs[key].to_excel(writer, sheet_name=key, index=True)

    print(f"DataFrames saved in: {excel_path}")


def create_scenario_dataframes(x, impact_categories_names, scen_list) -> dict:

    if len(x.shape) == 2:
        x = np.expand_dims(x, axis=0)
    else:
        pass

    categories, scenarios, years = x.shape
    if len(impact_categories_names) != categories or len(scen_list) != scenarios:
        raise ValueError("Mismatch between array dimensions and provided category/scenario lists")

    scenario_dfs = {}

    # Loop over each scenario index
    for i, scenario in enumerate(scen_list):
        # Extract data for the current scenario (shape: categories x years)
        scenario_data = x[:, i, :]

        # Transpose so years become rows and categories become columns
        df = pd.DataFrame(scenario_data.T, columns=impact_categories_names)

        # Store in dictionary with the scenario name as key
        scenario_dfs[scenario] = df

    return scenario_dfs


def create_and_save_dataframes_per_scenario_and_per_category(impact_array, column_names, file_path, save = False):

    if save == True:
        with pd.ExcelWriter(file_path) as writer:
            df = pd.DataFrame(impact_array[:, :], columns=column_names)
            df.to_excel(writer)
    elif save == False:
        df = pd.DataFrame(impact_array[:, :], columns=column_names)
        print('Dataframes not save, set save to True to save them')

    return df


def create_and_save_dataframes_time_series(res_array, impacts, scenarios, excel_file_name = 'time_series_output.xlsx', save = False):

    dataframes = []

    if save == False:

        if res_array.ndim == 3:
            for i, category in enumerate(impacts):
                df = pd.DataFrame(res_array[i, :, :].T, columns=scenarios)
                dataframes.append(df)
            print('Dataframes not save, set save to True to save them')
        elif res_array.ndim == 2:
            df = pd.DataFrame(res_array[:, :].T, columns=scenarios)
            dataframes.append(df)
            print('Dataframes not save, set save to True to save them')

    if save == True:

        with pd.ExcelWriter(excel_file_name) as writer:

            if res_array.ndim == 3:
                for i, category in enumerate(impacts):
                    df = pd.DataFrame(res_array[i, :, :].T, columns=scenarios)
                    dataframes.append(df)
                    df.to_excel(writer, sheet_name=category)
            elif res_array.ndim == 2:
                df = pd.DataFrame(res_array[:, :].T, columns=scenarios)
                dataframes.append(df)
                df.to_excel(writer, sheet_name=impacts[0])

    return dataframes


def plot_bar_charts_by_category(scenarios, scenarios_to_plot=None, impacts_to_plot=None, target_dir=".", figsize=(10, 5),
                                dpi=300, per_fu='', name = "", con_years = 0):
    """
    Plots bar charts from a dictionary of DataFrames where each key represents a scenario,
    and each DataFrame contains categories as columns and steps as rows.

    Parameters:
    scenarios (dict): Dictionary containing Pandas DataFrames.
    keys_to_plot (list, optional): List of scenario keys to plot. If None, all scenarios are plotted.
    scenarios_to_plot (list, optional): List of category names (columns) to plot. If None, all categories are plotted.
    target_dir (str): Directory to save the plots.
    per_fu (str, optional): Additional string for filename customization.
    """

    # Determine which keys (scenarios) to plot
    scenarios_to_plot = scenarios_to_plot if scenarios_to_plot is not None else scenarios.keys()

    for key in scenarios_to_plot:
        if key not in scenarios:
            print(f"Warning: Key '{key}' not found in the dictionary.")
            continue

        if con_years != 0:
            df = scenarios[key].iloc[con_years:, :]
        else:
            df = scenarios[key]

        # Determine which columns (categories) to plot
        categories_to_plot = impacts_to_plot if impacts_to_plot is not None else df.columns

        # Filter DataFrame to include only selected categories
        for category in categories_to_plot:
            plt.figure(figsize=figsize, dpi=dpi)
            sns.barplot(x=df.index, y=df[category], color='skyblue')

            plt.xlabel("Time")
            plt.ylabel("Impact")

            # Save the figure
            filename = f"{key}_barplot_{category}_{name}_{per_fu}.png"
            filepath = os.path.join(target_dir, filename)
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            plt.show()
            plt.close()
            print(f"Plot saved: {filepath}")


def visualize_dict_lineplots(dfs, impact_names, target_dir, con_years = 0, keys_to_plot=None, scenarios_to_plot=None, name = '', return_dict = True):
    """
    Visualizes the content of a dictionary where each element is a Pandas DataFrame.
    Each DataFrame is visualized as a line plot in a separate figure.

    Parameters:
    my_dict (dict): Dictionary containing Pandas DataFrames.
    keys_to_plot (list, optional): List of dictionary keys to plot. If None, all elements are plotted.
    scenarios_to_plot (list, optional): List of column names (scenarios) to plot. If None, all columns are plotted.
    """
    my_dict = dict(zip(impact_names, dfs))

    # Determine which keys to plot
    keys_to_plot = keys_to_plot if keys_to_plot is not None else my_dict.keys()

    for key in keys_to_plot:
        if key not in my_dict:
            print(f"Warning: Key '{key}' not found in the dictionary.")
            continue

        if con_years != 0:
            df = my_dict[key].iloc[con_years:, :]
        else:
            df = my_dict[key]


        # Determine which columns (scenarios) to plot
        columns_to_plot = scenarios_to_plot if scenarios_to_plot is not None else df.columns

        # Filter dataframe to include only selected scenarios
        df_filtered = df[columns_to_plot]

        # Create the line plot
        plt.figure(figsize=(10, 6))
        sns.lineplot(data=df_filtered)

        plt.xlabel("Time")
        plt.ylabel("Impact")
        plt.title(f"{key}")
        plt.legend(df_filtered.columns, title="Scenarios")

        # Save the figure
        scenarios_str = "all" if scenarios_to_plot is None else "_".join(scenarios_to_plot)
        excel_file_path = os.path.join(target_dir, f"{key}_lineplot_{scenarios_str}_{name}.png")
        plt.savefig(excel_file_path, dpi=300, bbox_inches='tight')
        plt.show()
        plt.close()

    if return_dict:
        return my_dict


def visualize_stacked_barchart_time_series_impact(impact, scen_idx, category_names, mapping, target_dir, name = "", per_fu = ''):

    _, categories, scenarios, times = impact.shape

    process_names = list(mapping.keys())

    for cat_idx in range(categories):
        category_data = impact[:, cat_idx, scen_idx, :]
        total = np.sum(category_data, axis=0)

        # Calculate percentage contributions
        percentages = category_data / total * 100

        plt.figure(figsize=(12, 6))
        bottom = np.zeros(times)

        for process_idx in range(len(process_names)):
            plt.bar(
                range(1, times + 1),
                percentages[process_idx],
                bottom=bottom,
                label=process_names[process_idx]
            )
            bottom += percentages[process_idx]

        plt.ylabel(category_names[cat_idx])
        plt.xlabel('Years')
        plt.xticks(range(1, times + 1), labels=[f"{t}" for t in range(1, times + 1)])
        plt.legend(title="Processes", bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()

        # Adjust layout for better visibility
        excel_file_path = os.path.join(target_dir, f'impact_stacked_bars_in_time_{category_names[cat_idx]}_{per_fu}_{name}.png')
        plt.savefig(excel_file_path)
        plt.show()
        plt.close()


def plot_fcf_line_per_flow(scenario_dict, scenario_names, flow_name, target_dir, category_name = 'GWP', figsize = (5,3), dpi = 300):
    """
    Plots the development of a variable over time for selected scenarios.

    Parameters:
    - scenario_dict (dict): Dictionary where keys are scenario names and values are DataFrames.
      Each DataFrame contains a single column representing the variable over time (0-11 years).
    - scenario_names (list): List of scenario names to be plotted.

    Returns:
    - A line plot showing the variable's progression over time for selected scenarios.
    """

    plt.figure(figsize=figsize, dpi=dpi)

    for scenario in scenario_names:
        if scenario in scenario_dict[flow_name]:
            df = pd.DataFrame(scenario_dict[flow_name][scenario])
            variable_name = df.columns[0]  # Assuming a single variable per DataFrame
            plt.plot(df.index, df[variable_name], label=scenario)
        else:
            print(f"Warning: Scenario '{scenario}' not found in the dictionary.")

    plt.xlabel("Time (Years)")
    plt.ylabel("Impact")
    plt.legend()
    plt.title(f"{flow_name}")
    excel_file_path = os.path.join(target_dir, f'impact_fcf_{category_name}_{flow_name}.png')
    plt.savefig(excel_file_path, bbox_inches="tight")
    plt.show()
    plt.close()


def map_fcf_icf_results_to_flows(biosphere_dict, scenario_names, total_impact_fcf_per_flow):
    x = {
        str(biosphere_dict[i]): {
            scenario_names[j]: total_impact_fcf_per_flow[i, j, :]  # Assign each row (1x12) to a scenario name
            for j in range(len(scenario_names))  # Each 2D slice has 10 rows, one per scenario
        }
        for i in range(len(biosphere_dict))
    }

    return x


def plot_icf_line(scenario_dict, scenario_names, target_dir, years_to_plot = 100, category_name = 'GWP', figsize = (5,3), dpi = 300):
    """
    Plots the development of a variable over time for selected scenarios.

    Parameters:
    - scenario_dict (dict): Dictionary where keys are scenario names and values are DataFrames.
      Each DataFrame contains a single column representing the variable over time (0-11 years).
    - scenario_names (list): List of scenario names to be plotted.

    Returns:
    - A line plot showing the variable's progression over time for selected scenarios.
    """

    plt.figure(figsize=figsize, dpi=dpi)

    for scenario in scenario_names:
        if scenario in scenario_dict:
            df = scenario_dict[scenario].iloc[:years_to_plot]
            variable_name = df.columns[0]  # Assuming a single variable per DataFrame
            plt.plot(df.index, df[variable_name], label=scenario)
        else:
            print(f"Warning: Scenario '{scenario}' not found in the dictionary.")

    plt.xlabel("Time (Years)")
    plt.ylabel(variable_name)
    plt.legend()
    excel_file_path = os.path.join(target_dir, f'impact_fcf_{category_name}.png')
    plt.savefig(excel_file_path, bbox_inches="tight")
    plt.show()
    plt.close()


def plot_icf_line_per_flow(scenario_dict, scenario_names, flow_name, target_dir, years_to_plot = 100, category_name = 'GWP', figsize = (5,3), dpi = 300):
    """
    Plots the development of a variable over time for selected scenarios.

    Parameters:
    - scenario_dict (dict): Dictionary where keys are scenario names and values are DataFrames.
      Each DataFrame contains a single column representing the variable over time (0-11 years).
    - scenario_names (list): List of scenario names to be plotted.

    Returns:
    - A line plot showing the variable's progression over time for selected scenarios.
    """

    plt.figure(figsize=figsize, dpi=dpi)

    for scenario in scenario_names:
        if scenario in scenario_dict[flow_name]:
            df = pd.DataFrame(scenario_dict[flow_name][scenario]).iloc[:years_to_plot]
            variable_name = df.columns[0]  # Assuming a single variable per DataFrame
            plt.plot(df.index, df[variable_name], label=scenario)
        else:
            print(f"Warning: Scenario '{scenario}' not found in the dictionary.")

    plt.xlabel("Time (Years)")
    plt.ylabel("Impact")
    plt.legend()
    plt.title(f"{flow_name}")
    excel_file_path = os.path.join(target_dir, f'impact_fcf_{category_name}_{flow_name}.png')
    plt.savefig(excel_file_path, bbox_inches="tight")
    plt.show()
    plt.close()


def sum_scenarios_per_flow(data: dict, flows: list, scenarios: list, name: str) -> dict:
    """
    Sums the NumPy arrays for the given scenarios across the specified flows.

    Parameters:
        data (dict): The nested dictionary {flow: {scenario: np.array}}.
        flows (list): List of outer dictionary keys to include in the sum.
        scenarios (list): List of inner dictionary keys to sum across the flows.

    Returns:
        dict: A dictionary with scenario names as keys and summed np.arrays as values.
    """
    result = {scenario: None for scenario in scenarios}  # Initialize result dictionary

    for flow in flows:
        if flow in data:  # Ensure the flow exists in the dictionary
            for scenario in scenarios:
                if scenario in data[flow]:  # Ensure the scenario exists in the flow
                    if result[scenario] is None:
                        result[scenario] = data[flow][scenario].copy()
                    else:
                        result[scenario] += data[flow][scenario]

    df_result = pd.DataFrame.from_dict(result)

    return {name: df_result}


def plot_stacked_percentage_bar_sub_processes(data_dict, key, filepath, label_fontsize=14, tick_fontsize=14, title_fontsize=14,
                                              figsize = (5,3), dpi = 600, top_x=5,  verbose = 'False', ylabel="Processes", xlabel="Contribution (%)"):
    """
    Creates a stacked percentage bar chart for the given key.

    Parameters:
    - data_dict: Dictionary containing dataframes.
    - key: The category key to plot.
    - top_x: Number of top indices to keep, others are grouped as "Other".
    """
    if key not in data_dict:
        print(f"Key '{key}' not found in the dictionary.")
        return

    # Extract the relevant DataFrame
    df = data_dict[key].copy()

    # Ensure sorting in descending order (already sorted but just in case)
    df = df.sort_values(by="Value", ascending=False)

    # Select top X indices
    df_top = df.iloc[:top_x]

    # Sum the remaining values as "Other"
    other_value = df.iloc[top_x:]["Value"].sum()

    # Append "Other" category if needed
    if other_value > 0:
        df_other = pd.DataFrame({"Value": [other_value]}, index=["Other"])
        df_final = pd.concat([df_top, df_other])
    else:
        df_final = df_top

    # Convert values to percentages
    df_final["Percentage"] = df_final["Value"] / df_final["Value"].sum() * 100

    # Plot stacked bar chart
    fig, ax = plt.subplots(figsize=figsize, dpi = dpi)
    ax.barh(df_final.index, df_final["Percentage"], color=plt.cm.Paired.colors[:len(df_final)])

    # Add labels
    for i, v in enumerate(df_final["Percentage"]):
        ax.text(v + 1, i, f"{v:.1f}%", va='center')

    ax.set_xlabel(xlabel, fontsize=label_fontsize)
    ax.grid(False)
    ax.set_ylabel(ylabel, fontsize=label_fontsize)
    ax.tick_params(axis='both', labelsize=tick_fontsize)
    ax.set_title(f"{key}", fontsize=title_fontsize)
    plt.savefig(filepath, bbox_inches='tight')

    plt.gca().invert_yaxis()  # Highest value at top
    if verbose:
        plt.show()
    else:
        plt.close(fig)


def plot_stacked_percentage_bar_grid(data_dict, keys, filepath, figsize=(15, 12), dpi=600, top_x=5, ylabel="Processes", 
                                     xlabel="Contribution (%)", label_fontsize=14, tick_fontsize=14, title_fontsize=16):
    """
    Creates a 3x3 grid of stacked percentage bar charts for the given keys.

    Parameters:
    - data_dict: Dictionary containing dataframes.
    - keys: List of 9 category keys to plot.
    - filepath: Path to save the figure.
    - top_x: Number of top indices to keep, others are grouped as "Other".
    """
    if len(keys) != 9:
        print("Error: Exactly 9 keys must be provided.")
        return

    fig, axes = plt.subplots(3, 3, figsize=figsize, dpi=dpi)
    axes = axes.flatten()  # Flatten for easy iteration

    for idx, key in enumerate(keys):
        if key not in data_dict:
            print(f"Key '{key}' not found in the dictionary.")
            continue

        # Extract and process data
        df = data_dict[key].copy()
        df = df.sort_values(by="Value", ascending=False)
        df_top = df.iloc[:top_x]
        other_value = df.iloc[top_x:]["Value"].sum()

        if other_value > 0:
            df_other = pd.DataFrame({"Value": [other_value]}, index=["Other"])
            df_final = pd.concat([df_top, df_other])
        else:
            df_final = df_top

        df_final["Percentage"] = df_final["Value"] / df_final["Value"].sum() * 100

        # Plot in subplot
        ax = axes[idx]
        ax.barh(df_final.index, df_final["Percentage"], color=plt.cm.Paired.colors[:len(df_final)])

        for i, v in enumerate(df_final["Percentage"]):
            ax.text(v + 1, i, f"{v:.1f}%", va='center')

        ax.set_xlabel(xlabel, fontsize=label_fontsize)
        ax.set_ylabel(ylabel, fontsize=label_fontsize)
        ax.set_title(key, fontsize=title_fontsize)
        ax.tick_params(axis="both", labelsize=tick_fontsize)
        ax.invert_yaxis()

    plt.tight_layout()
    plt.savefig(filepath, bbox_inches='tight')
    plt.show()
    plt.close(fig)


def make_characterized_inventory_dfs(char_invs, impact_categories, biosphere_dict, scenario_index):

    num_categories, num_flows, num_scenarios, time_steps = char_invs.shape

    if len(impact_categories) != num_categories:
        raise ValueError(f"Expected {num_categories} category names, got {len(impact_categories)}")
    if len(biosphere_dict) != num_flows:
        raise ValueError(f"Expected {num_flows} flows in flow_dict, got {len(biosphere_dict)}")
    if not (0 <= scenario_index < num_scenarios):
        raise IndexError(f"scenario_idx must be in 0…{num_scenarios - 1}, got {scenario_index}")

    flow_labels = list(biosphere_dict.values())
    time_labels = list(range(time_steps))  # or e.g. [f"t{t}" for t in range(n_ts)]

    dict_with_dfs = {}
    char_invs_for_scenario = char_invs[:, :, scenario_index, :]

    for i, cat_name in enumerate(impact_categories):

        data = char_invs_for_scenario[i, :, :]

        df = pd.DataFrame(data, index=flow_labels, columns=time_labels)
        dict_with_dfs[cat_name] = df

    return dict_with_dfs


def make_characterized_inventory_dfs_simple_lca(char_invs, impact_categories, biosphere_dict, scenario_index):

    num_categories, num_flows = char_invs.shape

    if len(impact_categories) != num_categories:
        raise ValueError(f"Expected {num_categories} category names, got {len(impact_categories)}")
    if len(biosphere_dict) != num_flows:
        raise ValueError(f"Expected {num_flows} flows in flow_dict, got {len(biosphere_dict)}")

    flow_labels = list(biosphere_dict.values())

    dict_with_dfs = {}
    char_invs_for_scenario = char_invs[:, :]

    for i, cat_name in enumerate(impact_categories):

        data = char_invs_for_scenario[i, :]

        df = pd.DataFrame(data, index=flow_labels)
        dict_with_dfs[cat_name] = df

    return dict_with_dfs





#Obsolete functions


def visualize_dict_lineplots_per_fu(my_dict, target_dir, con_years, keys_to_plot=None, scenarios_to_plot=None):
    """
    Visualizes the content of a dictionary where each element is a Pandas DataFrame.
    Each DataFrame is visualized as a line plot in a separate figure.

    Parameters:
    my_dict (dict): Dictionary containing Pandas DataFrames.
    keys_to_plot (list, optional): List of dictionary keys to plot. If None, all elements are plotted.
    scenarios_to_plot (list, optional): List of column names (scenarios) to plot. If None, all columns are plotted.
    """

    # Determine which keys to plot
    keys_to_plot = keys_to_plot if keys_to_plot is not None else my_dict.keys()

    for key in keys_to_plot:
        if key not in my_dict:
            print(f"Warning: Key '{key}' not found in the dictionary.")
            continue

        df = my_dict[key].iloc[con_years:, :]

        # Determine which columns (scenarios) to plot
        columns_to_plot = scenarios_to_plot if scenarios_to_plot is not None else df.columns

        # Filter dataframe to include only selected scenarios
        df_filtered = df[columns_to_plot]

        # Create the line plot
        plt.figure(figsize=(10, 6))
        sns.lineplot(data=df_filtered)

        plt.xlabel("Time")
        plt.ylabel("Impact")
        plt.title(f"{key}")
        plt.legend(df_filtered.columns, title="Scenarios")

        # Save the figure
        scenarios_str = "all" if scenarios_to_plot is None else "_".join(scenarios_to_plot)
        excel_file_path = os.path.join(target_dir, f"{key}_lineplot_{scenarios_str}.png")
        plt.savefig(excel_file_path, dpi=300, bbox_inches='tight')
        plt.show()
        plt.close()


def create_scenario_dataframes_fcf(x, scen_list, impact_categories_names = ['GWP']) -> dict:
    scenarios, years = x.shape
    if len(scen_list) != scenarios:
        raise ValueError("Mismatch between array dimensions and provided scenario lists")

    scenario_dfs = {}

    # Loop over each scenario index
    for i, scenario in enumerate(scen_list):
        # Extract data for the current scenario (shape: categories x years)
        scenario_data = x[i, :]

        # Transpose so years become rows and categories become columns
        df = pd.DataFrame(scenario_data.T, columns=impact_categories_names)

        # Store in dictionary with the scenario name as key
        scenario_dfs[scenario] = df

    return scenario_dfs


def fcf_scenario_bar(scenario_dict, scenario_name, target_dir, category_name = 'GWP', figsize = (5,3), dpi = 300):
    """
    Plots the development of a variable over time as a bar plot for a given scenario.

    Parameters:
    - scenario_dict (dict): Dictionary where keys are scenario names and values are DataFrames.
      Each DataFrame contains a single column representing the variable over time (0-11 years).
    - scenario_name (str): The scenario name to be plotted.

    Returns:
    - A bar plot showing the variable's progression over time for the selected scenario.
    """

    if scenario_name not in scenario_dict:
        print(f"Error: Scenario '{scenario_name}' not found in the dictionary.")
        return

    df = scenario_dict[scenario_name]
    variable_name = df.columns[0]  # Assuming a single variable per DataFrame

    plt.figure(figsize=figsize, dpi=dpi)
    plt.bar(df.index, df[variable_name], color='skyblue')

    plt.xlabel("Time (Years)")
    plt.ylabel(variable_name)
    plt.xticks(df.index)  # Ensure all time points are labeled
    excel_file_path = os.path.join(target_dir, f'impact_fcf_{category_name}_barplot.png')
    plt.savefig(excel_file_path, bbox_inches="tight")
    plt.show()
    plt.close()


def plot_fcf_line(scenario_dict, scenario_names, target_dir, category_name = 'GWP', figsize = (5,3), dpi = 300):
    """
    Plots the development of a variable over time for selected scenarios.

    Parameters:
    - scenario_dict (dict): Dictionary where keys are scenario names and values are DataFrames.
      Each DataFrame contains a single column representing the variable over time (0-11 years).
    - scenario_names (list): List of scenario names to be plotted.

    Returns:
    - A line plot showing the variable's progression over time for selected scenarios.
    """

    plt.figure(figsize=figsize, dpi=dpi)

    for scenario in scenario_names:
        if scenario in scenario_dict:
            df = scenario_dict[scenario]
            variable_name = df.columns[0]  # Assuming a single variable per DataFrame
            plt.plot(df.index, df[variable_name], label=scenario)
        else:
            print(f"Warning: Scenario '{scenario}' not found in the dictionary.")

    plt.xlabel("Time (Years)")
    plt.ylabel(variable_name)
    plt.legend()
    excel_file_path = os.path.join(target_dir, f'impact_fcf_{category_name}.png')
    plt.savefig(excel_file_path, bbox_inches="tight")
    plt.show()
    plt.close()


def plot_fcf_line_per_flow_real(scenario_dict, scenario_names, flow_name, target_dir, category_name = 'GWP', figsize = (5,3), dpi = 300):
    """
    Plots the development of a variable over time for selected scenarios.

    Parameters:
    - scenario_dict (dict): Dictionary where keys are scenario names and values are DataFrames.
      Each DataFrame contains a single column representing the variable over time (0-11 years).
    - scenario_names (list): List of scenario names to be plotted.

    Returns:
    - A line plot showing the variable's progression over time for selected scenarios.
    """

    # print(scenario_dict[flow_name][scenario_names[0]])

    plt.figure(figsize=figsize, dpi=dpi)

    for scenario in scenario_names:
        print(scenario)
        try:
            df = scenario_dict[flow_name][scenario] # Assuming a single variable per DataFrame
            plt.plot(df, label=scenario)

            plt.xlabel("Time (Years)")
            plt.ylabel('Impact')
            plt.legend()
            plt.title(f'{flow_name}')
            excel_file_path = os.path.join(target_dir, f'impact_fcf_{category_name}_{flow_name}.png')
            plt.savefig(excel_file_path, bbox_inches="tight")
            plt.show()
            plt.close()

        except:
            print(f"Warning: Scenario '{scenario}' or flow '{flow_name}' not found in the dictionary.")


def create_scenario_dataframes_contributions(x, impact_categories_names, scen_list, subprocesses_list) -> dict:
    subprocesses, categories, scenarios, years = x.shape
    if len(impact_categories_names) != categories or len(scen_list) != scenarios or len(subprocesses_list) != subprocesses:
        raise ValueError("Mismatch between array dimensions and provided category/scenario/sub_processes lists")

    scenario_dfs = {}

    # Loop over each scenario index
    for i, scenario in enumerate(scen_list):
        # Extract data for the current scenario (shape: categories x years)
        scenario_data = x[:, :, i, :]

        # Transpose so years become rows and categories become columns
        df = pd.DataFrame(scenario_data.T, columns=impact_categories_names)

        # Store in dictionary with the scenario name as key
        scenario_dfs[scenario] = df

    return scenario_dfs


def boxplot_per_category(df, ylabel, target_dir, per_fu = ''):

    for i, column in enumerate(df.columns):

        plt.figure(figsize=(8, 6))
        sns.boxplot(y=df[column])

        # Customize the plot
        plt.ylabel(ylabel[i])
        plt.xlabel(column)

        excel_file_path = os.path.join(target_dir, f"boxplot_{column}_{per_fu}.png")

        plt.savefig(excel_file_path)


def plot_line_charts_by_category(impact, category_names, target_dir, scen_names, per_fu = ''):

    categories, scenarios, time = impact.shape

    for cat_idx in range(categories):
        plt.figure(figsize=(10, 6))

        for scen_idx in range(scenarios):
            sns.lineplot(x=range(time), y=impact[cat_idx, scen_idx], label = scen_names[scen_idx])

        plt.xlabel("Time")
        plt.ylabel(category_names[cat_idx])
        plt.legend(loc="upper left", bbox_to_anchor=(1.05, 1))
        excel_file_path = os.path.join(target_dir, f'impact_evolution_in_time_{category_names[cat_idx]}_{per_fu}.png')
        plt.savefig(excel_file_path, bbox_inches="tight")
        plt.close()


def create_dict_from_lists(my_list, my_dfs):
    """
    Create a dictionary with elements from my_list as keys and dataframes from my_dfs as values.

    :param my_list: List of keys
    :param my_dfs: List of pandas DataFrames
    :return: Dictionary mapping my_list elements to corresponding DataFrames
    """
    if len(my_list) != len(my_dfs):
        raise ValueError("Both lists must have the same length.")

    return dict(zip(my_list, my_dfs))

# def create_scenario_dataframes_fcf(x, impact_categories_names, scen_list) -> dict:
#
#     x = np.expand_dims(x, axis=0)
#
#
#     categories, scenarios, years = x.shape
#     if len(impact_categories_names) != categories or len(scen_list) != scenarios:
#         raise ValueError("Mismatch between array dimensions and provided category/scenario lists")
#
#     scenario_dfs = {}
#
#     # Loop over each scenario index
#     for i, scenario in enumerate(scen_list):
#         # Extract data for the current scenario (shape: categories x years)
#         scenario_data = x[:, i, :]
#
#         # Transpose so years become rows and categories become columns
#         df = pd.DataFrame(scenario_data.T, columns=impact_categories_names)
#
#         # Store in dictionary with the scenario name as key
#         scenario_dfs[scenario] = df
#
#     return scenario_dfs
