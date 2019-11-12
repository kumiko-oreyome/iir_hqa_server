class RequestQA():
    def __init__(self,json_req):
        self.json_req = json_req
        self.parse()
    def parse(self):
        self.question =self.json_req['question']
        self.answer_num = int(self.json_req['answer_num'])
        self.algo_version = int(self.json_req['algo_version'])