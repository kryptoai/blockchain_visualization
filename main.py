from flask import Flask, request, redirect, current_app
import flask
from functools import wraps
from pymongo import MongoClient
import requests
import json
import time

app = Flask(__name__)

@app.route('/', methods=['GET','POST'])
def reply():
    data = request.get_json()
    # print data["walletId"]
    # nodes = []
    # edges = []
    # obj = {}
    # nodes,edges = findWalletTxs(data["walletId"])
    # obj = findWalletTxs(data["walletId"])
    # obj["nodes"] = nodes
    # obj["edges"] = edges
    # print json.dumps(obj)
    if request.method == "POST":
        data = request.get_json()
        print data
        obj = findWalletTxs(data["walletId"])
        obj["addressInfo"] = addressInfo(data["walletId"])
        obj["txsHistory"] = txsHistory(data["walletId"])
        print "************"
        print firstTx(txsHistory(data["walletId"]))
        print "*************"
        print json.dumps(obj)
        return flask.jsonify(obj)
        # print json.dumps(addressInfo(data["walletId"]))

        # return flask.jsonify({ "nodes" : ["123" , "456" , "789"], "edges" : [{ "123" : "789" }, {"456": "789"}] })
        # return flask.jsonify({ "nodes" : { "regular" : ["123" , "456" , "789"], "intermediary": ["213", "345", "111"] }, "edges" : [{"123" : "456"}] })
    elif request.method == "GET":
        return "test"

# { "nodes" : ["123" , "456" , "789"], "edges" : [{ "from" : "123", "intermediary": "54300", "value": "1.2"} }, { "intermediary":"54300", "to": "789", "value": "0.7"}] }

# { "nodes" : { "regular" : ["123" , "456" , "789"], "intermediary": ["213", "345", "111"] }, "edges" : [{ "from" : "123", "to": "54300", "value": "1.2"} }, { "from":"54300", "to": "789", "value": "0.7"}], "addressInfo": { "coinRisk": "45", "classification": "exchange", "balance": "12", "balanceUSD": "200000", "totalTxs": "6", "avgTxs": "514.2", "firstReceived": "08/16/2014 22:43", "totalReceived": "92", "totalSent": "92"} , "txsHistory": [ { "blockHeight": "500000", "txsHash": "a00...", "txsDate": "12/20/2017", "amount": "2", "amountUSD": "13000", "from": "blah", "to": "blah" } ] }



@app.route('/data')
def data():
    return "data"

def findWalletTxs(walletId):
    nodes = []
    inter_nodes = []
    edges = []
    client = MongoClient('18.222.1.53',username='admin',password='diet4coke')
    db = client.cryptoData
    queryWallet = { "_id": walletId}
    cursor = db.wallets.find(queryWallet)
    for wallet in cursor:
        # print json.dumps(wallet)
        # break
        for txs in wallet["txs"]:

            # print json.dumps(txs)
            # break

            # if only 1 sender  
            if len(txs["vin"]) < 2:
                in_addr = txs["vin"][0]["addr"]
                # add nodes 
                if in_addr not in nodes:
                    nodes.append(in_addr)
                for vout in txs["vout"]:
                    out_addr = vout["scriptPubKey"]["addresses"][0]
                    if out_addr not in nodes:
                        nodes.append(out_addr)
                    edge_obj = {}
                    edge_obj["from"] = in_addr
                    edge_obj["to"] = out_addr
                    tx_value = vout["value"]
                    edge_obj["value"] = tx_value
                    edges.append(edge_obj)

            # if multiple senders 
            elif len(txs["vin"]) > 1:
                # add in nodes 
                for vin in txs["vin"]:
                    in_addr = vin["addr"]
                    if in_addr not in nodes:
                        nodes.append(in_addr)
                    edge_obj = {}
                    edge_obj["from"] = in_addr
                    tx_id = txs["txid"]
                    if tx_id not in inter_nodes:
                        inter_nodes.append(tx_id)
                    edge_obj["to"] = tx_id
                    tx_value = vin["value"]
                    edge_obj["value"] = str(tx_value)
                    edges.append(edge_obj)
                # add out nodes
                for vout in txs["vout"]:
                    out_addr = vout["scriptPubKey"]["addresses"][0]
                    if out_addr not in nodes:
                        nodes.append(out_addr)
                    edge_obj = {}
                    edge_obj["to"] = out_addr
                    tx_id = txs["txid"]
                    if tx_id not in inter_nodes:
                        inter_nodes.append(tx_id)
                    edge_obj["from"] = tx_id
                    tx_value = vout["value"]
                    edge_obj["value"] = str(tx_value)
                    edges.append(edge_obj)

        all_nodes = {}
        all_nodes["regular"] = nodes
        all_nodes["intermediary"] = inter_nodes
        return_obj = {}
        return_obj["nodes"] = all_nodes
        return_obj["edges"] = edges
        return return_obj

def addressInfo(addressId):
    addressInfo = {}
    addressInfo["coinRisk"] = coinRisk(addressId)
    addressInfo["classification"] = classify(addressId)
    r = requests.get("https://blockexplorer.com/api/addr/" + addressId + "/balance")
    addressInfo["balance"] = r.text
    addressInfo["balanceUSD"] = btcUSD(addressInfo["balance"])
    addressInfo["totalTxs"] = numberOfTxs(addressId)
    r = requests.get("https://blockexplorer.com/api/addr/" + addressId + "/totalReceived")
    addressInfo["totalReceived"] = int(r.text) * 0.00000001
    r = requests.get("https://blockexplorer.com/api/addr/" + addressId + "/totalSent")
    addressInfo["totalSent"] = int(r.text) * 0.00000001
    addressInfo["avgTxs"] = float(addressInfo["totalSent"]) / float(numberOfTxs(addressId))
    return addressInfo


def btcUSD(btc):
    r = requests.get("https://api.coinmarketcap.com/v1/ticker/bitcoin/")
    data = json.loads(r.text)
    return float(btc) * float(data[0]["price_usd"])

def numberOfTxs(addressId):
    client = MongoClient('18.222.1.53',username='admin',password='diet4coke')
    db = client.cryptoData
    queryWallet = { "_id": addressId }
    cursor = db.wallets.find(queryWallet)
    for wallet in cursor:
        counter = 0
        for txs in wallet["txs"]:
            counter += 1
    return counter

def txsHistory(addressId):
    client = MongoClient('18.222.1.53',username='admin',password='diet4coke')
    db = client.cryptoData
    queryWallet = { "_id": addressId }
    cursor = db.wallets.find(queryWallet)
    txList = []
    for wallet in cursor:
        for txs in wallet["txs"]:
            data = {}
            data["txsHash"] = txs["txid"]
            data["height"] = txs["blockheight"]
            data["time"] = txs["blocktime"]
            data["amount"] = txs["valueOut"]
            data["amountUsd"] = btcUSD(data["amount"])
            # get in address and amount 
            in_list = []
            for vin in txs["vout"]:
                in_obj = {}
                in_addr = vin["scriptPubKey"]["addresses"][0]
                in_value = vin["value"]

                in_obj["addr"] = in_addr
                in_obj["value"] = in_value

                in_list.append(in_obj)

            # get in address and amount 
            out_list = []
            for vout in txs["vin"]:
                out_obj = {}
                out_addr = vout["addr"]
                out_value = vout["value"]

                out_obj["addr"] = out_addr
                out_obj["value"] = out_value

                out_list.append(out_obj)            

            data["from"] = in_list
            data["to"] = out_list
            txList.append(data)
    return txList

def firstTx(txList):
    firstTxTime = time.time()
    for tx in txList:
        if tx["time"] <= firstTxTime:
            firstTxTime = tx["time"]
    return firstTxTime

def coinRisk(addressId):
    return "40"

def classify(addressId):
    return "Exchange"


if __name__ == "__main__":
	app.run()


client = MongoClient('18.222.1.53/admin',username='admin',password='diet4coke')
