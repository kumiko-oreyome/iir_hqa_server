pipeline_mrc_model = {'model_type':'pipeline','device':'cpu','ranker_config_path':'./data/model/pointwise/answer_doc/config.json',\
    'reader_config_path':'./data/model/reader/bert_default/config.json','kwargs':{}}

pipeline_mrc_model2 = {'model_type':'pipeline','device':'cpu','class':'SelectorReaderModel',\
       'reader_config_path':'./data/model/reader/bert_default/config.json','selector': {'class':'bert_ranker','kwargs':{'ranker':'./data/model/pointwise/answer_doc/config.json','k':2}},'kwargs':{} }

mock_mrc_model = {'model_type':'mock'}


MODEL_CONFIG =  pipeline_mrc_model2 
PORT = 5001