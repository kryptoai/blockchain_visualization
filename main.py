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
    findWalletTxs(data["walletId"])
    if request.method == "POST":
        return flask.jsonify({ "nodes" : ["123" , "456" , "789"], "edges" : [{ "123" : "789" }, {"456": "789"}] })
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
            for out in txs["vout"]:
                out_addr = out["scriptPubKey"]["addresses"][0]
                print out_addr
                if out_addr not in nodes:
                    nodes.append(out_addr)
                else:
                    continue
        print nodes
        return wallet
        break

if __name__ == "__main__":
	app.run()


client = MongoClient('18.222.1.53/admin',username='admin',password='diet4coke')
