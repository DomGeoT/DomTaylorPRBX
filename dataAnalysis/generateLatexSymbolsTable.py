from utils import *

q = '''
SELECT DISTINCT ?companyURI ?symbol WHERE
{
    ?companyURI <http://dbpedia.org/property/symbol> ?symbol .
}
'''

res = executeQueryString('../data/symbolURIPairs.ttl', q)

d = dict()

for i in res:
    d[i['companyURI']['value'].replace('http://dbpedia.org/resource/', 'dbr:')] = i['symbol']['value']

for i in d.keys():
    print('compName & {} & {} & Automated \\\ '.format(i, d[i]))


res = executeQueryString('../data/symbolURIPairsManual.ttl', q)

d = dict()

for i in res:
    d[i['companyURI']['value'].replace('http://dbpedia.org/resource/', 'dbr:')] = i['symbol']['value']

for i in d.keys():
    print('compName & {} & {} & Manual \\\ '.format(i, d[i]))
