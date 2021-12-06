import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt


def read_ceda_heathrow(filepath, target_DOY):
    """

    :return:
    """

    # read raw data
    df_year = pd.read_csv(filepath)

    # convert times from string to datetime
    df_year['ob_end_time'] = pd.to_datetime(df_year['ob_end_time'], format='%Y-%m-%d %H:%M')

    DOY_selected = dt.datetime.strptime(str(target_DOY), '%Y%j')

    df_DOY = df_year.loc[
        (df_year['ob_end_time'].dt.day == DOY_selected.day) & (df_year['ob_end_time'].dt.month == DOY_selected.month)]

    df = df_DOY[['ob_end_time', ' mean_wind_dir', ' mean_wind_speed']].copy()

    df = df.rename(columns={'ob_end_time': 'time', ' mean_wind_dir': 'WD', ' mean_wind_speed': 'WS'})

    df = df.set_index('time')

    df.WS = pd.to_numeric(df.WS, errors='coerce')
    df.WD = pd.to_numeric(df.WD, errors='coerce')

    return df
