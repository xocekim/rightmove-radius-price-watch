import time
import sqlite3
import re

import requests
import lxml.html


URL_ROOT = "https://www.rightmove.co.uk/property-for-sale/find.html"
PARAMS = {
    "index": 0,
    "locationIdentifier": "REGION^888",
    "maxPrice": 270000,
    "minPrice": 200000,
    "radius": 1.0,
    "sortType": 6,
    "propertyTypes": "bungalow,detached",
    "includeSSTC": "false",
}

con = sqlite3.connect("rightmove.db")
cur = con.cursor()
page = 0
total_properties = 0
while True and page < 10:
    PARAMS["index"] = page * 24
    resp = requests.get(URL_ROOT, params=PARAMS)
    parser = lxml.html.fromstring(resp.content)
    properties = parser.cssselect("div.l-searchResult:not(.is-hidden)")
    if not properties:
        break
    for property in properties:
        if "is-hidden" in property.classes:
            continue
        p = {}
        prop_price_a = property.cssselect("a.propertyCard-salePrice")[0]
        p["id"] = int(re.search(r"properties\/(\d+)", prop_price_a.attrib["href"]).group(1))
        p["price"] = re.search(r"([\d,]+)", prop_price_a.text_content()).group(1)
        p["price"] = int(p["price"].replace(",", ""))
        p["img"] = property.cssselect("div.propertyCard-img img")[0].attrib["src"]
        p["address"] = property.cssselect("address")[0].text_content().strip()
        p["type"] = property.cssselect("h2.propertyCard-title")[0].text_content().strip()
        p["type"] = re.search(r"\d+ bedroom (.*) for sale", p["type"]).group(1)
        p["agent"] = property.cssselect("a.propertyCard-branchLogo-link")
        p["agent"] = p["agent"][0].attrib["title"].split(",")[0] if p["agent"] else "Private"
        cur.execute(
            "INSERT INTO property (id, price, address, type, agent, img, last_seen) "
            "VALUES (:id, :price, :address, :type, :agent, :img, CURRENT_TIMESTAMP) "
            "ON CONFLICT (id) DO UPDATE SET price=:price, address=:address, type=:type, "
            "agent=:agent, img=:img, last_seen=CURRENT_TIMESTAMP",
            p,
        )
        total_properties += 1
    page += 1
    time.sleep(5)
con.commit()
print(total_properties)
