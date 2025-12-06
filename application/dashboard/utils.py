import re

import pandas as pd
from django.contrib import messages

from django.db import connection
from dashboard import models


class CSVParser:
    def __init__(self, file, request=None):
        self.file = file
        self.df = pd.read_csv(file)
        self.request = request

    def clean_df(self):
        # clean title
        self.df["type"] = self.df["title"].apply(lambda x: x.split(":")[0].strip())

        def _clean_title_(title):
            txt = title.split(":")[-1].strip()
            if txt[-1] == "-":
                txt = txt[:-1].strip()
            return txt

        self.df["clean_title"] = self.df["title"].apply(_clean_title_)

        # clean description and parse out station name
        def _clean_station_(x):
            # seems like desc is delimited by semicolon
            desc = str(x).lower()
            desc = desc.replace("station:", "station ").replace("-station", ";station").replace("station sta", "station ")
            for item in desc.split(";"):
                if "station" in item and not re.search(r"station [ave|cr|dr|square|blvd|park|way|fire]", item) and re.search(r"station\s", item):
                    txt = item.replace("station", "").strip()
                    return txt if txt else "unknown"
            return "unknown"

        self.df["station"] = self.df["desc"].apply(_clean_station_).value_counts()

    def add_administrative_areas(self):
        # import administrative areas
        areas = self.df.loc[:, ["zip", "twp"]].value_counts()
        create_list = list()
        for zip_code, name in areas.index:
            name = name.upper()
            try:
                zip_code = int(zip_code)
            except:
                zip_code = None
            area = models.AdministrativeArea(name=name, zip_code=zip_code)
            create_list.append(area)
        x = models.AdministrativeArea.objects.bulk_create(create_list, ignore_conflicts=True)
        messages.success(self.request, f"Added {len(x)} administrative areas.")

    def parse(self):
        self.clean_df()
        connection.ensure_connection()
        self.add_administrative_areas()
