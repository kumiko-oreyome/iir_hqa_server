import httpx
import json
import jieba 
from  jieba import analyse

def jsonl_reader(path):
    with open(path,'r',encoding='utf-8') as f:
        for line in f :
            json_obj = json.loads(line.strip(),encoding='utf-8')
            yield json_obj

def jsonl_writer(path,items):
    with open(path,'w',encoding='utf-8') as f:
        for x in items:
            f.write(json.dumps(x,ensure_ascii=False)+'\n')






class Downloader():
    def __init__(self,timeout=5000,max_try=5):
        self.timeout = timeout
        self.max_try = max_try
    def get(self,url):
        try:
            r = httpx.get(url,timeout=self.timeout)
        except httpx.exceptions.ReadTimeout:
            print('timeout url is %s'%(url))
        return r.text
    def post(self,url):
        pass

    async def  async_get(self,url):
        async with httpx.AsyncClient() as client:
            try:
                r = await client.get(url,timeout=self.timeout)
            except httpx.exceptions.ReadTimeout:
                print('timeout url is %s'%(url))
  
            
        return r.text



class Query():
    def __init__(self,query,word_dict=[]):
        self.query = query
        self.word_dict = word_dict


    def extract_keywords(self,k=3):
        return analyse.extract_tags(self.query,topK=3)

    def extract_keywords_with_diciotnary(self):
        keywords = []
        for w in  self.word_dict:
            if w in self.query:
                keywords.append(w)
        return keywords

