from decimal import Decimal
import requests
import hmac
import hashlib
import time
import urllib.parse

def decoder(data):

    blockLength = int.from_bytes(data[0:2],byteorder='little') 
    templateId = int.from_bytes(data[2:4],byteorder='little')
    schemaId = int.from_bytes(data[4:6],byteorder='little') 
    version = int.from_bytes(data[6:8],byteorder='little') 

    if templateId == 201:
        priceExponent = int.from_bytes(data[8:9],byteorder='little',signed=True)
        qtyExponent = int.from_bytes(data[9:10],byteorder='little',signed=True) 


        blockLength_group = int.from_bytes(data[10:12],byteorder='little') 
        numInGroup = int.from_bytes(data[12:16],byteorder='little') 

        # print(len(data))
        # print(blockLength_group)
        # print(numInGroup)


        trades = list()

        for i in range(numInGroup):

            trade = dict()

            id = int.from_bytes(data[16 + i*blockLength_group : 24 + i*blockLength_group], byteorder='little')  
            price = int.from_bytes(data[24 + i*blockLength_group : 32 + i*blockLength_group], byteorder='little')
            qty = int.from_bytes(data[32 + i*blockLength_group : 40 + i*blockLength_group], byteorder='little')
            quoteQty = int.from_bytes(data[40 + i*blockLength_group : 48 + i*blockLength_group], byteorder='little')
            time = int.from_bytes(data[48 + i*blockLength_group : 56 + i*blockLength_group], byteorder='little')
            isBuyerMaker = int.from_bytes(data[56 + i*blockLength_group: 57 + i*blockLength_group], byteorder='little',signed=True) 
            isBestMatch = int.from_bytes(data[57 + i*blockLength_group : 58 + i*blockLength_group], byteorder='little',signed=True) 

            trade["id"] = id
            trade["price"] = str(Decimal(price)*Decimal(10)**Decimal(priceExponent))
            trade["qty"] = str(Decimal(qty)*Decimal(10)**Decimal(qtyExponent))
            trade["quoteQty"] = str(Decimal(quoteQty)*Decimal(10)**Decimal(priceExponent))
            trade["time"] = time
            trade["isBuyerMaker"] = True if isBuyerMaker else False
            trade["isBestMatch"] = True if isBestMatch else False

            trades.append(trade)


        obj = {
            "blockLength": blockLength,
            "templateId": templateId,
            "schemaId": schemaId,
            "version": version,
            "priceExponent": priceExponent,
            "qtyExponent": qtyExponent,
            "blockLength_group": blockLength_group,
            "numInGroup": numInGroup,
            "trades": trades
        }

    elif templateId == 100:

        code = int.from_bytes(data[8:10],byteorder='little',signed=True)
        serverTime = int.from_bytes(data[10:18],byteorder='little')
        retryAfter = int.from_bytes(data[18:26],byteorder='little')

        msg_length = int.from_bytes(data[26:28],byteorder='little') 
        msg_varData = data[28:28 + msg_length]
        msg_data = int.from_bytes(data[28 + msg_length:blockLength],byteorder='little') 


        errorMessage = dict()

        errorMessage["code"] = code
        errorMessage["serverTime"] = serverTime
        errorMessage["retryAfter"] = retryAfter
        errorMessage["msg_length"] = msg_length
        errorMessage["msg_varData"] = msg_varData.decode(encoding="utf-8")
        errorMessage["msg_data"] = msg_data

        obj = {
            "blockLength": blockLength,
            "templateId": templateId,
            "schemaId": schemaId,
            "version": version,
            "errorMessage": errorMessage
        }

    return obj



if __name__ == "__main__":
    api_key = ""
    secret_key= ""
    base_url = "https://testnet.binance.vision"
    endpoint_path = '/api/v3/trades'


    params = {
        "symbol": "BTCUSDT",
        "limit": 3
    }
    querystring = urllib.parse.urlencode(params)
    print(querystring,'\n')

    url = base_url + endpoint_path + "?" + querystring #+ "&signature=" + signature
    print(url,'\n')

    payload = {}
    headers= {
        'Accept':'application/sbe',
        'X-MBX-SBE': '1:0',
        'X-MBX-APIKEY': api_key
    }

    response = requests.get(url, headers=headers, data = payload)

    print(response.status_code)

    print(decoder(response.content))
