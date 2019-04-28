import statsmodels
import statsmodels.api
import itertools
from utils import *


def extractStockData(stockData):
    '''
    converts JSON data into dictionary

    SYMBOL
      |
      +--Date
          |
          +--Time
              |
              +--Attributes...
              |
              +--Attributes...

    :param stockData: stockdata collected as result of JSON query
    :return: dictionary form of stock data
    '''

    results = dict()

    for entry in stockData:
        entrySymbol = entry['symbol']['value']
        entryDate = datetime.datetime.strptime(entry['date']['value'], '%Y-%m-%d').date()
        entryTime = datetime.datetime.strptime(entry['time']['value'], '%H:%M:%S').time()

        entryAttributes = dict()
        attributes = ['open', 'close', 'high', 'low', 'volume']
        # open
        for attribute in attributes:
            if attribute in entry:
                entryAttributes.update({attribute : float(entry[attribute]['value'])})

        if not entrySymbol in results.keys():
            results[entrySymbol] = {entryDate : {entryTime : entryAttributes}}
        elif not entryDate in results[entrySymbol].keys():
            results[entrySymbol][entryDate] = {entryTime : entryAttributes}
        elif not entryTime in results[entrySymbol][entryDate].keys():
            results[entrySymbol][entryDate].update({entryTime : entryAttributes})

    return results


def constructStockDataExtractQuery(symbols):
    symbolUnions = ''

    for i in range(len(symbols)):
        symbolUnions += '{ ?datapoint1 dbpedia2:symbol \'' + symbols[i] + '\' }'

        if i < len(symbols) - 1:
            symbolUnions += ' UNION '
    symbolUnions += ' .'


    return '''PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX dbpedia2: <http://dbpedia.org/property/>
    
    SELECT DISTINCT ?symbol ?date ?time ?open ?close ?high ?low ?volume WHERE
    {
    ''' + symbolUnions + '''
        ?datapoint1 dbpedia2:symbol ?symbol .
        ?datapoint1 xsd:date ?date .
        ?datapoint1 xsd:time ?time .
        ?datapoint1 <Datapoint/open> ?open .
        ?datapoint1 <Datapoint/close> ?close .
        ?datapoint1 <Datapoint/high> ?high .
        ?datapoint1 <Datapoint/low> ?low .
        ?datapoint1 <Datapoint/volume> ?volume .	
    } ORDER BY ?time     
    '''


def getDateRangeOfTurtleFile(turtleFileName):
    '''
    finds the earliest startDate and startTime and latest endDate and endTime

    :param turtleFileName: file to check dates in
    :return: earliest startDate and startTime and latest endDate and endTime
    '''
    queryResults = executeQuery(turtleFileName, '../queries/dataQueries/dateRangeQuery.rq')
    startDate = datetime.datetime.strptime(queryResults[0]['date']['value'], '%Y-%m-%d').date()
    startTime = datetime.datetime.strptime(queryResults[0]['time']['value'], '%H:%M:%S').time()
    endDate = datetime.datetime.strptime(queryResults[-1]['date']['value'], '%Y-%m-%d').date()
    endTime = datetime.datetime.strptime(queryResults[-1]['time']['value'], '%H:%M:%S').time()

    return startDate, startTime, endDate, endTime

def testForCointegration(stockData, attribute, symbol1, symbol2, startDate, startTime, endDate, endTime):
    '''
    using the provided stock data runs a cointegration test on the 2 given symbols for the data points between the specified times
    discards incomplete datapoints i.e. if symbol1 has a value at 2018-12-17 09:31:00 but symbol2 doesn't then symbol1's datapoint will be discarded

    :param stockData:
    :param attribute:
    :param symbol1:
    :param symbol2:
    :param startDate:
    :param startTime:
    :param endDate:
    :param endTime:
    :return:
    '''
    # check that stockData contains the relevant symbols
    if not symbol1 in stockData.keys() or not symbol2 in stockData.keys():
        # missing either symbol1 or symbol2 from stock data
        raise RuntimeError('Cannot perform cointegration test due to missing stock symbol')

    timestamps = generateTimeStamps(startDate, startTime, endDate, endTime)

    dataSet1 = []
    dataSet2 = []

    for dt in timestamps:
        # check datapoint exists at this date+time for symbol1
        if dt[0] in stockData[symbol1]:
            if dt[1] in stockData[symbol1][dt[0]]:
                pass
            else:
                continue
        else:
            continue

        # check datapoint exists at this date+time for symbol1
        if dt[0] in stockData[symbol2]:
            if not dt[1] in stockData[symbol2][dt[0]]:
                continue
        else:
            continue

        # both datapoints exist
        dataSet1.append(stockData[symbol1][dt[0]][dt[1]][attribute])
        dataSet2.append(stockData[symbol2][dt[0]][dt[1]][attribute])

    if len(dataSet1) < 10:
        print('WARNING only {} datapoints available for pair {} and {}'.format(len(dataSet1), symbol1, symbol2))

    return statsmodels.tsa.stattools.coint(dataSet1, dataSet2), len(dataSet1)


def getStockData(symbols):
    cmd = constructStockDataExtractQuery(symbols)
    queryRes = executeQueryString("../data/financialData.ttl", cmd)
    stockData = extractStockData(queryRes)
    return stockData


def calculateCointegrationValues(turtleFileName, attribute, datasetSizeThreshold = 100):
    symbolsInTurtleFile = getSymbolsFromTurtle(turtleFileName)
    sd, st, ed, et = getDateRangeOfTurtleFile(turtleFileName)
    stockData = getStockData(symbolsInTurtleFile)

    cointVals = dict()

    for symbolPair in itertools.combinations(symbolsInTurtleFile, 2):
        try:
            val, datasetSize = testForCointegration(stockData, attribute, symbolPair[0], symbolPair[1], sd, st, ed, et)

            if datasetSize < datasetSizeThreshold: # check pair meets minimum number of datapoints
                continue

            d = dict()
            d['coint_t'] = val[0]
            d['pvalue'] = val[1]
            d['crit_value'] = val[2].tolist()
            d['datasetSize'] = datasetSize

            cointVals[getSymbolPairKey(symbolPair[0], symbolPair[1])] = d
        except Exception as e:
            print('error occurred whilst testing {} and {}'.format(symbolPair[0], symbolPair[1]))
            print(e)
            print()

    return cointVals


