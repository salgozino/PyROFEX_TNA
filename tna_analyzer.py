import indicadores
import PMY_REST as rest
import matplotlib.pyplot as plt
import matplotlib.dates as dates
import pandas as pd
import numpy as np
from datetime import datetime
import schedule
import time
plt.style.use('ggplot')

#Logging to the API
rest.init("user1","password","",1)    
rest.login()

#Defino que indice y futuro voy a analizar. Además se debe definir la fecha de vto del futuro.
index = 'I.RFX20'
futuro = 'RFX20Sep18'
fecha_vto = datetime.strptime('2018-09-28 23:59:59','%Y-%m-%d %H:%M:%S')

entries = 'BI,LA,OF'
def look_TNA(spot,futuro,fecha_vto,entries):
    """
       Busca el precio del index, del futuro, y en función de la fecha de vto y la fecha del día, se calcula la tasa implicita.
    """
    
    hoy = datetime.today()
    price_spot = {}
    price_futuro = {}
    TNA = {}
    for entrie in entries.split(','):
        r = rest.MD(spot,entrie)
        if r['status'] == 'OK':
            #price_spot = r['marketData']['CL']['price']
            value = r['marketData'][entrie]
            if value is None:
                value = float('nan')
            elif type(value) is list and len(value) != 0:
                if type(value[0]) is dict:
                    value = value[0]['price']
            elif type(value) is dict:
                value = value['price']
            else:
                value = float('nan')
            price_spot[entrie] = value

        r = rest.MD(futuro,entrie)
        if r['status'] == 'OK':
            value = r['marketData'][entrie]
            if value is None:
                value = float('nan')
            elif type(value) is list and len(value) != 0:
                if type(value[0]) is dict:
                    value = value[0]['price']
            elif type(value) is dict:
                value = value['price']
            else:
                value = float('nan')
            price_futuro[entrie] = value

        TNA[entrie] = indicadores.tasa_implicita(price_futuro[entrie],price_spot[entrie],hoy,fecha_vto)
    data = {'Spot':price_spot, 'Futuro':price_futuro,'TNA':TNA,'date':hoy}
    return data

    
    
def data_to_df(data):
    """
    Generación del DataFrame a partir de los datos obtenidos de la API para todas las entries.
    """
    final_data = {}
    for ticker in data:
        if not isinstance(data[ticker], datetime):
            for entrie in data[ticker]:
                final_data[ticker+'_'+entrie] = data[ticker][entrie]
        else:
            final_data[ticker] = data[ticker]

    df = pd.DataFrame(final_data,index=[0])
    df.set_index('date',inplace=True)
    return df

# Inicializo el dataframe con el primer valor.
data = look_TNA(index,futuro,fecha_vto,entries)
df = data_to_df(data)



#Genero la figura base
fig = plt.figure()
ax1 = plt.subplot(211)
ax2 = plt.subplot(212,sharex=ax1)
fig.show()
fig.canvas.draw()
fig.canvas.flush_events()
plt.ion()
#Comienzo de la zona de funcionamiento continuo
def job(index,futuro,fecha_vto,entries,filename):
    global df, ax1, ax2, fig, seconds_to_wait
    print("Working...")
    
    #Obtengo los datos nuevos.
    data = look_TNA(index,futuro,fecha_vto,entries)
    df2 = data_to_df(data)
    print(df.filter(regex='TNA').tail(10))
    df3 = df
    df = pd.concat([df3,df2])
    
    #Exporto los datos a csv para que me quede registro
    filename = datetime.today().strftime("%Y-%m-%d") + '-' +filename
    try:
        df.to_csv(filename,sep=',')
    except:
        print("Error: The file could not wrote. Check if another app is using the file.\n Don't Worry, the data was not missed. Later will be recorded to the file.")
    
    #Grafico
    timestamp = df.index
    ax1.clear()
    for entrie in entries.split(','):
        df.plot(x=timestamp,y='TNA_{}'.format(entrie),ax=ax1, kind='line', grid=True, ylim=(0,max((df['TNA_{}'.format(entrie)].fillna(0).max()+0.2,1.))))
        ax1.set_xlabel("")
        ax1.xaxis.set_major_formatter(plt.NullFormatter())
          
    ax2.clear()
    for entrie in entries.split(','):
        df.plot(x=timestamp,y='Spot_{}'.format(entrie),ax=ax2, kind='line', grid=True)
        df.plot(x=timestamp,y='Futuro_{}'.format(entrie),ax=ax2, kind='line', grid=True)
        
    plt.xlim((df.index.min(), df.index.max()+ pd.Timedelta(seconds=seconds_to_wait*3)))
    ax1.set_title('Analizador de TNA')
    fig.canvas.draw()
    fig.canvas.flush_events()
    #plt.draw()
    plt.pause(1)
 


seconds_to_wait = 3
#Cada cuanto voy a realizar las acciones
schedule.every(seconds_to_wait).seconds.do(job,index,futuro,fecha_vto,entries,'TNA.csv')

#Para frenar el proceso lo puedo hacer con Ctrl+C, De esta forma es mas elegante
run = True
while run:
    try:
        schedule.run_pending()
        print("Waiting for {} seconds...".format(seconds_to_wait))
        time.sleep(seconds_to_wait)
        
    except KeyboardInterrupt:
        schedule.cancel_job(job)
        print("Finalizado el proceso por el usuario.\nGracias por haber usado el analizador de TNA en tiempo real")
        run = False