from pyDataverse.api import DataAccessApi
from pyDataverse.api import NativeApi
from pyDataverse.Croissant import Croissant
import json

host = "https://dataverse.nl" 
doi = "doi:10.34894/GJKOCJ"
croissant = Croissant(doi=doi, host=host)
record = croissant.get_record()
print(record) #, indent=4, default=str))
