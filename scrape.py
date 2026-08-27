import requests
import re
import json

url = "https://stardewvalleywiki.com/mediawiki/api.php"

# Parsnip - testing crops
# params = {
#     "action": "parse",
#     "page": "Parsnip",
#     "prop": "wikitext",
#     "format": "json"
# }
# response = requests.get(url, params = params)

# data = response.json()['parse']['wikitext']['*']
# end_indx = data.find("\n}}")
# data = data[2:end_indx]
# info = data.split('\n')
# dct = {info[i].split('=')[0].strip().strip('|'):
#        info[i].split('=')[1].strip().strip('|') for i in range(1,len(info))}

# dictionary cleanup
# dct['growth'] = int(dct["growth"][0])
# dct.pop('xp', None)
# dct.pop('edibility', None)
# dct.pop('color', None)
# print(dct)

# Parsnip - testing seeds
# url_seeds = "https://stardewvalleywiki.com/mediawiki/api.php"
# params_seeds = {
#     "action": "parse",
#     "page": "Parsnip Seeds",
#     "prop": "wikitext",
#     "format": "json"
# }
# response_seeds = requests.get(url_seeds, params = params_seeds)
# data_seeds = response_seeds.json()['parse']['wikitext']['*']
# end_indx_seeds = data_seeds.find("\n}}")
# data_seeds = data_seeds[2:end_indx_seeds]
# info_seeds = data_seeds.split('\n')
# dct_seeds = {info_seeds[i].split('=')[0].strip().strip('|'):
#        info_seeds[i].split('=')[1].strip().strip('|') for i in range(1,len(info_seeds))}

# # dictionary clean up
# popped_lst = ['image', 'crop', 'growth', 'season', 'nmday', 'sellprice']
# for keys in popped_lst:
#     dct_seeds.pop(keys, None)
# for k in dct_seeds.keys():
#     match = re.search(r"\|(\d+)", dct_seeds[k])
#     dct_seeds[k] = int(match.group(1))

# print(dct_seeds)

# spring crops - testing
# params_spring = {
#     'action': 'query',
#     'list': 'categorymembers',
#     'cmtitle': 'Category:Spring crops',
#     'cmlimit': 500,
#     'format': 'json'
# }
# spring_crops = requests.get(url, params = params_spring)
# spring_crops = spring_crops.json()['query']['categorymembers']
# spring_crops = [spring_crops[i]['title'] for i in range(len(spring_crops))]
# print(spring_crops)

# crops for each season
seasons = ['Spring', 'Summer', 'Fall', 'Winter']
crops_names_all = {}
for s in seasons:
    params = {
        'action': 'query',
        'list': 'categorymembers',
        'cmtitle': f'Category:{s} crops',
        'cmlimit': 500,
        'format': 'json'
    }
    crops_list = requests.get(url, params = params)
    crops_list = crops_list.json()['query']['categorymembers']
    crops_list = [crops_list[i]['title'] for i in range(len(crops_list))]
    crops_names_all[f"{s}"] = crops_list
crops_names_all['Winter'] += ['Powdermelon']


all_crops = []
seen_crops = set()
for season, crop_list in crops_names_all.items():
    for crop_name in crop_list:
        if crop_name in seen_crops:
            continue
        seen_crops.add(crop_name) # adds crop to seen crops list

        # requesting CROPS info into dictionary
        params = {
            "action": "parse",
            "page": crop_name,
            "prop": "wikitext",
            "format": "json"
        }
        response = requests.get(url, params = params)
        data = response.json()['parse']['wikitext']['*']
        full_wikitext = data
        end_indx = data.find("\n}}")
        data = data[2:end_indx]
        info = data.split('\n')
        dct = {info[i].split('=')[0].strip().strip('|'):
               info[i].split('=')[1].strip().strip('|') for i in range(1,len(info))}

        if full_wikitext.find("Regrowth:") == -1: # determines if regrows
            dct["regrowDays"] = None
        else:
            match = re.search(r"Regrowth:\s*(\d+)\s*Days?", full_wikitext)
            dct["regrowDays"] = int(match.group(1))

        # clean up
        dct['growth'] = int(dct["growth"].split()[0])
        dct['seed'] = dct['seed'].split('|')[1].strip('}')
        pop_crops_lst = ['xp', 'edibility', 'color']

        if dct['season'].find("{{") == -1:
            dct['season'] = [dct['season']]
        else:
            dct['season'] = re.findall(r"\{\{Season\|(\w+)\}\}", dct['season'])
            
        for k in pop_crops_lst:
            dct.pop(k, None)

        # requesting SEEDS info
        params_seeds = {
            "action": "parse",
            "page": dct['seed'],
            "prop": "wikitext",
            "format": "json"
        }
        response_seeds = requests.get(url, params = params_seeds)
        data_seeds = response_seeds.json()['parse']['wikitext']['*']
        end_indx_seeds = data_seeds.find("\n}}")
        data_seeds = data_seeds[2:end_indx_seeds]
        info_seeds = data_seeds.split('\n')
        dct_seeds = {info_seeds[i].split('=')[0].strip().strip('|'):
                     info_seeds[i].split('=')[1].strip().strip('|') for i in range(1,len(info_seeds))}
        popped_lst = ['eng', 'image', 'crop', 'growth', 'season', 'nmday', 'sellprice', 'note', 'desc']
        for keys in popped_lst:
            dct_seeds.pop(keys, None)
        for k in dct_seeds.keys():
            match = re.search(r"\|(\d+)", dct_seeds[k])
            if match:
                dct_seeds[k] = int(match.group(1))
            else:
                dct_seeds[k] = None
        dct |= dct_seeds
        all_crops.append(dct)
        print(f"Added: {crop_name}")

with open('crops.json', 'w') as w:
    json.dump(all_crops, w, indent = 2)

