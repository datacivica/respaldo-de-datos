#######################################################
############### ORG: DataCivica ##################
#######################################################
############### Author: Basem Hamza ##################
#######################################################
#######################################################

import json
import logging
from time import sleep
import time
import zipfile
from docopt import docopt
import openpyxl
import pandas as pd
import asyncio
import nest_asyncio
from playwright.async_api import async_playwright
from playwright.async_api import Playwright
import os
import random
import re
from playwright._impl._errors import Error as PlaywrightError
from playwright._impl._errors import TimeoutError
from urllib3.exceptions import ProtocolError
from websockets.exceptions import ConnectionClosedError

#######################################################
############### logging basic Config ##################
#######################################################
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
formatter2 = logging.Formatter("%(message)s")

# Extract html logs
logger = logging.getLogger("fetch_html_logger")
file_handler = logging.FileHandler("fetch_html.log")
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
## download files logs
logger_download = logging.getLogger("download_files_logger")
file_download_handler = logging.FileHandler("download_files.log")
file_download_handler.setLevel(logging.INFO)
file_download_handler.setFormatter(formatter)
logger_download.addHandler(file_download_handler)

#######################################################
#######################################################
############... async fetch_html() ...#################
#######################################################
#######################################################

nest_asyncio.apply()


class ScrapingDataFrame:
    def __init__(
        self,
        file_path: str,
        file_format: str,
        sem: int | None,
        output_file_name: str | None,
        name: str,
        downloads_path: str | None,
        column_name: str | None,
    ):
        self.file_path = file_path
        self.file_format = file_format
        self.sem = sem if sem is not None else 10
        self.output_file_name = (
            f"{output_file_name}_{name}"
            if output_file_name is not None
            else f"output_{name}"
        )
        self.name = name
        self.downloads_path = (
            downloads_path if downloads_path is not None else "downloads"
        )
        self.column_name = (
            column_name if column_name is not None else "Dirección del anuncio"
        )
        self.index = self.load_state()

    def load_state(self) -> int:
        try:
            with open("state.json", "r") as f:
                state = json.load(f)
                return state["index"]
        except FileNotFoundError:
            return 0

    def save_state(self) -> int:
        state = {"index": self.index}
        with open("state.json", "w") as f:
            json.dump(state, f)

    def zip_folder(self, folder_path, output_path) -> None:
        with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    zipf.write(
                        os.path.join(root, file),
                        os.path.relpath(os.path.join(root, file), folder_path),
                    )

    def delete_folder(self, folder_path):
        if os.path.exists(folder_path):
            os.system(f"rm -rf {folder_path}")
            sleep(0.2)
        else:
            print("Directory does not exist.")

    async def save_df(
        self,
        # response,
        url,
        uuid,
        i,
        df: pd.DataFrame,
        csv_file,
        downloads_path,
    ):
        dfs = await self.downloadFiles(url, uuid, downloads_path, df=df)

        mode = "a" if os.path.exists(os.path.join("output", csv_file)) else "w"
        if dfs is not None:
            dfs = dfs.drop_duplicates(subset=["uuid"], keep="first")
            dfs.iloc[i : i + 1].to_csv(
                os.path.join("output", csv_file),
                mode=mode,
                header=not os.path.exists(os.path.join("output", csv_file)),
                index=False,
            )
            file_path = os.path.join("output", f"{csv_file}.xlsx")
            if not os.path.exists(file_path):
                dfs.iloc[i : i + 1].to_excel(file_path, index=False, header=True)
            else:
                book = openpyxl.load_workbook(file_path)
                sheet = book.active
                sheet.append(dfs.iloc[i].tolist())
                book.save(file_path)
            return

    async def fetch_urls(
        self,
        url,
        uuid,
        i,
        df: pd.DataFrame,
        csv_file,
        downloads_path,
        sem,
        retries=10,
    ) -> None:
        async with sem:
            await self.save_df(
                # response=response,
                url=url,
                uuid=uuid,
                i=i,
                df=df,
                csv_file=csv_file,
                downloads_path=downloads_path,
            )

            self.index += 1
            self.save_state()
            return

    async def fetch_batch_urls(self, urls, df, csv_file, sem, downloads_path) -> None:
        sem = asyncio.Semaphore(sem)
        tasks = [
            self.fetch_urls(url, uuid, i, df, csv_file, downloads_path, sem)
            for i, (uuid, url) in enumerate(urls)
        ]
        await asyncio.gather(*tasks)

    def uuidMatch(
        self,
        url,
    ) -> str:
        regex = r"detalle\/(.*)\/"
        matches = re.finditer(regex, url, re.IGNORECASE)
        match = "".join([match.group(1) for match in matches])
        return match

    # Function chromium launcher
    async def launch_browser(
        self,
        url,
        p: Playwright,
        listpaths,
        uuid,
        downloads_path,
        browser,
        df: pd.DataFrame,
        retry=0,
    ) -> pd.DataFrame:
        start_time = time.time()
        page = await browser.new_page()
        try:
            await page.goto(url, timeout=20**4)
            await page.wait_for_timeout(3000)

            label_text = await page.inner_text(
                'div:has-text("Código del expediente:") label:last-child'
            )
            if label_text != "":
                body_content = await page.inner_html("body")
                logger.info(f"Successfully fetched content for {url}")
                datos_relevantes = await page.query_selector("td.p-link2")
                if datos_relevantes:
                    try:
                        await datos_relevantes.click(timeout=10**4)
                        async with page.expect_download(
                            timeout=10**5
                        ) as relevantes_info:
                            await page.click('span.p-button-label:text("Exportar")')
                            download = await relevantes_info.value
                            file_name = download.suggested_filename
                            file_path = os.path.join(
                                f"{downloads_path}/{uuid}", file_name
                            )
                            listpaths.append(file_path)
                            await download.save_as(file_path)
                        await page.click(
                            "span.p-dialog-header-close-icon.ng-tns-c51-6.pi.pi-times"
                        )

                    except TimeoutError:
                        await self.launch_browser(
                            url=url,
                            uuid=uuid,
                            p=p,
                            listpaths=listpaths,
                            downloads_path=downloads_path,
                            df=df,
                            browser=browser,
                        )
                        logger_download.error(f" download file {file_name} from {url}")
                        pass
                else:
                    print("Element not found")

                download_elements = await page.query_selector_all(
                    "i.pi.pi-download.ng-star-inserted"
                )
                if download_elements:
                    for i, element in enumerate(download_elements):
                        try:
                            async with page.expect_download(
                                timeout=15**6
                            ) as download_info:
                                await element.click()
                                download = await download_info.value
                                # await page.wait_for_timeout(3000)
                                file_name = download.suggested_filename
                                file_path = os.path.join(
                                    f"{downloads_path}/{uuid}", file_name
                                )
                                listpaths.append(file_path)
                                await download.save_as(file_path)

                                logger_download.info(
                                    f"Successfully download file {file_name} on {file_path} with {uuid}"
                                )
                                continue
                        except TimeoutError:
                            logger_download.error(
                                f" download file {file_name} from {url}"
                            )
                            await self.launch_browser(
                                url=url,
                                uuid=uuid,
                                p=p,
                                listpaths=listpaths,
                                downloads_path=downloads_path,
                                df=df,
                                browser=browser,
                            )
                            continue

                else:
                    print("No elements found for download.")
                df["html"] = body_content
                df["Files"] = f"{listpaths}"
                await browser.close()
                if os.path.exists(f"{downloads_path}/{uuid}"):
                    self.zip_folder(
                        f"{downloads_path}/{uuid}", f"{downloads_path}/{uuid}.zip"
                    )
                    self.delete_folder(f"{downloads_path}/{uuid}")
                elapsed_time = time.time() - start_time
                print(f"Fetching took {elapsed_time:.2f} seconds")
                return df
            else:
                logger.warning(f"Error server is closed waiting 1 hour {url}")
                await asyncio.sleep(3361)
                logger.info(f"Retrying {url}")
                return await self.launch_browser(
                    url=url,
                    uuid=uuid,
                    p=p,
                    listpaths=listpaths,
                    downloads_path=downloads_path,
                    df=df,
                    browser=browser,
                )

        except TimeoutError:
            if retry < 5:
                await page.close()
                logger_download.error(
                    f" retry {retry} timeout in launch_browser from {url}"
                )
                await self.launch_browser(
                    url=url,
                    uuid=uuid,
                    p=p,
                    listpaths=listpaths,
                    downloads_path=downloads_path,
                    df=df,
                    retry=retry + 1,
                    browser=browser,
                )
            else:
                logger_download.error(f" abandoned after 5 retries {url}")
                return

    # Function asyncio to process URLs for Download files
    async def downloadFiles(
        self, url, uuid, downloads_path, df, retries=10
    ) -> pd.DataFrame:
        listpaths = []
        attempt = 0

        async with async_playwright() as p:
            while attempt < retries:
                try:
                    browser = await p.chromium.launch(headless=True, timeout=10**6)
                    return await self.launch_browser(
                        url=url,
                        uuid=uuid,
                        p=p,
                        listpaths=listpaths,
                        downloads_path=downloads_path,
                        df=df,
                        browser=browser,
                    )
                except ProtocolError as e:
                    print(
                        "The server closed the connection unexpectedly. Please try again later."
                    )
                    attempt += 1
                    logger_download.error(
                        f"Error fetching {url} (attempt {attempt}): {e}"
                    )
                    sleep_time = 1800 * (2 ** (attempt - 1)) + random.uniform(0, 0.1)
                    await asyncio.sleep(sleep_time)
                    return await self.launch_browser(
                        url=url,
                        uuid=uuid,
                        p=p,
                        listpaths=listpaths,
                        downloads_path=downloads_path,
                        df=df,
                        browser=browser,
                    )

                except TimeoutError:
                    logger_download.error(f" timeout in downloadFile from {url}")
                    await self.launch_browser(
                        url=url,
                        uuid=uuid,
                        p=p,
                        listpaths=listpaths,
                        downloads_path=downloads_path,
                        df=df,
                        browser=browser,
                    )
                    continue
                except PlaywrightError as e:
                    if "net::ERR_NAME_NOT_RESOLVED" in str(e):
                        print(
                            "Unable to resolve the URL. Please check the URL or your network connection."
                        )
                        attempt += 1
                        logger_download.exception(
                            f"Error fetching {url} (attempt {attempt}): {e}"
                        )
                        sleep_time = 1800 * (2 ** (attempt - 1)) + random.uniform(
                            0, 0.1
                        )
                        logger_download.info(
                            f"Retrying {url} in {sleep_time:.2f} seconds..."
                        )
                        await asyncio.sleep(sleep_time)
                        return await self.launch_browser(
                            url=url,
                            uuid=uuid,
                            p=p,
                            listpaths=listpaths,
                            downloads_path=downloads_path,
                            df=df,
                            browser=browser,
                        )
                    if "net::ERR_INTERNET_DISCONNECTED" in str(e):
                        print(
                            "ERR_INTERNET_DISCONNECTED Unable waiting until load to resolve the URL. Please check the URL or your network connection."
                        )
                        attempt += 1
                        logger_download.exception(
                            f"Error fetching {url} (attempt {attempt}): {e}"
                        )
                        sleep_time = 1800 * (2 ** (attempt - 1)) + random.uniform(
                            0, 0.1
                        )
                        logger_download.info(
                            f"Retrying {url} in {sleep_time:.2f} seconds..."
                        )
                        await asyncio.sleep(sleep_time)
                        return await self.launch_browser(
                            url=url,
                            uuid=uuid,
                            p=p,
                            listpaths=listpaths,
                            downloads_path=downloads_path,
                            df=df,
                            browser=browser,
                        )

                    else:
                        logger_download.error(f"Unhandled error fetching {url}")
                        raise e
                except (
                    ConnectionClosedError,
                    ConnectionResetError,
                    ConnectionError,
                ) as e:
                    print(
                        "The connection was closed unexpectedly. Please try again later."
                    )
                    attempt += 1
                    logger_download.exception(
                        f"Error fetching {url} (attempt {attempt}): {e}"
                    )
                    sleep_time = 1800 * (2 ** (attempt - 1)) + random.uniform(0, 0.1)
                    logger_download.info(
                        f"Retrying {url} in {sleep_time:.2f} seconds..."
                    )
                    await asyncio.sleep(sleep_time)
                    return await self.launch_browser(
                        url=url,
                        uuid=uuid,
                        p=p,
                        listpaths=listpaths,
                        downloads_path=downloads_path,
                        df=df,
                        browser=browser,
                    )

    def main(self) -> None:
        #######################################################
        #######################################################
        ##########... extract URL from dataFrame ...###########
        #######################################################
        #######################################################
        if self.file_format == "xlsx":
            df = pd.read_excel(f"{self.file_path}", sheet_name="Hoja1")
        if self.file_format == "csv":
            df = pd.read_csv(f"{self.file_path}")

        if self.column_name not in df.columns:
            raise ValueError(
                "The DataFrame does not contain a column name, please check column name."
            )
        dfs = df.iloc[self.index :]
        print(len(dfs))
        urls = dfs[self.column_name]

        #######################################################
        ############... Run Function ...#################
        #######################################################
        uuid = [self.uuidMatch(url) for url in urls]
        dfs["uuid"] = uuid

        csv_file = f"{self.output_file_name}.csv"
        if not os.path.exists("output"):
            os.makedirs("output")
        uuid_html_list = []
        for index, row in dfs.iterrows():
            uuid_html_list.append((row["uuid"], row[self.column_name]))

        retries = 10
        attempt = 0
        while attempt < retries:
            try:
                start_time = time.time()
                asyncio.run(
                    self.fetch_batch_urls(
                        uuid_html_list,
                        dfs,
                        csv_file,
                        self.sem,
                        self.downloads_path,
                    )
                )

                elapsed_time = time.time() - start_time
                return print(f"Fetching took {elapsed_time:.2f} seconds")
            except ConnectionError as e:
                if "ERR_INTERNET_DISCONNECTED" in str(e):
                    print(
                        "Unable to connect to the internet. Please check your network connection."
                    )
                    attempt += 1
                    logger_download.warning(f"Error (attempt {attempt}): {e}")
                    sleep_time = 720 * (2 ** (attempt - 1)) + random.uniform(0, 0.1)
                    print(f"Retrying  in {sleep_time:.2f} seconds...")
                    sleep(sleep_time)
                    asyncio.run(
                        self.fetch_batch_html(
                            uuid_html_list,
                            dfs,
                            csv_file,
                            self.sem,
                            self.downloads_path,
                        )
                    )
                    continue
        os.system("killall 'Chromium'")
        print(f"Session end .......o_o.........o_o.......o_o........")
        sleep(7)
