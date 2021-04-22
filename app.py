from flask import Flask, jsonify, request, Response
from flask_restful import Resource,Api,fields, marshal_with
from flask_sqlalchemy import SQLAlchemy
from models import db, Document
from difflib import SequenceMatcher

app=Flask(__name__)
api=Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/instaIndex.db'
app.config['SECRET_KEY'] = 'secret'

app.app_context().push()
db.init_app(app)

DocumentResourceFields={
    'id':  fields.Integer,
    'text': fields.String,
    'status': fields.String
}

def similarity(a,b):
    return SequenceMatcher(None, a, b).ratio()

def tokenize(queryString,delimiter=' '):
    return queryString.split(delimiter)

def normalize(word,operation='lower'):
    if operation=='lower':
        return word.lower()

class DocumentDAO(object):
    def __init__(self,id,text,status):
        self.id=id
        self.text=text
        self.status=status

class DocumentAPI(Resource):
    @marshal_with(DocumentResourceFields)
    def post(self):
        try:
            requestBody=request.get_json()
            documentID=requestBody['id']
            text=requestBody['text']
        
            new_document=Document(documentID,text)
            db.session.add(new_document)
            db.session.flush()
            db.session.commit()

            return DocumentDAO(id=documentID,text=text,status="Record Added")

        except:
            return Response("Improper Request Body", status=400)

class SearchAPI(Resource): 
    def get(self):
        try:
            searchQry=request.args.get('query')
            if searchQry:
                tokenizedQuery=tokenize(searchQry, ' ')
                normalizedQuery=[normalize(word) for word in tokenizedQuery]
                tokenizedAndNormalizedQuery=' '.join(word for word in normalizedQuery)
                query=Document.query.filter(Document.text.ilike('%'+ tokenizedAndNormalizedQuery +'%'))
                records=[u.__dict__ for u in query.all()]
            
                response_records=[]
                for record in records:
                    d={}
                    d['id']=record['document_id']
                    d['text']=record['text']
                    response_records.append(d)

                response={}
                response['count']=len(records)
                response['documents']=sorted(response_records, key=lambda i:similarity(i['text'],searchQry), reverse=True)

                return response

        except Exception as error:
            return Response(error, status=400)

api.add_resource(DocumentAPI,'/document',endpoint='Document')
api.add_resource(SearchAPI,'/search',endpoint='Search')

if __name__=='__main__':
    db.create_all()
    app.run('127.0.0.1', port=5000, debug=True)