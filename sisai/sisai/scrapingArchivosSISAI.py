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
        self.sem = sem if sem is not None else 1
        self.downloads_path = (
            downloads_path
            if downloads_path is not None
            else f"archivo_adjunto_sisai_{file_path.replace('.json','')}"
        )
        self.column_name = "archivo_adjunto"
        self.index = self.load_state()

    def load_state(self) -> int:
        try:
            with open(
                f"state_index_SISAI_{self.file_path.replace('.json','')}.json", "r"
            ) as f:
                state = json.load(f)
                return state["index"]
        except FileNotFoundError:
            return 0

    def save_state(self) -> int:
        state = {"index": self.index}
        with open(
            f"state_index_SISAI_{self.file_path.replace('.json','')}.json", "w"
        ) as f:
            json.dump(state, f)

    async def fetch_batch_urls(self, urls, df, sem, downloads_path) -> None:
        chunks = [urls[i : i + 10] for i in range(0, len(urls), 10)]
        sem = asyncio.Semaphore(sem)
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False, timeout=10**6)
            context = await browser.new_context(bypass_csp=True)
            page1 = await context.new_page()
            try:
                await page1.goto(
                    "https://google.com",
                )
                for chunk in chunks:
                    await self.fetch_urls(chunk, df, downloads_path, sem, context)
            finally:
                page1.close()
                await context.close()
                await browser.close()

    async def fetch_urls(self, chunk, df, downloads_path, sem, context) -> None:
        list_paths = []
        tasks = []
        async with sem:
            for i, url in enumerate(chunk):
                self.index += 1
                self.save_state()
                task = asyncio.create_task(
                    self.launch_browser(
                        url=url,
                        list_paths=list_paths,
                        downloads_path=downloads_path,
                        df=df,
                        context=context,
                    )
                )
                tasks.append(task)
            await asyncio.gather(*tasks)
            await asyncio.sleep(random.uniform(4, 20.9))

    # Function chromium launcher
    async def launch_browser(
        self,
        url,
        list_paths,
        downloads_path,
        context,
        df: pd.DataFrame,
    ) -> pd.DataFrame:
        page = await context.new_page()
        try:

            async with page.expect_download(timeout=10000) as download_info:
                try:
                    await page.goto(url, timeout=5000)
                    recaptcha = await page.locator(".main-container").first.is_visible(
                        timeout=30000
                    )
                    timeOutserver = await page.locator(
                        "body > div > p.message"
                    ).first.is_visible(timeout=120000)
                    while True:
                        title_text = await page.title()
                        if "error" in title_text.lower():
                            await page.reload()
                            if download_info:
                                print(f"Download info: {download_info}")
                                break
                        else:
                            break

                    while recaptcha:
                        await page.reload()
                        if download_info:
                            print(f"Download info: {download_info}")
                            break

                    while timeOutserver:
                        await page.reload()
                        if download_info:
                            print(f"Download info: {download_info}")
                            break

                except:
                    pass
                print(f"Navigated to {url}")
                download = await download_info.value
                logger_download.info(f"Download info: {download}")
                file_name = download.suggested_filename
                file_path = os.path.join(downloads_path, file_name)
                list_paths.append(file_path)

                await download.save_as(file_path)
                print(f"File downloaded and saved to {file_path}")
            await page.close()
            # return df
        except Exception:
            await page.close()
            logger_download.exception(
                f" retry Exception internet connection fails in launch_browser from {url}"
            )
            await page.close()
            await self.launch_browser(
                url=url,
                list_paths=list_paths,
                downloads_path=downloads_path,
                context=context,
                df=df,
            )

        except TimeoutError:
            await page.close()
            logger_download.error(f" retry timeout in launch_browser from {url}")
            await page.close()
            await self.launch_browser(
                url=url,
                list_paths=list_paths,
                downloads_path=downloads_path,
                context=context,
                df=df,
            )

    def main(self) -> None:
        #######################################################
        #######################################################
        ##########... extract URL from Json ...###########
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
