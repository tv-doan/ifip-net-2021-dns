import pandas as pd
import sqlite3
import numpy as np
import base64
from ripe.atlas.sagan.helpers import abuf as abuf_parser
from ripe.atlas.cousteau import (
  Ping,
  Traceroute,
  Dns,
  AtlasSource,
  AtlasCreateRequest,
  AtlasResultsRequest
)
import csv
import os
import sys
import requests
import json
import time
from datetime import timedelta, date, datetime

db_location = "ripe-dns-all-probes.db"
db_with_abuf_location = "ripe-dns-all-probes-with-abuf.db"
msm_ids_location = 'msm_id_list.csv'



measurements = pd.read_csv(msm_ids_location, header=None)[0].unique()

msm_result = []
for msm_id in measurements:
    print('.',end='')
    kwargs = {
        "msm_id": msm_id
    }
    is_success, results = AtlasResultsRequest(**kwargs).create()
    if is_success:
        for result in results:
            msm_result.append(result)
    else:
        print(results)


def parse_result(result_dict):
    resolver_address = address_family = rt = error = abuf = ''
    
    
    #Get resolver IP
    if 'dst_addr' in result_dict:
        resolver_address = result_dict['dst_addr']
    elif 'dst_name' in result_dict:
        resolver_address = result_dict['dst_name']
    
    #Get address family
    if 'af' in result_dict:
        address_family = result_dict['af']
        
        
    #actual result dictionary inside the outer dictionary
    if 'result' in result_dict:
        if 'rt' in result_dict['result']:
            rt = str(result_dict['result']['rt'])
            
        #Abuf contains almost all additional info we need
        if 'abuf' in result_dict['result']:
            abuf = result_dict['result']['abuf']
        '''
            raw_data = abuf.AbufParser.parse(base64.b64decode(result_dict['result']['abuf']))
            #Return code
            if 'HEADER' in raw_data:
                if 'ReturnCode' in raw_data['HEADER']:
                    rcode = raw_data['HEADER']['ReturnCode']
                else:
                    rcode = 'No return code'
            #Target name
            if 'QuestionSection' in raw_data:
                if len(raw_data['QuestionSection']) > 0:
                    if 'Qname' in raw_data['QuestionSection'][0]:
                        target_name = raw_data['QuestionSection'][0]['Qname']
            #Response type, TTL and address
            if 'AnswerSection' in raw_data:
                if len(raw_data['AnswerSection']) > 0:
                    for answer in raw_data['AnswerSection']:
                        if 'Type' in answer:
                            response_type = answer['Type']
                            if response_type != 'CNAME':
                                if 'Address' in answer:
                                    response_address = answer['Address']
                                else:
                                    print('Non-CNAME with no address:' + response_type)
                        if 'TTL' in answer:
                            ttl = answer['TTL']
        '''         
            
    
    #error case, should not have result dictionary
    if 'error' in result_dict:
        if 'result' in result_dict:
            print('error and result in same dict')
        error = result_dict['error']
        if type(error) == dict:
            error = json.dumps(error)
    
    
    
    
    
    return resolver_address, address_family, rt, error, abuf



conn = sqlite3.connect(db_location)
conn.isolation_level = None
cur = conn.cursor()
cur.execute('CREATE TABLE IF NOT EXISTS "data" ("msm_id" INTEGER, "prb_id" INTEGER, "timestamp" INTEGER, "resolver_address" TEXT, "address_family" TEXT, "rt" TEXT, "error" TEXT, "local_resolver" TEXT, "abuf" TEXT);')

'''CREATE TABLE "data" (
"msm_id" INTEGER,
  "prb_id" INTEGER,
  "timestamp" INTEGER,
  "resolver_address" TEXT,
  "address_family" TEXT,
  "rt" TEXT,
  "error" TEXT,
  "local_resolver" TEXT,
  "abuf" TEXT
);'''

    
chunk_of_data = []

total_len = 0


for i in range(len(msm_result)):
    print('.', end='')
    msm_id = prb_id = timestamp = ''

    #Can take this from normal header
    msm_id = msm_result[i]['msm_id']
    prb_id = msm_result[i]['prb_id']
    timestamp = msm_result[i]['timestamp']

    #If the local resolver flag is set, RIPE Atlas always returns a resultset, even if the length is 1
    #If a public resolver is used, we get single results instead (the results contain the first two answers)

    is_local_resolver = 'Unknown'

    #Local resolver
    if 'resultset' in msm_result[i]:

        is_local_resolver = 'True'

        #Edge case, not sure if this even happens, since without a working local resolver,
        #something might be wrong with the probe
        #if len(results[i]['resultset']) == 1:
        #    if 'error' in results[i]['resultset'][0]:
        #        print('Local resolver with single error found')
        #        print(results[i])

        #This is mostly a sanity check, this should in theory never happen
        #for result in msm_result[i]['resultset']:
        #    if not 'submax' in result:
        #        print('submax not in resultset section of msm '+str(msm_id) + 'probe ' + str(prb_id))

        #Parse results
        for result in msm_result[i]['resultset']:
            resolver, af, rt, error, abuf = parse_result(result)
            if af == '':
                if 'from' in msm_result[i]:
                    af = '6' if msm_result[i]['from'].find(':') > 0 else '4'
                #Just to be safe:
                #if results[i]['from'].find(':') > 0:
                #    if results[i]['from'].find('.') > 0:
                #        inferred_address_family = 'Unknown'
            
            chunk_of_data.append((msm_id, prb_id, timestamp, resolver, af, rt, error, is_local_resolver, abuf))
            #save_dns_response(msm_id, prb_id, timestamp,
                          #resolver, af,
                          #rt, error, is_local_resolver, abuf)




    #Public resolver
    elif 'result' in msm_result[i]:

        is_local_resolver = 'False'

        resolver, af, rt, error, abuf = parse_result(msm_result[i])
        if af == '':
            if 'from' in msm_result[i]:
                af = '6' if msm_result[i]['from'].find(':') > 0 else '4'
        chunk_of_data.append((msm_id, prb_id, timestamp, resolver, af, rt, error, is_local_resolver, abuf))
        #save_dns_response(msm_id, prb_id, timestamp,
                          #resolver, af,
                          #rt, error, is_local_resolver, abuf)



    #No results, still want to collect failure information; seems to have info 
    #on timeouts, i.e. resolver unreachable
    else:

        is_local_resolver = 'False'

        resolver = "Failed for other reasons"

        #The dst_addr field seems to be more likely in erronous results
        if 'dst_addr' in msm_result[i]:
            resolver = msm_result[i]['dst_addr']

        #If addr doesnt work, try name; should be an IP address as well
        elif 'dst_name' in msm_result[i]:
            resolver = msm_result[i]['dst_name']

        #If af is not in there we can kind of infer it from the source IP
        af = 'Unknown'
        if 'af' in msm_result[i]:
            af = msm_result[i]['af']
        else:
            if 'from' in msm_result[i]:
                af = '6' if msm_result[i]['from'].find(':') > 0 else '4'
                #Just to be safe:
                #if results[i]['from'].find(':') > 0:
                #    if results[i]['from'].find('.') > 0:
                #        af = 'Unknown'


        response_time = ''
        abuf = 'error, no abuf'

        error = 'Unknown'
        if 'error' in msm_result[i]:
            error = msm_result[i]['error']
            
        if type(error) == dict:
            error = json.dumps(error)
        chunk_of_data.append((msm_id, prb_id, timestamp, resolver, af, rt, error, is_local_resolver, abuf))
        #save_dns_response(msm_id, prb_id, timestamp,
                          #resolver, af,
                          #response_time, error, is_local_resolver, abuf)
        
    #dump data every 500 msm results
    if (i%1000 == 0 and i > 0) or i == len(msm_result)-1:
        print('\n'+str(i))
        total_len = total_len + len(chunk_of_data)
        
        print('Writing chunk')
        timer_for_chunk_tx = time.time()
        cur.execute('BEGIN TRANSACTION')
        for res_tuple in chunk_of_data:
                cur.execute('INSERT INTO "data" ("msm_id", "prb_id", "timestamp", "resolver_address", "address_family", "rt", "error", "local_resolver", "abuf") VALUES (?,?,?,?,?,?,?,?,?)', res_tuple)

        cur.execute('COMMIT')
        print('Done writing chunk')
        print('Clearing list')
        chunk_of_data.clear()
        print("Time Taken: %.3f sec" % (time.time() - timer_for_chunk_tx))

    #print(' ')
    #print('Finished msm '+str(msm))



def parse_abuf(abuf_str):
    print('.', end='')
    rcode = target_name = response_type = response_address = ttl = ''
    if abuf_str != '' and abuf_str != 'error, no abuf':
        raw_data = abuf_parser.AbufParser.parse(base64.b64decode(abuf_str))
        #Return code
        if 'HEADER' in raw_data:
            if 'ReturnCode' in raw_data['HEADER']:
                rcode = raw_data['HEADER']['ReturnCode']
            else:
                rcode = 'No return code'
        #Target name
        if 'QuestionSection' in raw_data:
            if len(raw_data['QuestionSection']) > 0:
                if 'Qname' in raw_data['QuestionSection'][0]:
                    target_name = raw_data['QuestionSection'][0]['Qname']
        #Response type, TTL and address
        if 'AnswerSection' in raw_data:
            if len(raw_data['AnswerSection']) > 0:
                for answer in raw_data['AnswerSection']:
                    if 'Type' in answer:
                        response_type = answer['Type']
                        if response_type != 'CNAME':
                            if 'Address' in answer:
                                response_address = answer['Address']
                            else:
                                print('Non-CNAME with no address:' + response_type)
                    if 'TTL' in answer:
                        ttl = answer['TTL']
    return target_name, rcode, response_type, response_address, ttl

conn = sqlite3.connect(db_location)
df = pd.read_sql_query("SELECT * FROM data", conn)
conn.close()

abuf_str_list = df['abuf'].unique()

ctr = 0
abuf_parse_res = []
for abuf_str in abuf_str_list:
    if ctr%10000==0:
        print('\n'+str(ctr))
    target_name, rcode, response_type, response_address, ttl = parse_abuf(abuf_str)
    abuf_parse_res.append((abuf_str, target_name, rcode, response_type, response_address, ttl))
    ctr = ctr + 1
    

df_abuf_res = pd.DataFrame(abuf_parse_res, columns = ['abuf', 'target_name', 'rcode', 'response_type', 'response_address', 'ttl'])

df_sql = pd.merge(df, df_abuf_res, how='left', on=['abuf'])
conn = sqlite3.connect(db_with_abuf_location)
df_sql.to_sql('data', conn, if_exists='append', index=False)
conn.close()

