DROP VIEW IF EXISTS public.stationLocations;
DROP TABLE IF EXISTS stationEntrances;
DROP TABLE IF EXISTS stations;
DROP TABLE IF EXISTS turnstileuse;


create table stations
(
    StationID            integer,
    ComplexID            integer,
    GTFSStopID          CHARACTER VARYING,
    division                CHARACTER VARYING,
    line                    CHARACTER VARYING,
    StopName             CHARACTER VARYING,
    borough                 CHARACTER VARYING,
    DaytimeRoutes        CHARACTER VARYING,
    structure               CHARACTER VARYING,
    GTFSLatitude         double PRECISION,
    GTFSLongitude        double PRECISION,
    NorthDirectionLabel CHARACTER VARYING,
    SouthDirectionLabel CHARACTER VARYING
);

alter table stations
    owner to postgres;




create table stationEntrances
(
    division           varchar,
    line               varchar,
    station_name       character varying,
    station_latitude   double PRECISION,
    station_longitude  double PRECISION,
    route_1            character varying,
    route_2            character varying,
    route_3            character varying,
    route_4            character varying,
    route_5            character varying,
    route_6            character varying,
    route_7            character varying,
    route_8            character varying,
    route_9            character varying,
    route_10           character varying,
    route_11           character varying,
    entrance_type      character varying,
    entry              character varying,
    exit_only          character varying,
    vending            character varying,
    staffing           character varying,
    staff_hours        character varying,
    ada                character varying,
    ada_notes          character varying,
    free_crossover     character varying,
    north_south_street character varying,
    east_west_street   character varying,
    corner             character varying,
    latitude           double PRECISION,
    longitude          double PRECISION
);

alter table stationentrances
    owner to postgres;


create table turnstileuse
(
	CA CHARACTER VARYING,
	UNIT CHARACTER VARYING,
	SCP CHARACTER VARYING,
	STATION CHARACTER VARYING,
	LINENAME CHARACTER VARYING,
	DIVISION CHARACTER VARYING,
	DATE DATE,
	TIME TIME,
	DESCRIPTION CHARACTER VARYING,
	ENTRIES INT,
	EXITS INT
);






CREATE OR REPLACE VIEW public.stationLocations 
AS
SELECT station_name, AVG(station_latitude) station_latitude, AVG(station_longitude) station_longitude
FROM stationentrances
GROUP BY station_name
ORDER BY 1;
