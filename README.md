# scrapy-zhihu
基于scrapy框架爬取知乎热门话题
==========================
主要内容
------
利用scrapy框架爬取知乎上本人所关注的全部话题，得到每个话题下100个

精华问题，并获取各问题的最高票回答。总数据量5w+，存储于Mysql数据库。


技术方案
------
1.通过加载cookie模拟登录，并在后续请求中保持登录状态

2.将所获取的数据分类，建立三个item，存储于不同的表中

3.改写pipeline文件，利用sql语句实现数据的去重及存储

4.每次发送请求前进行判断，避免重复爬取，以提高效率




