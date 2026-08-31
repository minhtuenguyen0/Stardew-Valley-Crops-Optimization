import json

with open("crops.json") as f:
    crops = json.load(f)

crops_name = {crop['eng']: crop for crop in crops}

def qualifying_crops(crop_name, season):
    crop = crops_name[crop_name]
    if season not in crop['season']:
        return False
    else:
        return True

def profit_calc(day, season, crop_name, store = 'General', fertilizer = None, multiseason = False, profession = None):
    crop = crops_name[crop_name]
    sell_price = crop['sellprice']
    regrow = crop.get('regrowDays')
    remaining = 28 - day
    harvests = 1

    # seed prices
    if store == 'General':
        seed_price = crop.get('gPrice') or crop.get('oPrice') or crop.get('tPrice')
    else: # joja
        seed_price = crop.get('jPrice')

    if seed_price == None:
        seed_price = 0
        
    # fertilizer
    if fertilizer == 'Speed-Gro':
        growth_days = int(crop['growth'] * 0.9)
    elif fertilizer == 'Deluxe Speed-Gro':
        growth_days = int(crop['growth'] * 0.75)
    elif fertilizer == 'Hyper Speed-Gro':
        growth_days = int(crop['growth'] * 0.66)
    else:
        growth_days = crop['growth']

    # check if growth days is more than remaining time
    if growth_days > remaining:
        return None

    # professions
    if profession == 'Tiller':
        sell_price = int(sell_price + (sell_price * 0.1))
    if profession == 'Agriculturist':
        growth_days = int(growth_days * 0.9)
    
    # multiple harvest
    if crop['multi'] is not None:
        sell_price *= crop['multi']

    # multiseason is false if the user doesn't want the crop to go over multiple seasons
    if multiseason:
        if len(crop['season']) > 1:
            indx = crop['season'].index(season)
            if indx == (len(crop['season']) - 1):
                pass
            else:
                remaining += (len(crop['season']) - (indx + 1)) * 28

    profit = sell_price - seed_price

    # regrowth
    if regrow is not None:
        regrow_days = remaining - growth_days
        harvests = regrow_days // regrow
        profit += harvests * sell_price

    gold_per_day = profit / remaining

    return profit, gold_per_day


def rank_crops(day, season, store = 'General', fertilizer = None, multiseason = False, profession = None, sort_by = 'profit'):
    crops_profit = {}
    for crop in crops_name:
        in_season = qualifying_crops(crop, season)
        if not in_season:
            continue
        result = profit_calc(day, season, crop, store, fertilizer, multiseason, profession)
        if result == None:
            continue
        profit, gold_per_day = result
        crops_profit[crop] = {'profit': profit, 'gold_per_day': gold_per_day}

    sorted_crops = dict(sorted(crops_profit.items(), key = lambda item: item[1][sort_by], reverse= True))
    return list(sorted_crops.items()) # all crops