import json

from lxml import etree,html

def jsonl_reader(path):
    with open(path,'r',encoding='utf-8') as f:
        for line in f :
            json_obj = json.loads(line.strip(),encoding='utf-8')
            yield json_obj

def remove_whilte_space(data):
    if type(data) == str:
        data = [data]
    l = []
    for s in data:
        s = "".join(s.split())
        l.append(s)
    return l

#def illegal_text(text):
#    if text.startsw

##方法一: n個字就變成一段
def get_article_paragraphs(html_content):
    max_char_num = 400
    parser = etree.HTMLParser(remove_blank_text=True)
    tree = etree.HTML(html_content,parser)
    for bad in tree.xpath("//div/script"):
        bad.getparent().remove(bad)
    text_content = tree.xpath("//div[@class='essay']//text()")
    text_content = list(map(lambda  x: x.rstrip().lstrip(),text_content))
    text_content = list(filter(lambda  x: len(x)>0,text_content))
    paragraphs = []
    current_paragraph  = ''
    current_len = 0
    for text in text_content:
        current_paragraph+=text
        current_len+=len(text)
        if current_len>max_char_num:
            paragraphs.append(current_paragraph)
            current_len = 0
            current_paragraph  = ''
    if len(current_paragraph)>0:
        paragraphs.append(current_paragraph)
    return paragraphs


##方法一: n個字就變成一段
def get_article_paragraphs_by_p_tags(html_content):
    max_char_num = 450
    parser = etree.HTMLParser(remove_blank_text=True)
    tree = etree.HTML(html_content,parser)
    for bad in tree.xpath("//div/script"):
        bad.getparent().remove(bad)
    pnodes = tree.xpath("//div[@class='essay']//p")
    paragraphs = []
    current_paragraph  = ''
    for p in pnodes:
        text = ''.join(p.itertext())
        text = text.rstrip().lstrip()
        if len(current_paragraph)+len(text)>max_char_num:
            paragraphs.append(current_paragraph)
            current_paragraph=''
        current_paragraph+=text
    if len(current_paragraph)>0:
        paragraphs.append(current_paragraph)
    return paragraphs


def preprocessing_paragraphs_yahoo():
    pass

        


if __name__ == '__main__':
    #SRC_PATH = './python_crawler/annotation_server/data/common_health/chiu_question.jsonl'
    #OUT_PATH = './python_crawler/annotation_server/data/common_health/chiu_question.paragraphs.jsonl'
    SRC_PATH = './python_crawler/annotation_server/data/common_health/chiu_common_health.jsonl'
    OUT_PATH = './python_crawler/annotation_server/data/common_health/chiu_common_health.paragraphs.ptag.jsonl'
    json_list = []
    for sample_json in jsonl_reader(SRC_PATH):
        print('question %s'%(sample_json['question']))
        for doc in sample_json["documents"]:
            paragraphs = get_article_paragraphs_by_p_tags( doc['body'])
            if len(paragraphs) == 0:
                print(doc['title'])
                print('%s paragraph length = 0'%(doc['title']))
                doc['paragraphs'] = '' 
                continue
            doc['paragraphs'] = paragraphs
        json_list.append(sample_json)

    with open(OUT_PATH,'w',encoding='utf-8') as f:
        for x in json_list:
            o = json.dumps(x,ensure_ascii=False)
            f.write(o+'\n')





