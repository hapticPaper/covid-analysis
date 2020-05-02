DROP VIEW IF EXISTS public.dailyCovidCases;
DROP TABLE IF EXISTS public.daily;

CREATE TABLE public.daily
(
    FIPS integer,
    Admin2 character varying,
    provinceState character varying,
    countryRegion character varying,
    lastUpdate timestamp,
    lat double precision,
    lng double precision,
    confirmed bigint,
    deaths bigint,
    recovered bigint,
    active bigint,
    combinedKey character varying
);


CREATE OR REPLACE VIEW public.dailyCovidCases 
AS
SELECT * FROM
              (SELECT combinedKey,lat, lng, confirmed, deaths, recovered,
                   d.lastUpdate,
                   lag(confirmed) OVER (order by combinedkey, d.lastUpdate) yesterdayConfirmed,
                   round(100*cast((confirmed-(lag(confirmed) OVER (partition by combinedkey order by combinedkey, d.lastUpdate))) as decimal)/(nullif(lag(confirmed) OVER (partition by combinedkey order by combinedkey, d.lastUpdate),0)),2) increaseRate,
                   confirmed - (lag(confirmed) OVER (partition by combinedkey order by combinedkey, d.lastUpdate)) newCases,
                   recovered-(lag(recovered) OVER (partition by combinedkey order by d.lastUpdate)) newRecoveries,
                   deaths - (lag(deaths) OVER (partition by combinedkey order by d.lastUpdate)) newDeaths
                    FROM (SELECT distinct * from daily
                            --where combinedkey='Unassigned, Tennessee, US'
                        ) d
    ) r
where (newCases is not null or newRecoveries is not null  or newDeaths is not null)
AND increaseRate<1000
order by newCases desc;