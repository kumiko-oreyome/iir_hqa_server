pipeline_mrc_model = {'model_type':'pipeline','device':'cpu','ranker_config_path':'./data/model/pointwise/answer_doc/config.json',\
    'reader_config_path':'./data/model/reader/bert_default/config.json'}
mock_mrc_model = {'model_type':'mock'}


MODEL_CONFIG =  pipeline_mrc_model 
PORT = 5001