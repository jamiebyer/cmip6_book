import json
import os
import re

#import dash
#import dash_bootstrap_components as dbc
#import dash_core_components as dcc
#import dash_html_components as html
import numpy as np
import xarray as xr
import plotly.graph_objects as go
from plotly.subplots import make_subplots
#from dash.dependencies import Input
#from dash.dependencies import Output
#from dash.exceptions import PreventUpdate

from cmip6_dash.src.case_utils import join_members
from cmip6_dash.src.plot_utils import plot_member_line_comp
from cmip6_dash.src.plot_utils import plot_model_comparisons
from cmip6_dash.src.plot_utils import plot_year_plotly
from cmip6_dash.src.wrangling_utils import dict_to_dash_opts
from cmip6_dash.src.wrangling_utils import get_cmpi6_model_run
from cmip6_dash.src.wrangling_utils import get_esm_datastore
from cmip6_dash.src.wrangling_utils import get_experiment_key
from cmip6_dash.src.wrangling_utils import get_model_key
from cmip6_dash.src.wrangling_utils import get_month_and_year
from cmip6_dash.src.wrangling_utils import get_var_key


#surface air temp for one timestep: august, 20 years after

# Grabbing the ESM datastore
col = get_esm_datastore()

var_key = get_var_key()
mod_key = get_model_key()
exp_key = get_experiment_key()
# Getting the names of the cases for the dropdown
path = "cmip6_dash/cases/"
cases = os.listdir(path)
cases = [case for case in cases if re.search(r".json$", case)]
case_defs = [{"label": "Developer Mode", "value": "None"}]
for case in cases:
    case_defs.append({"label": case, "value": case})


def update_map(scenario_drop, var_drop, mod_drop, date_input, exp_drop):
    date_list = date_input.split("/")
    if scenario_drop == "None":
        xarray_dset = get_cmpi6_model_run(col, var_drop, mod_drop, exp_drop)[0]
    else:
        folder_path = path + scenario_drop.split(".")[0]
        xarray_dset = xr.open_dataset(f"{folder_path}/{mod_drop}_{var_drop}.nc")

    fig = plot_year_plotly(
        xarray_dset,
        var_drop,
        mod_drop,
        month=date_list[1],
        year=date_list[0],
        exp_id=exp_drop,
    )
    full_var_name = var_key[var_drop]["fullname"]
    title = f"Heatmap of {full_var_name} on {date_list[0]}/{date_list[1]} \
     for {exp_drop} run of {mod_drop}"
    return fig, title



def main():
    var_drop_options=dict_to_dash_opts(var_key)
    mod_drop_options=dict_to_dash_opts(mod_key)
    exp_drop_options=dict_to_dash_opts(exp_key)
    scenario_drop_options = case_defs

    var_drop = var_drop_options[0]['value'] #tas
    exp_drop = exp_drop_options[0]['value'] #historical
    scenario_drop = scenario_drop_options[6]['value'] #pi_bc_case_mult
    date_input = "1870/08"

    mod_drop1 = mod_drop_options[3]['value'] #"CNRM-CM6-1-HR"
    mod_drop2 = mod_drop_options[4]['value'] #"NorESM2-MM"
    mod_drop3 = mod_drop_options[5]['value'] #"CESM2-WACCM"
    mod_drop4 = mod_drop_options[6]['value'] #"IITM-ESM"

    fig1_dict = update_map(scenario_drop, var_drop, mod_drop1, date_input, exp_drop)
    fig2_dict = update_map(scenario_drop, var_drop, mod_drop2, date_input, exp_drop)
    fig3_dict = update_map(scenario_drop, var_drop, mod_drop3, date_input, exp_drop)
    fig4_dict = update_map(scenario_drop, var_drop, mod_drop4, date_input, exp_drop)

    '''
    fig1 = go.Figure(data=fig1_dict[0]['data'], layout=fig1_dict[0]['layout'])
    fig2 = go.Figure(data=fig2_dict[0]['data'], layout=fig2_dict[0]['layout'])
    fig3 = go.Figure(data=fig3_dict[0]['data'], layout=fig3_dict[0]['layout'])
    fig4 = go.Figure(data=fig4_dict[0]['data'], layout=fig4_dict[0]['layout'])
    
    fig = make_subplots(rows=2, cols=2)
    fig.add_trace(fig1['data'][0], row=1, col=1)
    fig.add_trace(fig1['data'][1], row=1, col=1)
    fig.add_trace(fig1['data'][2], row=1, col=1)
    fig.add_trace(fig2['data'][0], row=1, col=2)
    fig.add_trace(fig3['data'][0], row=2, col=1)
    fig.add_trace(fig4['data'][0], row=2, col=2)
   '''
    #fig1 = go.Figure(data=fig1_dict[0]['data'], layout=fig1_dict[0]['layout'])
    fig1 = go.Figure(data=fig1_dict[0]['data'], layout=fig1_dict[0]['layout'])
    fig2 = go.Figure(data=fig2_dict[0]['data'], layout=fig2_dict[0]['layout'])
    fig3 = go.Figure(data=fig3_dict[0]['data'], layout=fig3_dict[0]['layout'])
    fig4 = go.Figure(data=fig4_dict[0]['data'], layout=fig4_dict[0]['layout'])

    fig1.update_layout(margin={"r": 10, "t": 50, "l": 10, "b": 10})
    fig2.update_layout(margin={"r": 10, "t": 50, "l": 10, "b": 10})
    fig3.update_layout(margin={"r": 10, "t": 50, "l": 10, "b": 10})
    fig4.update_layout(margin={"r": 10, "t": 50, "l": 10, "b": 10})

    fig1.write_image("plot_dir/pi_bc_mult1.png")
    fig2.write_image("plot_dir/pi_bc_mult2.png")
    fig3.write_image("plot_dir/pi_bc_mult3.png")
    fig4.write_image("plot_dir/pi_bc_mult4.png")


if __name__ == "__main__":
    main()
