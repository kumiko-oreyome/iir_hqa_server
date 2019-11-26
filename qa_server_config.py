YAHOO_ANSWER_SITE_URL = 'https://tw.answers.yahoo.com'
COMMON_HEALTH_SITE_URL  = 'https://www.commonhealth.com.tw/article'
# document retrievers
fake_retirever_cfg = {'class':'FakeRetriever','kwargs':{}}
gs_retriever_cfg = {'class':'GoogleSearchRetriever','kwargs':{'site_url':COMMON_HEALTH_SITE_URL,'k':5}}


# mrc models (real)
pipeline_mrc_model = {'model_type':'pipeline','device':'cpu','ranker_config_path':'./data/model/pointwise/answer_doc/config.json',\
    'reader_config_path':'./data/model/reader/bert_default/config.json'}
mock_mrc_model = {'model_type':'mock'}


# mrc models (wrapper)
test_mrc_app_model = {'class':'TestMrcApp','kwargs':{'config':mock_mrc_model}}
redirect_mrc_model = {'class':'RedirectMrcModel','kwargs':{'server_url':'http://localhost:5001/qa'}}
#MODEL_CONFIG = {'document_retrieval':gs_retriever_cfg ,'multi_mrc':redirect_mrc_model,'elastic_search':{'host':'192.168.99.100','port':9200}}
EL_CONFIG = {"host":'192.168.99.100',"port":9200,"index":'dev',"doc_type":'library'}
KW_DICT_PATH = "./data/keyword_dict.txt"
MODEL_CONFIG = {'document_retrieval':gs_retriever_cfg ,'multi_mrc':redirect_mrc_model,'elastic_search':{'host':'192.168.99.100','port':9200},"el_config":EL_CONFIG,"kw_dict_path":KW_DICT_PATH }



    
