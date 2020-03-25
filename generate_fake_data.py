import json 
import os 
import pandas as pd
import random
import numpy as np
import time 

hit_hospital_requests = [
    "We need additional ventilators ASAP. We were one of the first hospitals to be hit, so we were given an abundance of PPE. We even have empty beds, but we have to turn people away because we are so low on ventilators.", 
    "We donated extra PPE to local hospitals to aid them, but we were just hit by a wave of cases that's left us short on facemasks.",
    "Need 10000 masks by end of week.", 
    "We have no tests to evaluate our own staff's health", 
    "We need more nurses. The virus has spread through our entire nursing staff",
    "We are completely out of acetaminophen. I have no idea how this is even possible.",
    "Was told to expect a shipment of 500 SARS-nCoV-2 test kits from the state government, but have received only 50 so far",
    "We are out of PCR reagents, which is blocking many key laboratory tests, beyond just coronavirus tests", 
    "Cannot handle ER volume, need to set up triage tent outside, but drastically understaffed", 
    "We need more intubation kits. We have enough ventilators, but don't have the supplies we need to operate them", 
    "Our workers are threatening a strike unless we supply them PPE, but we don't have any available",
    "Not enough thermometers to run screening at all of the hospital's entrances",
    "Suffered theft of the last of our N95 masks.",
    "Our ER waiting room has a line outside the door and patients are becoming violent", 
    "We don't have enough ER physicians on staff to handle the huge of influx of patients"
    
]

ok_hospital_requests = [
    "We are completely out of masks and respirators. We were told by our GPO that we'd be stocked with at least surgical masks by last Friday, but so far we've seen nothing come through. We haven't had many suspected cases, but we're totally unprepared to handle any that come in.", 
    "There aren't any SARS-nCoV-2 cases here, but we are out of Z-packs for routine care, and we can't find any, anywhere!", 
    "Our health system's leadership is entirely unresponsive to the virus, and isn't taking appropriate steps to mitigate risks and keep us healthy as employees", 
    "GPO is totally unresponsive to our orders (non-Coronavirus related), we have other available sources for equipment, but we are contractually bound to go through the GPO",
    "Our wifi is down, but due to shelter-in-place, our IT contractor cannot come fix it for us. We are relying on pen-and-paper notes for now"
]

nursing_home_requests = [

    "We are a nursing home that is in dire need of additional staff. We believe about half of our staff may have virus and we don't want them to be interacting with our elderly population, which has left us incredibly shortstaffed.", 
]

nyc_hosps = []
upstate_hospitals = []
other_hospitals = []

with open('./gen_data/fused_coronavirus_county_data.json', 'r') as f: 
    county_data = json.loads(f.read())
 
fips_to_index = {} 
for i in range(len(county_data['features'])):
    fips_to_index[county_data['features'][i]['id']] = i

with open('./gen_data/hospitals.json', 'r') as f: 
    hospitals = json.loads(f.read())

fips_to_hospitals = {}

for county in county_data['features']: 
    fips = county['id'] 
    fips_to_hospitals[fips] = {}
    fips_to_hospitals[fips]['idx'] = {}
    fips_to_hospitals[fips]['uuid'] = {}

idx = 0
for h in hospitals: 
    if h['fips'] not in fips_to_hospitals:
        fips_to_hospitals[h['fips']] = {}
        fips_to_hospitals[h['fips']]['idx'] = {}
        fips_to_hospitals[h['fips']]['uuid'] = {}
    fips_to_hospitals[h['fips']]['idx'][idx] = 0 
    fips_to_hospitals[h['fips']]['uuid'][h['uuid']] = 0
    idx += 1

for c in county_data['features']:
    confirmed = c['properties']['covid_stats']['confirmed']

    county_hospitals = list(fips_to_hospitals[c['id']]['idx'].keys()) 
    total_beds = sum([max(0, hospitals[idx]['beds']) for idx in county_hospitals])
    if confirmed > 0 and total_beds > 0:
        for ch in county_hospitals:
            num_confirmed = int(round(confirmed*(max(0, hospitals[ch]['beds'])/total_beds)))

            fips_to_hospitals[c['id']]['idx'][ch] = num_confirmed
            fips_to_hospitals[c['id']]['uuid'][hospitals[ch]['uuid']] = num_confirmed
'''
for h in hospitals: 
    if 'new york,' in h['address'].lower(): 
        nyc_hosps += [h]
    elif 'ny ' in h['address'].lower(): # filter upstate hospitals
        upstate_hospitals += [h]
    else:
        other_hospitals += [h] 



ok_hospitals = [

]

hit_hospitals = [

]

for h in nyc_hosps:
    r = random.random()
    if r < .8:
        hit_hospitals += [h]
    else: 
        ok_hospitals += [h]

for h in upstate_hospitals:
    r = random.random()
    if r < .3:
        hit_hospitals += [h]
    else: 
        ok_hospitals += [h]

for h in other_hospitals:
    r = random.random()
    if r < .2:
        hit_hospitals += [h]
    else: 
        ok_hospitals += [h]
'''
fake_data = [] 

def str_time_prop(start, end, format="%Y-%m-%d %H:%M:%S"):
    prop = random.random()
    stime = time.mktime(time.strptime(start, format))
    etime = time.mktime(time.strptime(end, format))

    ptime = stime + prop * (etime - stime)

    return time.strftime(format, time.localtime(ptime))

def make_request(hospital_id, request_text, icu_beds, ventilators, days_ppe, n_cases, date_string):
    req = {'org_uuid' : hospital_id, 'text': request_text, 'phone' : '555-555-5555', 'email' : 'user@domain.org', 'icu_beds': icu_beds, 'days_ppe' : days_ppe, 'ventilators' : ventilators, 'n_cases' : n_cases, 'time' : date_string} 
    return req


for h in hospitals:
    r = random.random()
    if r < 1.0: 
        if h['beds'] > 0:
            icu_beds = int(round(.1*h['beds']))
        else: 
            icu_beds = -999
        n_ventilators = max(.1, random.random()) * max(0, icu_beds)

        n_cases = fips_to_hospitals[h['fips']]['uuid'][h['uuid']]
        if n_cases > 0:
            n_requests = np.random.randint(1, 10)
            days_ppe = np.random.randint(0,7)

        else: 
            n_requests = np.random.randint(1, 3) 
            days_ppe = np.random.randint(7,15)

        #n_cases = int(round(random.random()*h['beds']*.5))
        days_ppe = np.random.randint(0,15)

        if n_cases == 0:
            request_indices = list(np.random.choice(np.arange(len(ok_hospital_requests)), n_requests, replace=False))
        else: 
            request_indices = list(np.random.choice(np.arange(len(hit_hospital_requests)), n_requests, replace=False))


        for request_index in request_indices:
            t_string = str_time_prop('2020-03-19 00:00:00', '2020-03-24 00:00:00')
            if n_cases == 0:
                request_text = ok_hospital_requests[request_index]
            else: 
                request_text = hit_hospital_requests[request_index]
            req = make_request(h['uuid'], request_text, icu_beds, n_ventilators, days_ppe, n_cases, t_string)
            fake_data += [req]
'''
for hospital in ok_hospitals:
    if h['beds'] > 0:
        icu_beds = int(round(.1*h['beds']))
    else: 
        icu_beds = -999
    n_ventilators = max(.1, random.random()) * max(0, icu_beds)
    r = random.random()
    if r < .2: 
        n_requests = np.random.randint(1, 2)
        n_cases = 0
        for _ in range(n_requests):
            weeks_ppe = np.random.randint(0,2)
            t_string = str_time_prop('2020-03-19 00:00:00', '2020-03-24 00:00:00') 
            request_index = np.random.randint(0, len(ok_hospital_requests))
            request_text = ok_hospital_requests[request_index]
            req = make_request(h['uuid'], request_index, icu_beds, n_ventilators, weeks_ppe, n_cases, t_string)
            fake_data += [req]

'''
with open('./gen_data/fake_request_data.json', 'w') as f: 
    f.write(json.dumps(fake_data))
