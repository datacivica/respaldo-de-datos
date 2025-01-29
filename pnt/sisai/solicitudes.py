"""
Usage:
  solicitudes.py <file_path> [--sem=<sem>] [--downloads_path=<downloads_path>]

Arguments:
    -h --help
    
    file_path:      The path to the file that you want to process. This should be a string specifying the location of the file on your system.
   
Options:

    --sem=<sem>:               This flag is used to manage the number of concurrent connections and optimize performance. The value of <sem> represents the maximum number of simultaneous connections that the script will make to the server. This can help to prevent overloading the server and improve the speed of the scraping process.

    --downloads_path=<downloads_path>: This flag is used to specify the path where the files that are downloaded during the scraping process will be saved. The value of <downloads_path> should be a string that represents the desired file path (e.g. --downloads_path=/home/user/downloads).
    
    
"""

from scrapingArchivosSISAI import ScrapingDataFrame
from docopt import docopt


def main():
    arguments = docopt(__doc__)
    #######################################################
    ##################... Arguments Input ...##################
    #######################################################
    file_path = arguments["<file_path>"]
    sem = arguments["--sem"]
    downloads_path = arguments["--downloads_path"]
    scraping = ScrapingDataFrame(
        file_path=file_path,
        sem=sem,
        downloads_path=downloads_path,
    )
    scraping.main()


if __name__ == "__main__":
    main()
