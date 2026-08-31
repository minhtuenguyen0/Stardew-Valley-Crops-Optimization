let crops_name = {};
fetch("crops.json")
.then(response => response.json())
.then(data => {
    for (let crop of data) {
        crops_name[crop.eng] = crop;
    }
    const ranked = rank_crop(2, 'Summer');
    console.log(crops_name);
    console.log(ranked)
});

function qualifying_crops(crop_name, season) {
    const crop = crops_name[crop_name];
    if (!crop.season.includes(season)) {
        return false;
    } else {
        return true;
    }
}

function profit_calc(day, season, crop_name, store = 'General', fertilizer = null, multiseason = false, profession = null) {
    const crop = crops_name[crop_name];
    let sell_price = crop.sellprice;
    const regrow = crop.regrowDays;
    let remaining = 28 - day;
    let harvests = 1;

    // seed prices
    let seed_price;
    if (store === 'General') {
        seed_price = crop.gPrice || crop.oPrice || crop.tPrice;
    } else {
        seed_price = crop.jPrice;
    }
    if (seed_price == null) {
        seed_price = 0;
    }

    // fertilizer
    let growth_days;
    if (fertilizer === 'Speed-Gro') {
        growth_days = Math.floor(crop.growth * 0.9);
    } else if (fertilizer === 'Deluxe Speed-Gro') {
        growth_days = Math.floor(crop.growth * 0.75);
    } else if (fertilizer === 'Hyper Speed-Gro') {
        growth_days = Math.floor(crop.growth * 0.66);
    } else {
        growth_days = crop.growth;
    }

    // check if growth days is more than remaining time
    if (growth_days > remaining) {
        return null;
    }

    // professions
    if (profession === 'Tiller') {
        sell_price = Math.floor(sell_price + (sell_price * 0.1));
    }
    if (profession === 'Agriculturist') {
        growth_days = Math.floor(growth_days * 0.9);
    }

    // multiple harvest
    if (crop.multi != null) {
        sell_price *= crop.multi;
    }

    // mutiseason is false if the user doesn't want the crop to go over multiple seasons
    if (multiseason && (crop.season.length > 1)){
        let indx = crop.season.indexOf(season);
        if (indx === (crop.season.length - 1)) {
            // does nothing
        } else {
            remaining += (crop.season.length - (indx + 1)) * 28;
        }
    }

    let profit = sell_price - seed_price;

    // regrowth
    if (regrow != null) {
        const regrow_days = remaining - growth_days;
        harvests = Math.floor(regrow_days / regrow);
        profit += harvests * sell_price;
    }

    const gold_per_day = profit / remaining;

    return {'profit': profit, 'gold_per_day': gold_per_day};
};

function sortResults(results, sortBy) {
    results.sort((a, b) => b[1][sortBy] - a[1][sortBy]);
    return results;
}

function rank_crop(day, season, store = 'General', fertilizer = null, multiseason = false, profession = null, sort_by = 'profit') {
    const crops_profit = {};
    for (let crop in crops_name) {
        const in_season = qualifying_crops(crop, season);
        if (in_season == false) {
            continue;
        }

        const result = profit_calc(day, season, crop, store, fertilizer, multiseason, profession);
        if (result == null) {
            continue;
        }
        const {profit, gold_per_day} = result;
        crops_profit[crop] = {profit: profit, gold_per_day: gold_per_day};
    }
    const sorted_crops = sortResults(Object.entries(crops_profit), sort_by);
    return sorted_crops
}