import argparse
from sisai.scrapingArchivosSISAI import ScrapingDataFrame


def main():
    parser = argparse.ArgumentParser(
        description="Procesar un archivo y descargar adjuntos usando Scraping DataFrame. Este script toma un archivo JSON con registros SISAI y descarga los archivos adjuntos especificados."
    )
    parser.add_argument(
        "file_path",
        type=str,
        help="La ruta al archivo que desea procesar. Este archivo debe ser un JSON con registros SISAI.",
    )
    parser.add_argument(
        "-d",
        "--downloads_path",
        type=str,
        default=None,
        help="Ruta donde se guardarán los archivos descargados. Por defecto es None, lo que significa que se guardarán en el directorio actual.",
    )
    args = parser.parse_args()

    scraping = ScrapingDataFrame(
        file_path=args.file_path,
        sem=1,
        downloads_path=f"{args.downloads_path}/archivo_adjunto_sisai_{args.file_path.replace('.json','')}",
    )
    scraping.main()


if __name__ == "__main__":
    main()
