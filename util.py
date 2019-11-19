class RequestQA():
    def __init__(self,json_req):
        self.json_req = json_req
        self.parse()
    def parse(self):
        self.question =self.json_req['question']
        self.answer_num = int(self.json_req['answer_num'])
        self.algo_version = int(self.json_req['algo_version'])

class RequestMultiMRC():
    def __init__(self,json_req):
        self.json_req = json_req
        self.parse()
    def parse(self):
        self.mrc_input =self.json_req['mrc_input']
        self.answer_num = int(self.json_req['answer_num'])
        self.algo_version = int(self.json_req['algo_version'])


def check_input_format(mrc_input,type_name):
    assert type_name=='raw' or type_name=='multi_mrc'
    try:
        assert 'question' in mrc_input
        assert 'documents'in mrc_input
        assert len(mrc_input['documents'])>0
        for doc in mrc_input['documents']:
            assert ('body' in doc) and ('title' in doc) and ('url' in doc)
            if type_name == 'multi_mrc':
                assert 'paragraphs' in doc
    except AssertionError as e:
        print(str(e))
        return False

    return True

