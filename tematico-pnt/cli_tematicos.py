from script_tematicos import ScrapingDataFramePnt
import argparse


def main(args):

    #######################################################
    ##################... Arguments Input ...##################
    #######################################################

    scraping = ScrapingDataFramePnt(
        anos=args.anos,
        colaboradora=args.colaboradora,
        coleccion=args.coleccion.upper(),
        organos=args.organos,
    )
    scraping.main()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument(
        "-t",
        "--coleccion",
        required=False,
        help="coleccion de transparencia",
    )
    parser.add_argument(
        "-a",
        "--anos",
        nargs="+",
        default=[
            "2015",
            "2016",
            "2017",
            "2018",
            "2019",
            "2020",
            "2021",
            "2022",
            "2023",
            "2024",
            "2025",
        ],
        type=str,
        help="Lista de años",
    )
    parser.add_argument(
        "-o", "--organos", nargs="+", default=[], type=str, help="Lista de organos"
    )

    parser.add_argument(
        "-c",
        "--colaboradora",
        type=str,
        default="abrimos",
        help="Nombre de la colaboradora",
    )
    args = parser.parse_args()
    print(f"Running command")
    main(args=args)
