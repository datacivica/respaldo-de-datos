from script_tematicos import ScrapingDataFramePnt
import argparse


YELLOW = "\033[93m"
NEON_GREEN = "\033[92m"
RESET_COLOR = "\033[0m"


def main(args):

    #######################################################
    ##################... Arguments Input ...##################
    #######################################################

    scraping = ScrapingDataFramePnt(
        anos=args.anos,
        colaboradora=args.colaboradora,
        coleccion=args.coleccion,
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
    parser.add_argument("-a", "--anos", nargs="+", type=str, help="Lista de años")
    parser.add_argument(
        "-o", "--organos", nargs="+", default=[], type=str, help="Lista de organos"
    )

    parser.add_argument(
        "-c", "--colaboradora", type=str, help="Nombre de la colaboradora"
    )
    args = parser.parse_args()
    print(f"Running command")
    main(args=args)
