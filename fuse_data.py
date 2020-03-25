import pandas as pd 
import json 
import os 
import uuid

# Start by loading a GeoJSON file that maps a FIPS code to a GeoJSON boundary 
# Parse each raw data file we have and insert a field into the GeoJSON file that holds the relevant field
# Export the county level data
with open('./data/geojson_fips.json', 'r') as f:
    geojson = json.loads(f.read())

fips_to_idx = {}
for i in range(len(geojson['features'])):
    fips_to_idx[geojson['features'][i]['id']] = i

population = pd.read_csv('./data/co-est2018-alldata.csv', encoding='latin-1')
covid_cases = pd.read_csv('./data/covid_data_3-23-2020.csv')
poverty_estimates = pd.read_excel('./data/PovertyEstimates.xls', skiprows=4)
cms_data = pd.read_excel('./data/StateCountyAllTable2018.xlsx', skiprows=1)

for i in range(population.shape[0]):
    row = population.iloc[i]
    state = str(row['STATE'])
    if len(state) == 1:
        state = '0' + state
    county = str(row['COUNTY'])
    if county != '0':
        for _ in range(3 - len(county)):
            county = '0' + county 
        fips = state + county 
        count = int(row['POPESTIMATE2018'])
        
        try:
            idx = fips_to_idx[fips]
            geojson['features'][idx]['properties']['population'] = count
        except:
            print('Failed FIPS: {}'.format(fips))
for i in range(covid_cases.shape[0]): 
    row = covid_cases.iloc[i]
    if not pd.isna(row['FIPS']):   
        fips = str(int(row['FIPS']))
        for _ in range(5 - len(fips)): 
            fips = '0' + fips 
        confirmed_covid = int(row['Confirmed'])
        deaths = int(row['Deaths'])
        last_updated = row['Last_Update']

        covid_stats = {
            'confirmed' : confirmed_covid, 
            'deaths' : deaths,
            'last_update' : last_updated
        }
        try:
            idx = fips_to_idx[fips]
            geojson['features'][idx]['properties']['covid_stats'] = covid_stats
        except: 
            print('Failed FIPS: {}'.format(fips)) 

for i in range(len(geojson['features'])):
    if 'covid_stats' not in geojson['features'][i]['properties']: 
        geojson['features'][i]['properties']['covid_stats'] = {
            'confirmed' : 0, 
            'deaths' : 0,
            'last_update' : "2020-03-23 23:19:34"
        }
    if 'poverty_rate' not in geojson['features'][i]['properties']: 
        geojson['features'][i]['properties']['poverty_rate'] = 0.0
    if 'population' not in geojson['features'][i]['properties']: 
        geojson['features'][i]['properties']['population'] = 0.0

for i in range(poverty_estimates.shape[0]): 
    row = poverty_estimates.iloc[i]
    fips = str(row['FIPStxt'])
    for _ in range(5 - len(fips)): 
        fips = '0' + fips
    poverty_rate = row['PCTPOVALL_2018']/100.0
    try:
        idx = fips_to_idx[fips]
        geojson['features'][idx]['properties']['poverty_rate'] = poverty_rate
    except:
        print('Failed FIPS: {}'.format(fips))

with open('./gen_data/fused_coronavirus_county_data.json', 'w') as f:
    f.write(json.dumps(geojson))

# Standardize each raw coordinate based file we have into a common JSON form, and export those 
hospitals = pd.read_csv('./data/Hospitals.csv')
local_emergency_operations_centers = pd.read_csv('./data/Local_Emergency_Operations_Centers_EOC.csv')
nursing_homes = pd.read_csv('./data/Nursing_Homes.csv')
pharmacies = pd.read_csv('./data/pharmacies.csv')
public_health_departments = pd.read_csv('./data/Public_Health_Departments.csv')
state_emergency_operations_centers = pd.read_csv('./data/State_Emergency_Operations_Centers_EOC.csv')

hospitals_g = []
for i in range(hospitals.shape[0]): 
    row = hospitals.iloc[i]
    obj = {}
    obj['uuid'] = str(uuid.uuid4())
    obj['longitude'] = row['X']
    obj['latitude'] = row['Y']
    fips = str(row['COUNTYFIPS'])
    for _ in range(5 - len(fips)): 
        fips = '0' + fips 
    try:
        obj['county_poverty_pct'] = 100*geojson['features'][fips_to_idx[fips]]['properties']['poverty_rate'] 
        obj['county_population'] = geojson['features'][fips_to_idx[fips]]['properties']['population']
        obj['county_confirmed_cases'] = geojson['features'][fips_to_idx[fips]]['properties']['covid_stats']['confirmed'] 
        obj['county_confirmed_deaths'] = geojson['features'][fips_to_idx[fips]]['properties']['covid_stats']['deaths']
    except: 
        obj['county_poverty_pct'] = 0.0
        obj['county_population'] = 0.0
        obj['county_confirmed_cases'] = 0.0
        obj['county_confirmed_deaths'] = 0.0
    obj['fips'] = fips
    obj['name'] = row['NAME'] 
    obj['address'] = row['ADDRESS'] + ', ' + row['CITY'] + ', ' + row['STATE'] + ' ' + str(row['ZIP']) 
    obj['phone'] = ''
    if not pd.isna(row['TELEPHONE']):
        obj['phone'] = str(row['TELEPHONE'])
    obj['type'] = row['TYPE']
    obj['website'] = row['WEBSITE']
    obj['beds'] = int(row['BEDS'])
    obj['helipad'] = row['HELIPAD'] 
    obj['trauma_center'] = row['TRAUMA']
    hospitals_g += [obj] 

with open('./gen_data/hospitals.json', 'w') as f: 
    f.write(json.dumps(hospitals_g))


local_emergency_operations_centers_g = []
for i in range(local_emergency_operations_centers.shape[0]): 
    row = local_emergency_operations_centers.iloc[i] 
    obj = {} 
    obj['uuid'] = str(uuid.uuid4()) 
    obj['longitude'] = row['X']
    obj['latitude'] = row['Y'] 
    for _ in range(5 - len(fips)): 
        fips = '0' + fips 
    obj['fips'] = fips
    obj['name'] = row['NAME']  
    obj['address'] = row['ADDRESS'] + ', ' + row['CITY'] + ', ' + row['STATE'] + ' ' + str(row['ZIP']) 
    obj['phone'] = ''
    if not pd.isna(row['TELEPHONE']):
        obj['phone'] = str(row['TELEPHONE'])
    local_emergency_operations_centers_g += [obj] 
 

with open('./gen_data/local_emergency_operations_centers.json', 'w') as f: 
    f.write(json.dumps(local_emergency_operations_centers_g))

state_emergency_operations_centers_g = []
for i in range(state_emergency_operations_centers.shape[0]): 
    row = state_emergency_operations_centers.iloc[i] 
    obj = {}
    obj['uuid'] = str(uuid.uuid4())
    obj['longitude'] = row['X']
    obj['latitude'] = row['Y'] 
    obj['name'] = row['NAME'] 
    obj['address'] = row['ADDRESS1'] + ', ' + row['CITY'] + ', ' + row['STATE'] + ' ' + str(row['ZIP']) 
    obj['phone'] = ''
    if not pd.isna(row['TELEPHONE']):
        obj['phone'] = str(row['TELEPHONE'])
    state_emergency_operations_centers_g += [obj] 

with open('./gen_data/state_emergency_operations_centers.json', 'w') as f: 
    f.write(json.dumps(state_emergency_operations_centers_g))

nursing_homes_g = [] 
for i in range(nursing_homes.shape[0]): 
    row = nursing_homes.iloc[i] 
    obj = {}
    obj['uuid'] = str(uuid.uuid4())
    obj['longitude'] = row['X']
    obj['latitude'] = row['Y']
    fips = str(row['COUNTYFIPS'])
    for _ in range(5 - len(fips)): 
        fips = '0' + fips 
    obj['fips'] = fips
    obj['name'] = row['NAME'] 
    obj['address'] = row['ADDRESS'] + ', ' + row['CITY'] + ', ' + row['STATE'] + ' ' + str(row['ZIP'])
    obj['phone'] = ''
    if not pd.isna(row['TELEPHONE']):
        obj['phone'] = str(row['TELEPHONE'])
    obj['type'] = row['SOURCETYPE']
    obj['website'] = row['WEBSITE']
    obj['beds'] = int(row['BEDS'])
    nursing_homes_g += [obj]

with open('./gen_data/nursing_homes.json', 'w') as f: 
    f.write(json.dumps(nursing_homes_g))


pharmacies_g = [] 
for i in range(pharmacies.shape[0]): 
    row = pharmacies.iloc[i] 
    obj = {}
    obj['uuid'] = str(uuid.uuid4())
    location = row['CalcLocation'] 
    location = location.split(',') 
    lat = float(location[0]) 
    lon = float(location[1])
    obj['longitude'] = lon
    obj['latitude'] = lat
    
    obj['address'] = row['Address'] + ', ' + row['City'] + ', ' + row['State'] + ' ' + str(row['Zip']) 
    obj['phone'] = ''
    if not pd.isna(row['formated_phone']):
        obj['phone'] = str(row['formated_phone'])
    obj['type'] = row['Type']

    pharmacies_g  += [obj] 

with open('./gen_data/pharmacies.json', 'w') as f: 
    f.write(json.dumps(pharmacies_g))


public_health_departments_g = []

for i in range(public_health_departments.shape[0]): 
    row = public_health_departments.iloc[i] 
    obj = {} 
    obj['uuid'] = str(uuid.uuid4())
    obj['longitude'] = row['X']
    obj['latitude'] = row['Y'] 
    for _ in range(5 - len(fips)): 
        fips = '0' + fips 
    obj['fips'] = fips
    obj['name'] = row['NAME']  
    obj['address'] = row['ADDRESS'] + ', ' + row['CITY'] + ', ' + row['STATE'] + ' ' + str(row['ZIP'])
    obj['phone'] = ''
    if not pd.isna(row['TELEPHONE']):
        obj['phone'] = str(row['TELEPHONE'])
    public_health_departments_g += [obj]

with open('./gen_data/public_health_departments.json', 'w') as f: 
    f.write(json.dumps(public_health_departments_g))







