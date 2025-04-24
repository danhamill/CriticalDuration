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

    output = pd.DataFrame()
    for collection_id, scale_factor in zip(collection_ids[1:], scale_factors[1:]):
        scale_factor = scale_factor / 100

        path_flow_in = f"//TRM-TRM INFLOW-KAWEAH/FLOW//1HOUR/C:0000{str(collection_id).zfill(2)}|EXISTING C:{year}_SDI D:RESSIM-FRA SHIFT/"
        path_flow_out = f"//TRM-TRM OUTFLOW-KAWEAH/FLOW//1HOUR/C:0000{str(collection_id).zfill(2)}|EXISTING C:{year}_SDI D:RESSIM-FRA SHIFT/"
        path_elev = f"//TERMINUS DAM-POOL/ELEV//1HOUR/C:0000{str(collection_id).zfill(2)}|EXISTING C:{year}_SDI D:RESSIM-FRA SHIFT/"

        df = criticalDurationAnalysis(
            dss_file,
            year,
            ds_channel_capacity,
            path_flow_in,
            path_flow_out,
            path_elev,
            window,
            scale_factor,
            reservoir,
            outputDirectory
        )

        output = pd.concat([output, df])

    output.to_excel(rf"{outputDirectory}/{reservoir}_{year}_critical_duration_summary.xlsx")