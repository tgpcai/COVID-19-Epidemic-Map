import sys
import asyncio
import aiohttp
import time
import json
import requests
import pymysql
import traceback
from nameMap import namemap
from selenium.webdriver import Chrome, ChromeOptions


country_dict = {}


def get_tencent_data():
	#通过解析腾讯疫情网站，可以得知所有疫情数据来源于这两个url对应的api接口
	url1 = "https://view.inews.qq.com/g2/getOnsInfo?name=disease_h5"
	url2 = "https://view.inews.qq.com/g2/getOnsInfo?name=disease_other"

	#设置请求头，防止爬虫失败
	headers = {
		"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36"
	}

	#得到的r1、r2数据格式为json格式必须进行转换
	r1 = requests.get(url1, headers)
	r2 = requests.get(url2, headers)

	#将json格式转换为字典格式
	res1 = json.loads(r1.text)
	res2 = json.loads(r2.text)

	data_all1 = json.loads(res1["data"])
	data_all2 = json.loads(res2["data"])

	print(data_all2["chinaDayAddList"])

	history = {}
	for i in data_all2["chinaDayList"]:
		ds = "2020." + i["date"]
		tup = time.strptime(ds, "%Y.%m.%d")	# 匹配时间
		ds = time.strftime("%Y.%m.%d", tup) # 改变时间格式
		confirm = i["confirm"]
		suspect = i["suspect"]
		heal = i["heal"]
		dead = i["dead"]

		history[ds] = {"confirm": confirm, "suspect": suspect, "heal": heal, "dead": dead}

	for i in data_all2["chinaDayAddList"]:
		ds = "2020." + i["date"]
		if ds =="2020.01.20" or ds == "2020.01.21" or ds == "2020.01.22":
			continue

		tup = time.strptime(ds, "%Y.%m.%d")	# 匹配时间
		ds = time.strftime("%Y.%m.%d", tup) # 改变时间格式
		confirm = i["confirm"]
		suspect = i["suspect"]
		heal = i["heal"]
		dead = i["dead"]
		history[ds].update({"confirm_add": confirm, "suspect_add": suspect, "heal_add": heal, "dead_add": dead})

	details = []
	update_time = data_all1["lastUpdateTime"]
	data_country = data_all1["areaTree"]
	data_province = data_country[0]["children"]
	for pro_infos in data_province:
		province = pro_infos["name"]
		for city_infos in pro_infos["children"]:
			city = city_infos["name"]
			confirm_add = city_infos["today"]["confirm"]
			confirm = city_infos["total"]["confirm"]
			dead = city_infos["total"]["dead"]
			heal = city_infos["total"]["heal"]
			details.append([update_time, province, city, confirm, confirm_add, heal, dead])
	return history, details


def get_conn():
	# 建立连接
	conn = pymysql.connect(host = "127.0.0.1", user = "root", password = "123456", db = "cov",charset="utf8")
	# 创建游标
	cursor = conn.cursor()
	return conn, cursor


def close_conn(conn, cursor):
	if cursor:
		cursor.close()
	if conn:
		conn.close()


def update_history():
	conn, cursor = get_conn()
	try:
		dic = get_tencent_data()[0]	#0代表历史数据字典
		print(f"{time.asctime()}开始更新历史数据")
		conn, cursor = get_conn()
		sql = "insert into history value (%s,%s,%s,%s,%s,%s,%s,%s,%s)"
		# 根据爬虫得到的最新数据的时间(k)到history数据表中查询是否包含此条记录，如果包含则不必插入数据，如果不包含则插入
		sql_query = "select confirm from history where ds = %s"
		for k,v in dic.items():
			# 如果不包含数据则cursor.execute(sql_query, k)返回None
			if not cursor.execute(sql_query, k):
				cursor.execute(sql, [k, v.get("confirm"),v.get("confirm_add"),v.get("suspect"),
                               v.get("suspect_add"),v.get("heal"),v.get("heal_add"),
                               v.get("dead"),v.get("dead_add")])
		conn.commit()
		print(f"{time.asctime()}历史数据更新完毕")
	except:
		traceback.print_exc()
	finally:
		close_conn(conn, cursor)


def update_details():
	conn, cursor = get_conn()
	try:
		det = get_tencent_data()[1] #1代表details最新数据
		conn, cursor = get_conn()
		sql = "insert into details(update_time,province,city,confirm,confirm_add,heal,dead) values(%s,%s,%s,%s,%s,%s,%s)"
		sql_query = "select update_time from details order by id desc limit 1"
		# 如果是第一次更新details数据，数据库中该表为空表，所以执行sql_query的返回值为0
		val = cursor.execute(sql_query)
		# 如果数据库中details表中有数据，则获取details表中最新的时间数据并保存至form_time中
		if val != 0:
			form_time = cursor.fetchone()[0]
		# 与爬取数据的时间数据进行对比，如果不同则更新数据，反之。
		if val == 0 or str(form_time) != det[0][0]:
			print(f"{time.asctime()}开始更新数据")
			for item in det:
				cursor.execute(sql, item)
			conn.commit()
			print(f"{time.asctime()}更新到最新数据")
		else:
			print(f"{time.asctime()}已是最新数据！")
	except:
		traceback.print_exc()
	finally:
		close_conn(conn, cursor)


def get_baidu_hot():
	option = ChromeOptions()
	option.add_argument("--headless") # 隐藏浏览器
	option.add_argument("--no-sandbox")
	browser = Chrome(executable_path='/usr/local/bin/chromedriver',options=option)

	url = "https://voice.baidu.com/act/virussearch/virussearch?from=osari_map&tab=0&infomore=1"
	browser.get(url)
	# 找到加载更多在页面上的位置
	# but = browser.find_element_by_css_selector('#ptab-0 > div > div.VirusHot_1-5-3_32AY4F.VirusHot_1-5-3_2RnRvg > section > div')
	but = browser.find_element_by_xpath('//*[@id="ptab-0"]/div/div[1]/section/div')
	# 模拟人点击加载更多
	but.click()
	time.sleep(1)
	c = browser.find_elements_by_xpath('//*[@id="ptab-0"]/div/div[1]/section/a/div/span[2]')
	context = [i.text for i in c]
	browser.close()
	return context


def update_hotsearch():
	cursor = None
	conn = None
	try:
		context = get_baidu_hot()
		print(f"{time.asctime()}开始更新数据")
		conn,cursor = get_conn()
		sql = "insert into hotsearch(dt,content) values(%s,%s)"
		ts = time.strftime("%Y-%m-%d %X")
		for i in context:
			cursor.execute(sql,(ts,i))
		conn.commit()
		print(f"{time.asctime()}数据更新完毕")
	except:
		traceback.print_exc()
	finally:
		close_conn(conn,cursor)


# 异步协程，发送请求，获取各国数据
async def get_url_country(country_name, url):
    header = {
		"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36"
    }
    async with aiohttp.ClientSession() as session:
        async with await session.get(url, headers=header) as response:
            # 请求各国数据, 获取响应，获取 {'ret': , 'info': '', 'data': ....}里的'data'值
            res = json.loads(await response.text())
            res = res['data']
            if res:  # 不为空
                country_dict[country_name] = res  # 返回添加各国数据，存储到字典


# 处理外国各国数据
def get_country_data(*country_list):
    # 未特指国家，默认指世界各国
    start_time = time.time()
    if not country_list:
        country_list = list(namemap.values())[1:]  # 各国列表
    else:
        country_list = country_list[0]

    task_list = []
    new_loop = asyncio.new_event_loop()  # 指定event loop对象
    asyncio.set_event_loop(new_loop)  # 指定event loop对象
    for country in country_list:
        url = 'https://api.inews.qq.com/newsqa/v1/automation/foreign/daily/list?country=' + country
        request = get_url_country(country, url)  # 协程请求各国数据
        task = asyncio.ensure_future(request)
        task_list.append(task)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.wait(task_list))

    # 返回数据经过筛选的各国字典
    country_data = {}
    for country in country_dict:
        daily_data = []
        for value in country_dict.get(country):  # 各国数据处理
            # value 格式{'date': '02.01', 'confirm_add': 0, 'confirm': 2, 'heal': 0, 'dead': 0}
            ds = '2020' + value['date']
            tup = time.strptime(ds, '%Y%m.%d')
            update_time = time.strftime('%Y-%m-%d', tup)  # 改变时间格式，不然插入数据库会报错
            value['date'] = update_time
            daily_data.append(list(value.values()))
        daily_data.reverse()  # 倒序，将最新日期置为首部，提高数据库操作效率
        country_data[country] = daily_data
    print("各国数据请求完毕:", time.time() - start_time, '秒')
    return country_data


def update_fforeign(*country_list):
	"""
	插入国外数据，更新当日国外各数据
	mysql建立表fforeign的sql语句：

	create table fforeign(
	id int(11) not null auto_increment,
	update_time datetime default null comment '数据最后更新时间',
	country varchar(50) not null comment'国',
	confirm int(11) default null comment'累计确诊',
	confirm_add int(11) default null comment'新增确诊',
	heal int(11) default null comment'累计治愈',
	dead int(11) default null comment'累计死亡',
	primary key(id)
	)engine=InnoDB default charset=utf8mb4;

	:return:
	"""
	cursor = None
	conn = None
	try:
		conn, cursor = get_conn()
		# 数据不存在, 插入数据
		sql_query_insert = 'select confirm from fforeign where country = %s and update_time= %s'
		sql_query = "select update_time from fforeign order by update_time desc limit 1"
		sql_insert = 'insert into fforeign(country,update_time,confirm_add,confirm,heal,dead) ' \
			  'values(%s,%s,%s,%s,%s,%s)'
		# 请求各国数据，未特指国家，默认指世界各国
		country_data = get_country_data(*country_list)
		time_data = country_data["美国"][0][0]+" 00:00:00"
		val = cursor.execute(sql_query)
		if val != 0:
			form_time = cursor.fetchone()[0]

		# 与爬取数据的时间数据进行对比，如果不同则更新数据，反之。
		if val == 0 or str(form_time) != time_data:
			print(f'{time.asctime()} -- 正在更新国外数据，数据量较大请稍微等待一会')
			# 更新数据库
			for country, dailyData in country_data.items():  # 迭代国家列表
				# 该国有疫情数据
				for item in dailyData:  # 获取该国每日数据, item 格式['2020-01-28', 0, 5, 0, 0]
					cursor.execute(sql_query_insert, [country, item[0]])  # country代表国家, item[0]代表日期
					# 该日确诊数据为null, 插入数据
					if not cursor.fetchone():
						cursor.execute(sql_insert, [country, item[0], item[1], item[2], item[3], item[4]])  # 插入数据
						conn.commit()  # 提交事务
						continue
					break
		else:
			print(f'{time.asctime()} -- 已是国外最新数据')
	except:
		traceback.print_exc()
	finally:
		close_conn(conn, cursor)


if __name__ == '__main__':
	# l = len(sys.argv)
	# if l == 1:
	# 	s = """
	# 	请输入参数
	# 	参数说明
	# 	up_his 更新历史记录表
	# 	up_hot 更新实时热搜
	# 	up_det 更新详细表
	# 	up_fore 更新世界疫情地图
	# 	"""
	# 	print(s)
	# else:
	# 	order = sys.argv[1]
	# 	if order == "up_his":
	# 		update_history()
	# 	elif order == "up_det":
	# 		update_details()
	# 	elif order == "up_hot":
	# 		update_hotsearch()
	# 	elif order == "up_fore":
	# 		update_fforeign()
	update_history()