#!/usr/bin/python

import logging
import os
#import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, create_engine, inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy import *
from statsd import StatsClient
from logging.config import dictConfig
from logging.handlers import SysLogHandler

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'DEBUG',
        'handlers': ['wsgi'],
        'propagate': True,
    }
})

import json

statsd = StatsClient(host='localhost',
                     port=8125,
                     prefix='fitcycle-api-server',
                     maxudpsize=512)

# REST Client
import requests
from requests.auth import HTTPBasicAuth

from flask import Flask, render_template, jsonify, flash, request
app = Flask(__name__)
app.debug=True

#with open('./mysql.json') as json_data:
#    data=json.load(json_data)
#    mysqlId=data['id']
#    mysqlPassword=data['password']
#    mysqlServer=data['server']
#    print mysqlId, mysqlPassword


# set variables with env variables
mysqlId=os.environ['MYSQL_ID']
mysqlPassword=os.environ['MYSQL_PASSWORD']
mysqlServer=os.environ['MYSQL_SERVER']

Base = declarative_base()

to_conn_str = 'mysql://%s:%s@%s:3306/prospect'%(mysqlId,mysqlPassword,mysqlServer)
eng_to = create_engine(to_conn_str, echo=False)
meta=MetaData(eng_to)


polls_prospect = Table('polls_prospect', meta, autoload=True, autoload_with=eng_to)

@statsd.timer('prospectPullTime')
def getPollsProspect():

    PPTable = []
    PPRow = {}

    q = select([polls_prospect.c.id, polls_prospect.c.firstname, polls_prospect.c.lastname, polls_prospect.c.email]) 

    results = q.execute()
    
    statsd.incr('ProspectPull', rate=1)

    for row in results:

        PPRow['id'] = int(row.id)
        PPRow['firstname'] = row.firstname
        PPRow['lastname'] = row.lastname
        PPRow['email'] = row.email

        PPTable.append(PPRow)

        PPRow = {}

    
 #   print "json", calljson

    return PPTable

@app.route('/api/v1.0/signups', methods=['GET'])
def get_tasks():
    app.logger.info('getting all records')
    PPTable = getPollsProspect()
    return jsonify({'polls_prospect': PPTable})


@app.route('/')
def hello_world(name=None):
	return render_template('hello.html') 


if __name__ == '__main__':

    app.run(host='0.0.0.0', port=5000)

