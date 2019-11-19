from lxml import etree,html
import re
from .util import Downloader
import asyncio
from pyppeteer import launch

class HealthArticlePage():
    def __init__(self,html_text):
        self.html_text = html_text
        self.tree = html.fromstring(html_text)
    def get_title(self):
        ele = self.tree.xpath("//h1[@class='title']")[0]
        return ele.text
    def get_body(self):
        body_ele = self.tree.xpath("//div[@class='essay']")[0]
        return html.tostring(body_ele,pretty_print=True).decode()
    def to_json(self):
        return {'body':self.get_body(),'title':self.get_title()}

class HealthArticleRequest():
    def __init__(self,url,event_loop=None):
        self.url = url
        self.article_id = self.parse_nid() 
        self.event_loop = event_loop

    def parse_nid(self):
        m = re.search(r'article\.action\?nid=(\d+)',self.url)
        if m is None:
            return None
        return m.group(1)

    def send(self):
        assert self.article_id is not None
        html = Downloader().get(self.url)
        page = HealthArticlePage(html)
        return page

    async def _async_send(self):
        assert self.article_id is not None
        html = await Downloader().async_get(self.url)
        page = HealthArticlePage(html)
        return page

    async def _async_send_render(self):
        assert self.article_id is not None
        browser = await launch()
        page = await browser.newPage()
        await page.goto(self.url)
        html = await page.content()
        return HealthArticlePage(html)

    def async_send_render(self):
        loop = asyncio.get_event_loop()
        page = loop.run_until_complete(self._async_send_render())
        return page

    def async_send(self):
        if self.event_loop is None:
            self.event_loop = asyncio.get_event_loop()
        page = self.event_loop.run_until_complete(self._async_send())
        return page
        





if __name__ == '__main__':
    #with open('test.html','r',encoding='utf-8') as f:
    #    print('(%s)'%(HealthArticlePage(f.read()).get_title()))
    r = HealthArticleRequest('https://www.commonhealth.com.tw/article/article.action?nid=80297')
    print(r.article_id)
    loop = asyncio.get_event_loop()
    page = loop.run_until_complete(r.async_send())
    print(page.get_title())
    loop.close()
