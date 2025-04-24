from critical_duration.data_processing import (
    getVolumeWindowData,
    readDssData,
    getCriticalDurationPlotData,
)
import pandas as pd


class TestClass:

    def test_get_flow_in_data(self):
        # Test parameters
        dss_file = "data/Terminus_Data.dss"
        sf = 0.5
        year = 2023
        ds_channel_capacity = 5500
        pathFlowIn = "//TRM-TRM INFLOW-KAWEAH/FLOW//1HOUR/C:000010|EXISTING C:2023_SDI D:RESSIM-FRA SHIFT/"
        pathFlowOut = "//TRM-TRM OUTFLOW-KAWEAH/FLOW//1HOUR/C:000010|EXISTING C:2023_SDI D:RESSIM-FRA SHIFT/"
        pathElev = "//TERMINUS DAM-POOL/ELEV//1HOUR/C:000010|EXISTING C:2023_SDI D:RESSIM-FRA SHIFT/"
        window = ("01Dec2021 01:00", "10Dec2021 02:00")

        volumeWindowData, criticalTimes = getVolumeWindowData(
            dss_file,
            sf,
            year,
            ds_channel_capacity,
            pathFlowIn,
            pathFlowOut,
            pathElev,
            window,
        )

        assert isinstance(volumeWindowData, pd.DataFrame), "flowIn should be a DataFrame"
        assert "flow" in volumeWindowData.columns, "flowIn DataFrame should contain 'flow' column"
        assert isinstance(criticalTimes.time_peak_stor, pd.Timestamp), (
            "time_peak_stor should be a Timestamp"
        )
        assert criticalTimes.time_peak_stor == pd.Timestamp("2021-12-07 01:00:00"), (
            f"Expected time_peak_stor to be '2021-12-07 01:00:00', but got {criticalTimes.time_peak_stor}"
        )

    def test_readDssData(self):
        # Test parameters
        dss_file = "data/Terminus_Data.dss"
        path = "//TRM-TRM INFLOW-KAWEAH/FLOW//1HOUR/C:000001|EXISTING C:2023_SDI D:RESSIM-FRA SHIFT/"
        variable = "flow"
        window = ("01Dec2021 01:00", "10Dec2021 02:00")

        df = readDssData(dss_file, path, variable, window)

        assert isinstance(df, pd.DataFrame), "Output should be a DataFrame"
        assert "flow" in df.columns, "DataFrame should contain 'flow' column"
        assert df.index.name == "date", "DataFrame index should be named 'date'"

    def test_two_wave_hydrograph(self):
        # Test parameters
        dss_file = "data/Terminus_Data.dss"
        sf = 0.5
        year = 2023
        ds_channel_capacity = 5500
        pathFlowIn = "//TRM-TRM INFLOW-KAWEAH/FLOW//1HOUR/C:000010|EXISTING C:2023_SDI D:RESSIM-FRA SHIFT/"
        pathFlowOut = "//TRM-TRM OUTFLOW-KAWEAH/FLOW//1HOUR/C:000010|EXISTING C:2023_SDI D:RESSIM-FRA SHIFT/"
        pathElev = "//TERMINUS DAM-POOL/ELEV//1HOUR/C:000010|EXISTING C:2023_SDI D:RESSIM-FRA SHIFT/"
        window = ("01Dec2021 01:00", "10Dec2021 02:00")
        durations = [1, 2, 3, 5, 7]

        df, criticalTimes = getVolumeWindowData(
            dss_file,
            sf,
            year,
            ds_channel_capacity,
            pathFlowIn,
            pathFlowOut,
            pathElev,
            window,
        )

        # Calculate n-day volumes
        df = getCriticalDurationPlotData(df, criticalTimes.time_peak_stor, durations)

        # Check nday duration dates
        dates = pd.concat(
            [
                df.groupby("metric").date.min().drop("flow"),
                df.groupby("metric").date.max().drop("flow"),
            ],
            axis=1,
            keys=["minDate", "maxDate"],
        )

        assert dates.loc[dates.index == "001-day", "minDate"].iloc[0] == pd.Timestamp(
            "2021-12-01 08:00:00"
        ), (
            f"001-day min date should be 2021-12-01 08:00:00, but is {dates['001-day'].minDate}"
        )
        assert dates.loc[dates.index == "002-day", "minDate"].iloc[0] == pd.Timestamp(
            "2021-12-01 08:00:00"
        ), (
            f"002-day min date should be 2021-12-01 08:00:00, but is {dates['002-day'].minDate}"
        )
        assert dates.loc[dates.index == "003-day", "minDate"].iloc[0] == pd.Timestamp(
            "2021-12-01 07:00:00"
        ), (
            f"003-day min date should be 2021-12-01 07:00:00, but is {dates['003-day'].minDate}"
        )
        assert dates.loc[dates.index == "005-day", "minDate"].iloc[0] == pd.Timestamp(
            "2021-12-01 09:00:00"
        ), (
            f"005-day min date should be 2021-12-01 09:00:00, but is {dates['005-day'].minDate}"
        )
        assert dates.loc[dates.index == "007-day", "minDate"].iloc[0] == pd.Timestamp(
            "2021-12-01 06:00:00"
        ), (
            f"007-day min date should be 2021-12-01 06:00:00, but is {dates['007-day'].minDate}"
        )

        assert dates.loc[dates.index == "001-day", "maxDate"].iloc[0] == pd.Timestamp(
            "2021-12-02 08:00:00"
        ), (
            f"001-day min date should be 2021-12-02 08:00:00, but is {dates['001-day'].minDate}"
        )
        assert dates.loc[dates.index == "002-day", "maxDate"].iloc[0] == pd.Timestamp(
            "2021-12-03 08:00:00"
        ), (
            f"002-day min date should be 2021-12-03 08:00:00, but is {dates['002-day'].minDate}"
        )
        assert dates.loc[dates.index == "003-day", "maxDate"].iloc[0] == pd.Timestamp(
            "2021-12-04 07:00:00"
        ), (
            f"003-day min date should be 2021-12-04 07:00:00, but is {dates['003-day'].minDate}"
        )
        assert dates.loc[dates.index == "005-day", "maxDate"].iloc[0] == pd.Timestamp(
            "2021-12-06 09:00:00"
        ), (
            f"005-day min date should be 2021-12-06 09:00:00, but is {dates['005-day'].minDate}"
        )
        assert dates.loc[dates.index == "007-day", "maxDate"].iloc[0] == pd.Timestamp(
            "2021-12-08 06:00:00"
        ), (
            f"007-day min date should be 2021-12-08 06:00:00, but is {dates['007-day'].minDate}"
        )

        # check volume window calculations
        volume_window_results = df.groupby("metric").text.first().drop("flow")
        assert volume_window_results["001-day"] == 2.952, (
            f"001-day volume should be 2.952, but is {volume_window_results['001-day']}"
        )
        assert volume_window_results["002-day"] == 1.991, (
            f"002-day volume should be 1.991, but is {volume_window_results['002-day']}"
        )
        assert volume_window_results["003-day"] == 1.640, (
            f"003-day volume should be 1.640, but is {volume_window_results['003-day']}"
        )
        assert volume_window_results["005-day"] == 1.140, (
            f"005-day volume should be 1.140, but is {volume_window_results['005-day']}"
        )
        assert volume_window_results["007-day"] == 0.906, (
            f"007-day volume should be 0.906, but is {volume_window_results['007-day']}"
        )
        print("here")
