-- create db 
CREATE DATABASE DrugOverdoseData;

-- use db
USE DrugOverdoseData;

-- Create table
CREATE TABLE DrugOverdoseDeaths (
    Indicator VARCHAR(255),
    Panel VARCHAR(255),
    Panel_Num INT,
    Unit VARCHAR(255),
    Unit_Num INT,
    Stub_Name VARCHAR(255),
    Stub_Name_Num INT,
    Stub_Label VARCHAR(255),
    Stub_Label_Num FLOAT,
    Year INT,
    Year_Num INT,
    Age VARCHAR(255),
    Age_Num FLOAT,
    Estimate FLOAT,
    Flag VARCHAR(255)
);

-- check count of records
SELECT COUNT(*) FROM DrugOverdoseDeaths;

-- Annual Trends: Aggregating the data to see trends over years.
SELECT Year, SUM(Estimate) AS TotalDeaths
FROM DrugOverdoseDeaths
GROUP BY Year
ORDER BY Year;

-- Comparsion by Drug Type for year 2018
SELECT Panel, Year, SUM(Estimate) AS TotalDeaths
FROM DrugOverdoseDeaths
WHERE Year = 2018
GROUP BY Panel, Year
ORDER BY TotalDeaths DESC;

-- Comparsion by Age group for year 2018
SELECT Age, SUM(Estimate) AS TotalDeaths
FROM DrugOverdoseDeaths
WHERE Year = 2018
GROUP BY Age
ORDER BY TotalDeaths DESC;

-- Specficly focusing on overdose deaths from heroin
SELECT Year, SUM(Estimate) AS TotalDeaths
FROM DrugOverdoseDeaths
WHERE Panel LIKE '%heroin%'
GROUP BY Year
ORDER BY Year;

-- This Calculates the mean, max, and min drug overdose death rate per 100,000 after the year 2010 
SELECT AVG(Estimate) AS AverageDeaths, MAX(Estimate) AS MaxDeaths, MIN(Estimate) AS MinDeaths
FROM DrugOverdoseDeaths
WHERE Year > 2010;

-- The mean of overdose deaths per 100,000 specific to each drug
SELECT Panel, AVG(Estimate) AS AverageDeaths
FROM DrugOverdoseDeaths
GROUP BY Panel
ORDER BY AverageDeaths DESC;

-- How deaths by heroin overdose trends over the years
SELECT Year, Panel, SUM(Estimate) AS TotalDeaths
FROM DrugOverdoseDeaths
WHERE Panel LIKE '%\heroin%'
GROUP BY Year, Panel
ORDER BY Year, Panel;

-- Overdose deaths for Non-Hispanic Black population in 2018
SELECT STUB_LABEL AS Demographic, SUM(Estimate) AS TotalDeaths
FROM DrugOverdoseDeaths
WHERE Year = 2018 AND STUB_LABEL LIKE '%Black%' AND STUB_LABEL NOT LIKE '%Hispanic%'
GROUP BY STUB_LABEL
ORDER BY TotalDeaths DESC;

-- Overdose deaths for Non-Hispanic Black/White/Asian populations in 2018
SELECT STUB_LABEL AS Demographic, SUM(Estimate) AS TotalDeaths
FROM DrugOverdoseDeaths
WHERE Year = 2018 AND STUB_LABEL REGEXP 'Black|White|Asian' and STUB_LABEL NOT LIKE '%Hispanic%'
GROUP BY STUB_LABEL
ORDER BY TotalDeaths DESC;

-- Male total deaths after the year 2010
SELECT 
    CASE 
        WHEN STUB_LABEL LIKE '%Male%' THEN 'Male'
    END AS Gender,
    SUM(Estimate) AS TotalDeaths
FROM DrugOverdoseDeaths
WHERE Year > 2010 AND (STUB_LABEL LIKE '%Male%')
GROUP BY Gender
ORDER BY TotalDeaths DESC;

-- Female total deaths after the year 2010
SELECT 
    CASE 
        WHEN STUB_LABEL LIKE '%Female%' THEN 'Female'
    END AS Gender,
    SUM(Estimate) AS TotalDeaths
FROM DrugOverdoseDeaths
WHERE Year > 2010 AND (STUB_LABEL LIKE '%Female%')
GROUP BY Gender
ORDER BY TotalDeaths DESC;
