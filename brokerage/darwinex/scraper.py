#we can scrape the html Darwinex site for assets tradable

import json
from bs4 import BeautifulSoup


assets = {}
#it seems that our scraping had issues as the nasdaq and nyse content is the same
with open("./htmls/nasdaq.txt") as f:
    contents = f.read()
    soup = BeautifulSoup(contents, "html.parser")
    stocks = soup.find(id="stocksUsd-content")
    rows = stocks.find_all("tr")
    codes = []
    for r in rows:
        code = str(r).split("</td>")[0].split("<td>")[1] #there are better ways to get this, but this works
        codes.append(code)
    assets["nasdaq"] = codes

with open("./htmls/nyse.txt") as f:
    contents = f.read()
    soup = BeautifulSoup(contents, "html.parser")
    stocks = soup.find(id="stocksUsd-content")
    rows = stocks.find_all("tr")
    codes = []
    for r in rows:
        code = str(r).split("</td>")[0].split("<td>")[1] #there are better ways to get this, but this works
        codes.append(code)
    assets["nyse"] = codes

with open("./htmls/commodities.txt") as f:
    contents = f.read()
    soup = BeautifulSoup(contents, "html.parser")
    items = soup.find(id="commodities-content")
    rows = items.find_all("tr")
    codes = []
    for r in rows:
        code = str(r).split("</td>")[0].split("<td>")[1] #there are better ways to get this, but this works
        codes.append(code)
    assets["commodities"] = codes

with open("./htmls/fx.txt") as f:
    contents = f.read()
    soup = BeautifulSoup(contents, "html.parser")
    items = soup.find(id="forex-content")
    rows = items.find_all("tr")
    codes = []
    for r in rows:
        code = str(r).split("</td>")[0].split("<td>")[1] #there are better ways to get this, but this works
        codes.append(code)
    assets["fx"] = codes
        
with open("./htmls/indices.txt") as f:
    contents = f.read()
    soup = BeautifulSoup(contents, "html.parser")
    items = soup.find(id="indices-content")
    rows = items.find_all("tr")
    codes = []
    for r in rows:
        code = str(r).split("</td>")[0].split("<td>")[1] #there are better ways to get this, but this works
        codes.append(code)
    assets["indices"] = codes
        
fx_codes = []
for fx in assets["fx"]:
    fx_codes.append(fx[:3])
    fx_codes.append(fx[3:])
fx_codes = list(set(fx_codes))
assets["fx_codes"] = fx_codes

commodity_lables = []
for com in assets["commodities"]:
    label = com[:3] + "_" + com[3:]
    commodity_lables.append(label)

fx_lables = []
for fx in assets["fx"]:
    label = fx[:3] + "_" + fx[3:]
    fx_lables.append(label)

assets["commodities"] = commodity_lables
assets["fx"] = fx_lables

print(json.dumps(assets, indent=4))

#lets try to write this to a json file and set our dwx_config
with open("assets.json", "w") as f:
    json.dump(assets, f, indent=4)