from scrapingDataFramepntSIPOT import ScrapingDataFramePnt
import argparse


YELLOW = "\033[93m"
NEON_GREEN = "\033[92m"
RESET_COLOR = "\033[0m"


def main(args):

    #######################################################
    ##################... Arguments Input ...##################
    #######################################################

    scraping = ScrapingDataFramePnt(
        id_sujeto_obligado=args.idSujetoObligado,
        nombre_del_sujeto=args.nombreSujeto,
        ano_de_empezar=args.ano_de_empezar,
        ano_de_terminal=args.ano_de_terminal,
        obligacion=args.idObligacion,
        colaboradora=args.colaboradora,
        hash_file_id=args.hashFileId,
    )
    scraping.main()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument(
        "--idSujetoObligado",
        required=True,
        type=str,
        help=f"""ID de hash de sujeto obligatorio, por favor revise los filtros antes de continuar\n 
        {YELLOW}Ejemplo: Ej0QcqjZqYSP04SKbKxVCw== es la Secretaria de Salud - (CDMX)"""
        + RESET_COLOR,
    )
    parser.add_argument(
        "--idObligacion",
        required=False,
        # type=str,
        help=f"""ID de hash de Entidad Federativa, por favor revise los filtros antes de continuar\n
        {YELLOW}Ejemplo: jLQwlFupM__ggUxKF26A3g==	es Padrón de personas físicas y morales que cumplen obligaciones"""
        + RESET_COLOR,
    )
    parser.add_argument(
        "--ano_de_empezar",
        required=True,
        # type=int,
        help=f"""Es un numero de cuatro digitos\n
        {YELLOW}Ejemplo: 2024"""
        + RESET_COLOR,
    )
    parser.add_argument(
        "--ano_de_terminal",
        required=False,
        # type=int,
        help=f"""Es un numero de index de empesar\n
        {YELLOW}Ejemplo: 2024"""
        + RESET_COLOR,
    )

    parser.add_argument("--nombreSujeto", type=list, help="Nombre de Sujeto")

    parser.add_argument("--colaboradora", type=str, help="Nombre de la colaboradora")
    parser.add_argument(
        "--hashFileId", type=str, required=True, help="hash file name SHA(256)"
    )

    args = parser.parse_args()
    print(f"Running command")
    main(args=args)
