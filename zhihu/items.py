# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ZhihuItemTopics(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    topic_title = scrapy.Field() #话题题目
    topic_link = scrapy.Field() #话题链接
    topic_description = scrapy.Field() #话题描述
    followers_num = scrapy.Field() #关注人数
    active_answerers = scrapy.Field() # 优秀回答者

class ZhihuItemQuestions(scrapy.Item):
	question_topic = scrapy.Field() #所属话题
	question_title = scrapy.Field() #问题题目
	question_link = scrapy.Field() #问题链接
	question_index = scrapy.Field() #问题排序！
	followers_num = scrapy.Field() # 关注人数
	browse_num = scrapy.Field() # 浏览量
	answers_num = scrapy.Field() # 回答数

class ZhihuItemAnswers(scrapy.Item):
	answer_topic = scrapy.Field() # 所属话题
	answer_question = scrapy.Field() #所属问题
	answerer_name = scrapy.Field() # 匿名？
	answerer_link = scrapy.Field() # 答主链接
	answer_content = scrapy.Field() # 回答内容
	votes_num = scrapy.Field() # 点赞数
	comments_num = scrapy.Field() # 评论数




