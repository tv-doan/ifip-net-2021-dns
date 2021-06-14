import csv
import os
import sys
from datetime import timedelta, date, datetime
from ripe.atlas.cousteau import (Dns, Traceroute, AtlasSource, AtlasCreateRequest)
import requests
import json
import time
from random import randrange

#
#   Right now one-off measurements cost double the amount per result of ongoing measurements.
#   So when doing one-offs one should set the number of packets to 1, otherwise 2.
#


num_days = 14


ATLAS_API_KEY = "{PASTE-API-KEY-HERE}"
#Download json data
def download(url):
    #Get request
    response = requests.get(url)
    #Load json
    json_data = json.loads(response.text)
    return json_data



#
#   IPv4 capable home probes
#

#
#   v3 Probes
#

next_url = "https://atlas.ripe.net:443/api/v2/probes/?status=1&is_anchor=false&tags=system-ipv4-works%2Chome%2Csystem-v3"
probes_v4 = []
next_bool = True
while next_bool:
    probes_json = download(next_url)
    for probe in probes_json['results']:
        probes_v4.append(probe)
    if probes_json['next'] == None:
        next_bool = False
    else: next_url = probes_json['next']

#
#   v4 probes
#

next_url = "https://atlas.ripe.net:443/api/v2/probes/?status=1&is_anchor=false&tags=system-ipv4-works%2Chome%2Csystem-v4"
next_bool = True
while next_bool:
    probes_json = download(next_url)
    for probe in probes_json['results']:
        probes_v4.append(probe)
    if probes_json['next'] == None:
        next_bool = False
    else: next_url = probes_json['next']



#Write full info to csv
with open("metadata/probe_v4_list.json", "w") as f:
    json.dump(probes_v4, f)

#Get ids for the query
id_list_v4 = []
for probe in probes_v4:
    id_list_v4.append(probe['id'])

#Write ids to csv
with open("metadata/probe_v4_id_list.csv", "w") as f:
    writer = csv.writer(f)
    for j in id_list_v4:
        writer.writerows([[j]])

print('Number of IPv4 probes:')
print(len(id_list_v4))


#
#   IPv6 capable home probes
#

#
#   v3 Probes
#

next_url = "https://atlas.ripe.net:443/api/v2/probes/?status=1&is_anchor=false&tags=system-ipv6-works%2Chome%2Csystem-v3"
probes_v6 = []
next_bool = True
while next_bool:
    probes_json = download(next_url)
    for probe in probes_json['results']:
        probes_v6.append(probe)
    if probes_json['next'] == None:
        next_bool = False
    else: next_url = probes_json['next']

#
#   v4 probes
#

next_url = "https://atlas.ripe.net:443/api/v2/probes/?status=1&is_anchor=false&tags=system-ipv6-works%2Chome%2Csystem-v4"
next_bool = True
while next_bool:
    probes_json = download(next_url)
    for probe in probes_json['results']:
        probes_v6.append(probe)
    if probes_json['next'] == None:
        next_bool = False
    else: next_url = probes_json['next']



#Write full info to csv
with open("metadata/probe_v6_list.json", "w") as f:
    json.dump(probes_v6, f)

#Get ids for the query
id_list_v6 = []
for probe in probes_v6:
    id_list_v6.append(probe['id'])

#Write ids to csv
with open("metadata/probe_v6_id_list.csv", "w") as f:
    writer = csv.writer(f)
    for j in id_list_v6:
        writer.writerows([[j]])

print('Number of IPv6 probes:')
print(len(id_list_v6))



with open('metadata/website_list_cdn.csv', 'r') as f:
    reader = csv.reader(f)
    tmp_list = list(reader)

    full_domain_list = [sublist[0] for sublist in tmp_list]



print('Number of websites')
print(len(full_domain_list))

#
#   Get IPv4 resolver addresses
#
with open("metadata/resolver_list_v4.txt", 'r') as f:
    reader = csv.reader(f)
    tmp_list = list(reader)
    resolver_list_v4 = [sublist[0] for sublist in tmp_list]

#
#   Get IPv6 resolver addresses
#
with open("metadata/resolver_list_v6.txt", 'r') as f:
    reader = csv.reader(f)
    tmp_list = list(reader)
    resolver_list_v6 = [sublist[0] for sublist in tmp_list]


#
#   Create source based on probes for IPv4 measurements
#
source_v4 = AtlasSource(
    type = "probes",
    value = ','.join(str(x) for x in id_list_v4),
    requested = len(id_list_v4)
)
#
#   Create source based on probes for IPv6 measurements
#
source_v6 = AtlasSource(
    type = "probes",
    value = ','.join(str(x) for x in id_list_v6),
    requested = len(id_list_v6)
)


print('Creating measurements for $r.google.com')
#
#   IPv4 measurements: Query A on IPv4 probes
#

msm_list_v4 = []
print('Creating measurements for $r.google.com A')
#Local resolver
msm_list_v4.append(Dns(af=4, interval=86400, use_probe_resolver = True, use_macros=True, query_class= "IN", query_type= "A", query_argument = "$r.google.com", description = "IPv4 DNS Query (UDP) for $r.google.com from probe's local resolver.", protocol="UDP", spread = 60))                        
#Pre-selected resolvers

for resolver_v4 in resolver_list_v4:
    msm_list_v4.append(Dns(af=4, interval=86400, target = resolver_v4, use_macros=True, query_class= "IN", query_type= "A", query_argument = "$r.google.com", description = "IPv4 DNS Query (UDP) for $r.google.com to "+ resolver_v4 + ".", protocol="UDP", spread = 60))                        

print("Creating request.")
#Create request, one-off two minutes from now
atlas_request = AtlasCreateRequest(
    start_time = datetime.utcnow() + timedelta(days=0, minutes=10),
    stop_time=datetime.utcnow() + timedelta(days=num_days+0, minutes=10),
    key = ATLAS_API_KEY,
    measurements = msm_list_v4,
    sources = [source_v4],
    is_oneoff = False
)

print("Submitting request to RIPE Atlas.")
(is_success, response) = atlas_request.create()
if is_success:
    print("Success!")
    print(len(response['measurements']))
    #If successful write msm_id to csv
    with open('metadata/msm_id_list.csv', 'a') as f:
        writer = csv.writer(f)
        for j in response['measurements']:
            writer.writerows([[j]])
else:
    print("Error when creating IPv4 caching measurements!")
    print(response)
    exit(1)



#
#   IPv6 measurements: Query AAAA on IPv6 probes
#

print("Creating IPv6 measurements for AAAA RRs")
#
#   Create measurements for batches of 2500 probes
#

msm_list_v6 = []
print('Creating measurements for $r.google.com AAAA')
#Local resolver
msm_list_v6.append(Dns(af=6, interval=86400, use_probe_resolver = True, use_macros=True, query_class= "IN", query_type= "AAAA", query_argument = "$r.google.com", description = "IPv6 DNS Query (UDP) for $r.google.com from probe's local resolver.", protocol="UDP", spread = 60))                        
#Pre-selected resolvers
for resolver_v6 in resolver_list_v6:
    msm_list_v6.append(Dns(af=6, interval=86400, target = resolver_v6, use_macros=True, query_class= "IN", query_type= "AAAA", query_argument = "$r.google.com", description= "IPv6 DNS Query (UDP) for $r.google.com to "+ resolver_v6 + ".", protocol="UDP", spread = 60))

print("Creating request.")
#Create request, one-off two minutes from now
atlas_request = AtlasCreateRequest(
    start_time = datetime.utcnow() + timedelta(days=0, minutes=10),
    stop_time = datetime.utcnow() + timedelta(days=num_days+0, minutes=10),
    key = ATLAS_API_KEY,
    measurements = msm_list_v6,
    sources = [source_v6],
    is_oneoff = False
)
print("Submitting request to RIPE Atlas.")
(is_success, response) = atlas_request.create()
if is_success:
    print("Success!")
    print(len(response['measurements']))
    #If successful write msm_id to csv
    with open('metadata/msm_id_list.csv', 'a') as f:
        writer = csv.writer(f)
        for j in response['measurements']:
            writer.writerows([[j]])
else:
    print("Error when creating IPv6 caching measurements!")
    print(response)
    exit(1)






print('Creating measurements for CDN website list')
for domain in full_domain_list:
    #
    #   IPv4 measurements: Query A on IPv4 probes
    #
    print("Creating IPv4 measurements for A RRs")
    
    msm_list_v4 = []
    print('Creating measurements for '+domain+' A')
    
    #Local resolver
    msm_list_v4.append(Dns(af=4, interval=86400, use_probe_resolver = True, query_class= "IN", query_type= "A", query_argument = domain, description = "IPv4 DNS Query (UDP) for " + domain +" from probe's local resolver.", protocol="UDP"))                        
    #Pre-selected resolvers
    for resolver_v4 in resolver_list_v4:
        msm_list_v4.append(Dns(af=4, interval=86400, target = resolver_v4, query_class= "IN", query_type= "A", query_argument = domain, description = "IPv4 DNS Query (UDP) for " + domain +" to "+ resolver_v4 + ".", protocol="UDP"))                        

    print("Creating request.")
    #Create request, one-off five minutes from now
    atlas_request = AtlasCreateRequest(
        start_time = datetime.utcnow() + timedelta(days=0,minutes=10),
        stop_time = datetime.utcnow() + timedelta(days=num_days+0, minutes=10),
        key = ATLAS_API_KEY,
        measurements = msm_list_v4,
        sources = [source_v4],
        is_oneoff = False
    )
    
    print("Submitting request to RIPE Atlas.")
    (is_success, response) = atlas_request.create()
    if is_success:
        print("Success!")
        print(len(response['measurements']))
        #If successful write msm_id to csv
        with open('metadata/msm_id_list.csv', 'a') as f:
            writer = csv.writer(f)
            for j in response['measurements']:
                writer.writerows([[j]])
    else:
        print("Error when creating IPv4 measurements!")
        print(response)
        exit(1)


    #
    #   IPv6 measurements: Query AAAA on IPv6 probes
    #
    print("Creating IPv6 measurements for AAAA RRs")


    msm_list_v6 = []
    print('Creating measurements for '+domain+' AAAA')
    
    #Local resolver
    msm_list_v6.append(Dns(af=6, interval=86400, use_probe_resolver = True, query_class= "IN", query_type= "AAAA", query_argument = domain, description = "IPv6 DNS Query (UDP) for " + domain +" from probe's local resolver.", protocol="UDP"))                        
    #Pre-selected resolvers
    for resolver_v6 in resolver_list_v6:
        msm_list_v6.append(Dns(af=6, interval=86400, target = resolver_v6, query_class= "IN", query_type= "AAAA", query_argument = domain, description= "IPv6 DNS Query (UDP) for " + domain +" to "+ resolver_v6 + ".", protocol="UDP"))

    print("Creating request.")
    #Create request, one-off five minutes from now
    atlas_request = AtlasCreateRequest(
        start_time = datetime.utcnow() + timedelta(days=0,minutes=10),
        stop_time = datetime.utcnow() + timedelta(days=num_days+0, minutes=10),
        key = ATLAS_API_KEY,
        measurements = msm_list_v6,
        sources = [source_v6],
        is_oneoff = False
    )
    print("Submitting request to RIPE Atlas.")
    (is_success, response) = atlas_request.create()
    if is_success:
        print("Success!")
        print(len(response['measurements']))
        #If successful write msm_id to csv
        with open('metadata/msm_id_list.csv', 'a') as f:
            writer = csv.writer(f)
            for j in response['measurements']:
                writer.writerows([[j]])
    else:
        print("Error when creating IPv6 measurements!")
        print(response)
        exit(1)
    




