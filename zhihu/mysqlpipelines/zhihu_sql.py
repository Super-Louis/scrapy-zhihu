import pymysql

conn = pymysql.connect(user = 'root', password = '******', database = 'zhihu', charset = 'utf8mb4')
cur = conn.cursor()

class Sql():
	@classmethod
	def select(cls, table, **kwargs):
		keys = []
		values = []
		for i in kwargs:
			key = i
			keys.append(key)
			value = kwargs[i]
			values.append(value)
		#检测主题的重复性
		if len(keys) == 1: 
			sql = "SELECT EXISTS (SELECT 1 FROM " + table + " WHERE " + keys[0] + "= %s)"
			value = (values[0], )
		else:
			sql = "SELECT EXISTS (SELECT 1 FROM " + table + " WHERE " + keys[0] + "= %s AND " + keys[1] + "= %s)"
			value = (values[0], values[1])
		cur.execute(sql, value)
		return cur.fetchall()[0]

	@classmethod
	def insert(cls, table, values):
		sql = 'INSERT INTO ' + table + ' VALUES (%s' + ', %s'*(len(values)-1) + ')' # 可行否？
		value = values
		cur.execute(sql, value)
		conn.commit()

	@classmethod
	def parse_item(cls, table, topic, N = None):
		if table == 'zhihu_topic':
			sql = "SELECT COUNT(answer_topic) FROM zhihu_answer WHERE answer_topic= %s"
			value = (topic, )
		elif table == 'zhihu_question':
			sql = "SELECT COUNT(question_index) FROM zhihu_question WHERE (question_topic=%s) AND (question_index BETWEEN " + str(N+1) + " AND " + str(N+20) + ")"
			value = (topic, )
		elif table == 'zhihu_answer':
			sql = "SELECT COUNT(answer_question) FROM zhihu_answer WHERE answer_question=%s"
			value = (N, )
		cur.execute(sql, value)
		return cur.fetchall()[0]




