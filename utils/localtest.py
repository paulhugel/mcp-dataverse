import anyio
import click
import urllib
import httpx
import mcp.types as types
from mcp.server.lowlevel import Server
from fastapi.responses import StreamingResponse
from fastapi import Request, Response
from typing import Optional
import pydoi
import json
import logging
import sys

logger = logging.getLogger(__name__)

def resolve_doi_old(doi_str):
    doi = pydoi.resolve(doi_str)
    print(doi)
    if 'values' in doi: 
        for value in doi["values"]:
            if 'url' in value:
                return value["url"]
    else:
        return None

def resolve_doi( doi_str):
    doi = pydoi.get_url(urllib.parse.quote(doi_str.replace("doi:", "")))
    print(doi)
    if 'http' in doi:
        return f"{urllib.parse.urlparse(doi).scheme}://{urllib.parse.urlparse(doi).hostname}"
    else:
        print(f"DOI is {doi}")
        return None

doi = "10.21410/7E4/2OHZ44"
doi = "10.21410/7E4/2OHZ44"
doi = "doi:10.17026/AR/GEFML7"
print(resolve_doi(doi))
