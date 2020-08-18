import pymysql
import time
from lxml import etree
import re
import sys
from spider.Get_api import download_page

conn = pymysql.connect(host='120.79.176.203', user='root', passwd='12345678', db='mydb', port=3306, charset='utf8mb4')
cursor = conn.cursor()


count = 105090

def get_url():
    sql = 'SELECT movie_link FROM `movie_link`'
    try:
        cursor.execute(sql)
        result = cursor.fetchall()
        for url in result[105089:]:
            get_info(url[0])
            time.sleep(2)
    except Exception as e:
        print(e)

def get_info(url):
    global count
    # html = selfproxy.download_page(url)
    # print(url)
    html = download_page(url)
    # print(html)
    # url = "'"+url+"'"
    if ('页面不存在'in html.text) or ('条目不存在'in html.text):
        # print('网页不存在')
        sql = 'INSERT INTO movie_new SET name="%s", movie_link="%s"' % ('网页不存在', url)
        # print(sql)
        cursor.execute(sql)
    else:
        selector = etree.HTML(html.text)
        #电影名
        name = selector.xpath('//*[@id="content"]/h1/span[1]/text()')[0]
        name = name.replace('\'', '‘')
        name = name.replace('"','”')
        # print(name)
        #导演
        if 'directedBy' in html.text:
            directors = selector.xpath('//*[@id="info"]/span[1]/span[2]/a/text()')
            director = ''
            for director_1 in directors:
                director = director + director_1 + ' '
        else:
            director = ''
        director = director.replace('\'', '‘')
        director = director.replace('"', '“')
        # print(director)
        #编剧
        if 'class=\'pl\'>编剧' in html.text and director != '':
            screenwrites = selector.xpath('//*[@id="info"]/span[2]/span[2]')[0]
            screenwrite = screenwrites.xpath('string(.)')
        elif 'class=\'pl\'>编剧' in html.text and director == '':
            screenwrites = selector.xpath('//*[@id="info"]/span[1]/span[2]')[0]
            screenwrite = screenwrites.xpath('string(.)')
        else:
            screenwrite = ''
        screenwrite = screenwrite.replace('\'', '‘')
        screenwrite = screenwrite.replace('"', '“')
        # print(screenwrite)
        #主演
        if 'class=\'pl\'>主演' in html.text and screenwrite != '' and director != '':
            actors = selector.xpath('//*[@id="info"]/span[3]/span[2]')[0]
            actor = actors.xpath('string(.)')
        elif ('class=\'pl\'>主演' in html.text and screenwrite == '' and director != '') or (
                'class=\'pl\'>主演' in html.text and screenwrite != '' and director == ''):
            actors = selector.xpath('//*[@id="info"]/span[2]/span[2]')[0]
            actor = actors.xpath('string(.)')
        elif 'class=\'pl\'>主演' in html.text and screenwrite == '' and director == '':
            actors = selector.xpath('//*[@id="info"]/span[1]/span[2]')[0]
            actor = actors.xpath('string(.)')
        else:
            actor = ''
        actor = actor.replace('\'', '‘')
        actor = actor.replace('"', '“')
        # print(actor)
        #类型
        types = re.findall('<span property="v:genre">(.*?)</span>', html.text, re.S)
        type_new = ''
        for type in types:
            type_new = type_new + type + '/'
        # print(type_new)
        #制片国家
        if '制片国家' in html.text:
            country = re.findall('制片国家/地区:</span>(.*?)<br/>', html.text, re.S)[0]
        else:
            country = ''
        # print(country)
        #语言
        if 'class="pl">语言:' in html.text:
            language = re.findall('语言:</span>(.*?)<br/>', html.text, re.S)[0]
        else:
            language = ''
        language = language.replace('\'', '‘')
        language = language.replace('"','”')
        # print(language)
        #上映日期
        if ('上映日期:' or '首播:') in html.text:
            release_time = re.findall('<span property="v:initialReleaseDate.*?>(.*?)</span>', html.text, re.S)
            thetime = ''
            for release in release_time:
                thetime = thetime + release + '/'
        else:
            thetime = ''
        thetime = thetime.replace('\'', '‘')
        thetime = thetime.replace('"','“')
        # print(thetime)
        #片长
        if '>片长:' in html.text:
            if 'runtime' in html.text:
                time = re.findall('片长:</span>.*?>(.*?)</span>', html.text, re.S)[0]
            else:
                time = re.findall('片长:</span>(.*?)<br/>', html.text, re.S)[0]
        else:
            time = ''
        time = time.replace('\'', '‘')
        time = time.replace('"', '“')
        # print(time)
        #IMDB
        if 'IMDb链接:' in html.text:
            IMDb = re.findall('MDb链接:</spa.*?href="(.*?)" target', html.text, re.S)[0]
        else:
            IMDb = ''
        # print(IMDb)
        #评分
        if '暂无评分' in html.text:
            score = ''
        elif '豆瓣评分' in html.text:
            score = re.findall('<strong class="ll rating_num" property="v:average">(.*?)</strong>', html.text, re.S)[0]
        else:
            score = ''
        # print(score)
        #简介
        if'all hidden'in html.text:
            info = selector.xpath('//span[@class="all hidden"]')[0]
            str = info.xpath('string(.)')
        elif 'v:summary' in html.text:
            info = selector.xpath('//span[@property="v:summary"]')[0]
            str = info.xpath('string(.)')
            # str = ''
            # for info in info_2:
            #     info1 = info.strip(r'\n                                \u3000\u3000')
            #     info2 = info1.strip()
            #     str = str + info2
        else:
            str = ''
        str = str.strip()
        str = str.replace('\n','')
        str = str.replace('                                    ','')
        str = str.replace('                                　　','')
        str = str.replace('\'', '‘')
        str = str.replace('\\', '')
        str = str.replace('"', '“')
        # print(str)
        # print(count)
        # print(name, director, screenwrite, actor, type_new, country, language, thetime, time, IMDb, score, str,url)
        #tag
        if 'tags-body' in html.text:
            tags = selector.xpath('//*[@class="tags-body"]')[0]
            tag = tags.xpath('string(.)')
            tag = tag.replace('"', '').replace('                ', '/')
        else:
            tag = ''
        # print(tag)
        # print(name, director, screenwrite, actor, type_new, country, language, thetime, time, IMDb, score, str, url, tag)
        cursor.execute(
            'INSERT INTO movie_new SET name = "%s",director = "%s",screenwriter = "%s",actor = "%s",style = "%s",production = "%s",language = "%s",thetime = "%s",time = "%s",IMDb = "%s",score = "%s",intro = "%s", movie_link = "%s", tag = "%s"' % (name, director, screenwrite, actor, type_new, country, language, thetime, time, IMDb, score, str, url, tag))
    print('写入成功',count,'条')
    sys.stdout.flush()
    count += 1
    conn.commit()


if __name__ == '__main__':
    # url = 'https://movie.douban.com/subject/5168203/'
    # get_info(url)
    get_url()
    conn.close()


