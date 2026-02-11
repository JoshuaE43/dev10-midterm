DROP DATABASE IF EXISTS demographics;
CREATE DATABASE demographics;
USE demographics;

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

  pop%_0_14 FLOAT,
  pop%_15_19 FLOAT,
  pop%_20_39 FLOAT,
  pop%_40_64 FLOAT,
  pop%_65_plus FLOAT,

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
