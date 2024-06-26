alter session set "_ORACLE_SCRIPT"=true;
CREATE TABLESPACE store_tables DATAFILE 'STORE_FILES_01.dbf' SIZE 500m;

CREATE TEMPORARY TABLESPACE store_temp TEMPFILE 'STORE_TEMP_01.dbf' SIZE 500m;

CREATE USER store IDENTIFIED BY &senha 
    DEFAULT TABLESPACE store_tables
    TEMPORARY TABLESPACE store_temp QUOTA
        UNLIMITED ON store_tables ;

GRANT CONNECT, RESOURCE, CREATE VIEW, CREATE SEQUENCE TO store;