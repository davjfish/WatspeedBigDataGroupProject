import re

import numpy as np
import pandas as pd
from django.contrib import messages

from django.db import connection
from . import models


def chunkify_df(df, n):
    """
    Credit to: https://stackoverflow.com/questions/312443/how-do-i-split-a-list-into-equally-sized-chunks
    Yield successive n-sized chunks from DataFrame.
    """

    for i in range(0, df.shape[0], n):
        yield df.iloc[i:i + n, :]


class PA911CSVParser:
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

        self.df["category"] = self.df["title"].apply(_clean_title_)

        # clean description and parse out station name
        def _clean_station_(x):
            # seems like desc is delimited by semicolon
            desc = str(x).lower()
            desc = desc.replace("station:", "station ").replace("-station", ";station").replace("station sta", "station ")
            for item in desc.split(";"):
                if "station" in item and not re.search(r"station [ave|cr|dr|square|blvd|park|way|fire]", item) and re.search(r"station\s", item):
                    txt = item.replace("station", "").strip()
                    return str(txt).upper() if txt else "unknown"
            return "unknown"

        self.df["station"] = self.df["desc"].apply(_clean_station_)

    def add_townships(self):
        create_list = list()
        for item in self.df.twp.dropna().unique():
            name = item.upper()
            create_list.append(models.Township(name=name, state="PA"))
        x = models.Township.objects.bulk_create(create_list, ignore_conflicts=True)

        # create a lookup
        twp_lookup = {f"{item.name}": item.id for item in models.Township.objects.all()}
        # add back to df
        self.df["twp_id"] = self.df.twp.map(twp_lookup)
        msg = f"Added {len(x)} administrative areas."
        if self.request:
            messages.success(self.request, msg)
        else:
            print(msg)

    def add_response_types(self):
        create_list = list()
        for name in self.df.type.dropna().unique():
            create_list.append(models.ResponseType(name=name))
        x = models.ResponseType.objects.bulk_create(create_list, ignore_conflicts=True)

        rtype_lookup = {f"{item.name}": item.id for item in models.ResponseType.objects.all()}
        # add back to df
        self.df["type_id"] = self.df.type.map(rtype_lookup)
        msg = f"Added {len(x)} response types."
        if self.request:
            messages.success(self.request, msg)
        else:
            print(msg)

    def add_categories(self):
        create_list = list()
        for name in self.df.category.dropna().unique():
            create_list.append(models.Category(name=name))
        x = models.Category.objects.bulk_create(create_list, ignore_conflicts=True)

        cat_lookup = {f"{item.name}": item.id for item in models.Category.objects.all()}
        # add back to df
        self.df["category_id"] = self.df.category.map(cat_lookup)
        msg = f"Added {len(x)} response types."
        if self.request:
            messages.success(self.request, msg)
        else:
            print(msg)

    def add_units(self):
        create_list = list()
        for station, type_id in self.df.loc[:, ["station", "type_id"]].value_counts().index:
            create_list.append(models.ResponseUnit(response_type_id=type_id, station_name=station))
        x = models.ResponseUnit.objects.bulk_create(create_list, ignore_conflicts=True)
        runit_lookup = {f"{item.response_type_id}-{item.station_name}": item.id for item in models.ResponseUnit.objects.all()}
        # add back to df
        self.df["unit"] = self.df.apply(lambda x: f"{int(x.type_id)}-{x.station}", axis=1)
        self.df["unit_id"] = self.df.unit.map(runit_lookup)
        msg = f"Added {len(x)} response units."
        if self.request:
            messages.success(self.request, msg)
        else:
            print(msg)


    def add_calls(self):
        models.EmergencyCall.objects.all().delete()
        self.df.replace(np.nan, None, inplace=True)
        create_list = list()

        def _make_call_from_row_(row):
            kwargs = {
                "datetime": row.timeStamp,
                "response_unit_id": row.unit_id,
                "category_id": row.category_id,
                "township_id": row.twp_id,
                "zip_code": row.zip,
                "address": row.addr,
                "latitude": row.lat,
                "longitude": row.lng,
            }
            create_list.append(models.EmergencyCall(**kwargs))

        x = 0
        for chunk in chunkify_df(self.df, 50000):
            create_list = list()
            chunk = chunk.copy(deep=True)
            chunk.apply(_make_call_from_row_, axis=1)
            out = models.EmergencyCall.objects.bulk_create(create_list)
            print(len(out), "emergency calls created.")
            x += len(out)

        if self.request:
            messages.success(self.request, f"Added {x} emergency calls.")

    def parse(self):
        connection.ensure_connection()
        self.clean_df()
        self.add_townships()
        self.add_response_types()
        self.add_categories()
        self.add_units()
        self.add_calls()
