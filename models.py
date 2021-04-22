from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Document(db.Model):
    __tablename__="document"
    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, unique=True, nullable=False)
    text = db.Column(db.String(300), unique=True, nullable=False)

    def __init__(self,id,text):
        self.document_id=id
        self.text=text

