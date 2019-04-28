import random
from output.calcDistanceScoresMethod1 import *


def runTrainingDist1(training):
    cointVals = getCointegrationVals(False, False, None, 'open', 100)
    print(cointVals)
    with open('../queries/endpointQueries/dist1RelationCheck.rq') as queryFile:
        query = queryFile.read()

    relationFrequency = dict()

    for companyPair in itertools.combinations(training.keys(), 2):
        symbolPair = getSymbolPairKey(training[companyPair[0]], training[companyPair[1]])
        if not symbolPair in cointVals:
            continue
        tempQ = query.replace("{companyURI1}", companyPair[0]).replace("{companyURI2}", companyPair[1])
        queryRes = queryEndpoint(tempQ)['results']['bindings']
        print(queryRes)
        for relation in queryRes:
            relationKey = relation['a']['value']
            if not relationKey in relationFrequency:
                relationFrequency[relationKey] = []
            relationFrequency[relationKey].append(cointVals[symbolPair]['pvalue'])
            print(companyPair, relation)

    with open('../data/significantRelationsDist1.json', 'w+') as file:
        json.dump(relationFrequency, file)


def runTestDist1(test):
    with open('../data/significantRelationsDist1.json', 'r') as fp:
        relationFrequency = json.load(fp)

    with open('../queries/endpointQueries/dist1FindPairs.rq') as queryFile:
        query = queryFile.read()

    queries = []
    for relation in sorted(relationFrequency, key=lambda k: len(relationFrequency[k])): # generate query structures
        h = sum(relationFrequency[relation]) / len(relationFrequency[relation])
        if h < 0.05:
            queries.append(query.replace('{relation}', relation))

    results = dict()
    for q in queries:
        results[q] = dict()
        for companyPair in itertools.combinations(test.keys(), 2):
            symbolPair = getSymbolPairKey(test[companyPair[0]], test[companyPair[1]])
            q2 = q.replace('{companyURI1}', companyPair[0]).replace('{companyURI2}', companyPair[1])
            res = queryEndpoint(q2)
            if len(res['results']['bindings']) > 0:
                print(companyPair, res)

            results[q][symbolPair] = res



def runTrainingDist2(training):
    cointegrationValues = getCointegrationVals(False, False, None, 'open', 100)
    print(cointegrationValues)
    with open('../queries/endpointQueries/dist2RelationCheck.rq') as queryFile:
        query = queryFile.read()

    relationFrequency = dict()

    for companyPair in itertools.combinations(training.keys(), 2):
        symbolPair = getSymbolPairKey(training[companyPair[0]], training[companyPair[1]])
        if not symbolPair in cointegrationValues:
            continue
        tempQ = query.replace("{companyURI1}", companyPair[0]).replace("{companyURI2}", companyPair[1])
        queryRes = queryEndpoint(tempQ)['results']['bindings']

        for relation in queryRes:
            relationKey = getSymbolPairKey(relation['a']['value'], relation['c']['value'])
            if not relationKey in relationFrequency:
                relationFrequency[relationKey] = []
            relationFrequency[relationKey].append(cointegrationValues[symbolPair]['pvalue'])


    with open('../data/significantRelationsDist2.json', 'w+') as file:
        json.dump(relationFrequency, file)



def runTestDist2(test):
    with open('../data/significantRelationsDist2.json', 'r') as fp:
        relationFrequency = json.load(fp)

    with open('../queries/endpointQueries/dist2FindPairs.rq') as queryFile:
        query = queryFile.read()

    queries = []
    for relation in sorted(relationFrequency, key=lambda k: len(relationFrequency[k])): # generate query structures
        h = sum(relationFrequency[relation]) / len(relationFrequency[relation])
        if h < 0.05:
            splitRelation = relation.split('*')
            queries.append(query.replace('{relationA}', splitRelation[0]).replace('{relationC}', splitRelation[1]))

    results = dict()
    for q in queries:
        results[q] = dict()
        for companyPair in itertools.combinations(test.keys(), 2):
            symbolPair = getSymbolPairKey(test[companyPair[0]], test[companyPair[1]])
            q2 = q.replace('{companyURI1}', companyPair[0]).replace('{companyURI2}', companyPair[1])
            res = queryEndpoint(q2)
            if len(res['results']['bindings']) > 0:
                print(companyPair, res)

            results[q][symbolPair] = res


def plotDist1Results():
    labels = []
    heights = []

    with open('../data/significantRelationsDist1.json', 'r') as fp:
        relFreqs = json.load(fp)

    for relation in sorted(relFreqs, key=lambda k: len(relFreqs[k])):
        labels.append(math.log(len(relFreqs[relation])))
        h = sum(relFreqs[relation]) / len(relFreqs[relation])
        heights.append(h)
        if h < 0.05:
            shortRel = relation.replace('http://dbpedia.org/ontology/', 'dbo:').replace('http://dbpedia.org/property/',
                                                                                        'dbp:').split('*')
            print(str(shortRel) + ' & ' + str(round(h, 4)) + ' & ' + str(len(relFreqs[relation])) + ' \\\ ')

    plt.title('Mean Cointegration \'pvalue\' plotted against\nthe log frequency of the relation occurring (distance 1)')
    plt.xlabel('Mean Cointegration \'pvalue\'')
    plt.ylabel('Log frequency of the relation')
    plt.scatter(heights, labels)
    plt.show()


def plotDist2Results():
    labels = []
    heights = []

    with open('../data/significantRelationsDist2.json', 'r') as fp:
        relFreqs = json.load(fp)

    for relation in sorted(relFreqs, key=lambda k: len(relFreqs[k])):
        labels.append(math.log(len(relFreqs[relation])))
        # labels.append(len(relFreqs[relation]))
        h = sum(relFreqs[relation]) / len(relFreqs[relation])
        heights.append(h)
        if h < 0.05:
            shortRel = relation.replace('http://dbpedia.org/ontology/', 'dbo:').replace('http://dbpedia.org/property/',
                                                                                        'dbp:').split('*')
            print(str(shortRel[0]) + ' & ' + str(shortRel[1]) + ' & ' + str(round(h, 4)) + ' & ' + str(
                len(relFreqs[relation])) + ' \\\ ')

    plt.title('Mean Cointegration \'pvalue\' plotted against\nthe log frequency of the relation occurring (distance 2)')
    plt.xlabel('Mean Cointegration \'pvalue\'')
    plt.ylabel('Log frequency of the relation')
    plt.scatter(heights, labels)
    plt.show()

def splitSymbols(symbols):
    set1 = dict()
    set2 = dict()

    count = 0
    keys = list(symbols.keys())
    random.seed(12)
    random.shuffle(keys)
    for key in keys:
        if count == 4:
            set2[key] = symbols[key]
            count = 0
        else:
            set1[key] = symbols[key]
        count += 1
    return set1, set2


if __name__ == '__main__':
    uriSymbolsDict = genURISymbolDict()
    identificationSet, testSet = splitSymbols(uriSymbolsDict)

    runTrainingDist1(identificationSet)
    runTestDist1(testSet)
    plotDist1Results()

    runTrainingDist2(identificationSet)
    runTestDist2(testSet)
    plotDist2Results()






















