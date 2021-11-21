import json
import requests


token = "YOUR TOKEN"
headers= {"Authorization": "Bearer %s" % token}
api = "https://api-invest.tinkoff.ru/openapi/"

def get_operations():
    endpoint = "operations?from=2021-04-25&to=2021-11-17T18%3A38%3A33%2B03%3A00"
    operations = requests.get(api + endpoint, headers=headers).json()
   # print(json.dumps(operations, ensure_ascii=False, sort_keys=True,indent=4))
    return operations

def get_portfolio():
    endpoint = "portfolio"
    portfolio = requests.get(api + endpoint, headers=headers).json()
    return portfolio

def get_currencies():
    endpoint = "portfolio/currencies"
    currencies = requests.get(api + endpoint, headers=headers).json()
    return currencies


currency = get_currencies()
operations = get_operations()
portfolio = get_portfolio()

sum = 0 #Все внесенные деньги
commissionUSD = 0  #Комиссия в USD
commissionRUB = 0 #Комиссия в рублях
inTheAccRub = 0 #Рубли на счету на данный момент
inTheAccUSD = 0 #Доллары на счету на данный момент
currencyBalance = 0 #USD на счету
currencyUSD = 0 #Курс USD
expectedYield = 0 #Изменение цены
buyPrice = 0 #Цена покупки

for item in operations["payload"]["operations"]:
    if item["operationType"] == "PayIn":
        sum += float(item["payment"])
    if item["operationType"] == "BrokerCommission":
        if item["currency"] == "USD":
            commissionUSD += float(item["payment"])
        else:
            commissionRUB += float(item["payment"])
    if item["operationType"] == "ServiceCommission":
        commissionRUB += float(item["payment"])


for item in portfolio["payload"]["positions"]:
    if item["instrumentType"] == "Currency":
        currencyBalance += float(item["balance"])
        expectedYield += float(item["expectedYield"]["value"])
        buyPrice +=  float(item["averagePositionPrice"]["value"])
    else:
            if item["averagePositionPrice"]["currency"] == "USD":
                inTheAccUSD += float(item["averagePositionPrice"]["value"]*item["balance"]+item["expectedYield"]["value"])
            else:
                inTheAccRub += float(item["averagePositionPrice"]["value"]*item["balance"]+item["expectedYield"]["value"])


for item in currency["payload"]["currencies"]:
    if item["currency"] == "RUB":
        inTheAccRub += float(item["balance"])
    

currencyUSD = (currencyBalance*buyPrice+expectedYield)/currencyBalance
allUSD = inTheAccUSD + currencyBalance #USD в акциях и на счете
earn = allUSD*currencyUSD+inTheAccRub-sum
print("Внесено денег:", sum, "руб.")
print("Комиссия за весь период в долларах:", commissionUSD, "$")
print("в рублях:", commissionRUB, "руб.")
print("Всего затрачено на коммисию:", commissionRUB + commissionUSD*currencyUSD, "руб.")
print(" ")
print("Сумма рублей на счету:", inTheAccRub, "руб.")
print("Сумма долларов на счету (вместе с валютой):", allUSD, "$")
print("в рублях:", (allUSD*currencyUSD), "руб.")
print("Всего денег на брокерском счете:", (allUSD*currencyUSD+inTheAccRub), "руб.")
print(" ")
print("За это время вы получили:", (earn - commissionRUB - commissionUSD*currencyUSD), "руб.")
print("с учетом комиссии:", earn, "руб.")
