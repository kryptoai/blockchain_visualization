from flask import Flask, request, redirect, current_app
import flask
from functools import wraps
from pymongo import MongoClient
import requests
import json

app = Flask(__name__)

# def support_jsonp(f):
#     """Wraps JSONified output for JSONP"""
#     @wraps(f)
#     def decorated_function(*args, **kwargs):
#         callback = request.args.get('callback', False)
#         if callback:
#             content = str(callback) + '(' + str(f().data) + ')'
#             return current_app.response_class(content, mimetype='application/json')
#         else:
#             return f(*args, **kwargs)
#     return decorated_function

@app.route('/', methods=['GET','POST'])
# @support_jsonp
def reply():
    data = request.get_json()
    # print data["walletId"]
    nodes = []
    edges = []
    obj = {}
    nodes,edges = findWalletTxs(data["walletId"])
    obj["nodes"] = nodes
    obj["edges"] = edges
    print json.dumps(obj)
    if request.method == "POST":
        return flask.jsonify(obj)
        # return flask.jsonify({ "nodes" : ["123" , "456" , "789"], "edges" : [{ "123" : "789" }, {"456": "789"}] })
    elif request.method == "GET":
        return "test"

# { "nodes": "" }

@app.route('/data')
def data():
    return "data"

def findWalletTxs(walletId):
    nodes = []
    edges = []
    client = MongoClient('18.222.1.53',username='admin',password='diet4coke')
    db = client.cryptoData
    queryWallet = { "_id": walletId}
    cursor = db.wallets.find(queryWallet)
    for wallet in cursor:
        for txs in wallet["txs"]:
            nodesIn = []
            nodesOut = []
            edgesTmp = []
            # print json.dumps(txs)
            # break
            for vout in txs["vout"]:
                out_addr = vout["scriptPubKey"]["addresses"][0]
                nodesOut.append(out_addr)
                # print out_addr
                # if out_addr not in nodes:
                #     nodes.append(out_addr)
                # else:
                #     continue
            for vin in txs["vin"]:
                in_addr = vin["addr"]
                nodesIn.append(in_addr)
                # if in_addr not in nodes:
                #     nodes.append(in_addr)
                # else:
                #     continue

            # create edges here
            if (len(nodesIn) >= 2 or len(nodesOut) >= 2):
                for node in nodesIn:
                    obj = {} 
                    obj[node] = txs["blockheight"]
                    edgesTmp.append(obj)
                for node in nodesOut:
                    obj = {} 
                    obj[node] = txs["blockheight"]
                    edgesTmp.append(obj)
                nodesIn.append(txs["blockheight"])
            else:
                obj = {}
                obj[nodesIn[0]] = nodesOut[0]

            for node in nodesIn:
                if node not in nodes:
                    nodes.append(node)
            for node in nodesOut:
                if node not in nodes:
                    nodes.append(node)
            for edge in edgesTmp:
                if edge not in edges:
                    edges.append(edge)
                # print edgesTmp
                # print "************"
        # print nodes
        # print "(((("
        # print edges
        # print "))))"
        # return wallet
        # break
    return nodes, edges

if __name__ == "__main__":
	app.run()


client = MongoClient('18.222.1.53/admin',username='admin',password='diet4coke')
