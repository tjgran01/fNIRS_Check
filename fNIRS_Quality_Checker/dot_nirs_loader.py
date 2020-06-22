from scipy.io import loadmat
import pandas as pd
import os

class DotNIRSLoader(object):
    def __init__(self, data_dir="../data_to_check/", data_sub_dir=""):
        self.data_dir = f"{data_dir}{data_sub_dir}"
        self.data_fnames, self.data_files = self.load_files()
        self.trigger_fnames, self.trigger_files = self.load_files(extension_to_find=".tri")


    def load_files(self, extension_to_find=".nirs"):
        """
        Combs through the self.data_dir and finds all .nirs files.

        Args:
            self.data_dir
        Returns:
            fnames(list): Names of files w/o path or file extentsion.
            files (dict): A dictionary containing all of the file data.
        """

        # find all files with .nirs extension.
        nirs_fnames = []
        for root, dirs, files in os.walk(self.data_dir):
           for fname in files:
               if fname.endswith(extension_to_find):
                   nirs_fnames.append(os.path.join(root, fname))
        if extension_to_find == ".nirs":
            return [fname[fname.rfind("/"):-5] for fname in nirs_fnames], [loadmat(f"{fname}") for fname in nirs_fnames]
        elif extension_to_find == ".tri":
            return [fname[fname.rfind("/"):-8] for fname in nirs_fnames], [pd.read_csv(f"{fname}", sep=";", names=["Time", "Index_Point", "Trigger_Value"]) for fname in nirs_fnames]


    def create_fnirs_dataframe(self, file):
        """
        Creates a pandas dataframe of the fnirs data including the time each
        sample was taken as well as event markers. Then exports that dataframe as
        a .csv file.

        Args:
            file(dict): the dictionary created from reading the .nirs file.
        Returns:
            fnirs_data(pd.DataFrame): The pandas dataframe of the fnirs data.
        """

        fnirs_data = pd.DataFrame(file["d"])

        channel_num = fnirs_data.shape[1] / 2
        col_names = []
        for indx, col in enumerate(fnirs_data.columns):
            if indx < channel_num:
                tag = "_wl1"
                col_name = f"CH_{indx}{tag}"
            else:
                tag = "_wl2"
                col_name = f"CH_{str(int(indx - channel_num))}{tag}"

            col_names.append(col_name)

        fnirs_data.columns = col_names
        fnirs_data.index.rename("Index", inplace=True)

        return fnirs_data


    def create_trigger_col(self, fname, num_rows):
        """
        Creates a trigger column for the .csv data export. Data point is 0 if
        there is no trigger during that timestep, and is an int > 0 if a trigger
        was detected.

        Args:
            fname(string): The fnirs file name, used to matcher .tri file.
            now_rows(int): How many rows (samples) the fnirs file has.
        Returns:
            col(list): The list of triggers to be added to a pd.DataFrame.
        """

        # Finds corresponding trigger file.
        trigger_fnames, trigger_files = self.load_files(extension_to_find=".tri")

        for i, tri_fname in enumerate(trigger_fnames):
            if tri_fname == fname:
                trigger_file = trigger_files[i]

        current_trigger = 0
        num_triggers = len(trigger_file["Index_Point"].tolist())

        col = []
        for x in range(num_rows):
            if current_trigger + 1 <= num_triggers:
                if x == trigger_file["Index_Point"].tolist()[current_trigger]:
                    col.append(trigger_file["Trigger_Value"].tolist()[current_trigger])

                    current_trigger += 1
                else:
                    col.append(0)
            else:
                col.append(0)

        return col
