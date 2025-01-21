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
import pandas as pd
import asyncio
import nest_asyncio
from playwright.async_api import async_playwright, Browser
import os
import random
from playwright._impl._errors import Error as PlaywrightError
from playwright._impl._errors import TimeoutError

#######################################################
############### logging basic Config ##################
#######################################################
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
formatter2 = logging.Formatter("%(message)s")

## download files logs
logger_download = logging.getLogger("download_files_logger")
file_download_handler = logging.FileHandler("download_files_PNT_SISAI.log")
file_download_handler.setLevel(logging.INFO)
file_download_handler.setFormatter(formatter)
logger_download.addHandler(file_download_handler)


#######################################################
#######################################################
############... async fetch() ...#################
#######################################################
#######################################################

nest_asyncio.apply()


class ScrapingDataFrame:
    def __init__(
        self,
        file_path: str,
        sem: int | None,
        downloads_path: str | None,
    ):
        self.file_path = file_path
        self.sem = sem if sem is not None else 10
        self.downloads_path = (
            downloads_path if downloads_path is not None else "archivo_adjunto_sisai"
        )
        self.column_name = "archivo_adjunto"
        self.index = self.load_state()

    def load_state(self) -> int:
        try:
            with open("state_index_SISAI.json", "r") as f:
                state = json.load(f)
                return state["index"]
        except FileNotFoundError:
            return 0

    def save_state(self) -> int:
        state = {"index": self.index}
        with open("state_index_SISAI.json", "w") as f:
            json.dump(state, f)

    async def fetch_urls(
        self,
        url,
        df: pd.DataFrame,
        downloads_path,
        sem,
    ) -> None:
        async with sem:
            await self.downloadFiles(url, downloads_path, df=df)
            self.index += 1
            self.save_state()
            return

    async def fetch_batch_urls(self, urls, df, sem, downloads_path) -> None:
        sem = asyncio.Semaphore(sem)
        tasks = [
            self.fetch_urls(url, df, downloads_path, sem)
            for i, (url) in enumerate(urls)
        ]
        await asyncio.gather(*tasks)

    # Function chromium launcher
    async def launch_browser(
        self,
        url,
        listpaths,
        downloads_path,
        browser: Browser,
        df: pd.DataFrame,
    ) -> pd.DataFrame:
        context = await browser.new_context(bypass_csp=True)
        page = await context.new_page()
        try:

            async with page.expect_download(timeout=60000) as download_info:
                try:
                    await page.goto(url, timeout=20000)
                    recaptcha = await page.locator(".main-container").first.is_visible(
                        timeout=30000
                    )
                    print(recaptcha)
                    while recaptcha:
                        await page.reload()
                        if download_info:
                            print(f"Download info: {download_info}")
                            break

                except:
                    pass
                print(f"Navigated to {url}")
                download = await download_info.value
                print()
                logger_download.info(f"Download info: {download}")
                file_name = download.suggested_filename
                file_path = os.path.join(downloads_path, file_name)
                listpaths.append(file_path)

                await download.save_as(file_path)
                print(f"File downloaded and saved to {file_path}")

            # return df
        except Exception:
            await browser.close()
            logger_download.exception(
                f" retry Exception timeout in launch_browser from {url}"
            )
            await self.downloadFiles(url=url, downloads_path=downloads_path, df=df)

        except TimeoutError:
            await browser.close()
            logger_download.error(f" retry timeout in launch_browser from {url}")
            await self.downloadFiles(
                url=url,
                downloads_path=downloads_path,
                df=df,
            )

    # Function asyncio to process URLs for Download files
    async def downloadFiles(self, url, downloads_path, df) -> pd.DataFrame:
        listpaths = []

        async with async_playwright() as p:
            try:

                browser = await p.chromium.launch(headless=False, timeout=10**6)

                return await self.launch_browser(
                    url=url,
                    listpaths=listpaths,
                    downloads_path=downloads_path,
                    df=df,
                    browser=browser,
                )

            except TimeoutError:
                logger_download.error(f" timeout in downloadFile from {url}")
                await browser.close()
                await self.downloadFiles(
                    url=url,
                    downloads_path=downloads_path,
                    df=df,
                )
            except PlaywrightError as e:
                if "net::ERR_NAME_NOT_RESOLVED" in str(e):
                    print(
                        "Unable to resolve the URL. Please check the URL or your network connection."
                    )
                    logger_download.exception(
                        f"Error fetching ERR_NAME_NOT_RESOLVED: {e}"
                    )
                    logger_download.info(
                        f"Retrying {url} in {sleep_time:.2f} seconds..."
                    )
                    await asyncio.sleep(sleep_time)
                    return await self.launch_browser(
                        url=url,
                        listpaths=listpaths,
                        downloads_path=downloads_path,
                        df=df,
                        browser=browser,
                    )
                if "net::ERR_INTERNET_DISCONNECTED" in str(e):
                    print(
                        "ERR_INTERNET_DISCONNECTED Unable waiting until load to resolve the URL. Please check the URL or your network connection."
                    )
                    logger_download.exception(
                        f"Error fetching ERR_INTERNET_DISCONNECTED: {e}"
                    )
                    sleep_time = 100
                    logger_download.info(
                        f"Retrying {url} in {sleep_time:.2f} seconds..."
                    )
                    await asyncio.sleep(sleep_time)
                    return await self.launch_browser(
                        url=url,
                        listpaths=listpaths,
                        downloads_path=downloads_path,
                        df=df,
                        browser=browser,
                    )

                else:
                    await browser.close()
                    logger_download.error(f"Unhandled error fetching {url}")
                    return await self.downloadFiles(
                        url=url,
                        downloads_path=downloads_path,
                        df=df,
                    )
            except (
                ConnectionResetError,
                ConnectionError,
            ) as e:
                print("The connection was closed unexpectedly. Please try again later.")
                logger_download.exception(f"Error fetching ConnectionError: {e}")
                sleep_time = 100
                logger_download.info(f"Retrying {url} in {sleep_time:.2f} seconds...")
                await asyncio.sleep(sleep_time)
                return await self.launch_browser(
                    url=url,
                    listpaths=listpaths,
                    downloads_path=downloads_path,
                    df=df,
                    browser=browser,
                )

    def main(self) -> None:
        #######################################################
        #######################################################
        ##########... extract URL from JsonL ...###########
        #######################################################
        #######################################################

        df = pd.read_json(f"{self.file_path}", lines=True)

        if self.column_name not in df.columns:
            raise ValueError(
                "The DataFrame does not contain a column name, please check column name."
            )
        df = df.iloc[self.index :]

        #######################################################
        ############... Run Function ...#################
        #######################################################

        if not os.path.exists(f"{self.downloads_path}"):
            os.makedirs(f"{self.downloads_path}")
        URL_List = df[self.column_name]

        retries = 10
        attempt = 0
        while attempt < retries:
            try:
                start_time = time.time()
                asyncio.run(
                    self.fetch_batch_urls(
                        URL_List,
                        df,
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
                        self.fetch_batch_urls(
                            URL_List,
                            df,
                            self.sem,
                            self.downloads_path,
                        )
                    )
                    continue
        print(f"Session end .......o_o.........o_o.......o_o........")
