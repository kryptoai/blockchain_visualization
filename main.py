from flask import Flask, request, redirect, current_app
import flask
from functools import wraps
from pymongo import MongoClient
import requests
import json

app = Flask(__name__)

@app.route('/', methods=['GET','POST'])
def reply():
    data = request.get_json()
    # print data["walletId"]
    # nodes = []
    # edges = []
    # obj = {}
    # nodes,edges = findWalletTxs(data["walletId"])
    obj = findWalletTxs(data["walletId"])
    # obj["nodes"] = nodes
    # obj["edges"] = edges
    print json.dumps(obj)
    if request.method == "POST":
        return flask.jsonify(obj)
        # return flask.jsonify({ "nodes" : ["123" , "456" , "789"], "edges" : [{ "123" : "789" }, {"456": "789"}] })
        # return flask.jsonify({ "nodes" : { "regular" : ["123" , "456" , "789"], "intermediary": ["213", "345", "111"] }, "edges" : [{"123" : "456"}] })
    elif request.method == "GET":
        return "test"

# { "nodes" : ["123" , "456" , "789"], "edges" : [{ "from" : "123", "intermediary": "54300", "value": "1.2"} }, { "intermediary":"54300", "to": "789", "value": "0.7"}] }

# { "nodes" : { "regular" : ["123" , "456" , "789"], "intermediary": ["213", "345", "111"] }, "edges" : [{ "from" : "123", "to": "54300", "value": "1.2"} }, { "from":"54300", "to": "789", "value": "0.7"}] }



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
        for txs in wallet["txs"]:

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
            # print nodes 
            # print edges 
            # break




        # print nodes
        # print "*****"
        # print edges
        # break


            # if multiple senders, create intermediary nodes for each 

            # print json.dumps(txs)
            # break
            # nodesIn = []
            # nodesOut = []
            # edgesTmp = []
            # for vout in txs["vout"]:
            #     out_addr = vout["scriptPubKey"]["addresses"][0]
            #     nodesOut.append(out_addr)
            # for vin in txs["vin"]:
            #     in_addr = vin["addr"]
            #     nodesIn.append(in_addr)

            # # create edges here
            # if (len(nodesIn) >= 2 or len(nodesOut) >= 2):
            #     for node in nodesIn:
            #         obj = {} 
            #         obj[node] = txs["blockheight"]
            #         edgesTmp.append(obj)
            #     for node in nodesOut:
            #         obj = {} 
            #         obj[node] = txs["blockheight"]
            #         edgesTmp.append(obj)
            #     nodesIn.append(txs["blockheight"])
            # else:
            #     obj = {}
            #     obj[nodesIn[0]] = nodesOut[0]

            # for node in nodesIn:
            #     if node not in nodes:
            #         nodes.append(node)
            # for node in nodesOut:
            #     if node not in nodes:
            #         nodes.append(node)
            # for edge in edgesTmp:
            #     if edge not in edges:
            #         edges.append(edge)

    # return nodes, edges

if __name__ == "__main__":
	app.run()


client = MongoClient('18.222.1.53/admin',username='admin',password='diet4coke')
