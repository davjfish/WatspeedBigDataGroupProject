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
