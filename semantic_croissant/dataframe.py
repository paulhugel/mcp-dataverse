import io
import pandas as pd
from pyDataverse.api import DataAccessApi
from pyDataverse.api import NativeApi
from pyDataverse.Croissant import Croissant
import requests
import json
import polars as pl
import zipfile
import os
import pydoi
import urllib.parse

class CroissantRecipe:
    def __init__(self, doi, file=None, host=None, debug=False):
        self.doi = doi
        if not host:
            self.host = self.resolve_doi(doi)
        else:
            self.host = host
        print(f"Host is {self.host}")
        self.debug = debug
        self.columns = {}
        self.descriptive_statistics = {}
        self.serializable_columns = {}
        self.files = {}

    def get_one_croissant(self):
        print(f"Getting croissant for {self.doi} on {self.host}")
        return Croissant(doi=self.doi, host=self.host)

    def get_files(self):
        self.native_api = NativeApi(self.host)
        self.resp = self.native_api.get_dataset(self.doi)
        self.datafiles = self.resp.json()["data"]["latestVersion"]["files"]
        self.files = {df["dataFile"]["filename"]: df["dataFile"]["id"] for df in self.datafiles}
        return self.datafiles

    def resolve_doi(self, doi_str):
        doi = pydoi.get_url(urllib.parse.quote(doi_str.replace("doi:", "")))
        if 'http' in doi:
            return f"{urllib.parse.urlparse(doi).scheme}://{urllib.parse.urlparse(doi).hostname}"
        else:
            print(f"DOI is {doi}")
            return None

    # Let's dig further and display the available files
    def get_datafiles(self):
        native_api = NativeApi(self.host)
        resp = native_api.get_dataset(self.doi)
        datafiles = resp.json()["data"]["latestVersion"]["files"]
        return datafiles

    def dataexport(self, datafile_id, format="csv"):
        if format == "csv":
            return self.datapandas(datafile_id)
        elif format == "json":
            return self.datapandas(datafile_id).to_json()
        elif format == "parquet":
            return self.datapandas(datafile_id).to_parquet()
        else:
            return None

    def file_reader(self, content_type, content):
        polars_df = None
        if 'text/tab-separated-values' in content_type.lower():
            polars_df = pl.read_csv(content, separator="\t")
        if 'text/csv' in content_type.lower():
            polars_df = pl.read_csv(content) #, separator="\t")
        if 'text/plain' in content_type.lower():
            polars_df = pl.read_csv(content, separator="\t")
        if 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' in content_type.lower():
            polars_df = pl.read_excel(content)
        if 'application/json' in content_type.lower():
            polars_df = pl.read_json(content)
        return polars_df

    # To download data, we need the DataAccess API
    def datapandas(self, datafile_id):
        da_api = DataAccessApi(self.host)
        polars_df = None

        # Download the datafile
        resp = requests.get(f"{self.host}/api/access/datafile/{datafile_id}")

        # Check the content type to determine how to handle the response
        content_type = resp.headers.get('Content-Type', '')
        if 'application/zip' in content_type.lower():
            TMPDIR = f"/tmp/{datafile_id}"
            print(f"Zip file {datafile_id}")
            with zipfile.ZipFile(io.BytesIO(resp.content), 'r') as zip_ref:
                zip_ref.extractall(TMPDIR)
            for file in os.listdir(TMPDIR):
                if file.endswith(".txt"):
                    polars_df = pl.read_csv(f"{TMPDIR}/{file}", separator="\t")
                if file.endswith(".tsv"):
                    polars_df = pl.read_csv(f"{TMPDIR}/{file}", separator="\t")
                if file.endswith(".tab"):
                    polars_df = pl.read_csv(f"{TMPDIR}/{file}", separator="\t")
                if file.endswith(".csv"):
                    polars_df = pl.read_csv(f"{TMPDIR}/{file}", separator="\t")
                if file.endswith(".xlsx") or file.endswith(".xls"):
                    polars_df = pl.read_excel(f"{TMPDIR}/{file}")
                if file.endswith(".json"):
                    polars_df = pl.read_json(f"{TMPDIR}/{file}")
        elif 'octet-stream' in content_type.lower():
            print(f"Octet stream {datafile_id}")
            #polars_df = pl.read_csv(resp.content, separator="\t")
        else:   
            try:
                polars_df = self.file_reader(content_type, resp.content)
            except Exception as e:
                print(f"Failed to read {datafile_id}: {e}")
                polars_df = None

        if polars_df is not None:
            self.local_columns = {}
            for col in polars_df.columns:
                self.local_columns[col] = polars_df[col].dtype
            if self.local_columns:
                self.columns[datafile_id] = self.local_columns
            if polars_df is not None:
                self.descriptive_statistics[datafile_id] = polars_df.describe()
        #self.serializable_columns = {k: {col: str(v) for col, v in self.columns[datafile_id].items()} for k, v in self.columns.items()}
        return polars_df

    def process_all_files(self, filefilter=None):
        datafiles = self.get_datafiles()
        for df in datafiles:
            filename = df["dataFile"]["filename"]
            datafile_id = df["dataFile"]["id"]
            self.files[filename] = datafile_id
            if filefilter is not None:
                if filefilter not in filename:
                    continue
            #if self.debug:
            print(f'Filename is "{filename}", datafile ID is "{datafile_id}"')
            if self.datapandas(datafile_id) is None:
                if self.debug:
                    print(f"Failed to read {filename}")
            else:
                print(self.datapandas(datafile_id).head(5))
        return self.columns, self.descriptive_statistics

# Establish API connection and retrieve content of the dataset
host = "https://dataverse.nl" 
doi = "doi:10.34894/GJKOCJ"
doi = "doi:10.7910/DVN/SR0IQI"
filefilter = "1.CODEBOOK.xlsx"
ACTION = "get_files1"
#ACTION = "get_croissant1"

# Initialize the class
semantic_croissant = CroissantRecipe(doi)
if ACTION == "get_files":
    semantic_croissant.get_files()

    # Process all files
    semantic_croissant.process_all_files(filefilter)
    serializable_columns = {k: {col: str(v) for col, v in v.items()} for k, v in semantic_croissant.columns.items()}
    #print(json.dumps(serializable_columns, indent=4))
    print(semantic_croissant.descriptive_statistics)
elif ACTION == "get_croissant":
    croissant = semantic_croissant.get_one_croissant()
    record = croissant.get_record()
    #print(json.dumps(record, indent=4))
    print(record)