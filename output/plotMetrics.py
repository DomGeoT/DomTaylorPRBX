import matplotlib.pyplot as plt

from dataAnalysis.cointegrationTesting import *


def plotPair(symbol1, symbol2, attribute):
    stockData = getStockData([symbol1, symbol2])
    startDate, startTime, endDate, endTime = getDateRangeOfTurtleFile('../data/financialData.ttl')

    print(stockData)
    print(startDate, startTime, endDate, endTime)

    timestamps = generateTimeStamps(startDate, startTime, endDate, endTime)

    stock1TimeStamps = []
    stock1Values = []

    stock2TimeStamps = []
    stock2Values = []

    xTickLabels = []
    xTickPositions = []
    currentDay = -1
    for i in range(len(timestamps)):
        # check datapoint exists at this date+time for symbol1
        dt = timestamps[i]
        if not currentDay == dt[0]:
            xTickLabels.append(dt[0].__str__())
            xTickPositions.append(i)

            currentDay = dt[0]


        if dt[0] in stockData[symbol1]:
            if dt[1] in stockData[symbol1][dt[0]]:
                stock1TimeStamps.append(i)
                stock1Values.append(stockData[symbol1][dt[0]][dt[1]][attribute])

        if dt[0] in stockData[symbol2]:
            if dt[1] in stockData[symbol2][dt[0]]:
                stock2TimeStamps.append(i)
                stock2Values.append(stockData[symbol2][dt[0]][dt[1]][attribute])

    plt.plot(stock1TimeStamps, stock1Values, c='r', label=symbol1)
    plt.plot(stock2TimeStamps, stock2Values, c='b', label=symbol2)
    plt.xticks(xTickPositions, xTickLabels)
    plt.gca().xaxis.grid(b=True, which='major', color='#666666', linestyle='-')
    plt.legend()
    plt.title(symbol1 + ' and ' + symbol2 + ' stock price between:\n' + startDate.__str__() + ' ' + startTime.__str__() + ' and ' + endDate.__str__() + ' ' + endTime.__str__())
    plt.xlabel('Time')
    plt.ylabel('Stock price: ' + attribute)
    plt.show()


def plotCointegrationVsDatasetSize():
    with open('../data/cointVals.json', 'r') as fp:
        cointegrationData = json.load(fp)

    pVals = []
    size = []

    for key in cointegrationData.keys():
        pVals.append(cointegrationData[key]["pvalue"])
        size.append(cointegrationData[key]["datasetSize"])

    plt.scatter(size, pVals)
    plt.xlabel('Dataset size')
    plt.ylabel('Cointegration p value')
    plt.title('Cointegration p value VS Dataset size')
    plt.show()


def plotCointPValHistorgram():
    pvalues = []
    with open('../data/cointVals.json', 'r') as fp:
        cVals = json.load(fp)
    print(len(cVals.keys()))
    for key, value in sorted(cVals.items(), key=lambda item: item[1]['pvalue'], reverse=True):
        print("%s: %s" % (key, value))

        pvalues.append(value['pvalue'])

    plt.hist(pvalues, bins=20, edgecolor='black', linewidth=1.2)
    plt.title('Histogram of the distribution of cointegration \'pvalues\'')
    plt.xlabel('Cointegration \'pvalue\'')
    plt.ylabel('Frequency Density')
    plt.show()



if __name__ == '__main__':
    plotCointPValHistorgram()
    plotCointegrationVsDatasetSize()
    plotPair('GOOGL', 'GOOG', 'open')

