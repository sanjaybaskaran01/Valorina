import aiohttp

async def viewBal(headers,puuid,region):
    session = aiohttp.ClientSession()
    async with session.get(f'https://pd.{region}.a.pvp.net/store/v1/wallet/{puuid}', headers=headers, json={}) as r:
        data = await r.json()
    await session.close()
    return(data['Balances']['85ad13f7-3d1b-5128-9eb2-7cd8ee0b5741'],data['Balances']['e59aa87c-4cbf-517a-5983-6e81511be9b7'])

