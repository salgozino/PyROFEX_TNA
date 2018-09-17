import pandas as pd
from datetime import datetime

def MACD(df,columna):
    """
    Calculo del MACD, histograma y señal del precio de cierre
    input:
        * dataframe de pandas con columna de precio de cierre llamada "close"
    outputs dentro del mismo dataframe:
        * MACD
        * Signal
        * hist
    """
    df['EMA12'] = compute_ema(12,df[columna])
    df['EMA26'] = compute_ema(26,df[columna])
    df['MACD'] = df['EMA26'] - df['EMA12']
    df['MACD_signal'] = df['MACD'].rolling(window=9).mean()
    df['MACD_hist'] = df['MACD'] - df['MACD_signal']
    return df

def compute_ema(window, points):
    """
    Compute exponential moving average of a list of points.
    :param float smoothing_factor: the smoothing factor.
    :param list points: the data points.
    :return list: all ema in a list.
    """
    ema = []
    smoothing_factor = 2/(window+1)
    # The initial point has a ema equal to itself.
    if(len(points) > 0):
        ema.append(points[0])
    for i in range(1, len(points)):
        ema.append(smoothing_factor * points[i] + (1 - smoothing_factor) * ema[i - 1])
    return ema
    
def RSI(df):
    """
    Compute the RSI indicator (relative strenght index) from the price_close column
    """
    window_length = 14
    delta = df['price_close'].diff()
    # Get rid of the first row, which is NaN since it did not have a previous 
    # row to calculate the differences
    delta = delta[1:] 

    # Make the positive gains (up) and negative gains (down) Series
    up, down = delta.copy(), delta.copy()
    up[up < 0] = 0
    down[down > 0] = 0
    roll_up1 = up.ewm(window_length).mean()
    roll_down1 = down.abs().ewm(window_length).mean()

    # Calculate the RSI based on EWMA
    RS1 = roll_up1 / roll_down1
    RSI1 = 100.0 - (100.0 / (1.0 + RS1))
    df['RSI1'] = RSI1
    
    # Calculate the SMA
    roll_up2 = up.rolling(window=window_length).mean()
    roll_down2 = down.abs().rolling(window=window_length).mean()

    # Calculate the RSI based on SMA
    RS2 = roll_up2 / roll_down2
    RSI2 = 100.0 - (100.0 / (1.0 + RS2))
    df['RSI2'] = RSI2
    return 
    
    
def tasa_implicita(futuro,spot,fecha_hoy,fecha_vto):
    """
    Determinación de la tasa implícita al día del vencimiento
    del futuro, considerando el precio del spot
    inputs:
        Cotización del Futuro
        Precio del Spot
        Fecha del día (datetime)
        Fecha del Vto (datetime)
    """
    if spot is None or futuro == float('nan'):
        tasa_implicita = float('nan')
    elif futuro is None or  futuro == float('nan'):
        tasa_implicita = float('nan')
    else:
        base = futuro - spot
        dias_vto = (fecha_vto - fecha_hoy).days
        tasa_implicita = base/spot *365/dias_vto
        
    return tasa_implicita