"""
Enter your config information.
You can run this file directly to help encode your password.
"""
import os, base64


settings = {
    "covidPath": os.path.join("/Users","ian","repos","COVID-19","csse_covid_19_data","csse_covid_19_daily_reports", "current"),
    "mtaPath": os.path.join("/Users","ian","repos","covid-analysis","mta"),
    "turnstilePath": os.path.join("/Users","ian","repos","covid-analysis","mta","turnstileUse"),
    "pgHost":"localhost",
    "pgDb":"covid",
    "pgUser":"postgres",
    "pgPass":os.environ['PGPASS']
}
print(settings['covidPath'])

if __name__=="__main__":
    p = base64.b64encode(input("What is your postgres password? ").encode('UTF8'))
    print("Your encoded password is ", p)