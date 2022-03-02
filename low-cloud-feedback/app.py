from os import environ

import dash
import numpy as np
import pandas as pd

import plotly.graph_objects as go
from dash import dcc, html
from dash.dependencies import Input, Output
from flask import Flask


from pathlib import Path

import json
import fsspec
#import intake
import xarray as xr
import pooch
#from pathlib import Path
import cftime
import datetime
#from dateutil.relativedelta import relativedelta
from scipy import signal

#install zarr
#install gcsfs

models_json = open('models.json')
models_dict = json.load(models_json)

# if we want to use all the models:
model_options = []
for model in models_dict["models"]:
    mod_id = model["mod_id"]
    model_options.append({"label": mod_id, "value": mod_id})

external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]

server = Flask(__name__)
app = dash.Dash(
    server=server,
    url_base_pathname=environ.get("JUPYTERHUB_SERVICE_PREFIX", "/"),
    external_stylesheets=external_stylesheets,
)


app.layout = html.Div(
    [
        dcc.Markdown(
            '''
            Low Cloud Feedback
            '''
        ),

        #select model
        html.Div(
            [
                dcc.Markdown("""Select Model: """),
                dcc.Dropdown(
                    id="model",
                    options=model_options,
                    value="CESM2",
                    #multi=True,
                ),
            ],
            style={"width": "50%", "display": "inline-block"},
        ),

        #select experiment
        html.Div(
            [
                dcc.Markdown("""Select Experiment: """),
                dcc.Dropdown(
                    id="exp",
                    options=[
                        {"label": "historical", "value": "historical"},
                        {"label": "piControl", "value": "piControl"},
                        {"label": "ssp585", "value": "ssp585"},
                    ],
                    value=["historical"],
                    multi=True,
                ),
            ],
            style={"width": "50%", "display": "inline-block"},
        ),


        #graph
        html.Div(
            [
                dcc.Graph(
                    id="graph",
                    config={
                        "displayModeBar": True,
                    },
                ),
            ],
            style={"width": "100%", "display": "inline-block",},
        ),


    ],
    style={"width": "1000px"},
)


def filter_cloud_cover(cloud_cover, n_years):
    #using average month length for now
    fs = 1/(30.437*24*60*60) #1 month in Hz (sampling frequency)
    nyquist = fs / 2 # 0.5 times the sampling frequency
    cutoff =  1/(n_years*365*24*60*60)# cutoff in Hz, n_years in Hz
    normal_cutoff = cutoff / nyquist
    
    b, a = signal.butter(5, normal_cutoff, btype='lowpass') #low pass filter
    cloud_cover_filt = signal.filtfilt(b, a, cloud_cover)
    return cloud_cover_filt

@app.callback(
    Output("exp", "options"),
    Input("model", "value"),
)
def update_dropdown(mod_id):
    options = []
    for model in models_dict["models"]:
        if model["mod_id"] == mod_id:
            for exp_id in model["exp_id"]:
                options.append({"label": exp_id, "value": exp_id})
    return options


@app.callback(
    Output("graph", "figure"),
    Input("model", "value"),
    Input("exp", "value"),
)
def update_graph(mod_id, exp_id_list):
    var_id = "cl"

    fig = go.Figure()


    for exp_id in exp_id_list:
        ds = xr.open_zarr(Path('models/'+mod_id+'_'+exp_id+'.zarr'))
        spatial_mean = ds.mean(dim=["lat", "lon", "lev"])
        times = spatial_mean.indexes["time"]
        
        '''
        if (mod_id == "GFDL-CM4") | (mod_id == "E3SM-1-0"):
            if (exp_id == "piControl"):
                times = xr.cftime_range(start="1850", periods=6000, freq="M", calendar="noleap")
                times = times.shift(-1, "M").shift(16, "D").shift(12, "H")
            elif (exp_id == "1pctCO2"):
                times = xr.cftime_range(start="1850", periods=1800, freq="M", calendar="noleap")
                times = times.shift(-1, "M").shift(16, "D").shift(12, "H")
        elif (mod_id == "MIROC6"):
            if (exp_id == "piControl") | (exp_id == "1pctCO2"):
                times = xr.cftime_range(start="1850", periods=1800, freq="M", calendar="noleap")
                times = times.shift(-1, "M").shift(16, "D").shift(12, "H")
        '''

        cloud_cover = spatial_mean[var_id].values
        cloud_cover_filt = filter_cloud_cover(cloud_cover, 10)

        fig.add_trace(go.Scatter(x=times, y=cloud_cover_filt, mode="lines", name=exp_id))
        


    fig.update_layout(title=mod_id + ", low level cloud cover, 10 year lowpass filter, eastern pacific", 
        xaxis_title="Time", yaxis_title="Percent", showlegend=True)

    #fig.update_xaxes(range=[times[0], times[-1]])

    return fig



if __name__ == "__main__":
    app.run_server(debug=True)