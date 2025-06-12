import pandas as pd
import os


def create_mapping(keys_total, key_list, number_of_infrastructural_processes = 0, tea_op = False, tea_con = False):
    """
        This function returns a dictionary where the keys are the keys of `keys_total`
        and the values are the elements of `list_with_dics`. It raises a ValueError if the lengths do not match.

        Parameters:
        - keys_total: A dictionary with string keys from keys_total of global parameters
        - list_with_dics: A list of dictionaries with the keys for each subprocess (keys_no1, keys_no2, ...)

        Returns:
        - A dictionary mapping each key from `keys_total` to the corresponding dictionary in `my_list`.

        Raises:
        - ValueError: If `keys_total` and `my_list` have different lengths.
    """
    if tea_op == False and tea_con == False:
        try:
            temp_list = [list(dictionary.values()) for dictionary in key_list]
        except:
            temp_list = key_list

        if len(keys_total) != len(temp_list):
            raise ValueError(f"Mismatch in lengths: keys_total has {len(keys_total)} keys, but my_list has {len(temp_list)} elements.")
        return dict(zip(keys_total.keys(), temp_list))

    elif tea_op == True and tea_con == False:

        keys_total = dict(list(keys_total.items())[number_of_infrastructural_processes:])
        key_list = key_list[number_of_infrastructural_processes:]

        try:
            temp_list = [list(dictionary.keys()) for dictionary in key_list]
        except:
            temp_list = key_list

        if len(keys_total) != len(temp_list):
            raise ValueError(
                f"Mismatch in lengths: keys_total has {len(keys_total)} keys, but my_list has {len(temp_list)} elements.")
        return dict(zip(keys_total.keys(), temp_list))

    elif tea_op == False and tea_con == True:

        keys_total = dict(list(keys_total.items())[:number_of_infrastructural_processes])
        key_list = key_list[:number_of_infrastructural_processes]

        try:
            temp_list = [list(dictionary.keys()) for dictionary in key_list]
        except:
            temp_list = key_list

        if len(keys_total) != len(temp_list):
            raise ValueError(
                f"Mismatch in lengths: keys_total has {len(keys_total)} keys, but my_list has {len(temp_list)} elements.")
        return dict(zip(keys_total.keys(), temp_list))



def create_list_with_unique_activities(key_list):
    """
        This function returns a list with the names of the sub_processes as defined in the keys.py file`
        Only unique names are included

        Parameters:
        - keys_total: A dictionary with string keys from keys_total of global parameters
        - list_with_dics: A list of dictionaries with the keys for each subprocess (keys_no1, keys_no2, ...)

        Returns:
        - A list with names of each sub_process used. Only unique names are included.

        Raises:
        - ValueError: If `keys_total` and `my_list` have different lengths.
    """
    my_list = []
    for item in key_list:
        x = item.keys()
        for item2 in x:
            my_list.append(item2)

    my_set = set(my_list)
    my_list = list(my_set)

    return my_list


def evaluate_same_dictionaries_in_process(my_list_dict):
    if not my_list_dict:
        print('Biosphere or technosphere Empty')

    first_dict = my_list_dict[0]
    for idx, d in enumerate(my_list_dict[1:], start=1):
        if d != first_dict:
            raise ValueError(f"Dictionaries differ at index {idx}: {d} != {first_dict}")
        else:
            print("All same")


def evaluate_same_dictionaries_between_processes(my_list_dict):

    all_dicts = [d for sublist in my_list_dict for d in sublist]

    if not all_dicts:
        # If there are no dictionaries, return True
        return True

    first_dict = all_dicts[0]
    for idx, d in enumerate(all_dicts[1:], start=1):
        if d != first_dict:
            raise ValueError(f"Dictionaries differ at index {idx}: {d} != {first_dict}")
        else:
            return d


def store_dictionaries(dict, target_dir, name):
    df = pd.DataFrame(list(dict.items()), columns=["Key", "Value"])
    file_path = os.path.join(target_dir, name)
    df.to_excel(file_path, index=False)