import httpx
import json

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