import util
from qa_mrc.common.util import jsonl_reader


def test_check_format():
    test_data = next(jsonl_reader('./data/test/test_mrc.jsonl'))
    assert True == util.check_input_format(test_data,'raw')
    assert False == util.check_input_format(test_data,'multi_mrc')



def test_mrc_server():
    from mrc_server import create_app,multi_doc_model_factory
    from preprocessing import  SimpleParagraphTransform
    test_data = next(jsonl_reader('./data/test/test_mrc.jsonl'))
    test_config = {'model_type':'mock'}
    model = multi_doc_model_factory(test_config)
    assert True == util.check_input_format(test_data,'raw')
    SimpleParagraphTransform().transform(test_data)
    assert util.check_input_format(test_data,'multi_mrc')
    print(model.get_answer_list(test_data))

test_mrc_server()