from common.util import load_json_config,Factory
from datautil.common_health import HealthArticleRequest
from datautil.yahoo_answer import YahooAnswerQuestionRequest
from preprocessing import   SimpleParagraphTransform
from datautil.google_search import GoogleSearchRequest
from datautil.common_health import  HealthArticleRequest
from datautil.util import Query

class WebRetriever():
    def __init__(self):
        pass





class FakeRetriever():
    def __init__(self):
      pass
    def retrieve_candidates(self,question):
       return {'question':'幫我發大決 冰鳥','documents':[{'body':"12345678",'title':'title1','url':'url1','paragraphs':['1234','5678']},\
              {'body':"abcdefghhjj",'title':'abde','url':'url2','paragraphs':['1234','5678']}]}


class CMKBElasticSearchRetriever():
    def __init__(self,es_db,k,word_dict):
        self.k = k
        self.es_db = es_db
        self.word_dict = word_dict
    def search_elk(self,question):
        query = Query(question,word_dict=self.word_dict)
        dic_keywords =query.extract_keywords_with_diciotnary()
        keywords  = list(set(dic_keywords+query.extract_keywords()))
        docs = self.es_db.retrieve_library_doc(keywords,size=self.k)
        # filter paragraphs without one of keywords
        for doc in docs:
            new_paragraphs = []
            for p in doc['paragraphs']:
                for dw in dic_keywords:
                    if dw in p:
                        new_paragraphs.append(p)
                        break
            doc['paragraphs'] = new_paragraphs
        return docs

    def retrieve_candidates(self,question):
        docs = self.search_elk(question)
        print('retrieve %d docs'%(len(docs)))
        sample_json = {"documents":[],'question':question}
        for i,x in enumerate(docs[0:self.k]):
            o = {'title':x['title'],'url':x['url'],'body':x['body'],'paragraphs':x['paragraphs']}
            sample_json['documents'].append(o)
        return sample_json
        





class GoogleSearchRetriever(WebRetriever):
    def __init__(self,site_url,k,event_loop,expand_keywords=False):
        super().__init__()
        self.site_url = site_url
        self.k = k
        self.req_cls = None
        self.event_loop = event_loop
        if 'commonhealth' in site_url:
            self.req_cls = HealthArticleRequest
        elif 'answers.yahoo' in site_url:
            self.req_cls = YahooAnswerQuestionRequest
        else:
            assert False
    def retrieve_candidates(self,question):
        gs_request = GoogleSearchRequest(question,self.site_url,loop=self.event_loop )
        page = gs_request.async_send()
        site_urls = page.get_result_links()
        sample_json = {"documents":[],'question':question}
        for doc_i,link in enumerate(site_urls[0:self.k]):
            print('request : %s'%(link))
            if ('commonhealth' not in link) and ('answers.yahoo' not in link):
                continue
            req = self.req_cls(link,event_loop=self.event_loop)
            article_page =  req.async_send()
            try:
                article =   article_page.to_json()
            except :
                print('error while parsing [%s]'%(link))
                continue
            article.update({'url':link})
            sample_json["documents"].append(article)
        SimpleParagraphTransform().transform(sample_json)
        return  sample_json


