from lxml import etree,html
import re

from .util import Downloader
from urllib.parse import quote
import asyncio
from pyppeteer import launch

GOOGLE_SEARCH_URL = 'https://www.google.com/search' 

class GoogleSearchResultPage():
    def __init__(self,html_text):
        self.html_text = html_text
        self.tree = html.fromstring(self.html_text)
    def get_result_links(self):
        a_elememts = self.tree.xpath("//div[@id='search']//div[@class='rc']/div[@class='r']/a")
        links = []
        for a in a_elememts:
            links.append(a.get("href"))
        print('len of links %d'%(len(links)))
        return links
    def get_next_page_link(self):
        e = self.tree.xpath("//div[@id='foot']//a[@class='pn']")
        if len(e) == 0:
            return None
        return '%s%s'%('https://www.google.com',e[0].get("href"))
    




class GoogleSearchRequest():
    def __init__(self,keywords=[],site_url=None,loop=None):
        if type(keywords) == str:
            self.keywords = [keywords]
        self.keywords = keywords
        self.site_url =site_url
        self.url = self.get_url()
        self.loop = loop

    def join_keywords_to_query(self,keywords):
        return '+'.join(keywords)

    def get_url(self):
        query = self.join_keywords_to_query(self.keywords)
        if self.site_url is not None:
            site_part = quote('site:%s'%(self.site_url))
            query = self.join_keywords_to_query([site_part,query])
        return '%s?q=%s'%(GOOGLE_SEARCH_URL,query)

    def send(self):
        html = Downloader().get(self.url)
        #with open('aaa.html','w',encoding='utf-8') as f:
        #    f.write(html)
        return GoogleSearchResultPage(html)
    async def _async_send(self):
        browser = await launch(   handleSIGINT=False,handleSIGTERM=False,handleSIGHUP=False)
        page = await browser.newPage()
        await page.goto(self.url)
        html = await page.content()
        return GoogleSearchResultPage(html)

    def async_send(self):
        if self.loop is None:
            self.loop = asyncio.get_event_loop()
        return self.loop.run_until_complete(self._async_send())








if __name__ == '__main__':
    COMMON_HEALTH_SITE_URL = 'https://www.commonhealth.com.tw/article'
    #req1 = GoogleSearchRequest(keywords=['糖尿病','胃繞道','飲食'])
    req2 =  GoogleSearchRequest(keywords=['糖尿病','胃繞道','飲食'],site_url=COMMON_HEALTH_SITE_URL)
    #req1.send()
    #print(req1.url)
    #html_text = asyncio.get_event_loop().run_until_complete(req2.async_send())
    #html_text = req1.send()
    #with open('google_search_test_2.html' ,'w',encoding='utf8') as f:
    #f.write(html_text)
    page =  asyncio.get_event_loop().run_until_complete(req2.async_send())
    print(len(page.get_result_links()))
    print(page.get_result_links())
    print(page.get_next_page_link())
    req3 =  GoogleSearchRequest(keywords=['做完胃繞道後變得很瘦，有沒有什麼飲食能讓他攝取多一點營養？'],site_url=COMMON_HEALTH_SITE_URL)
    page =  asyncio.get_event_loop().run_until_complete(req3.async_send())
    print(len(page.get_result_links()))
    print(page.get_result_links())
    print(page.get_next_page_link())