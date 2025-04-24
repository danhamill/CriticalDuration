from critical_duration.data_processing import getVolumeWindowData, getCriticalDurationPlotData
from critical_duration.plotting import plot_volume_window
import pandas as pd
from typing import Tuple, List
import os

def criticalDurationAnalysis(
    dss_file: str,
    year: int,
    ds_channel_capacity: int,
    pathFlowIn:str,
    pathFlowOut:str,
    pathElev:str,
    window:Tuple[str, str],
    scale_factor: float,
    reservoir:str,
    outputDirectory:str,
    durations: List[int]
)-> pd.DataFrame:
    
    # Get volume window data
    df, criticalTimes = getVolumeWindowData(
        dss_file,
        scale_factor,
        year,
        ds_channel_capacity,
        pathFlowIn,
        pathFlowOut,
        pathElev,
        window
    )

    # Calculate volume window volumes
    df = getCriticalDurationPlotData(df, criticalTimes.time_peak_stor, durations)

    plotWindow = [
        df.date.min().date().strftime("%Y-%m-%d"),
        (df.date.max().date() + pd.Timedelta("3Day")).strftime("%Y-%m-%d"),
    ]
    # Plot volume window
    vw_plot = plot_volume_window(df, plotWindow)
    plotDirectory = rf"{outputDirectory}\VolumeWindowPlots"
    os.makedirs(plotDirectory, exist_ok=True)
    # Save the plot to png file
    vw_plot.save(
        rf"{plotDirectory}\{reservoir}_{year}_{scale_factor:.2f}_volume_window.png"
    )

    df = df.loc[df.metric != "flow", :]
    df.loc[:, "scale_factor"] = scale_factor

    return df

if __name__ == "__main__":


    # Assign arguments to variables
    dss_file = "data/Terminus_Data.dss"
    reservoir = "TERMINUS"
    year = 2023
    ds_channel_capacity = 5500
    window = tuple("01Dec2021 01:00, 10Dec2021 02:00".split(","))
    scaleFactors = list(range(5, 201, 5))
    collectionIDs = list(range(1, 41))
    durations = [1, 2, 3, 5, 7]
    outputDirectory = "outputs"

    output = pd.DataFrame()
    for collectionID, scaleFactor in zip(collectionIDs[1:], scaleFactors[1:]):
        scaleFactor = scaleFactor / 100

        pathFlowIn = f"//TRM-TRM INFLOW-KAWEAH/FLOW//1HOUR/C:0000{str(collectionID).zfill(2)}|EXISTING C:{year}_SDI D:RESSIM-FRA SHIFT/"
        pathFlowOut = f"//TRM-TRM OUTFLOW-KAWEAH/FLOW//1HOUR/C:0000{str(collectionID).zfill(2)}|EXISTING C:{year}_SDI D:RESSIM-FRA SHIFT/"
        pathElev = f"//TERMINUS DAM-POOL/ELEV//1HOUR/C:0000{str(collectionID).zfill(2)}|EXISTING C:{year}_SDI D:RESSIM-FRA SHIFT/"

        df = criticalDurationAnalysis(
            dss_file,
            year,
            ds_channel_capacity,
            pathFlowIn,
            pathFlowOut,
            pathElev,
            window,
            scaleFactor,
            reservoir,
            outputDirectory,
            durations
        )

        output = pd.concat([output, df])

    output.to_excel(rf"outputs/{reservoir}_{year}_critical_duration_summary.xlsx")