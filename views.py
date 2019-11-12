from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for,Markup,jsonify
)


DB_POOL = {}





def get_full_db_path(app,filename):
    return "%s/%s"%(app.config['db_dir'],filename)


def create_bp(app,loop):
    from datautil.db import JsonlRCDatabase


    bp = Blueprint('main', __name__, url_prefix='')
    print(bp.root_path)
    print('db dir is %s'%(app.config['db_dir']))
    @bp.route('/', methods=['GET'])
    def list_db():
        filenames = [os.path.basename(filename) for filename in glob.glob("%s/*.jsonl"%(app.config['db_dir']))]
        return render_template('views/list_db.html',filename_list=filenames)


    @bp.route('/index/<db_filename>', methods=['GET'])
    def index(db_filename):
        if 'db_filename' not in session or  db_filename != session['db_filename']:
            session['db_filename'] = db_filename
            session['db_filename'] = db_filename
            session['db_path'] = get_full_db_path(app,db_filename)
        if  session['db_path'] not in DB_POOL :
            try:
                print(session['db_path'])
                DB_POOL[session['db_path']] = JsonlRCDatabase(session['db_path'],'qid')
            except :
                return 'db path not found'
        db = DB_POOL[session['db_path']]
        sample_dict = db.samples
        question_info = []
        for k,v in sample_dict.items():
            annotated = True  if len(v['answer_docs'])>0 else False
            question_info.append({'question':v['question'],'qid':v['qid'],'annotated':annotated})

        return render_template('views/index.html',question_info=question_info)

    @bp.route('/question/<int:qid>')
    def question_page(qid):
        db = DB_POOL[session['db_path']]
        sample = db.get_sample_by_id(qid)
        question = sample['question']
        docs = sample['documents']
        documents_info = []
        for doc in docs:
            documents_info.append({'doc_id':doc['doc_id'],'title':doc['title'],'qid':qid})
        return render_template('views/question_page.html',question=question ,documents_info=documents_info,answer_docs=sample['answer_docs'])

    @bp.route('/doc/<int:qid>/<int:doc_id>')
    def doc_page(qid,doc_id):
        db = DB_POOL[session['db_path']]
        sample = db.get_sample_by_id(qid)
        sample = JsonMrcSample(sample)
        if sample.get_document_by_id(doc_id) is None:
            return 'cannot find document'
        doc  = sample.get_document_by_id(doc_id).json_obj
        body = Markup(doc['body'])
        #'qid is %d document is %d title is %s'%(qid,doc_id,doc['title'])
        answers = sample.get_answers(doc_id)
            
        return render_template('views/doc_page.html',body=body,question=sample.sample_obj['question'],qid=qid,doc_id=doc_id,answers=answers)

    @bp.route('/answer/<int:qid>/<int:doc_id>/add',methods=['POST'])
    def annotate_answer(qid,doc_id):
        db = DB_POOL[session['db_path']]
        answer = request.form['answer']
        sample = db.get_sample_by_id(qid)
        sample = JsonMrcSample(sample)
        if sample.get_document_by_id(doc_id) is None:
            return 'cannot find document'
        sample.add_answer(doc_id,answer)
        db.save()
        return redirect(url_for('main.doc_page',qid=qid,doc_id=doc_id)) 




    @bp.route('/answer/<int:qid>/<int:doc_id>/list',methods=['GET'])
    def list_answers(qid,doc_id):
        db = DB_POOL[session['db_path']]
        sample = db.get_sample_by_id(qid)
        sample = JsonMrcSample(sample)
        if sample.get_document_by_id(doc_id) is None:
            return 'cannot find document'
        answers = sample.get_answers(doc_id)
        print(answers)
        return render_template('views/answer_page.html',qid=qid,doc_id=doc_id,answers=answers) 

    @bp.route('/answer/del',methods=['POST'])
    def delete_answer():
        db = DB_POOL[session['db_path']]
        rj = request.json
        sample = db.get_sample_by_id(rj["qid"])
        if sample is None:
            return jsonify({'result':'cannot find document'})
        sample = JsonMrcSample(sample)
        print(rj["answer"])
        db.save()
        return jsonify({'result':'success'})
    
    @bp.route('/question/query_google',methods=['POST'])
    def query_google():
        db = DB_POOL[session['db_path']]
        query = request.json["query_text"]
        print('query %s'%(query))
        try:
            default_data_collect_query(query,db,loop=loop)
        except Exception as e:
            print(e)
            return jsonify({'result':'false','message':'error while query to  google [%s]'%(str(e))})
        return jsonify({'result':'success'})

    @bp.route('/question/delete',methods=['POST'])
    def delete_question():
        qid = request.json["qid"]
        db = DB_POOL[session['db_path']]
        try:
           db.del_sample_by_id(qid)
        except Exception as e:
            print(e)
            return jsonify({'result':'false','message':'error while delete [%s]'%(str(e))})
        db.save()
        return jsonify({'result':'success'})

    return bp   


    




    
