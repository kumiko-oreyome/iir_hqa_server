from lxml import etree,html
import re

from .util import Downloader,jsonl_writer,jsonl_reader
from urllib.parse import quote
import asyncio,time
from pyppeteer import launch
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from elasticsearch_dsl import Search
from elasticsearch_dsl import Q
import random

##  pyppeteer.errors.NetworkError: Protocol Error (Runtime.callFunctionOn): Session closed. Most likely the page has been closed.   
##  SOLVE:https://github.com/miyakogi/pyppeteer/issues/178







def test():
    html = open('./data/cmkb_test.html','r',encoding='utf-8').read()
    page = CMKBLibraryPage(html)
    assert page.get_title() == '什麼是糖尿病？'
    paragraphs = html_parsing_paragraph(page.get_body())
    doc = CMKBDLibraryDocument(url='https://kb.commonhealth.com.tw/library/30.html',title=page.get_title(),body=page.get_body(),tags=['糖尿病'],paragraphs=paragraphs)
    jsonl_writer('./data/test_kb_data.jsonl',[doc.to_json()])


def test_elastic():
    db = CMKBElasticDB(host='192.168.99.100',port=9200,index='test',doc_type='docs')
    db.delete_all_docs()
    db.insert_library_docs_from_file('./data/test_kb_data.jsonl')
    res = db.retrieve_library_doc("糖尿病 高血壓 感冒")
    print('reteieve %d results'%(len(res)))
    for r in res:
        print(r['title'],r['tags'])


def test_cmkb_keyword_search():
    #html = open('./data/cmkb_kwpage_test.html','r',encoding='utf-8').read()
    #page = CMKBKeywordSearchPage(html)
    #item_infos = page.get_library_page_infos()
    #print(item_infos)
    loop = asyncio.get_event_loop()
    print('create kw search page')
    page = CMKBKeywordSearchPage('糖尿病',loop)
    print('start script')
    async def  script():
        await page.expand_page_until(3)
        print(len(page.current_page_infos))
        print(page.current_page_infos)
    html_content = loop.run_until_complete(script())
    #with open('cmkb_kwpage_test.html','w',encoding='utf-8') as f:
    #    f.write(html_content)

def build_elastic_cmkb_lib_from_file(host,port,index,doc_type,filepath,delete_previous=False):
    db = CMKBElasticDB(host,port,index,doc_type)
    if delete_previous :
        db.delete_all_docs()
    db.insert_library_docs_from_file(filepath)

def clear_duplicate_doc(filepath):
    l = []
    title_set = set()
    for sample in jsonl_reader(filepath):
        if sample['title'] not in title_set: 
            l.append(sample)
            title_set.add(sample['title'])
    print('total n no dup samples %d'%(len(l)))
    jsonl_writer(filepath,l)
    



def remove_white_spaces(texts):
    import re
    texts = list(map(lambda  x: x.rstrip().lstrip(),texts))
    texts = list(map(lambda  x: re.sub("[\n\t\r]","",x),texts))
    texts = list(filter(lambda  x: len(x)>0,texts))
    return texts





def html_parsing_paragraph(html_text):
    parser = etree.HTMLParser(remove_blank_text=True)
    tree = etree.HTML(html_text,parser)
    
    type1_paragraphs = []
    type2_paragraphs = []
    for pnode in tree.xpath("//div[@class='text-content']/p"):
        if pnode.text is None:
            continue
        type1_paragraphs.append(pnode.text)
    
    for node in tree.xpath("//div[@class='post-tab']/div[@class='panel-group']//div[@class='panel panel-default']"):
        title = node.xpath(".//h4[@class='panel-title']")[0].text
        if title == '貼心提醒':
            continue
        body = "".join(node.xpath(".//div[@class='panel-body']//text()"))
        type2_paragraphs.append('%s\n%s'%(title,body))
    return remove_white_spaces(type1_paragraphs+type2_paragraphs)


class CMKBParagraphTransform():
    def __init__(self):
        pass
    def transrofm(self):
        pass

class CMKBLibraryPage():
    def __init__(self,html_content):
        self.html_content = html_content
        self.tree = html.fromstring(html_content)
    def get_body(self):
        body_ele = self.tree.xpath("//div[@class='nm-post-content']/article")[0]
        return html.tostring(body_ele,pretty_print=True).decode()

    def get_title(self):
        ele = self.tree.xpath("//div[@class='nm-post-content']/article//div[@class='text-content']/h2")[0]
        return ele.text

    

class CMKBKeywordSearchPage():
    def __init__(self,keyword,loop):
        self.keyword = keyword
        self.url = self.get_keyword_serch_url(keyword)
        self.loop = loop
        self.page = self.loop.run_until_complete(self.open_keyword_serch_page())
        self.current_page_infos = []

        
    @classmethod
    def  get_keyword_serch_url(cls,keyword):
        return 'https://kb.commonhealth.com.tw/library/search?keyword=%s'%(keyword)

    @classmethod
    def get_more_btn_xpath(cls):
        return "//div[@class='resultList-box']/div[@class='box-btn']/a[@class='btn']"

    @classmethod  
    def _get_result_item_xpath(cls):
        return "//div[@class='box-data']/div[@class='result-item']"

    @classmethod  
    def keyword_search_request(cls,keyword):
        html_content = Downloader().get(cls. get_keyword_serch_url(keyword))
        return cls.get_library_page_infos(html_content)
    @classmethod 
    def get_library_page_infos(cls,html_content):
        html_content = html_content
        tree = html.fromstring(html_content)
        l   = []
        for node in tree.xpath(cls._get_result_item_xpath()):
            link = node.xpath('./a/@href')[0]
            title = node.xpath('./a/h3/text()')[0]
            tags =  node.xpath('./a/p/text()')[0]
            l.append({'url':link,'title':title,'tags':[tags]})
        return l

    def update_page_infos(self,new_page_infos):
        current_n  = len(self.current_page_infos)
        newer_n = len(new_page_infos)
        assert newer_n >= current_n
        self.current_page_infos.extend(new_page_infos[current_n:])

    async def  expand_page_until(self,expand_num=1000):
        for _ in range(expand_num):
            res = await self._get_more_items_by_click_btn()
            if res is None:
                break
            print('expand page : current item num %d'%(len(self.current_page_infos)))
        print('expaned : total %d'%(len(self.current_page_infos)))


    async def open_keyword_serch_page(self):
        browser = await launch({'headless': False,'timeout':1000*360})
        page = await browser.newPage()
        await page.goto(self.url)
        await page.setJavaScriptEnabled(enabled=True)
        return page


    async def _parse_current_page(self):
        page_infos = await self.page.evaluate("() =>{\
             let l = [];\
             for(let node of document.getElementsByClassName('result-item')){ \
                   let url = node.getElementsByTagName('a')[0].href;\
                   let title =   node.querySelector('a h3').innerText;\
                   let tags =   node.querySelector('a p').innerText;\
                   l.push({url:url,title:title,tags:[tags]});\
                 }return l;}")
        return page_infos

    async def _get_more_items_by_click_btn(self):
        #if self.first_seen:
        #    self.first_seen = False
        #    await self.page.setRequestInterception(True)
        #    async def intercept(request):
        #        if not request.url.startswith('https://kb.commonhealth'):
        #            await request.abort()
        #        else:
        #            print(request.url)
        #            await request.continue_()
        #    self.page.on('request', lambda req: asyncio.ensure_future(intercept(req)))
        #    self.page.on('response', lambda resp: asyncio.ensure_future(self.xhr_handler(resp)))
        flag = await self.page.evaluate("() =>{if(document.querySelector('div.box-btn a.btn').style.display=='none'){return false;}document.querySelector('div.box-btn a.btn').click();return true;}")
        if not flag:
            return None
        await self.page.waitFor(1000)
        page_infos = await self._parse_current_page()
        self.update_page_infos(page_infos)
        return page_infos
        
    async def xhr_handler(self,resp):
        print( resp.request.url)
        # = await resp.text()
        #("tmp.html",'w',encoding='utf-8').write(text)
        if 'https://kb.commonhealth.com.tw/library' in resp.request.url:
            print('on xhr handle')
            print( await resp.json())
    

class CMKBRequest():
    def __init__(self,loop=None):
        self.loop = loop
    def  get_library_page(self,url):
        html_content = Downloader().get(url)
        return CMKBLibraryPage(html_content)
    def crawl_keyword_search_page(self,keyword,click_more_num=1000,filepath='./test_kw_crawl.jsonl'):
        assert self.loop is not None
        async def a ():
            await page.expand_page_until(click_more_num)
        print('create keyword search page')
        page = CMKBKeywordSearchPage(keyword,self.loop)
        self.loop.run_until_complete(a())
        doc_jsons = []
        for item in page.current_page_infos:
            url,tags,title = item["url"], item["tags"], item["title"]
            print('request : %s --> %s'%(title,url))
            lib_page = self.get_library_page(url)
            time.sleep(2)
            paragraphs = html_parsing_paragraph(lib_page.get_body())
            doc = CMKBDLibraryDocument(url=url,title=lib_page.get_title(),body=lib_page.get_body(),tags=tags,paragraphs=paragraphs)
            doc_jsons.append(doc.to_json())
        jsonl_writer(filepath,doc_jsons)


class CMKBDLibraryDocument():
    def __init__(self,url,title,body,tags,paragraphs):
        self.url = url 
        self.title = title
        self.body = body
        self.tags = tags
        self.paragraphs = paragraphs

    def to_json(self):
        return {'url':self.url,'title':self.title,'tags':self.tags,'paragraphs':self.paragraphs,'body':self.body}



class CMKBElasticDB():
    def __init__(self,host,port,index,doc_type):
        self.es = Elasticsearch([{'host':host,'port':port}])
        self.index= index
        self.doc_type= doc_type

    def create_index(self):
        pass

    def create_library_docs(self):
        pass

    def insert_library_docs_from_file(self,filepath):
        insert_dict = []
        for json_obj in jsonl_reader(filepath):
            d =  CMKBDLibraryDocument(**json_obj).to_json()
            d.update({ "_index": self.index,"_type": self.doc_type})
            insert_dict.append(d)

        status,_ = bulk(self.es,insert_dict,index=self.index)
        print(status)

    def insert_doc(self,doc):
        pass

    def delete_all_docs(self):
        s = Search(index=self.index).using(self.es)
        s.update_from_dict({"query":{"match_all":{}},"size":1000})
        response = s.execute()
        actions = []
        for h in response.hits:
            actions.append({ '_op_type': 'delete',"_index" : self.index, "_id" : h.meta.id,'_type': self.doc_type })
        status,_ = bulk(self.es,actions)
        print("delete")
        print(status)
    #TODO
    # size bug in update_from_dict... size not working
    def retrieve_library_doc(self,keywords,size=10,search_fields=["title^3","tags^3","paragraphs"]):
        if type(keywords) == str:
            keywords = [keywords]
        query = " ".join(keywords)
        s = Search(index=self.index).using(self.es)
        s.update_from_dict({"query": {"simple_query_string" : {"fields" : search_fields,"query" :query}}})
        res = s.execute()
        l = []
        for d in res.hits:
            l.append(CMKBDLibraryDocument(url=d.url,title=d.title,body=d.body,tags=d.tags,paragraphs=[ s for s in d.paragraphs]).to_json())
        return l
        
    def get_results(self,res):
        l = []
        for hit in res['hits']['hits']:
            l.append(hit['_source'])
        return l
    



if __name__ == '__main__':
    #page = CMKBRequest().get_library_page('https://kb.commonhealth.com.tw/library/30.html')
    #html_parsing_paragraph(page.get_body())
    #with open('cmkb_test.html','w',encoding='utf-8') as f:
    #    f.write(page.html_content)

    #page =  CMKBRequest().keyword_search_request('糖尿病')
    #with open('cmkb_kwpage_test.html','w',encoding='utf-8') as f:
    #    f.write(page.html_content)
    #loop = asyncio.get_event_loop()
    #page = loop.run_until_complete( CMKBRequest().open_keyword_serch_page('糖尿病'))
    #with open('cmkb_kwpage_test.html','w',encoding='utf-8') as f:
    #    f.write(page.html_content)
    #test()
    #test_elastic()
    #test_cmkb_keyword_search()

    #loop = asyncio.get_event_loop()
    #req = CMKBRequest(loop)
    #req.crawl_keyword_search_page('高血壓',100,'./hasaki2.jsonl')
    #clear_duplicate_doc('./data/kb_2_disease_dataset.jsonl')
    #build_elastic_cmkb_lib_from_file('192.168.99.100',9200,'dev','library','./data/kb_2_disease_dataset.jsonl',True)
    db = CMKBElasticDB(host='192.168.99.100',port=9200,index='dev',doc_type='library')
    res = db.retrieve_library_doc(["高血壓"])
    print('reteieve %d results'%(len(res)))
    for r in res:
        print(r['title'],r['tags'])