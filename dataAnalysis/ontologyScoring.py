
from utils import *
import itertools
import json


def executeSimilarityQuery(queryFile, companyURI1, companyURI2):
    with open("../queries/similarityQueries/" + queryFile, "r") as f:
        query = f.read()
    query = query.replace("{companyURI1}", companyURI1).replace("{companyURI2}", companyURI2)
    results = queryEndpoint(query)

    return len(results['results']['bindings'])


def calculateOntologyScores(uriSymbolDict, queries):
    '''

    :param uriSymbolDict: dictionary of company URIs to their symbols
    :return:
    '''
    scores = dict()
    for companyPairs in itertools.combinations(uriSymbolDict.values(), 2):
        scores[getSymbolPairKey(companyPairs[0], companyPairs[1])] = 0

    for query in queries:
        for companyPair in itertools.combinations(uriSymbolDict.keys(), 2):
            key = getSymbolPairKey(uriSymbolDict[companyPair[0]], uriSymbolDict[companyPair[1]])
            scores[key] = scores[key] + executeSimilarityQuery(query, companyPair[0], companyPair[1])

    return scores

def calculateOntologyDistances(uriSymbolDict):
    distances = dict() # (pair symbol) -> array of num of mappings at that dist [dist1 = xx, dist2 = yy, dist 3 = zz]
    for companyPair in itertools.combinations(uriSymbolDict.keys(), 2):
        comp1Symbol = uriSymbolDict[companyPair[0]]
        comp2Symbol = uriSymbolDict[companyPair[1]]
        pairKey = getSymbolPairKey(comp1Symbol, comp2Symbol)
        distances[pairKey] = []

        queries = ['dist1.rq', 'dist2.rq']
        for q in range(len(queries)):
            with open("../queries/endpointQueries/" + queries[q], "r") as f:
                query = f.read()
            query = query.replace("{companyURI1}", companyPair[0]).replace("{companyURI2}", companyPair[1])
            results = queryEndpoint(query)['results']['bindings'][0]['aCount']['value']
            distances[pairKey].append(int(results))
        print(pairKey, distances[pairKey])

    return distances