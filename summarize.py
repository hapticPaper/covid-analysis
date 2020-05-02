import matplotlib
from matplotlib import pyplot as plt
import numpy as np, pandas as pd
import datetime, os, io
from config import settings
from sqlalchemy import create_engine
from  sqlalchemy.connectors import pyodbc
from sqlalchemy.dialects import postgresql
from PIL import Image
from IPython.display import Image as IImage


#gmaps.configure(api_key=os.environ["GMAPS_API_KEY"])
dt = datetime.datetime.today() #(2020,4,9)
DT = dt.strftime('%Y%m%d') #'20200322' #
DATEY = dt.strftime('%Y-%m-%d') #'2020-03-22' #
pgHost = settings['pgHost']
pgUser = settings['pgUser']
pgPass = os.environ['PGPASS']
pgDb = settings['pgDb']


pg = create_engine(f"postgresql://{pgUser}:{pgPass}@{pgHost}/{pgDb}")


dates = pd.read_sql(f"""SELECT distinct date(lastupdate) from  daily where combinedkey like '%%US' order by 1""", pg) #or (countryregion='US') or iso3='USA'
dates = [i.strftime('%Y-%m-%d') for i in dates.sort_values(by='date').date.tolist()]
print(dates)


imgs=[]

for dt in dates:
    DATEY = dt
    DT = dt.replace("-","")

    covidDf = pd.read_sql(f"""SELECT lat, lng, max(lastupdate) lastupdate, max(confirmed) confirmed, max(deaths) deaths 
from fa_daily  where combinedkey like '%%US'  and date(lastupdate)<='{DATEY}' group by  lat, lng, combinedkey
""", pg).fillna(0)


    fig, ax1 = plt.subplots(1,1)
    plt.figure(1, (24,12))
    ax1.scatter(covidDf.lng, covidDf.lat, sizes=covidDf.confirmed, alpha=0.1, color='#C70039')
    ax1.scatter(covidDf.lng, covidDf.lat, sizes=covidDf.deaths, alpha=0.1, color='#000000')
    ax1.set_xlim(-140, -60)
    ax1.set_ylim(20, 57)
    ax1.annotate(DATEY, (-135, 22))
    fig.suptitle("Covid Infections and Deaths",fontsize=25)

    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=100)
    buf.seek(0)
    im = Image.open(buf)
    n = Image.new('RGBA', (640,480))
    n.paste(im,(0,0))
    buf.close()
    imgs.append(n)
    #plt.show()




imgs[0].save(f'covid_2020.gif', 
        save_all=True,
        append_images=(imgs[1:]+[imgs[-1]]*4),
        optimize=True, 
        duration=200, 
        loop=0)

#IImage(filename="covid_2020.gif", format='png')