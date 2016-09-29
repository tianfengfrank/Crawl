# -*- coding: utf-8 -*-
import sys
import re
import sqlite3
import json
import urllib
import subprocess
import urllib2
from urllib import urlencode
reload(sys)
sys.setdefaultencoding('utf-8')
# 获取网页内容

def hosttogeo_online_ipip(dst):
	print dst
	errorresult=["",""]
	process = subprocess.Popen(["nslookup", dst], stdout=subprocess.PIPE)
	output = process.communicate()[0].split('\n')
	#print output

	ip_arr = []
	for data in output:
		if 'Address' in data:
			ip_arr.append(data.replace('Address: ',''))
	if len(ip_arr)<=1:
		return errorresult
	 	pass

	ip_arr.pop(0)
	success = False
	attempts = 0
	print ip_arr[0]
	req = urllib2.Request("http://ipapi.ipip.net/find?addr=%s" % ip_arr[0])
	req.add_header("Token","9a8bc1a059db4a14b4feb0f38db38bbf4d5353ab")#qq：9a8bc1a059db4a14b4feb0f38db38bbf4d5353ab   #163：f4f24f5817d67448fd6c7137fdf5bbc0cec7b4ec

	while attempts < 3 and not success:
			try:
				f = urllib2.urlopen(req)
				success = True 
			except:
				attempts += 1
				if attempts==3:
					print "IOerror"
	if success:
		the_page = f.read()
		res = json.loads(the_page)
		#print [res['data'][2].encode('utf-8'),res['data'][4].encode('utf-8')]
		return [res['data'][2].encode('utf-8'),res['data'][4].encode('utf-8')]
	else:
		return errorresult
	pass

def link_analyser_ping(url):
	process = subprocess.Popen(['ping','-c 2',url], stdout=subprocess.PIPE)#根据实验结果修改ping的次数
	output = process.communicate()[0].split('\n')
	#print output[len(output)-3]
	pattern="[0-9\.]+/[0-9\.]+/[0-9\.]+/[0-9\.]+"
	time=re.findall(pattern,output[len(output)-2])
	if len(time)<=0:
		return 0
	 	pass 
	else:
		ping_time_ave=time[0].split('/')[1]
		return  float(ping_time_ave)
	pass


def crawl(url):
	db = sqlite3.connect("./geo_gov.db")
	db_handle = db.cursor()
	db.text_factory = str
	page = urllib.urlopen(url)
	html = page.read()
	print html
	regExp = "www\.[0-9a-zA-Z\.]*.[cn|com|gov|org]"
	link_list =re.findall(regExp,html)
	for temp_url in link_list:
		print temp_url
		if link_analyser_ping(temp_url)==0:
			continue
		query="select CityId from beacon where Url like '%"+temp_url+"%'"
		db_handle.execute(query)
		check=db_handle.fetchone()
		if type(check)==type(None):#如果存在，不需要加载，提高运行效率
			temp=hosttogeo_online_ipip(temp_url)
			#print temp[0]#城市
			#print temp[1]#运营商
			if temp[0]!="":
				query="select City.Id,City.ProvinceId from City where City.Name like '%"+temp[0]+"%'"
				db_handle.execute(query)
				result=db_handle.fetchone()
				if type(result)!=type(None):
					cityId=result[0]
					provinceId=result[1]
					#print type(provinceId)
					db_handle.execute("select City.Name from City where City.ProvinceId=?",(provinceId,))
					result=db_handle.fetchone()
					capital=result[0].encode('utf-8')
					print "test"
					print capital
					print temp[0]
					print "test"
					if capital.find(temp[0])!=-1:
						flag=1
						pass
					else:
						flag=0
					insert_data=(cityId,provinceId,temp_url,flag,temp[1].encode('utf-8'))
					print insert_data
					db_handle.execute("insert into beacon(CityId, ProvinceId, Url, Capital, ISP) values(?, ?, ?, ?, ?)",insert_data)
					db.commit()
				pass
			pass
		pass
	pass
def stat():
	db = sqlite3.connect("./geo_gov.db")
	db_handle = db.cursor()
	query="select COUNT(DISTINCT CityId),COUNT(DISTINCT provinceId) from beacon where ISP not like '%电信%'"
	db_handle.execute(query)
	result=db_handle.fetchall()
	print result
	pass



stat()
#crawl(sys.argv[1])


