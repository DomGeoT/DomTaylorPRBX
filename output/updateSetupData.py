from dataAnalysis.cointegrationTesting import *
from dataCollection.runDataCollection import *

from dataCollection.dataCollector import runDataCollection
from dataCollection.symbolURIPairCollector import *
from utils import *


def genURISymbolDict():
    companyUriPairs = dict()  # dictionary mapping companyURI -> symbol
    for uriSymbol in executeQuery("../data/symbolURIPairs.ttl", "../queries/dataQueries/symbolsUriQuery.rq"):
        companyUriPairs[uriSymbol['companyURI']['value']] = uriSymbol['symbol']['value']
    for uriSymbol in executeQuery("../data/symbolURIPairsManual.ttl", "../queries/dataQueries/symbolsUriQuery.rq"):
        companyUriPairs[uriSymbol['companyURI']['value']] = uriSymbol['symbol']['value']
    return companyUriPairs


def getCompanyTriples(update):
    if update:
        findCompanies()  # generates ../data/symbolURIPairs.ttl

    return genURISymbolDict()  # generates dictionary from file ../data/symbolURIPairs.ttl


def getCointegrationVals(downloadFinanceData, recalculateValues, uriSymbolsDict, attribute, datasetSizeThreshold):
    if downloadFinanceData:
        runDataCollection("../data/financialData.ttl", uriSymbolsDict.values())  # collects past 5 day stock market data for symbols in
        cVals = calculateCointegrationValues("../data/financialData.ttl", attribute, datasetSizeThreshold=datasetSizeThreshold)
        with open('../data/cointVals.json', 'w') as fp:
            json.dump(cVals, fp)
    else:
        if recalculateValues:
            cVals = calculateCointegrationValues("../data/financialData.ttl", attribute, datasetSizeThreshold=datasetSizeThreshold)
            with open('../data/cointVals.json', 'w') as fp:
                json.dump(cVals, fp)
        else:
            with open('../data/cointVals.json', 'r') as fp:
                cVals = json.load(fp)
    return cVals


if __name__ == '__main__':
    updateCompanyTriples = False

    updateFinanceData = False  # redownloads stock data based on triples in symbolURIPairs.ttl and symbolURIPairsManual.ttl
    recalcCointVals = False  # use existing financial data in financialData.ttl

    compTriples = getCompanyTriples(updateCompanyTriples)
    cointegrationValues = getCointegrationVals(updateFinanceData, recalcCointVals, compTriples, 'open', 100)