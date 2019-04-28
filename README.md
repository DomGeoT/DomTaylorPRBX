# QUICK START
You should only need to run files within the output directory.

## updateSetupData.py
This program is used to setup the datafiles for the first time or update existing ones.

## plotMetrics.py
Draws some plots for general data analysis.

## calcDistanceScoresMethod1.py
Code for testing method 1 described in the main report.

## calcSignficantRelationsMethod2.py
Code for testing method 2 described in the main report.

# DATAFILES
## companylist.csv 
List of companies traded on the NASDAQ exchange

## financialData.ttl
Turtle file containing the last set of finance data downloaded from Alpha Vantage stored in turtle format

## symbolURIPairs.ttl and symbolURIPairsManual.ttl
The first file contains triples of company URIs and their stock symbols automatically identified through DBpedia. The second contains the same type of information but manually identified.

## cointVals.json
Stores last calculated cointegration values

## ontologyDistances.json
Stores last calculated distances - for method 1

## significantRelationsDist1.json and significantRelationsDist2.json
Stores last calculated significant relations identified in stage one of method two - for distance 1 and distance 2 respectively



 