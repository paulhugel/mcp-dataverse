from pyDataverse.models import Dataset
from pyDataverse.utils import read_file
import json

ds_filename = "./dataset_upload_default_full_01.json" #dataset_upload_default_min_01.json"
ds = Dataset()
ds.from_json(read_file(ds_filename))

# Output Dataset as dict
ds.get()
#print(ds.get()["title"])
print(json.dumps(ds.get(), indent=4, default=str))
