import os
import csv

class PrintLogger(object):
    def __init__(self, export_dir="./exports/", export_suffix="channel_reading_log.txt"):
        self.export_dir = export_dir
        self.export_suffix = export_suffix


    def print_and_export(self, string):
        """
        Prints a string to console and writes it to an output log file.

        Args:
            string: message to display.
        Returns:
            None
        """


        self.export_file.write(string)
        self.export_file.write("\n")
        print(string)


    def setup_export_file(self, fname):
        """
        Creates an export file for application to write log messages to.

        Args:
            fname(string): name of file to be written.
        Returns:
            None
        """

        if not os.path.exists(f"../exports/{fname}"):
            os.mkdir(f"../exports/{fname}")

        self.export_file = open(f"../exports/{fname}/{fname}_{self.export_suffix}", "w")


    def close_export_file(self):
        """
        Closes export file object.

        Args:
            None
        Returns:
            None
        """

        self.export_file.close()


    def print_formatted_message(self, message):
        """Prints message with some visual pagebreaks

        Args:
            message(string): What to print to console / write to logfile.
        Returns:
            None.
        """

        self.print_and_export("----------------------")
        self.print_and_export(message)
        self.print_and_export("----------------------\n")


    def create_csv(self, csv_data, fname):

        if not os.path.exists(f"../exports/csv_exports/"):
            os.mkdir(f"../exports/csv_exports/")

        with open(f"../exports/csv_exports/{fname}.csv", "w") as out_csv:
            writer = csv.writer(out_csv, delimiter=",")

            for row in csv_data:
                writer.writerow(row)
