from datetime import time
import pandas as pd
import numpy as np
from pydsstools.heclib.dss import HecDss
from pydsstools.core import TimeSeriesContainer, HecTime
import altair as alt
from altair import datum
from altair_saver import save
import os
alt.data_transformers.disable_max_rows()
alt.renderers.enable('altair_viewer')


def get_flow_in_data(dss_file, sf, year, ds_channel_capacity):
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
    
    sf = f'{sf:.2f}'
    assert len(str(year)) == 4, 'Year must be 4 digit with format YYYY'
    assert os.path.exists(dss_file), 'Cannot locate DSS file'
    print(f'{year} Hydrograph, {sf} Scale Factor.....')

    fid = HecDss.Open(dss_file)
    ts = fid.read_ts(f'//ISABELLA RESERVOIR-POOL/FLOW-IN//1HOUR/CD{year}_{sf}/', window = ("01Jan2020 01:00", '01Apr2020 01:00'), trim_missing=False)
    times = ts.pytimes
    values = ts.values
    idx = pd.Index(times, name = 'date')
    tmp = pd.DataFrame(index = idx, data = values.copy(), columns = ['flow'])
    fid.close()

    fid = HecDss.Open(dss_file)
    ts = fid.read_ts(f'//ISABELLA RESERVOIR-POOL/ELEV//1HOUR/CD{year}_{sf}/', window = ("01Jan2020 01:00", '01Apr2020 01:00'), trim_missing=False)
    times = ts.pytimes
    values = ts.values
    idx = pd.Index(times, name = 'date')
    a = pd.DataFrame(index = idx, data = values.copy(), columns = ['elev'])
    fid.close()

    time_peak_stor = a.elev.idxmax()
    print(f'Time of peak Storage {time_peak_stor}')

    fid = HecDss.Open(dss_file)
    ts = fid.read_ts(f'//ISABELLA RESERVOIR-POOL/FLOW-OUT//1HOUR/CD{year}_{sf}/', window = ("01Jan2020 01:00", '01Apr2020 01:00'), trim_missing=False)
    times = ts.pytimes
    values = ts.values
    idx = pd.Index(times, name = 'date')
    b = pd.DataFrame(index = idx, data = values.copy(), columns = ['flow'])
    fid.close()

    #Does Channel exceed downstream constraints?
    b = b.loc[b.flow>ds_channel_capacity,:]
    if not b.empty:
        time_exceed = b.index.min()
        print(f"Time of Downstream Channel Exceedance {time_exceed}")
    else:
        time_exceed = None

    if time_exceed is None:
        print('Event Volume calculated as peak in storage (normal operations)...')
        vol_event = tmp.loc[:time_peak_stor.isoformat(),'flow'].sum()*3600
    else:
        if (time_exceed < time_peak_stor) :
            print('Exceeded downstream channel capacity before peak storage...')
            vol_event = tmp.loc[:time_exceed.isoformat(),'flow'].sum()*3600
        else:
            print('Event Volume calculated as peak in storage...')
            vol_event = tmp.loc[:time_peak_stor.isoformat(),'flow'].sum()*3600

    return tmp, vol_event

def calculate_nday_vols(df, vol_event):

    max_vols = {}

    for n_day in [1,2,3,4,5,6,7,15,30,60]:

        met = f'{n_day}'.zfill(3) +'-day'
        df.loc[:, met] = df.flow.rolling(n_day * 24+1, center=True).mean()

        idx_max = df[met].idxmax()
        max_val = df[met].max()
        print(met, max_val)
        n_day_vol = max_val * 86400* n_day
        
        begin_date = (idx_max - pd.DateOffset(hours = n_day*12)).isoformat()
        end_date = (idx_max + pd.DateOffset(hours = n_day*12)).isoformat()
        mask = (df.index >= begin_date) & (df.index<end_date)

        v_event_n_day_window = df.loc[mask,'flow'].sum() * 3600
        norm_vol = vol_event/n_day_vol
        norm_vol = int(norm_vol*1000)/1000
        #Mask out all values outside window
        df.loc[(mask ), met] = max_val
        df.loc[df[met] != max_val, met] = np.nan
        max_vols.update({met:norm_vol})

    df = df.stack()
    df.index.names = ['date','metric']
    df.name = 'flow'
    df = df.reset_index()
    df.loc[df.metric!= 'flow','text'] = df.loc[df.metric!= 'flow','metric'].map(max_vols)

    return df

def plot_volume_window(df):

    base = alt.Chart(df).mark_line(color='black', strokeWidth=1).encode(
        x = alt.X('date:T', 
                  scale = alt.Scale(domain = ['2020-01-01','2020-04-01']),
                  axis = alt.Axis(title = 'Date')
                  ),
        y = alt.Y('flow', 
                  axis = alt.Axis(title = 'Flow [cfs]'),
                  scale = alt.Scale(domain = [0,df.flow.max()])),
        # color = 'metric'
    ).transform_filter(datum.metric == 'flow')

    rule = alt.Chart(df).mark_bar(height = 2).encode(
            x = 'min(date):T',
            x2 = 'max(date):T',
            y = alt.Y('flow',
                    scale = alt.Scale(domain = [0,df.flow.max()])),
            color = 'metric', 
        ).transform_filter(datum.metric != 'flow')

    tex = alt.Chart(df).mark_text(align = 'left', baseline = 'middle', dx = 10).encode(
        x = 'max(date):T',
        y = alt.Y('flow', aggregate={'argmax':'date'},
                    scale = alt.Scale(domain = [0,df.flow.max()])),
        color = 'metric',
        text = alt.Text('text', format = '.1%')
    ).transform_filter(datum.metric != 'flow')


    return (base+rule + tex).interactive()

dss_file = r'C:\workspace\Isabella_Dam\Task2\model\Isabella-Construction\rss\CriticalDuraiton_v2\simulation.dss'
ds_channel_capacity = 4595


output = pd.DataFrame()
years = {}
for year in [1966]:
    vw_plots = {}
    for scale_factor in [1.0,1.5,1.8,1.9,2.0,2.5,3.0]:
        df, vol_event = get_flow_in_data(dss_file, scale_factor, year, ds_channel_capacity)

        df = calculate_nday_vols(df, vol_event)

        vw_plot = plot_volume_window(df)

        vw_plots.update({scale_factor:vw_plot})

        #Save the plots to png file
        save (rf'C:\workspace\Isabella_Dam\Task2\outputs\Volume_Window_plots\{year}_{scale_factorf}_volume_window.png')
        tmp = df[['metric','text']].drop_duplicates().dropna()
        tmp = tmp.set_index('metric').T
        tmp.index = pd.Index([scale_factor], name = 'scale_factor')
        tmp = pd.concat([tmp],keys = [year], names =['Year'])
        output = pd.concat([output, tmp])
    years.update({year: vw_plots})



