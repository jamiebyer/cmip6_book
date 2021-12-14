from pathlib import Path

import fsspec
import intake
import xarray as xr
import matplotlib.pyplot as plt

#surface air temp for one timestep: august, 20 years after
#get esm datastore
csv_filename = "pangeo-cmip6.csv"
root = "https://storage.googleapis.com/cmip6"
if Path(csv_filename).is_file():
    print(f"found {csv_filename}")
else:
    print(f"downloading {csv_filename}")
    data_read.download(csv_filename, root=root)
json_filename = "https://storage.googleapis.com/cmip6/pangeo-cmip6.json"
data_store = intake.open_esm_datastore(json_filename)

var_id = "tas"
mod_id = "CNRM-CM6-1-HR"
exp_id = "historical"
members = 1
monthly_table = "Amon"
year = "1870"
month = "08"

# Querying datastore to get xarr file
query_variable_id = dict(
    experiment_id=[exp_id],
    source_id=mod_id,
    table_id=[monthly_table],
    variable_id=[var_id],
)

datasets = data_store.search(**query_variable_id)

dsets = []
# Getting the member number for the each experiment
for member_num in range(members):
    member_ids = datasets.df["member_id"][member_num]
    dstore_filename = datasets.df.query("member_id==@member_ids")["zstore"].iloc[0]
    dsets.append(
        xr.open_zarr(fsspec.get_mapper(dstore_filename), consolidated=True)
    )

xarray_dset = dsets[0]

#print(xarray_dset)

start_date = year + "-" + month + "-" + "14"
end_date = year + "-" + month + "-" + "17"

var_data = xarray_dset[var_id].sel(time=slice(start_date, end_date))[0, :, :]

if "member_num" in var_data.dims:
    var_data = var_data.sel(member_num=0)

var_df = var_data.to_dataframe().reset_index()
var_df["lon_adj"] = var_df["lon"].apply(lambda x: x - 360 if x > 180 else x)

var_df = var_df[((var_df['lon_adj'] <= -114.068333) & (var_df['lon_adj'] >= -139.05))]
var_df = var_df[((var_df['lat'] <= 60) & (var_df['lat'] >= 49))]

plt.tricontourf(var_df['lon_adj'], var_df['lat'], var_df['tas'])
#plt.scatter(var_df['lat'], var_df['lon'], c=var_df['tas'])
#plt.xlim([-139.05, -114.068333])
#plt.ylim([49, 60])
plt.title("Near-Surface Air Temperature 1870-08 CNRM-CM6-1-HR")
plt.show()

#fig = px.scatter(df, x="lon", y="lat", color=var_id, opacity=0)
#fig.show()


'''
var_id: "tas"
mod_id_list: "CNRM-CM6-1-HR", "NorESM2-MM", "CESM2-WACCM", "IITM-ESM"
exp_id: "historical",
members: 1,
start_date: "1850-01",
end_date: "1950-01",
top_left: [
    60,
    -139.05
],
bottom_right: [
    49,
    -114.068333
]
'''