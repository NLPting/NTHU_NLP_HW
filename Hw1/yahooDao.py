#coding=utf-8
import pyodbc
import pandas as pd
import re
import codecs
from datetime import date, datetime, timedelta

class DataDao():

	def __init__(self):
		self.news_config = {}
		with open('F:/FBD_PROD/Python/Yahoo_API/bapfin.properties', 'r') as f:
			for line in f:
				line = line.strip()
				if '=' not in line: continue
				if line.startswith('#'): continue

				k, v = line.split('=', 1)
				self.news_config[k] = v


		self.server = self.news_config['server']
		self.database = self.news_config['database']
		self.username = self.news_config['username']
		self.password = self.news_config['password']
		#self.docsubj = self.news_config['docsubj']
		self.lang = self.news_config['lang']
		self.ver = datetime.now().strftime("%Y-%m-%d")
		self.createuser = self.news_config['createuser']
		self.driver = '{ODBC Driver 13 for SQL Server}'
		self.cnxn = pyodbc.connect('DRIVER=' + self.driver +
		                      ';PORT=1433;SERVER=' + self.news_config['server'] + ';PORT=1433;DATABASE=' +
		                      self.news_config['database'] + ';UID=' + self.news_config['username'] + 
							  ';PWD=' + self.news_config['password'])
		self.cursor = self.cnxn.cursor()

	def insert_report(self, ver_no, company,op_seg , rpt_type, anal_catg_level1, anal_catg_level2 ,anal_catg_level3, preiod ,report_create_date ,num ,num_unit,curr_cd,create_user, create_date, update_user , update_date,fiscal_qtr , fiscal_year):
		exec_start_time = str(datetime.now())[0:-3]
		
		query_str = 'INSERT INTO [BAS].[SEC_FIN_CNSLDT_STMT_SUM] (VER_NO, CO_CD ,OP_SEG, RPT_TYPE, ANAL_CATG_LEVEL1, ANAL_CATG_LEVEL2,ANAL_CATG_LEVEL3, PERIOD_DESC , RPT_CREATE_DT , NUM , NUM_UNIT , CURR_CD, CREATE_USER , CREATE_DT, UPDATE_USER , UPDATE_DT ,FISCAL_QTR, FISCAL_YEAR) \
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);'
		self.cursor.execute(query_str, self.ver, company,op_seg , rpt_type , anal_catg_level1, anal_catg_level2,anal_catg_level3, preiod , exec_start_time, num,  num_unit, curr_cd, self.createuser, exec_start_time, self.createuser ,exec_start_time, fiscal_qtr , fiscal_year )
		self.cnxn.commit()

	def insert_period_map_report(self , company , call_year , call_qtr ,fiscal_year , fiscal_qtr , IS_ACTIVE ,create_user, create_date, update_user , update_date ):
		exec_start_time = str(datetime.now())[0:-3]
		query_str = 'INSERT INTO [BAS].[FIN_RPT_PERIOD_MAP] (CO_CD,CAL_YEAR_NO,CAL_QTR_NO,FISCAL_YEAR_NO,FISCAL_QTR_NO,IS_ACTIVE,CREATE_USER,CREATE_DT,UPDATE_USER,UPDATE_DT)\
		VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);'
		self.cursor.execute(query_str,company , call_year , call_qtr ,fiscal_year , fiscal_qtr , IS_ACTIVE, self.createuser,exec_start_time,self.createuser,exec_start_time)
		self.cnxn.commit()

	def update_period_map_report(self ,company ,activate, f_qtr , f_year):
		query_str = 'UPDATE [BAS].[FIN_RPT_PERIOD_MAP] SET IS_ACTIVE = ? WHERE CO_CD = ? and FISCAL_QTR_NO = ? and FISCAL_YEAR_NO = ?'
		self.cursor.execute(query_str, activate, company , f_qtr , f_year)
		self.cnxn.commit()
			

	def query_templaet_report(self , company):
		query_str = "SELECT [YAHOO_API_NAME],[SECOND_YAHOO_API_NAME],[FORMULA],[DB_NAME] From [BAS].[Y_FIN_MAP_INFO]  where [CO_CD] = ?"
		result = self.cursor.execute(query_str , company)
		result_set = result.fetchall()
		return result_set
	
	def query_data_report(self , company , db_name , qtr , year , num):
		#query_str = "SELECT * From [BAS].[SEC_FIN_CNSLDT_STMT_SUM]  where [CO_CD] = ? and [ANAL_CATG_LEVEL3] = ? and [NUM] = ? and [PERIOD_DESC] = ?"
		#query_str = "SELECT * From [BAS].[SEC_FIN_CNSLDT_STMT_SUM]  where [CO_CD] = ? and [ANAL_CATG_LEVEL3] = ? and [NUM] = ? and [FISCAL_QTR] = ? and [FISCAL_YEAR] = ?"
		#query_str = "SELECT * From [BAS].[SEC_FIN_CNSLDT_STMT_SUM]  where [CO_CD] = ? and [ANAL_CATG_LEVEL3] = ? and [FISCAL_QTR] = ? and [FISCAL_YEAR] = ?"
		query_str = "SELECT * From [BAS].[SEC_FIN_CNSLDT_STMT_SUM]  where [CO_CD] = ? and [ANAL_CATG_LEVEL3] = ? and [FISCAL_QTR] = ? and [FISCAL_YEAR] = ? and [NUM] = ?"

		result = self.cursor.execute(query_str , company , db_name , qtr , year , num)
		result_set = result.fetchall()
		return result_set

	def query_period_map_report(self , company , IS_ACTIVE):
		query_str = "SELECT [FISCAL_QTR_NO] ,[FISCAL_YEAR_NO]  From [BAS].[FIN_RPT_PERIOD_MAP]  where [CO_CD] = ? and [IS_ACTIVE] = ?"
		result = self.cursor.execute(query_str , company , IS_ACTIVE)
		result_set = result.fetchall()
		return result_set
	

if __name__ == '__main__':
	stat = DataDao()
	test = stat.query_data_report('200710' , 'Total liabilities', '3' , '2019' , 53313882.09)
	
	print(test)
	#test = stat.query_period_map_report('RTK' , 'Y')
	#print(test)
	#stat.insert_period_map_report('RTK' , '2019' , '4' ,'2019' , '4' , 'N','NULL','NULL','NULL','NULL')
	#stat.update_period_map_report('RTK','N','3','2019')
	
	
	#print(now_qtr , now_year)
	
	


	