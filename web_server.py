# -*- coding:utf-8 -*-
from flask import Flask,jsonify,request
import sqlite3
import flight.Fly
app = Flask(__name__)

@app.route('/')
def index():
	return 'Hello World'

@app.route('/Flight/api/v1.0/query',methods=['GET'])	#参数: 航班号flightno 出发机场三字码depairport  目的机场三字码arrairport	计划日期date
def get_json():
	FlightNo = request.args.get('flightno',0) #航班号
	depair = request.args.get('depairport',0) #出发机场三字码
	arrair = request.args.get('arrairport',0) #到达机场三字码
	date = request.args.get('date',0) #出发时间
	if FlightNo == 0 or depair == 0 or arrair == 0 or date == 0:
		return u'参数传输错误！'
	if date.find('-')!=-1:
		date_list = date.split('-')
		if len(date_list) != 3:
			return u'日期参数传输错误！'
	else:
		return u'日期参数传输错误！'
	fly = flight.Fly.Flight(FlightNo,arrair,depair,date_list)
	fly.predict()
	# return str(fly.state)
	return jsonify({'Flight': fly.json})

if __name__ == '__main__':
	app.run(host='0.0.0.0',port=8080)