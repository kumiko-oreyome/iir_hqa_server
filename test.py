import util
from qa_mrc.common.util import jsonl_reader


def test_check_format():
    test_data = next(jsonl_reader('./data/test/test_mrc.jsonl'))
    assert True == util.check_input_format(test_data,'raw')
    assert False == util.check_input_format(test_data,'multi_mrc')



def test_mrc_server():
    test_data = next(jsonl_reader('./data/test/test_mrc.jsonl'))
test_check_format()