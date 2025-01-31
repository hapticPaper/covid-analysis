
"""
This will load csv files formatted with a FIPS id column.
It relies on the parameters in config.py.
"""
from config import settings
import os, numpy, io, datetime, json, requests, pandas as pd
from sqlalchemy import create_engine
from  sqlalchemy.connectors import pyodbc
from sqlalchemy.dialects import postgresql
from psycopg2 import ProgrammingError
import matplotlib
from matplotlib import pyplot as plt
from PIL import Image
from IPython.display import Image as IImage

from queries import  *
from config import settings
pgHost = settings['pgHost']
pgUser = settings['pgUser']
pgPass = os.environ['PGPASS']
pgDb = settings['pgDb']
covidPath = settings['covidPath']
pgDb = settings['pgDb']
gkey = os.environ['GMAPS_API_KEY']



#gmaps.configure(api_key=os.environ["GMAPS_API_KEY"])
dt = datetime.datetime.today() #(2020,4,9)
DT = dt.strftime('%Y%m%d') #'20200322' #
DATEY = dt.strftime('%Y-%m-%d') #'2020-03-22' #



GMAPS_BASE = 'https://maps.googleapis.com/maps/api'

pg = create_engine(f"postgresql://{pgUser}:{pgPass}@{pgHost}/{pgDb}").raw_connection()





def GET_COLUMNS(line):
    line = line.decode("utf-8-sig").replace("\r","").replace("\n","")
    with open('field_mappings.json', 'r') as fm:
        mapped_fields = json.loads(fm.read())
    return f"({', '.join([mapped_fields[i] for i in line.split(',')])})"


def sqlExecute(conn, sql):
    dc = conn.cursor()
    dc.execute(sql)
    conn.commit()
    try:
        return dc.fetchall()
    except Exception as e:
        if type(e)==ProgrammingError:
            if e.args[0]=='no results to fetch':
                pass
        else:
            print("Poop")
        return

def loadData(data, sql, conn=pg):
    with open(f"{data}", 'r') as f:
        cursor = pg.cursor()
        cursor.copy_expert(sql, f)
        pg.commit()
        print(data)  
            
def loadDataPath(path, conn=pg):
    print(f"\nLoading data from {path}")
    last = sqlExecute(pg, LAST_UPDATE)[0]
    for file in os.listdir(path):
        if file[-4:]=='.csv': # and file[:-4]>last[0].strftime('%m-%d-%Y'):
            #ddf = pd.read_csv(os.path.join(path, file))
            with open(os.path.join(path, file), 'rb') as ft:
                l = ft.readline()
                loadData(f"{path}\{file}", COPY('daily', GET_COLUMNS(l)), conn)
    sqlExecute(pg, UPDATE_KEY)

def lookupCoords(location: str, orignalKey=None):
    try:
        resp = requests.get(f"{GMAPS_BASE}/geocode/json", params={"address":location,'key':gkey}).json()
        print(resp['results'])
        l= resp['results'][0]['geometry']['location']
        u = sqlExecute(pg, UPDATE_KEY_GEO(orignalKey or location, l['lat'], l['lng']))
        return 1
    except Exception as e:
        if resp.get('status')=='ZERO_RESULTS':
            print(f"Couldnt get location for {location} - {resp}")
            if location[:4]=='None':
                if lookupCoords(location.replace("None, ", ""), orignalKey=location)!=1:
                    sqlExecute(pg, UPDATE_KEY_GEO(location, 0,0))
            else: 
                sqlExecute(pg, UPDATE_KEY_GEO(location, 0, 0))
        elif type(e)==KeyError:
            print(f"Couldnt get {e} for {location} - {resp}")
        else:
            print(f"Some other issue with {location} - {e}: {resp}")
        
   

def getNewPlaces():
    return [i[0] for i in sqlExecute(pg, NEW_PLACES)]

print("\n\nTruncating daily")
sqlExecute(pg, """TRUNCATE TABLE daily""")

if __name__=="__main__":
    loadDataPath(covidPath, pg)
    [lookupCoords(i) for i in getNewPlaces()]

    
    #loadData('StationEntrances.csv', COPY('stationEntrances'), pg)
    #loadData('Stations.csv', COPY('stations'), pg)
    #loadDataPath(turnstilePath, COPY('turnstileUse'), pg)



    with open(f"coivid_daily_processed.csv", 'w') as f:
        f.write("locale\tlat\tlng\tconfirmed\tdeaths\trecovered\tlastUpdated\tyesterdayConfirmed\tdeltaPct\tnewCases\tnewRecovered\tnewDeaths\n")
        data=sqlExecute(pg, SUMMARY_CSV)
        f.write("\n".join(["\t".join([str(t) for t in i]) for i in data]))
        pg.commit()
    pg.close()
    print(f"Processed data written to coivid_daily_processed.csv")



    conn = create_engine(f"postgresql://{pgUser}:{pgPass}@{pgHost}/{pgDb}")

    dates = pd.read_sql(DATES, conn) #or (countryregion='US') or iso3='USA'
    dates = [i.strftime('%Y-%m-%d') for i in dates.sort_values(by='date').date.tolist()]
    print(dates)


    imgs=[]

    for dt in dates[-30:]:
        DATEY = dt
        DT = dt.replace("-","")

        covidDf = pd.read_sql(DAILY_UPDATE(DATEY), conn).fillna(0)


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
            append_images=(imgs[1:]+[imgs[-1]]*15),
            optimize=True, 
            duration=180, 
            loop=0)

    #IImage(filename="covid_2020.gif", format='png')