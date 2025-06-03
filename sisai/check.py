import pandas as pd
from os import listdir
from os.path import isfile, join
import argparse


def check(args):

    df = pd.read_json(f"{args.json}", lines=True)
    df = df.iloc[args.index : args.current_index]

    def replaceIdentifier(x: str):
        newx = (
            x.replace("FED-IP-", "")
            .replace("CDMX-IP-", "")
            .replace("SLP-IP-", "")
            .replace("DGO-IP-", "")
            .replace("SLP-IP-", "")
            .replace("SIN-IP-", "")
            .replace("QROO-IP-", "")
            .replace("MEX-IP-", "")
            .replace("PUE-IP-", "")
            .replace("GRO-IP-", "")
            .replace("HGO-IP-", "")
            .replace("JAL-IP-", "")
            .replace("MOR-IP-", "")
            .replace("CHIS-IP-", "")
            .replace("GTO-IP-", "")
            .replace("COL-IP-", "")
            .replace("VER-IP-", "")
            .replace("QRO-IP-", "")
            .replace("TLAX-IP-", "")
            .replace("YUC-IP-", "")
            .replace("SON-IP-", "")
            .replace("MICH-IP-", "")
        )
        return newx

    onlyfiles = [
        f for f in listdir(f"{args.folder}") if isfile(join(f"{args.folder}", f))
    ]
    list_file2 = [x.replace(".zip", "") for x in onlyfiles]
    df["archivo_faltan"] = df["folio_unico"].apply(
        lambda x: "archivo_faltan" if replaceIdentifier(x) not in list_file2 else None
    )
    df = df[df["archivo_faltan"].notnull()]
    df.to_json(
        f"{args.json.replace('.json','')}_faltan.json",
        lines=True,
        orient="records",
        index=False,
        force_ascii=False,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check differences between two lists")
    parser.add_argument("json", type=str, help="json list to compare")
    parser.add_argument("folder", type=str, help="folder list to compare")
    parser.add_argument("index", type=int, help="index to start check")
    parser.add_argument("current_index", type=int, help="current index to check")
    args = parser.parse_args()
    check(args)
