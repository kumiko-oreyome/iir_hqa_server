from lxml import etree,html
import re

from .util import Downloader,jsonl_writer,jsonl_reader
from urllib.parse import quote
import asyncio
from pyppeteer import launch
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from elasticsearch_dsl import Search
from elasticsearch_dsl import Q


        




def remove_white_spaces(texts):
    import re
    texts = list(map(lambda  x: x.rstrip().lstrip(),texts))
    texts = list(map(lambda  x: re.sub("[\n\t]","",x),texts))
    texts = list(filter(lambda  x: len(x)>0,texts))
    print(texts)
    return texts



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
    

class CMKBRequest():
    def __init__(self,loop=None):
        self.loop = loop
    def  get_library_page(self,url):
        html_content = Downloader().get(url)
        return html_content


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

        status,_ = bulk(self.es,insert_dict)
        print(status)

    def insert_doc(self,doc):
        pass

    def delete_all_docs(self):
        s = Search.from_dict({"query":{"match_all":{}} }).using(self.es)
        response = s.execute()
        actions = []
        for h in response.hits:
            actions.append({ '_op_type': 'delete',"_index" : self.index, "_id" : h.meta.id,'_type': self.doc_type })
        status,_ = bulk(self.es,actions)
        print(status)
        


    def retrieve_library_doc(self,keywords):
        query = " ".join(keywords)
        res = Search.from_dict({"query": {"simple_query_string" : {"fields" : ["title","paragraphs","tags"],"query" : query}}}).using(self.es).execute()
        l = []
        for d in res.hits:
            l.append(CMKBDLibraryDocument(url=d.url,title=d.title,body=d.body,tags=d.tags,paragraphs=d.paragraphs).to_json())
        return l
        
    def get_results(self,res):
        l = []
        for hit in res['hits']['hits']:
            l.append(hit['_source'])
        return l
    



if __name__ == '__main__':
    #html = CMKBRequest().get_library_page('https://kb.commonhealth.com.tw/library/30.html')
    #page = CMKBLibraryPage(html)
    #html_parsing_paragraph(page.get_body())
    #with open('cmkb_test.html','w',encoding='utf-8') as f:
    #    f.write(html)
    #test()
    test_elastic()