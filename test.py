import util
from qa_mrc.common.util import jsonl_reader


def test_check_format():
    test_data = next(jsonl_reader('./data/test/test_mrc.jsonl'))
    assert True == util.check_input_format(test_data,'raw')
    assert False == util.check_input_format(test_data,'multi_mrc')



def test_mrc_model():
    from mrc_server import create_app,multi_doc_model_factory
    from preprocessing import  SimpleParagraphTransform
    test_data = next(jsonl_reader('./data/test/test_mrc.jsonl'))
    test_config = {'model_type':'mock'}
    model = multi_doc_model_factory(test_config)
    assert True == util.check_input_format(test_data,'raw')
    SimpleParagraphTransform().transform(test_data)
    assert util.check_input_format(test_data,'multi_mrc')
    print(model.get_answer_list(test_data))


def test_mock_mrc_server():
    from mrc_server import create_app
    from qa_mrc.ranker import RankerFactory
    from preprocessing import  SimpleParagraphTransform
    test_data = next(jsonl_reader('./data/test/test_mrc.jsonl'))
    test_config = {'model_type':'mock'}
    assert True == util.check_input_format(test_data,'raw')
    SimpleParagraphTransform().transform(test_data)
    assert util.check_input_format(test_data,'multi_mrc')
    app = create_app(test_config)
    with app.test_client() as c:
        rv = c.post('/qa', json={'mrc_input':test_data,'answer_num':3,'algo_version':0})
    json_data = rv.get_json()
    print(json_data)

def test_mrc_server():
    from mrc_server import create_app
    from preprocessing import  SimpleParagraphTransform
    test_data = next(jsonl_reader('./data/test/test_mrc.jsonl'))
    test_config = {'model_type':'pipeline','device':'cpu','ranker_config_path':'./data/model/pointwise/answer_doc/config.json','reader_config_path':'./data/model/reader/bert_default/config.json'}
    assert True == util.check_input_format(test_data,'raw')
    SimpleParagraphTransform().transform(test_data)
    assert util.check_input_format(test_data,'multi_mrc')
    app = create_app(test_config)
    print('send data')
    with app.test_client() as c:
        rv = c.post('/qa', json={'mrc_input':test_data,'answer_num':3,'algo_version':0})
    json_data = rv.get_json()
    print(json_data)

test_mrc_server()

