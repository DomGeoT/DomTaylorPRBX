import os
import json
import datetime
from SPARQLWrapper import SPARQLWrapper, JSON
import time
from subprocess import check_output

def executeQueryString(dataFilename, queryString):
    with open('../data/tempQuery.rq', 'w+') as f:
        f.write(queryString)
    res = executeQuery(dataFilename, '../data/tempQuery.rq')
    os.remove('../data/tempQuery.rq')
    return res


def executeQuery(dataFileName, queryFileName):
    '''
    executes the supplied query on the given data file
    query output is sent to a temp.json file which is read into a dictionary and the temp file removed
    the dictionary results is then returned

    :param dataFileName: path to data file relative to this python file
    :param queryFileName: path to query file relative to this python file
    :return: dictionary containing query output
    '''

    print(os.getcwd())

    command = 'arq --data \"{}\" --query \"{}\" --results=JSON > tempResults.json'.format(dataFileName, queryFileName)
    print(command)
    print(check_output("cd", shell=True).decode())

    check_output(command, shell=True)

    with open('tempResults.json', 'r') as f:
        queryResults = json.load(f)
    os.remove("tempResults.json")

    return queryResults["results"]["bindings"]


def getSymbolPairKey(symbol1, symbol2):
    x = [symbol1, symbol2]
    x.sort()
    return x[0] + '*' + x[1]


def retry(delay, attempts):
    def wrapper(func):
        def wrapped(*args, **kwargs):
            for i in range(attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    print(str(e))
                    print("failure after attempt", attempts, "- retrying in...", delay)
                    time.sleep(delay * (i + 1))
        return wrapped
    return wrapper


@retry(60, 10)
def queryEndpoint(query):
    sparql = SPARQLWrapper("http://dbpedia.org/sparql")
    sparql.setReturnFormat(JSON)

    sparql.setQuery(query)  # the previous query as a literal string

    return sparql.query().convert()


def generateTimeStamps(startDate, startTime, endDate, endTime):
    '''
    generates an array of tuples (date, time) for every minute between the start and end date/time
    only generates times between 0930 and 1600 and only monday to friday

    :param startDate: date object of when to begin generating timestamps from (inclusive)
    :param startTime: time object of when to begin generating timestamps from (inclusive)
    :param endDate: date object of when to generate timestamps upto
    :param endTime: time object of when to generate timestamps upto
    :return: array of tuples of timestamps between specified dates and times
    '''
    timestamps = []
    currentDate = startDate
    currentTime = startTime

    while True:
        timestamps.append((currentDate, currentTime))
        currentTime = (datetime.datetime(1, 1, 1, currentTime.hour, currentTime.minute) + datetime.timedelta(minutes = 1)).time() # go to next minute

        if currentDate >= endDate and currentTime > endTime:
            break

        if currentTime > datetime.time(16, 0):
            # after 16:00, goto next morning
            currentTime = datetime.time(9, 31)

            currentDate = currentDate + datetime.timedelta(days=1)
            if currentDate.weekday() == 5:
                # week has ended, goto next monday
                currentDate = currentDate + datetime.timedelta(days = 2)
    return timestamps


def getSymbolsFromTurtle(turtleFileName):
    '''

    :param turtleFileName:
    :return: list of string of symbols in the provided turtle file
    '''
    symbols = executeQuery(turtleFileName, '../queries/dataQueries/symbolsQuery.rq')
    output = []
    for symbol in symbols:
        output.append(symbol['symbol']['value'])
    return output