import pandas as pd
import numpy as np
from pydsstools.heclib.dss import HecDss
import os
from collections import namedtuple
from typing import Tuple, NamedTuple, List


def getCriticalDurationPlotData(
    df: pd.DataFrame, time_peak_stor: pd.Timestamp, durations: List = [1, 2, 3, 5, 7]
) -> pd.DataFrame:
    """
    Calculates n-day rolling volumes and normalizes them based on event windows.

    Args:
        df (pd.DataFrame): DataFrame containing flow data with a 'flow' column.
        time_peak_stor (pd.Timestamp): Timestamp of the peak storage event.

    Returns:
        pd.DataFrame: Transformed DataFrame with n-day rolling volumes, normalized values,
                      and additional metrics for visualization.

    Raises:
        KeyError: If the 'flow' column is missing in the input DataFrame.
        ValueError: If the DataFrame index is not a DatetimeIndex.

    Notes:
        - The function computes rolling averages for 1, 2, 3, 5, and 7-day windows.
        - Normalized volumes are calculated as the ratio of event volume to n-day volume.
        - Adds new columns for each n-day metric and prepares the DataFrame for visualization.
    """

    df, max_vols = volumeWindowCalculations(df, time_peak_stor, durations)

    df = df.stack()
    df.index.names = ["date", "metric"]
    df.name = "flow"
    df = df.reset_index()
    df.loc[df.metric != "flow", "text"] = df.loc[df.metric != "flow", "metric"].map(
        max_vols
    )

    return df


def volumeWindowCalculations(
    df: pd.DataFrame, time_peak_stor: pd.Timestamp, durations: List[int]
) -> Tuple[pd.DataFrame, dict]:
    max_vols = {}
    for n_day in durations:
        met = f"{n_day}".zfill(3) + "-day"
        df.loc[:, met] = df.flow.rolling(n_day * 24, closed="left").mean()

        idx_max = df[met].idxmax()
        max_val = df[met].max()
        print(met, max_val)
        n_day_vol = max_val * 86400 * n_day

        beginWindow = idx_max - pd.DateOffset(hours=24 * n_day)
        endWindow = idx_max

        eventMask = (df.index >= beginWindow) & (df.index <= time_peak_stor)
        windowMask = (df.index >= beginWindow) & (df.index <= endWindow)

        v_event_n_day_window = df.loc[eventMask, "flow"].sum() * 3600
        norm_vol = v_event_n_day_window / n_day_vol
        norm_vol = int(norm_vol * 1000) / 1000  # Mask out all values outside window
        df.loc[(windowMask), met] = max_val
        df.loc[df[met] != max_val, met] = np.nan
        max_vols.update({met: norm_vol})

    return df, max_vols


def getVolumeWindowData(
    dss_file: str,
    sf: float,
    year: int,
    ds_channel_capacity: int,
    pathFlowIn: str,
    pathFlowOut: str,
    pathElev: str,
    window: Tuple[str, str],
) -> Tuple[pd.DataFrame, NamedTuple]:
    sf = f"{sf:.2f}"
    assert len(str(year)) == 4, "Year must be 4 digit with format YYYY"
    assert os.path.exists(dss_file), f"Cannot locate DSS file {dss_file}"
    print(f"{year} Hydrograph, {sf} Scale Factor.....")

    CriticalTimes = namedtuple(
        "CriticalTimes", ["time_peak_stor", "time_ds_channel_exceed"]
    )

    flowIn = readDssData(
        dss_file,
        pathFlowIn,
        variable="flow",
        window=window,
    )
    flowOut = readDssData(
        dss_file,
        pathFlowOut,
        variable="flow",
        window=window,
    )
    elev = readDssData(
        dss_file,
        pathElev,
        variable="elev",
        window=window,
    )

    time_peak_stor = elev.elev.idxmax()
    print(f"Time of peak Storage {time_peak_stor}")

    flowOut = flowOut.loc[flowOut.flow > ds_channel_capacity, :]
    if not flowOut.empty:
        time_exceed = flowOut.index.min()
        print(f"Time of Downstream Channel Exceedance {time_exceed}")
    else:
        time_exceed = None
    criticalTimes = CriticalTimes(time_peak_stor, time_exceed)

    return flowIn, criticalTimes


def readDssData(
    dss_file: str, path: str, variable: str, window: Tuple[str, str] = None
) -> pd.DataFrame:
    assert len(path.split("/")) == 8, (
        f"Path must be in the format /A/B/C/D/E/F/, but is {path}"
    )

    fid = HecDss.Open(dss_file)
    ts = fid.read_ts(path, window=window, trim_missing=False)
    times = ts.pytimes
    values = ts.values
    idx = pd.Index(times, name="date")
    tmp = pd.DataFrame(index=idx, data=values.copy(), columns=[variable])
    fid.close()

    return tmp
