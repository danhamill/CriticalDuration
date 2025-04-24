import pandas as pd
from critical_duration.main import criticalDurationAnalysis

if __name__ == "__main__":

    outputDirectory = "outputs"
    dss_file = "data/Terminus_Data.dss"
    reservoir = "TERMINUS"
    year = 2023
    ds_channel_capacity = 5500
    window = tuple("01Dec2021 01:00, 10Dec2021 02:00".split(","))
    scale_factors = list(range(5, 201, 5))
    collection_ids = list(range(1, 41))
    durations = [1, 2, 3, 5, 7]

    output = pd.DataFrame()
    for collection_id, scale_factor in zip(collection_ids[1:], scale_factors[1:]):
        scale_factor = scale_factor / 100

        pathFlowIn = f"//TRM-TRM INFLOW-KAWEAH/FLOW//1HOUR/C:0000{str(collection_id).zfill(2)}|EXISTING C:{year}_SDI D:RESSIM-FRA SHIFT/"
        pathFlowOut = f"//TRM-TRM OUTFLOW-KAWEAH/FLOW//1HOUR/C:0000{str(collection_id).zfill(2)}|EXISTING C:{year}_SDI D:RESSIM-FRA SHIFT/"
        pathElev = f"//TERMINUS DAM-POOL/ELEV//1HOUR/C:0000{str(collection_id).zfill(2)}|EXISTING C:{year}_SDI D:RESSIM-FRA SHIFT/"

        df = criticalDurationAnalysis(
            dss_file,
            year,
            ds_channel_capacity,
            pathFlowIn,
            pathFlowOut,
            pathElev,
            window,
            scale_factor,
            reservoir,
            outputDirectory,
            durations
        )

        output = pd.concat([output, df])

    output.to_excel(rf"{outputDirectory}/{reservoir}_{year}_critical_duration_summary.xlsx")