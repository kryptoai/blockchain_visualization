from flask import Flask, request, redirect, current_app
import flask
from functools import wraps
import json

app = Flask(__name__)

def support_jsonp(f):
    """Wraps JSONified output for JSONP"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        callback = request.args.get('callback', False)
        if callback:
            content = str(callback) + '(' + str(f().data) + ')'
            return current_app.response_class(content, mimetype='application/json')
        else:
            return f(*args, **kwargs)
    return decorated_function

@app.route('/')
@support_jsonp
def reply():
    print request.args
    callback = request.args.get('callback')
    # return '{0}({1})'.format(callback, {'node': 10, 'label': 'alex'})
    return flask.jsonify({'node': 10, 'label': 'alex'})
    # return flask.jsonify({'id': "1", 'label' : 'Alex'})


if __name__ == "__main__":
	app.run()