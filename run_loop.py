#!/usr/bin/env python

import argparse
import json
import os
import subprocess


def load_state():
    if os.path.exists("state_run_loop.json"):

        with open("state_run_loop.json", "r") as f:
            state = json.load(f)
            currentOrgano = state.get("currentOrgano")
            finishTermatico = state.get("finishTermatico")
            return {
                "currentOrgano": currentOrgano,
                "finishTermatico": finishTermatico,
            }


def save_state(finishTermatico: str, currentOrgano: str):
    state = {"finishTermatico": finishTermatico, "currentOrgano": currentOrgano}
    with open("state_run_loop.json", "w") as file:
        json.dump(state, file)


def create_commends(args):
    state = load_state()
    last_organo = state.get("currentOrgano") if state else None
    last_tematico = state.get("finishTermatico") if state else None

    organos = args.organos
    tematicos = [
        "directorio",
        "Servicios",
        "Contratos",
        "Tramites",
        "servidores_sancionados",
        "PRESUPUESTO_ANUAL",
        "EJERCICIO_PRESUPUESTO",
        "resoluciones",
        "sueldos",
        # "PADRON_BENEFICIARIOS",
    ]

    skip = True if last_organo or last_tematico else False

    for organo in organos:
        for t in tematicos:
            if skip:
                if organo == last_organo and t == last_tematico:
                    skip = False
                continue

            command = [
                "python3",
                "cli_tematicos.py",
                "-t",
                t.upper(),
                "-o",
                "%s" % organo,
                "-c",
                "abrimos",
            ]
            subprocess.run(command)
            save_state(finishTermatico=t, currentOrgano=organo)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("-o", "--organos", nargs="+", type=str, help="organos /estados")
    parser.add_argument(
        "-c", "--colaboradora", nargs="+", type=str, help="Nombre de la colaboradora"
    )
    args = parser.parse_args()
    create_commends(args=args)
