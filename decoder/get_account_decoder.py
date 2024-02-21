from decimal import Decimal
import requests
import hmac
import hashlib
import time
import urllib.parse

def decoder(data):
    
    # print(len(data))
    obj = dict()

    blockLength = int.from_bytes(data[0:2],byteorder='little') 
    templateId = int.from_bytes(data[2:4],byteorder='little')
    schemaId = int.from_bytes(data[4:6],byteorder='little') 
    version = int.from_bytes(data[6:8],byteorder='little') 

    obj['blockLength'] = blockLength
    obj['templateId'] = templateId
    obj['schemaId'] = schemaId
    obj['version'] = version

    if templateId == 400:
        
        commissionExponent = int.from_bytes(data[8:9],byteorder='little',signed=True)
        commissionRateMaker = int.from_bytes(data[9:17],byteorder='little')
        commissionRateTaker = int.from_bytes(data[17:25],byteorder='little')
        commissionRateBuyer = int.from_bytes(data[25:33],byteorder='little')
        commissionRateSeller = int.from_bytes(data[33:41],byteorder='little')
        
        canTrade = True if int.from_bytes(data[41:42],byteorder='little') else False
        canWithdraw = True if int.from_bytes(data[42:43],byteorder='little') else False
        canDeposit = True if int.from_bytes(data[43:44],byteorder='little') else False
        brokered = True if int.from_bytes(data[44:45],byteorder='little') else False
        requireSelfTradePrevention = True if int.from_bytes(data[45:46],byteorder='little') else False
        preventSor = True if int.from_bytes(data[46:47],byteorder='little') else False
        updateTime = int.from_bytes(data[47:55],byteorder='little')      
        accountType = int.from_bytes(data[55:56],byteorder='little')
        tradeGroupId = int.from_bytes(data[56:64],byteorder='little')
        uid = int.from_bytes(data[64:72],byteorder='little')
        

        obj['commissionExponent'] = commissionExponent
        obj['commissionRateMaker'] = commissionRateMaker
        obj['commissionRateTaker'] = commissionRateTaker
        obj['commissionRateBuyer'] = commissionRateBuyer
        obj['commissionRateSeller'] = commissionRateSeller

        obj['canTrade'] = canTrade
        obj['canWithdraw'] = canWithdraw
        obj['canDeposit'] = canDeposit
        obj['brokered'] = brokered
        obj['requireSelfTradePrevention'] = requireSelfTradePrevention
        obj['preventSor'] = preventSor
        obj['updateTime'] = updateTime
        obj['accountType'] = accountType
        obj['tradeGroupId'] = tradeGroupId
        obj['uid'] = uid




        group_balances_blockLength = int.from_bytes(data[72:74],byteorder='little')
        group_balances_numInGroup = int.from_bytes(data[74:78],byteorder='little')

        obj['group_balances_blockLength'] = group_balances_blockLength
        obj['group_balances_numInGroup'] = group_balances_numInGroup

        balances = list()

        balance_offset = 0
        for i in range(group_balances_numInGroup):

            balance = dict()

            exponent = int.from_bytes(data[78+balance_offset:79+balance_offset],byteorder='little',signed=True)
            free = int.from_bytes(data[79+balance_offset:87+balance_offset],byteorder='little')
            locked = int.from_bytes(data[87+balance_offset:95+balance_offset],byteorder='little')
            

            asset_length = int.from_bytes(data[95+balance_offset:96+balance_offset],byteorder='little')
            asset_varData = data[96+balance_offset:96+asset_length+balance_offset]
            
            balance_offset = balance_offset + group_balances_blockLength + asset_length + 1

            balance['exponent'] = exponent
            balance['free'] = str(Decimal(free)*Decimal(10)**Decimal(exponent))
            balance['locked'] = str(Decimal(locked)*Decimal(10)**Decimal(exponent))
            balance['asset_length'] = asset_length
            balance['asset_varData'] = asset_varData.decode(encoding='utf-8')

            balances.append(balance)

        
        obj['balances'] = balances

        
        permissions_start = 78 + balance_offset

        # print(data[permissions_start:len(data)])
        # print(data[permissions_start:len(data)].hex())

        group_permissions_blockLength = int.from_bytes(data[permissions_start:permissions_start+2],byteorder='little')
        group_permissions_numInGroup = int.from_bytes(data[permissions_start+2:permissions_start+6],byteorder='little')

        obj['group_permissions_blockLength'] = group_permissions_blockLength
        obj['group_permissions_numInGroup'] = group_permissions_numInGroup
        # print(group_permissions_blockLength)
        # print(group_permissions_numInGroup)

        permissions = list()

        permission_offset = 0
        for i in range(group_permissions_numInGroup):
            permission = dict()

            permission_length = int.from_bytes(data[permissions_start+6+permission_offset:permissions_start+7+permission_offset],byteorder='little')
            permission_varData = data[permissions_start+7+permission_offset:permissions_start+7+permission_length+permission_offset]

            permission_offset = permission_offset + 0 + permission_length + 1

            permission['permission_length'] = permission_length
            permission['permission_varData'] = permission_varData.decode(encoding='utf-8')

            permissions.append(permission)

        obj['permissions'] = permissions




        reduceOnlyAssets_start = permissions_start+6+permission_offset

        group_reduceOnlyAssets_blockLength = int.from_bytes(data[reduceOnlyAssets_start:reduceOnlyAssets_start+2],byteorder='little')
        group_reduceOnlyAssets_numInGroup = int.from_bytes(data[reduceOnlyAssets_start+2:reduceOnlyAssets_start+6],byteorder='little')
        obj['group_reduceOnlyAssets_blockLength'] = group_reduceOnlyAssets_blockLength
        obj['group_reduceOnlyAssets_numInGroup'] = group_reduceOnlyAssets_numInGroup
        # print(group_reduceOnlyAssets_blockLength)
        # print(group_reduceOnlyAssets_numInGroup)

        reduceOnlyAssets = list()

        reduceOnlyAsset_offset = 0

        for i in range(group_reduceOnlyAssets_numInGroup):
            reduceOnlyAsset = dict()

            reduceOnlyAsset_length = int.from_bytes(data[reduceOnlyAssets_start+6+reduceOnlyAsset_offset:reduceOnlyAssets_start+7+reduceOnlyAsset_offset],byteorder='little')
            reduceOnlyAsset_varData = data[reduceOnlyAssets_start+7+reduceOnlyAsset_offset:reduceOnlyAssets_start+7+reduceOnlyAsset_length+reduceOnlyAsset_offset]

            reduceOnlyAsset_offset = reduceOnlyAsset_offset + 0 + reduceOnlyAsset_length + 1

            reduceOnlyAsset['reduceOnlyAsset_length'] = reduceOnlyAsset_length
            reduceOnlyAsset['reduceOnlyAsset_varData'] = reduceOnlyAsset_varData.decode(encoding='utf-8')

            reduceOnlyAssets.append(reduceOnlyAsset)

        obj['reduceOnlyAssets'] = reduceOnlyAssets



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
    endpoint_path = '/api/v3/account'

    timestamp = round(time.time()*1000)
    params = {
        "recvWindow": 60000,
        "timestamp": timestamp
    }
    querystring = urllib.parse.urlencode(params)
    print(querystring,'\n')

    querystring = urllib.parse.urlencode(params)
    signature = hmac.new(secret_key.encode('utf-8'),msg = querystring.encode('utf-8'), digestmod = hashlib.sha256).hexdigest()
    url = base_url + endpoint_path + "?" + querystring + "&signature=" + signature

    print(url,'\n')

    payload = {}
    headers= {
        'Accept':'application/sbe',
        'X-MBX-SBE': '1:0',
        'X-MBX-APIKEY': api_key
    }

    response = requests.get(url, headers=headers, data = payload)

    print(response.status_code)

    data = response.content

    print(decoder(response.content))
