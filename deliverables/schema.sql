DROP DATABASE IF EXISTS demographics;
CREATE DATABASE demographics;
USE demographics;

DROP TABLE IF EXISTS population_stats;
DROP TABLE IF EXISTS fertility_stats;
DROP TABLE IF EXISTS countries;


CREATE TABLE countries (
  alpha_2 CHAR(2) PRIMARY KEY,
  name VARCHAR(255),
  region VARCHAR(255)
);

CREATE TABLE population_stats (
  alpha_2 CHAR(2),
  year INT,

  population BIGINT,
  median_age FLOAT,

  pct_0_14 FLOAT,
  pct_15_19 FLOAT,
  pct_20_39 FLOAT,
  pct_40_64 FLOAT,
  pct_65_plus FLOAT,

  PRIMARY KEY (alpha_2, year),
  FOREIGN KEY (alpha_2)
    REFERENCES countries(alpha_2)
);

CREATE TABLE fertility_stats (
  alpha_2 CHAR(2),
  year INT,

  births BIGINT,
  tfr FLOAT,

  PRIMARY KEY (alpha_2, year),
  FOREIGN KEY (alpha_2)
    REFERENCES countries(alpha_2)
);


SELECT * 
FROM fertility_stats;

