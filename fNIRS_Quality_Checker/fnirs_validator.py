import pandas as pd
import math
from scipy.stats import variation

from dot_nirs_loader import DotNIRSLoader
from print_logger import PrintLogger

class ChannelValidator(object):
    def __init__(self, signal_threshold=0.7, chunk_size=120, detrend_data=False,
                 sample_rate=5, **kwargs):
        self.signal_threshold = signal_threshold
        self.chunk_size = chunk_size
        self.sample_rate = sample_rate
        self.detrend_data = detrend_data
        self.logger = PrintLogger()

        if len(kwargs):
            self.reader = DotNIRSLoader(data_sub_dir=kwargs["data_sub_dir"])
        else:
            self.reader = DotNIRSLoader()

        self.run_validation()


    def chunk_and_validate(self, fnirs_data, fname):

        step = self.chunk_size * self.sample_rate
        chunk_num = math.ceil(fnirs_data.shape[0] / (self.chunk_size * self.sample_rate))

        invalid_channels = []
        valid_channels = []
        row_data = [["Channel_Number", "Sample_Chunk", "CV"]]

        for chunk in range(chunk_num):
            data_chunk = fnirs_data[chunk * step:chunk * step + step]
            channel_cvs = variation(data_chunk)

            for indx, cv in enumerate(channel_cvs):
                if cv > self.signal_threshold:
                    msg = f"Channel value: ({indx}) is above the acceptable threshold at sample section: {chunk * step} to {chunk * step + step}"
                    invalid_channels.append([indx, chunk * step])
                    row_data.append([indx , chunk * step, cv])
                else:
                    msg = None
                    valid_channels.append([indx, chunk * step])

                if msg:
                    self.logger.print_and_export(msg)

        self.logger.print_formatted_message(f"Summary of file: {fname}")
        self.logger.print_and_export("Total Channels : {0}".format(len(channel_cvs)))
        self.logger.print_and_export("Validity Threshold : {0}".format(self.signal_threshold))
        self.logger.print_and_export(("Proportion acceptable : {0}".format(round(len(valid_channels)/(len(valid_channels) + len(invalid_channels)), 3))))
        self.logger.print_and_export(f"{len(valid_channels)} samples have acceptable signal quality.")
        self.logger.print_and_export(f"{len(invalid_channels)} samples have inadequate signal quality.")

        self.logger.create_csv(row_data, fname)
        self.logger.close_export_file()



    def run_validation(self):

        for i, fname in enumerate(self.reader.data_fnames):
            self.logger.setup_export_file(fname[1:])
            self.logger.print_formatted_message(f"Channel signal checking for file: {self.reader.data_fnames[i][1:]}")
            fnirs_data = self.reader.create_fnirs_dataframe(self.reader.data_files[i])
            self.chunk_and_validate(fnirs_data, fname)

            self.export_fnirs_csv(fnirs_data, self.reader.data_files[i]['t'], fname)


    def export_fnirs_csv(self, fnirs_data, time_series, fname, append_meta_data=True):
        """
        Exports fnirs data as .csv file.

        Args:
            fnirs_data(pd.DataFrame): DataFrame object of fnirs data.
            fname(string): The name of the the exported file.
        Args (Optional):
            append_meta_data(bool): True if meta data columns should be added.
        Returns:
            None.
        """

        fnirs_data["time"] = time_series
        # Worry on this later.
        # fnirs_data["triggers"] = self.create_trigger_col(fname, fnirs_data.shape[0])

        fnirs_data.to_csv(f"../exports/{fname[1:]}/{fname[1:]}.csv")


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

        for i, tri_fname in enumerate(self.reader.trigger_fnames):
            if tri_fname == fname:
                trigger_file = self.reader.trigger_files[i]

        start_trigger = trigger_file['Index_Point'].tolist()[0]
        end_trigger = trigger_file['Index_Point'].tolist()[-1]

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

        return col, start_trigger, end_trigger


cv = ChannelValidator()
