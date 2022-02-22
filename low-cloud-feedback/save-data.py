import xarray as xr
import pooch
import pandas as pd
import fsspec
from pathlib import Path
import time
import numpy as np
import json

#get esm datastore
odie = pooch.create(
    path="./.cache",
    base_url="https://storage.googleapis.com/cmip6/",
    registry={
        "pangeo-cmip6.csv": "e319cd2bf1daf9b5aa531f92c022d5322ee6bce0b566ac81dfae31dbae203fd9"
    },
)

file_path = odie.fetch("pangeo-cmip6.csv")
df_og = pd.read_csv(file_path)

fs = fsspec.filesystem("filecache", target_protocol='gs', target_options={'anon': True}, cache_storage='/tmp/files/')


var_id = "cl"
mod_id = "GFDL-ESM4"
exp_id_list = ["piControl"]
monthly_table = "Amon"


for exp_id in exp_id_list:
    query = "variable_id=='"+var_id+"' & experiment_id=='"+exp_id+"' & source_id=='"+mod_id+"' & table_id=='"+monthly_table+"'"
    df = df_og.query(query)
    zstore_url = df["zstore"].values[0]
    the_mapper = fs.get_mapper(zstore_url)
    ds = xr.open_zarr(the_mapper, consolidated=True)

    ds = ds.sel(lat=slice(32, 46))
    ds = ds.sel(lon=slice(200, 243))

    spatial_mean = ds.mean(dim=["lat", "lon", "lev"])
    print(type(spatial_mean))
    times = spatial_mean.indexes["time"]
    cloud_cover = spatial_mean['cl']
    test = cloud_cover[...]
    print(test)
    print(cloud_cover)
    t0 = time.time()
    #print(cloud_cover)
    t1 = time.time()
    print(t1-t0)
