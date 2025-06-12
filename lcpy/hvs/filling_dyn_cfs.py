import pandas as pd
import numpy as np
from ..calculators.bw_int import mpLCAer


def calculate_fcf(file_path, sheet_name, category, name_for_saving, configuration_dictionary, return_array = False):
    df = pd.read_excel(file_path, sheet_name=sheet_name)
    df.fillna(0, inplace=True)
    bio_dict = dict(zip(df.iloc[:, 0], df.iloc[:, 1]))
    char_factors = df.iloc[:, 2:].values

    temp_lcaer = mpLCAer(1, [category], configuration_dictionary)
    temp_lcaer.import_isolated_environment()

    characterization_matrixes, gen_bio_dict = temp_lcaer.derive_char_matrixes_for_one_category()

    num_cat = len(characterization_matrixes)
    for cat in range(num_cat):

        char_mat = characterization_matrixes[cat]
        char_mat_array_raveled = char_mat.sum(axis=1).A
        for i in range(len(char_mat_array_raveled)):
            if char_factors[i, 0] == 0:
                char_factors[i, :] = char_mat_array_raveled[i, 0]

    np.save(f"FCF_{name_for_saving}.npy", char_factors)
    data_array_df = pd.DataFrame(char_factors)
    with pd.ExcelWriter(f"FCF_{name_for_saving}.xlsx") as writer:
        data_array_df.to_excel(writer, sheet_name= f"FCF_{name_for_saving}", index=False)

    if return_array:
        return char_factors


def calculate_icf(file_path, sheet_name, category, name_for_saving, configuration_dictionary, return_array = False):

    df = pd.read_excel(file_path, sheet_name=sheet_name)
    df.fillna(0, inplace=True)

    bio_dict = dict(zip(df.iloc[:, 0], df.iloc[:, 1]))
    char_factors = df.iloc[:, 2:].values

    temp_lcaer = mpLCAer(1, [category], configuration_dictionary)
    temp_lcaer.import_isolated_environment()

    characterization_matrixes, gen_bio_dict = temp_lcaer.derive_char_matrixes_for_one_category()
    num_cat = len(characterization_matrixes)

    for cat in range(num_cat):

        char_mat = characterization_matrixes[cat]
        char_mat_array_raveled = char_mat.sum(axis=1).A
        for i in range(len(char_mat_array_raveled)):
            if char_factors[i, 0] == 0:
                char_factors[i, 0] = char_mat_array_raveled[i, 0]
                char_factors[i, -1] = 20598

    np.save(f"ICF_{name_for_saving}.npy", char_factors)
    data_array_df = pd.DataFrame(char_factors)
    with pd.ExcelWriter(f"ICF_{name_for_saving}.xlsx") as writer:
        data_array_df.to_excel(writer, sheet_name=f"ICF_{name_for_saving}", index=False)

    if return_array:
        return char_factors