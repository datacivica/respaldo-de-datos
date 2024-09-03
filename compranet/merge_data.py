"""
Usage:
  merge_data.py <outputFolder_path> <dev_name>

Arguments:
    -h --help
    
    outputFolder_path:     Where you want to save Merge csv and xlsx files
    dev_name:              Your name 
"""

import os
import pandas as pd
from docopt import docopt

arguments = docopt(__doc__)

output_folder = arguments["<outputFolder_path>"]
dev_name = arguments["<dev_name>"]


########################################################################
########################################################################
############... Merge All output files ...#############
########################################################################
########################################################################
def merge_csv_files(directory_path):
    dataframes = []
    for root, dirs, files in os.walk(directory_path):
        files.sort(key=lambda x: os.path.getmtime(os.path.join(root, x)))
        for filename in files:
            if filename.endswith(".csv"):
                file_path = os.path.join(root, filename)
                df = pd.read_csv(file_path)
                dataframes.append(df)

    # Concatenate all DataFrames
    merged_df = pd.concat(dataframes, ignore_index=True)

    return merged_df


def main(output_folder, dev_name):
    directory_path = "outputs_folders/"
    merged_df = merge_csv_files(directory_path)

    if not os.path.exists(os.path.join(f"{output_folder}/")):
        os.makedirs(os.path.join(f"{output_folder}"))

    merged_df.to_csv(
        f"{output_folder}/Expedientes_PICompraNet2024_{dev_name}.csv", index=False
    )
    merged_df.to_excel(
        f"{output_folder}/Expedientes_PICompraNet2024_{dev_name}.xlsx", index=False
    )
    print("Finish merging all files")


if __name__ == "__main__":
    main(output_folder=output_folder, dev_name=dev_name)
