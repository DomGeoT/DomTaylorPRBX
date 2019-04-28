import math

import matplotlib.pyplot as plt
import scipy.stats

from dataAnalysis.ontologyScoring import *
from output.updateSetupData import *


def plotCointegrationVsOntologyDistances(cointegrationData, distances):
    cointVals = []
    ontologyVals = []
    for key in list(set(cointegrationData.keys()) & set(distances.keys())):
        #if distances[key] == [0, 0]:
         #   continue
        cointVals.append(cointegrationData[key]["pvalue"])
        ontologyVals.append(math.log(1 + distances[key][1] + 100 * distances[key][0]))

    plt.scatter(cointVals, ontologyVals)
    plt.xlabel('Cointegration \'pvalue\'')
    plt.ylabel('High Cointegration Predictor')
    plt.title('Pair of stocks Cointegration \'pvalue\' plotted against the\nHigh Cointegration Predictor for the pair')
    plt.show()

    print(len(cointVals))
    print(len(ontologyVals))
    print('SPEARMAN DISTANCE TEST', scipy.stats.spearmanr(cointVals, ontologyVals))


def getOntologyDistances(update, uriSymbolsDict):
    if update:
        ontologyDistances = calculateOntologyDistances(uriSymbolsDict)
        with open('../data/ontologyDistances.json', 'w') as fp:
            json.dump(ontologyDistances, fp)

    else:
        with open('../data/ontologyDistances.json', 'r') as fp:
            ontologyDistances = json.load(fp)

    return ontologyDistances

if __name__ == '__main__':
    compTriples = getCompanyTriples(False)
    cointegrationValues = getCointegrationVals(False, False, compTriples, 'open', 100)
    ontDistances = getOntologyDistances(False, compTriples)

    plotCointegrationVsOntologyDistances(cointegrationValues, ontDistances)