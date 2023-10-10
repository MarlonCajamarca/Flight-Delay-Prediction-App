# Fligh Delay Prediction Application

## Overview

The following is an end-to-end example of how to build a machine learning model, deploy it as an API, and test it for an specific use case: flight delay prediction. The model was trained with public and real data, and it was deployed in an AWS Lambda function. The API was built with FastAPI and it was deployed in a Docker container. The CI/CD pipeline was built with GitHub Actions. The entire workflow was automated with a Makefile and can be use as a template for future projects.

## Problem

A jupyter notebook (`exploration.ipynb`) has been provided with the work of a Data Scientist (from now on, the DS). The DS, trained a model to predict the probability of **delay** for a flight taking off or landing at SCL airport. The model was trained with public and real data, below we provide you with the description of the dataset:

|Column|Description|
|-----|-----------|
|`Fecha-I`|Scheduled date and time of the flight.|
|`Vlo-I`|Scheduled flight number.|
|`Ori-I`|Programmed origin city code.|
|`Des-I`|Programmed destination city code.|
|`Emp-I`|Scheduled flight airline code.|
|`Fecha-O`|Date and time of flight operation.|
|`Vlo-O`|Flight operation number of the flight.|
|`Ori-O`|Operation origin city code.|
|`Des-O`|Operation destination city code.|
|`Emp-O`|Airline code of the operated flight.|
|`DIA`|Day of the month of flight operation.|
|`MES`|Number of the month of operation of the flight.|
|`AÑO`|Year of flight operation.|
|`DIANOM`|Day of the week of flight operation.|
|`TIPOVUELO`|Type of flight, I =International, N =National.|
|`OPERA`|Name of the airline that operates.|
|`SIGLAORI`|Name city of origin.|
|`SIGLADES`|Destination city name.|

In addition, the DS considered relevant the creation of the following columns:

|Column|Description|
|-----|-----------|
|`high_season`|1 if `Date-I` is between Dec-15 and Mar-3, or Jul-15 and Jul-31, or Sep-11 and Sep-30, 0 otherwise.|
|`min_diff`|difference in minutes between `Date-O` and `Date-I`|
|`period_day`|morning (between 5:00 and 11:59), afternoon (between 12:00 and 18:59) and night (between 19:00 and 4:59), based on `Date-I`.|
|`delay`|1 if `min_diff` > 15, 0 if not.|

## Workflow

### Instructions

1. Use the **main** branch for any official release that we should review. It is highly recommended to use [GitFlow](https://www.atlassian.com/git/tutorials/comparing-workflows/gitflow-workflow) development practices. **NOTE: do not delete your development branches.**
      
2. All the documentation and explanations that you have to give, must go in the `challenge.md` file inside `docs` folder.

### Context:

We need to operationalize the data science work for the airport team. For this, we have decided to enable an `API` in which they can consult the delay prediction of a flight.

### Part I

In order to operationalize the model, transcribe the `.ipynb` file into the `model.py` file:

- The DS proposed a few models in the end. Choose the best model at your discretion, argue why.
- Apply all the good programming practices that you consider necessary in this item.
- The model should pass the tests by running `make model-test`.

### Part II

Deploy the model in an `API` with `FastAPI` using the `api.py` file.

- The `API` should pass the tests by running `make api-test`.

### Part III

Deploy the `API` in your favorite cloud provider.

- Put the `API`'s url in the `Makefile` (`line 26`).
- The `API` should pass the tests by running `make stress-test`.

### Part IV

Implement a proper `CI/CD` implementation for this development. For this, you must use Github Actions.

- Complete both `ci.yml` and `cd.yml`(consider what you did in the previous parts).