# -*- coding: utf-8 -*- #
import scrapy
import http.cookiejar
import requests
import json
from zhihu.items import ZhihuItemTopics, ZhihuItemQuestions, ZhihuItemAnswers # 完整路径
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
import time
import re
import copy
from zhihu.mysqlpipelines.zhihu_sql import Sql

class ZhihuspiderSpider(scrapy.Spider):
	name = 'zhihuspider'
	allowed_domains = ['zhihu.com']
	start_urls = 'https://www.zhihu.com/followed_topics?offset=0&limit=100'#从0开始，增量为1，上限为100，即（0,100】
	filename = "your cookie's path"
	#可直接导入cookies，避过登录；亦可将登录时request header中的cookie复制过来
	cookies = http.cookiejar.LWPCookieJar()
	cookies.load(filename, ignore_discard=True, ignore_expires=True)
	cookies = requests.utils.dict_from_cookiejar(cookies) 

	def start_requests(self):
		#该方法必须返回一个可迭代对象
		yield scrapy.Request(self.start_urls, cookies=self.cookies, callback=self.get_topics) #self.

	def get_topics(self, response):
		item_topic = ZhihuItemTopics() 
		# print(response.text)
		base_url = 'https://www.zhihu.com/topic/'
		tail_url = '/top-answers'
		res_dict = json.loads(response.text)
		for topic in res_dict['payload']:
			topic_name = topic['name']
			topic_description = topic['introduction']
			middle_url = topic['url_token']
			topic_url = base_url + middle_url + tail_url
			item_topic['topic_title'] = topic_name
			item_topic['topic_link'] = topic_url
			try:
				item_topic['topic_description'] = re.sub(r'<.+?>', '', topic_description.replace(' ', ''))# pattern, repl, string
			except:
				item_topic['topic_description'] = topic_description
			# time.sleep(1)
			check = Sql.parse_item('zhihu_topic', topic_name)
			if check[0] == 100:
				print("话题已全部加载")
			else:
				yield scrapy.Request(topic_url, meta={'item':copy.deepcopy(item_topic)}, callback=self.parse_topics)
	
	def parse_topics(self, response):
		item_topic = response.meta['item']
		topic_title = item_topic['topic_title']
		followers = response.xpath('//*[@id="zh-topic-side-head"]/div/a/strong/text()').extract()[0]
		item_topic['followers_num'] = followers
		active_answerers = []
		try:
			names = response.xpath('//div[@class="zm-topic-side-person-item"]/div/a/text()').extract()
			urls =  response.xpath('//div[@class="zm-topic-side-person-item"]/div/a/@href').extract()
		# 优秀回答者
			for i in range(len(names)):
				active_answerer = {}
				active_answerer['name'] = names[i]
				active_answerer['url'] ='http://www.zhihu.com' + urls[i]
				active_answerers.append(active_answerer)
			item_topic['active_answerers'] = json.dumps(active_answerers) #是一个列表，应转化为字符串后再存储！！
		except:
			item_topic['active_answerers'] = ''
		#前100个问题
		for n in range(1, 6): 
			url = response.url + '?page=' + str(n)
			# time.sleep(1)
			question_rank = (n-1)*20
			check = Sql.parse_item('zhihu_question', topic_title, question_rank)
			#得到的是一个元组，所以要加0！
			if check[0] == 20:
				print("该页面问题已加载")
			else:
				yield scrapy.Request(url, meta={'topic_title':topic_title, 'question_rank':question_rank}, callback=self.get_questions)
		#导出item_topic
		yield item_topic

	def get_questions(self, response):
		topic = response.meta['topic_title']
		#如果没有结果，看下是不是xpath写错了，导致为空！！！
		urls = response.xpath('//div[@class="feed-main"]/div/h2/a/@href').extract() 
		titles = response.xpath('//div[@class="feed-main"]/div/h2/a/text()').extract() 
		question_rank = response.meta['question_rank']
		for i in range(len(urls)):
			question_rank += 1 
			question_url = 'https://www.zhihu.com' + urls[i]
			#去除首尾的空格！
			question_title = titles[i].strip() 
			check = Sql.parse_item('zhihu_answer', topic, question_title)
			if check[0] == 1:
				print("该问题已加载")
			else:
				yield scrapy.Request(question_url, meta={'index':question_rank, 'topic':topic, 'title':question_title}, callback=self.parse_questions)#不要掉了self!!!


	def parse_questions(self, response):
		item_question = ZhihuItemQuestions()
		question_topic = response.meta['topic']
		question_url = response.url
		question_rank = response.meta['index']
		question_title = response.meta['title']
		followers = response.xpath('//div[@class="QuestionFollowStatus"]/div/button/div[2]/text()').extract()[0]
		viewers = response.xpath('//div[@class="QuestionFollowStatus"]/div/div/div[2]/text()').extract()[0]
		item_question['question_topic'] = question_topic
		item_question['question_link'] = question_url
		item_question['question_index'] = question_rank
		item_question['followers_num'] = followers
		item_question['browse_num'] = viewers
		item_question['question_title'] = question_title
		num = response.xpath('//h4[@class="List-headerText"]/span/text()').extract()[0]
		answers_num = re.findall(r'(\d+).+', num)[0]
		item_question['answers_num'] = answers_num
		yield item_question
		item_answer = ZhihuItemAnswers()
		item_answer['answer_topic'] = response.meta['topic']
		item_answer['answer_question'] = response.meta['title']
		try:
			item_answer['answerer_name'] = response.xpath('//div[@class="AuthorInfo-content"]/div/span/div/div/a/text()').extract()[0]
			item_answer['answerer_link'] = 'http://www.zhihu.com' + response.xpath('//div[@class="AuthorInfo-content"]/div/span/div/div/a/@href').extract()[0]
		except:
			item_answer['answerer_name'] = '匿名用户'
			item_answer['answerer_link'] = ''
		answer_content = response.xpath('//div[@class="RichContent-inner"]/span//text()').extract()
		answer_content = [content.strip() for content in answer_content]
		item_answer['answer_content'] = '\n'.join(answer_content)
		try:
			item_answer['votes_num'] = response.xpath('//button[@class="Button VoteButton VoteButton--up"]//text()').extract()[0]
		except:
			item_answer['votes_num'] = None
		answer_comments = response.xpath('//button[@class="Button ContentItem-action Button--plain"]//text()').extract()[0]
		try:
			item_answer['comments_num'] = re.findall(r'(\d+).+', answer_comments)[0]
		except:
			item_answer['comments_num'] = None
		yield item_answer


