/****************************************************************
 * PostgreSQL Install Scripts for rain server
 * Schema Version: 0.0.20220411
 ****************************************************************/

-- Create application table if not exists
create table IF NOT EXISTS o_applications (
    application_id varchar(128) not null primary key,
    tables_version varchar(30) not null,
    pg_created_utc timestamp not null default timezone('utc', now()),
    pg_updated_utc timestamp not null default timezone('utc', now())
)
;

create table if not exists d_locations (
    location_id varchar(128) not null primary key,
    location_name varchar(255) not null,
    location_tz varchar(100) not null default 'UTC',
    pg_created_utc timestamp not null default timezone('utc', now()),
    pg_updated_utc timestamp not null default timezone('utc', now())
)
;

create table d_sensors (
    sensor_id varchar(128) not null primary key,
    sensor_name varchar(100) not null unique,
    location_id varchar(128) not null,
    pg_created_utc timestamp not null default timezone('utc', now()),
    pg_updated_utc timestamp not null default timezone('utc', now())
)
;

create table d_measurements_units(
    measurement_name varchar(300) primary key,
    measurement_unit varchar(32) null
)
;

create table d_measurements(
    sensor_id varchar(128) not null,
    measurement_name varchar(300) not null,
    reporting_date_utc timestamp not null,
    measurement_value numeric(36,15),
    constraint pk_d_measurements primary key (sensor_id, measurement_name, reporting_date_utc)
)
;

create index d_measurements_date_index on d_measurements (reporting_date_utc);

insert into o_applications(application_id, tables_version) VALUES ('rain-server', '0.1.20220411');
