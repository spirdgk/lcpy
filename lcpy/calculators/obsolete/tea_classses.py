import pandas as pd
import os
import numpy as np


class TEAListHolder:

    def __init__(self):
        """Initialize empty lists."""
        self.no_names_dict = {}

    def create_lca_lists(self, label, keys_no):
        no_names = []

        no_names = []

        for name, key in keys_no.items():
            no_names.append(name)

        self.no_names_dict[label] = no_names

    def get_names(self, label):
        """Return the no_names list."""
        return self.no_names_dict.get(label)
