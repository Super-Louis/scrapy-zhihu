from zhihu.mysqlpipelines.zhihu_sql import Sql
from zhihu.items import ZhihuItemTopics, ZhihuItemQuestions, ZhihuItemAnswers

class ZhihuPipeline(object):
	def process_item(self, item, spider):
		if isinstance(item, ZhihuItemTopics):
			table = 'zhihu_topic'
			title = item['topic_title']
			count = Sql.select(table, topic_title=title)
			#不要掉了0！
			if count[0] == 1:
				print("该话题已存在")
			else:
				print("存储话题：",title)
				topic_link = item['topic_link']
				topic_description = item['topic_description']
				followers_num = item['followers_num']
				active_answerers = item['active_answerers']
				values = (title, topic_link, topic_description, followers_num, active_answerers)
				Sql.insert(table, values)
		if isinstance(item, ZhihuItemQuestions):
			table = 'zhihu_question'
			question_title = item['question_title']
			count = Sql.select(table, question_title=question_title)
			if count[0] == 1:
				print("该问题已存在")
			else:
				print("存储问题：", question_title)
				question_topic = item['question_topic']
				question_link = item['question_link']
				question_index = item['question_index']
				followers_num = item['followers_num']
				browse_num = item['browse_num']
				answers_num = item['answers_num']
				values = (question_topic, question_title, question_link, question_index, followers_num, browse_num, answers_num)
				Sql.insert(table, values)
		if isinstance(item, ZhihuItemAnswers):
			table = 'zhihu_answer'
			answer_topic = item['answer_topic']
			answer_question = item['answer_question']
			count = Sql.select(table, answer_topic=answer_topic, answer_question=answer_question)
			if count[0] == 1:
				print('该回答已存在')
			else:
				print("存储回答")
				answerer_name = item['answerer_name']
				answerer_link = item['answerer_link']
				answer_content = item['answer_content']
				votes_num = item['votes_num']
				comments_num = item['comments_num']
				values = (answer_topic, answer_question, answerer_name, answerer_link, answer_content, votes_num, comments_num) 
				Sql.insert(table, values)






