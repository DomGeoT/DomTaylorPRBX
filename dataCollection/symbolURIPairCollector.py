import pandas
from utils import *

def writeResultsToFile(results, resultsFileName):
    with open("../queries/" + resultsFileName, "w+") as f:
        json.dump(results, f)


def loadCompanyData():
    companyData = pandas.read_csv("../data/companylist.csv", sep=',',header=0)
    companyData = companyData.loc[:, ["date","minute",""]]

    return companyData

def storeResults(uriSymbolPairs):
    with open("../data/symbolURIPairs2.ttl", "w+") as f:
        f.write("@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>\n")
        for pair in uriSymbolPairs:
            f.write("<{}> <http://dbpedia.org/property/symbol> \"{}\"^^rdf:langString .\n".format(pair[0], pair[1]))


def findCompanies():
    companySymbols = loadCompanyData()
    with open("../queries/endpointQueries/uriSymbolPair.rq") as queryFile:
        queryTemplate = queryFile.read()

    results = []

    for count, data in companySymbols.iterrows():

        query = queryTemplate.replace("{symbol}", data['Symbol'])
        result = queryEndpoint(query)
        print(data['Symbol'], result['results']['bindings'])
        if len(result['results']['bindings']) > 0:
            for r in result['results']['bindings']:
                print(data['Symbol'], r)
                results.append((r['company']['value'], data['Symbol']))
        else:
            print(data['Symbol'], "no results")
    storeResults(results)

if __name__ == '__main__':
    findCompanies()