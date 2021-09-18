import re
import aiohttp
import asyncio
import json

async def getStore(headers,user_id,region):
    session = aiohttp.ClientSession()
    async with session.get(f'https://pd.{region}.a.pvp.net/store/v2/storefront/{user_id}', headers=headers) as r:
        data = json.loads(await r.text())
    await session.close()
    skinPanel=data['SkinsPanelLayout']
    return await getSkinDetails(headers,skinPanel,region)

def convert(seconds):
    seconds = seconds % (24 * 3600)
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    return f"{hour} hours {minutes} minutes and {seconds} seconds remaining"

async def getSkinDetails(headers,skinPanel,region):
    session = aiohttp.ClientSession()
    async with session.get(f'https://shared.{region}.a.pvp.net/content-service/v2/content', headers=headers) as r:
        content = json.loads(await r.text())
    async with session.get(f'https://pd.{region}.a.pvp.net/store/v1/offers/', headers=headers) as r:
        offers=json.loads(await r.text())
    
    await session.close()
    
    skinIDcost=[]
    skinNames=[]
    offerSkins=[]
    
    for item in offers["Offers"]:
        if (skinPanel['SingleItemOffers'].count(item["OfferID"].lower())>0):
            skinIDcost.append({"id":item["OfferID"].lower(),"cost":list(item["Cost"].values())[0]})
    
    for item in content['SkinLevels']:
        if (skinPanel['SingleItemOffers'].count(item["ID"].lower())>0):
            skinNames.append({"id":item["ID"].lower(),"name":item["Name"]})

    for item in skinNames:
        for item2 in skinIDcost:
            if item['id'] in item2['id']:
                offerSkins.append([item["name"],item2["cost"],f"https://media.valorant-api.com/weaponskinlevels/{item['id']}/displayicon.png"])
    return(offerSkins,convert(skinPanel["SingleItemOffersRemainingDurationInSeconds"]))