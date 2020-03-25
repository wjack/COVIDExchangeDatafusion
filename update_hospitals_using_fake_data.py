import pandas as pd 
import numpy as np
import time
import json 
 
with open('./gen_data/fake_request_data.json', 'r') as f: 
    fake_requests = json.loads(f.read()) 

with open('./gen_data/hospitals.json', 'r') as f:
    hospitals = json.loads(f.read()) 

uuid_to_requests = {h['uuid'] : [] for h in hospitals}  
for r in fake_requests: 
    uuid = r['org_uuid']
    uuid_to_requests[uuid] += [r]



for i in range(len(hospitals)): 
    uuid = hospitals[i]['uuid'] 
    requests = uuid_to_requests[uuid]
    if len(requests) > 0:
        requests = sorted(requests, key=lambda elt: time.strptime(elt['time'], "%Y-%m-%d %H:%M:%S")) 
        last_request = requests[-1]
        hospitals[i]['icu_beds'] = last_request['icu_beds']
        hospitals[i]['days_ppe'] = last_request['days_ppe']
        hospitals[i]['ventilators'] = last_request['ventilators']
        hospitals[i]['n_cases'] = last_request['n_cases']
        hospitals[i]['n_requests'] = len(requests)
    else:
        hospitals[i]['icu_beds'] = 0
        hospitals[i]['days_ppe'] = 0
        hospitals[i]['ventilators'] = 0
        hospitals[i]['n_cases'] = 0
        hospitals[i]['n_requests'] = 0
        

bed_dist = [h['beds'] for h in hospitals if h['beds'] > 0]
icu_dist = [h['icu_beds'] for h in hospitals if h['icu_beds'] > 0] 

bed_max = np.quantile(bed_dist, .95)
icu_max = np.quantile(icu_dist, .95)
ventilators_max = icu_max 
case_max = max([h['n_cases'] for h in hospitals])
days_ppe_max = 14
n_requests_max = 10
 
for i in range(len(hospitals)):
    hospitals[i]['icu_beds_scaled'] = 10*hospitals[i]['icu_beds']/icu_max
    hospitals[i]['days_ppe_scaled'] = 10*hospitals[i]['days_ppe']/days_ppe_max
    hospitals[i]['ventilators_scaled'] = 10*hospitals[i]['ventilators']/ventilators_max
    hospitals[i]['n_cases_scaled'] = 10*hospitals[i]['n_cases']/case_max
    hospitals[i]['beds_scaled'] = 10*hospitals[i]['beds']/bed_max
    hospitals[i]['n_requests_scaled'] = 10*hospitals[i]['n_requests']/n_requests_max




with open('./gen_data/hospitals.json', 'w') as f:
    f.write(json.dumps(hospitals))