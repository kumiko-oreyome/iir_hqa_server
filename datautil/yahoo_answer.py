from lxml import etree,html
import re
from .util import Downloader
import asyncio
from pyppeteer import launch

class YahooAnswerQuestionPage():
    def __init__(self,html_text):
        self.html_text = html_text
        self.tree = html.fromstring(html_text)
    def get_title(self):
        ele = self.tree.xpath("//h1[contains(@class,'Question__title___')]")[0]
        return ele.text
    def get_body(self):
        body_ele = self.tree.xpath("//div[contains(@id,'qnaContainer-')]")
        if body_ele is None:
            return None
        body_ele = body_ele[0]
        return html.tostring(body_ele,pretty_print=True).decode()
    def to_json(self):
        return {'body':self.get_body(),'title':self.get_title()}

class YahooAnswerQuestionRequest():
    def __init__(self,url,event_loop=None):
        self.url = url
        self.event_loop = event_loop
       
    def send(self):
        html = Downloader().get(self.url)
        page = YahooAnswerQuestionPage(html)
        return page

    async def _async_send(self):
        html = await Downloader().async_get(self.url)
        page = YahooAnswerQuestionPage(html)
        return page

    #async def _async_send_render(self):
    #    browser = await launch()
    #    page = await browser.newPage()
    #    await page.goto(self.url)
    #    html = await page.content()
    #    return YahooAnswerQuestionPage(html)

    #def async_send_render(self):
    #    loop = asyncio.get_event_loop()
    #    page = loop.run_until_complete(self._async_send_render())
    #    return page

    def async_send(self):
        if self.event_loop is None:
            self.event_loop = asyncio.get_event_loop()
        page = self.event_loop.run_until_complete(self._async_send())
        return page
        





if __name__ == '__main__':
    r = YahooAnswerQuestionRequest('https://tw.answers.yahoo.com/question/index?qid=20191025153345AAXp5e3')
    page = r.async_send()
    print(page.get_title())
    print(page.get_body())
    #with open('test_yahoo.html','w',encoding='utf-8') as f:
    #    f.write(page.html_text)