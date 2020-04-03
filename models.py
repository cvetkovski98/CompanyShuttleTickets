import mongoengine as db
import mongoengine_goodjson as gj


class Address(gj.EmbeddedDocument):
    city = db.StringField(required=True, max_length=35)
    state = db.StringField(required=True, max_length=255)
    zip_code = db.IntField(required=True)


class User(gj.Document):
    id = db.StringField(required=True, primary_key=True)
    name = db.StringField(required=True, max_length=50)
    surname = db.StringField(required=True, max_length=50)
    role = db.StringField(required=True, max_length=20)
    address = db.EmbeddedDocumentField(required=True, document_type=Address)


class Comment(gj.EmbeddedDocument):
    timestamp = db.DateTimeField(required=True)
    written_by = db.ReferenceField(User)
    content = db.StringField(required=True, max_length=350)


class Ticket(gj.Document):
    id = db.StringField(required=True, primary_key=True)
    title = db.StringField(required=True, max_length=100)
    content = db.StringField(required=True, max_length=350)
    timestamp = db.DateTimeField(required=True)
    status = db.StringField(required=True, max_length=100)
    created_by = db.ReferenceField(User, reverse_delete_rule=db.NULLIFY)
    comments = db.EmbeddedDocumentListField(Comment)
