import time
import pymysql
import nameMap


def get_time():
    time_str = time.strftime("%Y{}%m{}%d{} %X")
    return time_str.format("年", "月", "日")


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


def query(sql, *args):
	conn, cursor = get_conn()
	cursor.execute(sql, args)
	res = cursor.fetchall()
	close_conn(conn, cursor)
	return res

def test():
	sql = "select * from details"
	res = query(sql)

def get_c1_data():
	# sql = "select sum(confirm)," \
    #       "(select suspect from history order by ds desc limit 1)," \
    #       "sum(heal),sum(dead) from details " \
    #       "where update_time=(select update_time from details order by update_time desc limit 1) "
	sql = "select confirm,suspect,heal,dead from history order by ds desc limit 1"
	res = query(sql)
	return res[0]


def get_c2_data():
	"""
	因为会更新多次数据，所以取时间戳选择最新的数据
	:return: 返回各省市的数据
	"""
	sql = "select province,sum(confirm) from details " \
          "where update_time=(select update_time from details " \
          "order by update_time desc limit 1) " \
          "group by province"
	res = query(sql)
	return res

def get_l1_data():
	sql = "select ds,confirm,suspect,heal,dead from history"
	res = query(sql)
	return res

def get_l2_data():
	sql = "select ds,confirm_add,suspect_add from history"
	res = query(sql)
	return res

def get_r1_data():
	# sql语句上半部分是查询除了"湖北","北京","上海","天津","重庆","香港"这6个地区外其他城市确诊人数排名
	# sql语句下半部分是查询除了"湖北"之外5个地区确诊人数排名
	sql = 'select city,confirm from ' \
		  '(select city,confirm from details ' \
		  'where update_time=(select update_time from details order by update_time desc limit 1) ' \
		  'and province not in ("湖北","北京","上海","天津","重庆","香港") ' \
		  'union all ' \
		  'select province as city,sum(confirm) as confirm from details ' \
		  'where update_time=(select update_time from details order by update_time desc limit 1) ' \
		  'and province in ("北京","上海","天津","重庆","香港") group by province) as a ' \
		  'order by confirm desc limit 5'
	res = query(sql)
	return res


def get_r2_data():
	sql = "select content from hotsearch order by id desc limit 20"
	res = query(sql)
	return res

def get_l1_data():
	sql = "select ds,confirm,suspect,heal,dead from history"
	res = query(sql)
	return res

def get_l2_data():
	sql = "select ds,confirm_add,suspect_add from history"
	res = query(sql)
	return res

# 获取world数据，世界疫情地图
def get_world():
	"""

	:return:返回世界各国数据
	"""
	conn, cursor = get_conn()
	country_list = list(nameMap.namemap.values())
	global_dict = {}
	for item in country_list:
		sql = 'select confirm from fforeign where country = %s order by update_time desc limit 1'
		if cursor.execute(sql, item):
			res = cursor.fetchall()
			global_dict[item] = res[0][0]
	close_conn(conn, cursor)
	return global_dict

if __name__ == '__main__':
	get_c1_data()