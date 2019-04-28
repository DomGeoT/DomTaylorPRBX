import urllib.request
from utils import *


# collects data from NASDAQ market
# opens   0930 Eastern -> 1430 GMT
# closes  1600 Eastern -> 2100 GMT

# data collection occurs at approximately 2200 GMT

@retry(60, 5)
def requestStockData(symbol):
    '''
    fetches the minutely stock data for the previous 5 days
    stores data in csv file called query.csv

    :param symbol: stock symbol of stock to get data of
    '''
    urllib.request.urlretrieve("https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=" + symbol + "&interval=1min&outputsize=full&apikey=2S3GL20FT2RNU6O0&datatype=csv", "query.csv")

def convertToRDFString(symbol, date, timestamp, openValue, closeValue, highValue, lowValue, volValue):
    '''
    converts the given stock data to rdf string format

    :param symbol: stock's symbol
    :param date: date of data collection
    :param timestamp: time of data collect
    :param openValue: stock's opening value
    :param closeValue: stock's closing value
    :param highValue: stock's high value
    :param lowValue: stocks's low value
    :param volValue: stock's volume
    :return: rdf string of stock data
    '''
    rdfString = ""

    datapointID = str(symbol) + str(date) + str(timestamp)

    rdfString += "<Datapoint/ID={}> rdf:type dbpedia2:observationData . \n".format(datapointID)
    rdfString += "<Datapoint/ID={}> <Datapoint#ID> '{}' . \n".format(datapointID, datapointID)
    rdfString += "<Datapoint/ID={}> dbpedia2:symbol '{}' . \n".format(datapointID, symbol)
    rdfString += "<Datapoint/ID={}> xsd:date '{}' . \n".format(datapointID, date)
    rdfString += "<Datapoint/ID={}> xsd:time '{}' . \n".format(datapointID, timestamp)

    rdfString += "<Datapoint/ID={}> <Datapoint/open> '{}' . \n".format(datapointID, openValue)
    rdfString += "<Datapoint/ID={}> <Datapoint/close> '{}' . \n".format(datapointID, closeValue)
    rdfString += "<Datapoint/ID={}> <Datapoint/high> '{}' . \n".format(datapointID, highValue)
    rdfString += "<Datapoint/ID={}> <Datapoint/low> '{}' . \n".format(datapointID, lowValue)
    rdfString += "<Datapoint/ID={}> <Datapoint/volume> '{}' . \n\n".format(datapointID, volValue)

    return rdfString


def storeStockData(symbol, storeName):
    if not os.path.isdir("../data"):
        os.mkdir("../data")

    collatedDataFile = open("../data/{}".format(storeName), "a+")
    collatedDataFile.write("@prefix xsd: <http://www.w3.org/2001/XMLSchema#>\n")
    collatedDataFile.write("@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>\n")
    collatedDataFile.write("@prefix dbpedia2: <http://dbpedia.org/property/>\n\n")

    # check to see if day already included
    dailyDataFile = open("query.csv", "r")

    data = dailyDataFile.readlines()
    dailyDataFile.close()

    firstLine = True
    for line in data:
        if firstLine:
            firstLine = False
            continue

        splitData = line.strip().split(",")
        date = splitData[0].split(" ")[0]
        timestamp = splitData[0].split(" ")[1]

        openValue = float(splitData[1])
        closeValue = float(splitData[2])
        highValue = float(splitData[3])
        lowValue = float(splitData[4])
        volValue = int(splitData[5])

        rdfString = convertToRDFString(symbol, date, timestamp, openValue, closeValue, highValue, lowValue, volValue)
        collatedDataFile.write(rdfString)

    collatedDataFile.close()

def loadSymbols():
    symbols = open("symbols.txt", "r")

    text = symbols.read()
    return text.split("\n")

def collectStockData(symbol, storeName):
    requestStockData(symbol)
    storeStockData(symbol, storeName)

def runDataCollection(storeName, symbols):
    print(symbols)
    lastAPICall = datetime.datetime.now()

    for company in symbols:
        while (datetime.datetime.now() - lastAPICall).seconds < 15:
            time.sleep(1)

        try:
            print("Collecting data for", company)
            lastAPICall = datetime.datetime.now()
            collectStockData(company, storeName)
        except Exception as e:
            print("WARNING error caught when executing data collection for", company)
            log = open('log.txt', 'a+')
            log.write(str("{} Data collection failed for symbol at on {} \n".format(company, str(datetime.datetime.now()))))
            log.close()
        finally:
            os.remove("query.csv")