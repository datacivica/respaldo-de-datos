"""
Usage:
  main.py <file_path> <file_format> <name> [--sem=<sem>] [--output_file_name=<output_file_name>] [--downloads_path=<downloads_path>] [--col=<column_name>]

Arguments:
    -h --help
    
    file_path:      The path to the file that you want to process. This should be a string specifying the location of the file on your system.

    file_format:    The format of the file you are working with. This should be either 'csv' or 'xlsx', indicating whether the file is a comma-separated values file or an Excel spreadsheet.
    
    name:           Name for reference
Options:

    --sem=<sem>:               This flag is used to manage the number of concurrent connections and optimize performance. The value of <sem> represents the maximum number of simultaneous connections that the script will make to the server. This can help to prevent overloading the server and improve the speed of the scraping process.
    
    --col=<column_name>:       This flag is used the name of the urls column in pandas DataFrame.

    --output_file_name=<output_file_name>:   This flag is used to specify the name of the output data file. The value of <csv> should be a string that represents the desired name of the output file, including the file extension (e.g. --output_file_name=my_data.csv).

    --downloads_path=<downloads_path>: This flag is used to specify the path where the files that are downloaded during the scraping process will be saved. The value of <downloads_path> should be a string that represents the desired file path (e.g. --downloads_path=/home/user/downloads).
    
"""

from scrapingDataFrame import ScrapingDataFrame
from docopt import docopt


def main():
    arguments = docopt(__doc__)
    #######################################################
    ##################... Arguments Input ...##################
    #######################################################
    file_path = arguments["<file_path>"]
    file_format = arguments["<file_format>"]
    name = arguments["<name>"]
    sem = arguments["--sem"]
    output_file_name = arguments["--output_file_name"]
    downloads_path = arguments["--downloads_path"]
    column_name = arguments["--col"]

    sem = int(sem) if sem is not None else 10
    scraping = ScrapingDataFrame(
        file_path=file_path,
        file_format=file_format,
        name=name,
        output_file_name=output_file_name,
        sem=sem,
        downloads_path=downloads_path,
        column_name=column_name,
    )
    scraping.main()


if __name__ == "__main__":
    main()
