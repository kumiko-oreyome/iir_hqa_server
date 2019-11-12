
class JsonMrcSample():
    def __init__(self,sample_obj):
        self.sample_obj = sample_obj

    def get_documents(self):
        return [ JsonDocument(json) for json in self.sample_obj['documents']]

    def check_id_valid(self,doc_id):
        if  doc_id < 0 or doc_id>= len(self.get_documents()):
            return False
        return True

    def get_document_by_id(self,doc_id):
        if not self.check_id_valid(doc_id):
            return None
        return JsonDocument(self.sample_obj['documents'][doc_id])

    def get_answer_docs(self):
        return self.sample_obj['answer_docs']

    def add_answer(self,doc_id,answer):
        if not self.check_id_valid(doc_id):
            return
        self.sample_obj['doc2_answers'][doc_id].append(answer)
        self.sample_obj['answers'].append(answer)

        if doc_id not in self.sample_obj['answer_docs']:
            self.sample_obj['answer_docs'].append(doc_id)

    def delete_answer(self,doc_id,answer):
        if not self.check_id_valid(doc_id):
            return
        assert answer in self.sample_obj['doc2_answers'][doc_id]
        x = self.sample_obj['doc2_answers'][doc_id]
        x.remove(answer)
        self.sample_obj['answers'].remove(answer)

        if len(self.sample_obj['doc2_answers'][doc_id])==0:
            self.sample_obj['answer_docs'].remove(doc_id)



    def get_answers(self,doc_id=None):
        if not self.check_id_valid(doc_id):
            return []
        if doc_id is not None:
            return self.sample_obj['doc2_answers'][doc_id]
        return self.sample_obj['answers']

    def flatten(self,sample_fields,doc_fields):
        ret = []
        for doc_id,doc in  enumerate(self.get_documents()):
            passage_list  = doc.flatten(doc_fields)
            for obj in passage_list:
                obj.update({ 'doc_id':doc_id}) 
                obj.update({ k:self.sample_obj[k] for k in sample_fields}) 
            ret.extend(passage_list)
        return ret




class JsonDocument():
    #ALL_FIELDS = ['title','most_related_para']
    def __init__(self,json_obj):
        self.json_obj = json_obj
    #TODO add other fields like doc tokens...
    def get_paragraphs(self):
        return self.json_obj['paragraphs']

    def get_paragraph_by_id(self,pid):
        return self.get_paragraphs()[pid]

    def flatten(self,fields=[]):
        ret = []
        for para_id,passage in enumerate(self.get_paragraphs()):
            obj = {'passage':passage,'passage_id':para_id}
            obj.update({ k:self.json_obj[k] for k in fields})
            ret.append(obj)
        return ret