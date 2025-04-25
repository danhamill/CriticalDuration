# Critical Duration Analysis

This project is designed to analyze critical inflow volume duration events using hydrological data. It processes data from DSS files, calculates relevant metrics, and visualizes the results through interactive plots.

The library calculated the volume window, a ratio of the event volume to n-day unregulated volume durations.

[readthedocs](https://criticalduration.readthedocs.io/en/latest/)

```math
V_{window} = \frac{V_{Event}}{V_{n-day}}
```

![method diagram](images/Volume_window_Diagram.png)
[readthedocs](https://criticalduration.readthedocs.io/en/latest/)

## Project Structure

```
CriticalDuration
├── critical_duration
│   ├── __init__.py
│   ├── data_processing.py
│   ├── plotting.py
│   ├── utils.py
│   └── main.py
├── scripts
│   └── run_analysis.py
├── data
│   └── Terminus_Data.dss
├── tests
│   ├── __init__.py
│   └── test_critical_duration.py
├── setup.py
├── requirements.txt
└── README.md
```

## Installation

To install the required dependencies, run:

```
pip install -r requirements.txt
```

If something is not working, it may be heplpful to install using

```
python setup.py develop
```

## Usage

To run the analysis, execute the following command:

```
python scripts/run_analysis.py
```

Make sure to adjust the parameters in `run_analysis.py` as needed for your specific analysis.

## Functions

- **Data Processing**: The `data_processing.py` module contains functions for reading and processing hydrological data from DSS files.
- **Plotting**: The `plotting.py` module provides functions for visualizing the processed data using Altair.


## Testing

Unit tests for the package can be found in the `tests` directory. To run the tests, use:

```
pytest tests/
```

The test data used to validate the compuations came from HDR IPAST software.

## License

This project is licensed under the MIT License. See the LICENSE file for details.
