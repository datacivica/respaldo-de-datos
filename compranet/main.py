#######################################################
############### ORG:DataCivica ##################
#######################################################
############### Author: Basem Hamza ##################
#######################################################
#######################################################
"""
Usage:
  main.py <file_path> <file_format> <start_index> <end_index> <dev_name>

Arguments:
    -h --help
    
    file_path:     The path to the file that you want to process. This should be a string specifying the location of the file on your system.

    file_format:   The format of the file you are working with. This should be either 'csv' or 'xlsx', indicating whether the file is a comma-separated values file or an Excel spreadsheet.

    start_index:   The starting index of the range within the DataFrame from which you will begin scraping URLs. This should be an integer indicating the first row of the DataFrame to process.

    end_index:     The ending index of the range within the DataFrame where you will stop scraping URLs. This should be an integer indicating the last row of the DataFrame to process.
    
    dev_name:      Your name
    
"""
#######################################################
#######################################################

import logging
from time import sleep
from docopt import docopt
import numpy as np
import pandas as pd
import asyncio
import nest_asyncio
from requests_html import AsyncHTMLSession
import os

arguments = docopt(__doc__)
#######################################################
##################... Arguments Input ...##################
#######################################################
file_path = arguments["<file_path>"]
file_format = arguments["<file_format>"]
dev_name = arguments["<dev_name>"]
start_index = arguments["<start_index>"]
end_index = arguments["<end_index>"]
start_index = int(start_index)
end_index = int(end_index)
#######################################################
############### logging basic Config ##################
#######################################################
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("fetch_html_logger")
file_handler = logging.FileHandler("fetch_html.log")
file_handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

#######################################################
#######################################################
############... async fetch_html() ...#################
#######################################################
#######################################################

nest_asyncio.apply()


async def fetch_html(session, url):
    try:
        response = await session.get(url)
        await response.html.arender(sleep=3)
        body_content = response.html.find("body", first=True).html
        logger.info(f"Successfully fetched content for {url}")
        return body_content
    except Exception as e:
        logger.error(f"Error fetching {url}: {e}")
        body_content = f"Fetching Error"
        return body_content


async def fetch_batch_html(urls, batch_size):
    session = AsyncHTMLSession()
    tasks = [fetch_html(session, url) for url in urls[:batch_size]]
    results = await asyncio.gather(*tasks)
    await session.close()

    return results


# Function asyncio to process URLs
async def process_urls_in_batches(urls, batch_size):
    print("Session Start ..................-_-..................")
    all_results = []
    for i in range(0, len(urls), batch_size):
        batch_urls = urls[i : i + batch_size]
        print(
            f"Processing batch {i // batch_size + 1} of {(len(urls) + batch_size - 1) // batch_size}"
        )
        batch_results = asyncio.run(fetch_batch_html(batch_urls, batch_size))
        all_results.extend(batch_results)
    return all_results


def main(file_path, file_format, dev_name):
    #######################################################
    #######################################################
    ##########... extract URL from dataFrame ...###########
    #######################################################
    #######################################################
    if file_format == "xlsx":
        df = pd.read_excel(f"{file_path}", sheet_name="Sheet1")
    if file_format == "csv":
        df = pd.read_csv(f"{file_path}")

    if "Dirección del anuncio" not in df.columns:
        raise ValueError("The DataFrame does not contain a 'url' column.")

    ########################################################################
    ########################################################################
    ############... Create Chunks por 10 row for each chunk ...#############
    ########################################################################
    ########################################################################
    chunks = np.array_split(
        df.iloc[start_index:end_index], (len(df.iloc[start_index:end_index]) + 9) // 10
    )
    for i, chunk in enumerate(chunks):
        urls = chunk["Dirección del anuncio"].tolist()

        #######################################################
        ############... Run Function ...#################
        #######################################################

        html_contents = asyncio.run(process_urls_in_batches(urls, len(chunk)))

        ################# Add a new column html ##############

        chunk["html"] = html_contents

        #######################################################
        ################# Save Excel file and CSV ############
        #######################################################
        if not os.path.exists(
            os.path.join(f"outputs_folders/{start_index}_{end_index}/")
        ):
            os.makedirs(os.path.join(f"outputs_folders/{start_index}_{end_index}"))
            os.makedirs(os.path.join(f"outputs_folders/{start_index}_{end_index}/csv"))

        chunk.to_csv(
            f"outputs_folders/{start_index}_{end_index}/csv/Expedientes_PICompraNet2024_{dev_name}_output_file{i}.csv",
            index=False,
        )
        os.system("killall 'Chromium'")
        print(f"Session number {i} end .......o_o.........o_o.......o_o........")
        sleep(7)


if __name__ == "__main__":
    main(file_path=file_path, file_format=file_format, dev_name=dev_name)
