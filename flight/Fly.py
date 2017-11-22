# -*- coding:utf-8 -*-
import sqlite3
import datetime,os,sys
path = os.getcwd()
os.chdir(path+r'\libsvm-3.21\python')
sys.path.append(path+r'\libsvm-3.21\python')
from svmutil import *
os.chdir(path)
sys.path.append(path)
class Flight(object):
	"""docstring for Flight"""
	#FliNo 航班号  #Arrsan 目的机场	#Depsan 出发机场 #Date	出发日期
	def __init__(self, FliNo,Arrsan,Depsan,Date):
		super(Flight, self).__init__()
		self.FliNo = FliNo
		self.Arrsan = Arrsan
		self.Depsan = Depsan
		self.json = dict(flight_no=self.FliNo,plan_dep_date='',plan_arv_date='',plan_dep_time='',plan_arv_time='',fcst_dep_date='',fcst_arv_date='',fcst_dep_time='',fcst_arv_time='',is_delayed=False)
		self.Date = Date 
		# self.time_difference(Date)
		self.DB = sqlite3.connect(path+'\\DB.db')	#存储需要用到的数据
		self.April = []	#取出四月用于预测的特征值
		self.state = 0    #三种状态   0 表示初始化   'ab'表示航班无前序航班   'abc'表示航班有前序航班
		self.delay = [0,0] #第一个元素表示起飞延误  第二个元素表示到达延误
		self.time_gather = []	#三个元素   1.预计起飞时间  2.预计到达时间 	3.日期
	def predict(self): #Flight主函数
		self.share_query()
		self.switch_fight()
		self.switch_air()
		self.Get_April()
		self.write_txt()
		self.data_guiyi()
		self.use_model()
		self.handle()
	def switch_fight(self):	#量化航班号
		cur = self.DB.cursor()
		sql = "SELECT ID FROM Company WHERE Company='"+self.FliNo[:2]+"'"
		cur.execute(sql)
		for row in cur.fetchall():
			self.FliNo = str(row[0]) + str(self.FliNo[2:])

	def share_query(self):	#查询是否共享航班，如果是则改变航班号为主航班
		cur = self.DB.cursor()
		sql = "SELECT FlightNo FROM ab_share WHERE FlightNo2='"+self.FliNo+"'"
		cur.execute(sql)
		for row in cur.fetchall():
			self.FliNo = row[0]
			return
		sql = "SELECT FlightNo FROM abc_share WHERE FlightNo2='"+self.FliNo+"'"
		cur.execute(sql)
		for row in cur.fetchall():
			self.FliNo = row[0]
			break

	def Get_April(self):	#获取四月数据
		cur = self.DB.cursor()
		sql = "SELECT * FROM ab_data WHERE FlightNo='"+self.FliNo+"' and DepAirport='"+self.Depsan+"' and ArrAirport='"+self.Arrsan+"' and TimeSeries="+str(self.time_difference(self.Date))
		cur.execute(sql)
		for row in cur.fetchall():
			for i in xrange(15,len(row)):
				self.April.append(row[i])
			self.json['plan_dep_time'] = self.switch_time(row[4])
			self.json['plan_arv_time'] = self.switch_time(row[5])
			d1 = datetime.datetime(int(self.Date[0]),int(self.Date[1]),int(self.Date[2]))
			self.json['plan_dep_date'] = d1.strftime("%Y-%m-%d")
			d1 = d1 + datetime.timedelta(int(row[6]))
			self.json['plan_arv_date'] = d1.strftime("%Y-%m-%d")
			self.time_gather.append(row[4])
			self.time_gather.append(row[5])
			self.time_gather.append(row[0])
			return
		sql = "SELECT * FROM abc_data WHERE FlightNo='"+self.FliNo+"' and DepAirport='"+self.Depsan+"' and ArrAirport='"+self.Arrsan+"' and TimeSeries="+str(self.time_difference(self.Date))
		cur.execute(sql)
		for row in cur.fetchall():
			for i in xrange(15,len(row)):
				self.April.append(row[i])
			self.json['plan_dep_time'] = self.switch_time(row[4])
			self.json['plan_arv_time'] = self.switch_time(row[5])
			d1 = datetime.datetime(int(self.Date[0]),int(self.Date[1]),int(self.Date[2]))
			self.json['plan_dep_date'] = d1.strftime("%Y-%m-%d")
			d1 = d1 + datetime.timedelta(int(row[6]))
			self.json['plan_arv_date'] = d1.strftime("%Y-%m-%d")
			self.time_gather.append(row[4])
			self.time_gather.append(row[5])
			self.time_gather.append(row[1])
			return
	def switch_air(self):
		cur = self.DB.cursor()
		sql = "SELECT * FROM air WHERE air='"+self.Arrsan+"'"
		cur.execute(sql)
		row = cur.fetchone()
		if len(row) != 0:
			self.Arrsan = str(int(row[0]))
		sql = "SELECT * FROM air WHERE air='"+self.Depsan+"'"
		cur.execute(sql)
		row = cur.fetchone()
		if len(row) != 0:
			self.Depsan = str(int(row[0]))
	def switch_time(self,time_int):
		if int(time_int)<60:
			return '00:'+str(int(time_int))
		else:
			hour = int(int(time_int)/60)
			minute = int(int(time_int)%60)
			if hour<10:
				hour = '0'+str(hour)
			if minute<10:
				minute = '0'+str(minute)
			return str(hour)+':'+str(minute)

	def time_difference(self,date_list):
		d1 = datetime.datetime(int(date_list[0]),int(date_list[1]),int(date_list[2]))
		d2 = datetime.datetime(2016,1,2)
		return (d1-d2).days

	def write_txt(self):
		f = open(os.getcwd()+r'\value.txt','w')
		newlist = []
		newlist.append('0')
		count  = 0
		for value in self.April:
			count = count + 1
			newlist.append(str(count)+':'+value)
		wenben = ' '.join(newlist)
		if len(self.April)>16:
			self.state = 'abc'
		else:
			self.state = 'ab'
		f.write(wenben+'\n')
		f.close()

	def data_guiyi(self):
		cmd = os.getcwd()+r'\libsvm-3.21\windows\svm-scale.exe -r '+os.getcwd()+r'\rule\guize_'+self.state+'_qifei\\'+self.FliNo+'_guize.txt value.txt>qifei.txt'
		os.system(cmd)
		cmd = os.getcwd()+r'\libsvm-3.21\windows\svm-scale.exe -r '+os.getcwd()+r'\rule\guize_'+self.state+'_daoda\\'+self.FliNo+'_guize.txt value.txt>daoda.txt'
		os.system(cmd)

	def use_model(self):
		y,x = svm_read_problem(r'qifei.txt')
		model = svm_load_model(os.getcwd()+r'\model\yi_'+self.state+'_qifei\\'+self.FliNo+'.model')
		p_label,p_acc,p_val = svm_predict(y,x,model)
		qifei = p_label
		y,x = svm_read_problem(r'daoda.txt')
		model = svm_load_model(os.getcwd()+r'\model\yi_'+self.state+'_daoda\\'+self.FliNo+'.model')
		p_label,p_acc,p_val = svm_predict(y,x,model)
		daoda = p_label
		f = open(os.getcwd()+r'\rule\guize_'+self.state+'_daoda\\'+self.FliNo+'_guize.txt','r')
		try:
		     all_text = f.read()
		finally:
		     f.close()
		temp_guize = all_text.split('\n')
		y_value = temp_guize[2].split(' ')
		y_min = int(y_value[0])
		y_max = int(y_value[1])
		y_lower = -1
		y_upper = 1
		daoda = ((daoda[0] - y_lower)*(y_max-y_min)/(y_upper-y_lower))+y_min
		self.delay[1] = int(round(daoda))
		f = open(os.getcwd()+r'\rule\guize_'+self.state+'_qifei\\'+self.FliNo+'_guize.txt','r')
		try:
		     all_text = f.read()
		finally:
		     f.close()
		temp_guize = all_text.split('\n')
		y_value = temp_guize[2].split(' ')
		y_min = int(y_value[0])
		y_max = int(y_value[1])
		qifei = ((qifei[0] - y_lower)*(y_max-y_min)/(y_upper-y_lower))+y_min
		self.delay[0] = int(round(qifei))
	def handle(self):
		if self.delay[1]>0:
			self.json['is_delayed'] = True
		dep_time = self.delay[0] + int(self.time_gather[0])
		self.json['fcst_dep_time'] = self.switch_time(str(dep_time))
		arv_time = self.delay[0] + int(self.time_gather[1])
		self.json['fcst_arv_time'] = self.switch_time(str(arv_time))
		d1 = datetime.datetime(int(self.Date[0]),int(self.Date[1]),int(self.Date[2]))
		d2 = d1 + datetime.timedelta(int(dep_time/1440))
		d1 = d1 + datetime.timedelta(int(arv_time/1440))
		self.json['fcst_dep_date'] = d2.strftime("%Y-%m-%d")
		self.json['fcst_arv_date'] = d1.strftime("%Y-%m-%d")
