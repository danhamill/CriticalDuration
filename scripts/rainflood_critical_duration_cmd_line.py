import argparse
from datetime import time
import pandas as pd
import numpy as np
from pydsstools.heclib.dss import HecDss
from pydsstools.core import TimeSeriesContainer, HecTime
import altair as alt
from altair import datum
import os
from typing import Tuple
alt.data_transformers.disable_max_rows()
alt.renderers.enable("browser")


def get_flow_in_data(
    dss_file, sf, year, ds_channel_capacity, pathFlowIn, pathFlowOut, pathElev
):
    """
    Function to pull dss recoreds related to critical duration

    Args:
        dss_file ([str]): [dss path name]
        sf ([float]): [scale factor]
        year ([int]): [Analysis year]
        ds_channel_capacity ([int or float])" : Downstream channel capacity

    Returns:
        tmp [pd.DataFrame]: [Dataframe with inflow hydrograph]
        vol_event [float] : Maximum Volume for Event
    """

    sf = f"{sf:.2f}"
    assert len(str(year)) == 4, "Year must be 4 digit with format YYYY"
    assert os.path.exists(dss_file), "Cannot locate DSS file"
    print(f"{year} Hydrograph, {sf} Scale Factor.....")

    flowIn = readDssData(
        dss_file,
        pathFlowIn,
        variable="flow",
        window=("01Jan2020 01:00", "01Apr2020 01:00"),
    )
    flowOut = readDssData(
        dss_file,
        pathFlowOut,
        variable="flow",
        window=("01Jan2020 01:00", "01Apr2020 01:00"),
    )
    elev = readDssData(
        dss_file,
        pathElev,
        variable="elev",
        window=("01Jan2020 01:00", "01Apr2020 01:00"),
    )

    time_peak_stor = elev.elev.idxmax()
    print(f"Time of peak Storage {time_peak_stor}")

    # Does Channel exceed downstream constraints?
    flowOut = flowOut.loc[flowOut.flow > ds_channel_capacity, :]
    if not flowOut.empty:
        time_exceed = flowOut.index.min()
        print(f"Time of Downstream Channel Exceedance {time_exceed}")
    else:
        time_exceed = None

    if time_exceed is None:
        print("Event Volume calculated as peak in storage (normal operations)...")
        vol_event = flowIn.loc[: time_peak_stor.isoformat(), "flow"].sum() * 3600
    else:
        if time_exceed < time_peak_stor:
            print("Exceeded downstream channel capacity before peak storage...")
            vol_event = flowIn.loc[: time_exceed.isoformat(), "flow"].sum() * 3600
        else:
            print("Event Volume calculated as peak in storage...")
            vol_event = flowIn.loc[: time_peak_stor.isoformat(), "flow"].sum() * 3600

    return flowIn, vol_event


def readDssData(dss_file, path, variable, window):
    fid = HecDss.Open(dss_file)
    ts = fid.read_ts(path, window=window, trim_missing=False)
    times = ts.pytimes
    values = ts.values
    idx = pd.Index(times, name="date")
    tmp = pd.DataFrame(index=idx, data=values.copy(), columns=[variable])
    fid.close()

    return tmp


def calculate_nday_vols(df, vol_event):

    max_vols = {}

    for n_day in [1, 2, 3, 4, 5, 6, 7, 15, 30]:

        met = f"{n_day}".zfill(3) + "-day"
        df.loc[:, met] = df.flow.rolling(n_day * 24 + 1, center=True).mean()

        idx_max = df[met].idxmax()
        max_val = df[met].max()
        print(met, max_val)
        n_day_vol = max_val * 86400 * n_day

        begin_date = (idx_max - pd.DateOffset(hours=n_day * 12)).isoformat()
        end_date = (idx_max + pd.DateOffset(hours=n_day * 12)).isoformat()
        mask = (df.index >= begin_date) & (df.index < end_date)

        v_event_n_day_window = df.loc[mask, "flow"].sum() * 3600
        norm_vol = vol_event / n_day_vol
        norm_vol = int(norm_vol * 1000) / 1000
        # Mask out all values outside window
        df.loc[(mask), met] = max_val
        df.loc[df[met] != max_val, met] = np.nan
        max_vols.update({met: norm_vol})

    df = df.stack()
    df.index.names = ["date", "metric"]
    df.name = "flow"
    df = df.reset_index()
    df.loc[df.metric != "flow", "text"] = df.loc[df.metric != "flow", "metric"].map(
        max_vols
    )

    return df


def plot_volume_window(df):

    base = (
        alt.Chart(df)
        .mark_line(color="black", strokeWidth=1)
        .encode(
            x=alt.X(
                "date:T").scale(
                    domain=["2020-01-01", "2020-04-01"]
                ).axis(
                    title="Date"
            ),
            y=alt.Y(
                "flow").axis(title="Flow [cfs]"
                    ).scale(
                        domain=[0, df.flow.max()])
        ).transform_filter(
            datum.metric == "flow"
        )
    )

    rule = (
        alt.Chart(df)
        .mark_bar(height=2)
        .encode(
            x="min(date):T",
            x2="max(date):T",
            y=alt.Y("flow").scale(domain=[0, df.flow.max()]),
            color="metric",
        )
        .transform_filter(datum.metric != "flow")
    )

    tex = (
        alt.Chart(df)
        .mark_text(align="left", baseline="middle", dx=10)
        .encode(
            x="max(date):T",
            y=alt.Y(
                "flow",
                aggregate={"argmax": "date"},
            ).scale(
                domain=[0, df.flow.max()]
            ),
            color="metric",
            text=alt.Text("text", format=".1%"),
        )
        .transform_filter(datum.metric != "flow")
    )

    return (base + rule + tex).interactive()


def main(
    dss_file, year, ds_channel_capacity, pathFlowIn, pathFlowOut, pathElev, window
):
    # Get flow in data
    df, vol_event = get_flow_in_data(
        dss_file, 1.0, year, ds_channel_capacity, pathFlowIn, pathFlowOut, pathElev
    )

    # Calculate n-day volumes
    df = calculate_nday_vols(df, vol_event)

    # Plot volume window
    vw_plot = plot_volume_window(df)

    # Save the plot to png file
    vw_plot.save(
        rf"outputs\Volume_Window_plots\{year}_volume_window.png"
    )


if __name__ == "__main__":

    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Process critical duration data.")
    parser.add_argument("--dss_file", 
                        type=str, 
                        help="Path to the DSS file",
                        default=r'data\simulationData.dss')
    
    parser.add_argument("--year", 
                        type=int, 
                        help="Analysis year (YYYY format)",
                        default=1966)
    parser.add_argument(
        "--ds_channel_capacity", 
        type=float, 
        help="Downstream channel capacity",
        default=4595.0
    )
    parser.add_argument(
        "--pathFlowIn",
        type=str,
        default="//ISABELLA RESERVOIR/FLOW-IN//1HOUR/CD1966_1.60/",
        help="path to flow in data",
    )
    parser.add_argument(
        "--pathFlowOut",
        type=str,
        default="//ISABELLA RESERVOIR-POOL/FLOW-OUT//1HOUR/CD1966_1.60/",
        help="path to flow out data",
    )
    parser.add_argument(
        "--pathElev", 
        type=str, 
        default="//ISABELLA RESERVOIR-POOL/ELEV//1HOUR/CD1966_1.60/", 
        help="path to elevation data"
    )

    parser.add_argument(
        "--window",
        type=Tuple[str],
        default=("01Jan2020 01:00", "01Apr2020 01:00"),
        help="Time window for data extraction",
    )
    args = parser.parse_args()

    # Assign arguments to variables
    dss_file = args.dss_file
    year = args.year
    ds_channel_capacity = args.ds_channel_capacity
    pathFlowIn = args.pathFlowIn
    pathFlowOut = args.pathFlowOut
    pathElev = args.pathElev
    window = args.window

    main(dss_file, year, ds_channel_capacity, pathFlowIn, pathFlowOut, pathElev, window)



