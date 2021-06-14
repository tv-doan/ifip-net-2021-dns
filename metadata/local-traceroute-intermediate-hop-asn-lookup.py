import sys
import requests
import json

import sqlite3
import pandas as pd

import codecs


def get_json_resource_from_absolute_uri(url, query_params):
    try: res = requests.get(url, params = query_params)
    except Exception as e: print(e, sys.stderr)
    else:
        try: res_json = res.json()
        except Exception as e: print(e, sys.stderr)
        else:
            return res_json


# ASN lookup by IP address
def get_asn_from_endpoint(endpoint):
    asn = holder = None
    base_uri = 'https://stat.ripe.net'; url = '%s/data/prefix-overview/data.json'%base_uri
    params = {'resource' : endpoint}
    try: res = get_json_resource_from_absolute_uri(url, params)
    except Exception as e: print(e, sys.stderr); return None
    try:
        asns_holders = []
        for item in res['data']['asns']:
            asn = item['asn']; holder = item['holder']
            asns_holders.append((asn, holder))
    except Exception as e: print(e, sys.stderr)
    return asns_holders


# ===============================================
# lookup of AS numbers for intermediate endpoints
# ===============================================

with open('intermediate-hops-LOCAL.csv', 'r') as f:
    log = codecs.open('intermediate-hops-asns-LOCAL.csv', 'w', 'utf-8')
    log.write('%s;%s;%s\n' % ('ip', 'asn', 'holder'))  # header line

    for endpoint in f.read().splitlines():
        lookup = get_asn_from_endpoint(endpoint)

        if lookup:
            for asn, holder in lookup:
                log.write('%s;%d;%s\n' % (endpoint, asn, holder))
        else:
            log.write('%s;-1;NO HOLDER\n' % (endpoint))
                
    log.close()
