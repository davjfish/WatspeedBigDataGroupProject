import re

import pandas as pd


def parse_911_csv(file):
    df = pd.read_csv(file)
    df["type"] = df["title"].apply(lambda x: x.split(":")[0].strip())

    def clean_title(title):
        txt = title.split(":")[-1].strip()
        if txt[-1] == "-":
            txt = txt[:-1].strip()
        return txt
    df["clean_title"] = df["title"].apply(clean_title)

    def clean_station(x):
        # seems like desc is delimited by semicolon
        desc = str(x).lower()
        desc = desc.replace("station:", "station ").replace("-station", ";station").replace("station sta", "station ")
        for item in desc.split(";"):
            if "station" in item and not re.search(r"station [ave|cr|dr|square|blvd|park|way|fire]", item) and re.search(r"station\s", item):
                txt = item.replace("station", "").strip()
                return txt if txt else "unknown"
        return "unknown"
    df["desc"] = df["desc"].apply(clean_station).value_counts()

