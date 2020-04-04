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
    email = db.EmailField(required=True, unique=True)
    password = db.StringField(required=True)
    role = db.StringField(required=True, max_length=20)
    address = db.EmbeddedDocumentField(required=True, document_type=Address)


class Comment(gj.EmbeddedDocument):
    timestamp = db.DateTimeField(required=True)
    written_by = db.ReferenceField(User)
    content = db.StringField(required=True, max_length=350)
    statusChangedTo = db.StringField(required=False, max_length=80)
    assignee = gj.FollowReferenceField(User, required=False, default=None)


class Ticket(gj.Document):
    id = db.StringField(required=True, primary_key=True)
    title = db.StringField(required=True, max_length=100)
    content = db.StringField(required=True)
    timestamp = db.DateTimeField(required=True)
    status = db.StringField(required=True, max_length=100)
    created_by = db.ReferenceField(User, reverse_delete_rule=db.NULLIFY)
    comments = db.EmbeddedDocumentListField(Comment)
    assignee = db.ReferenceField(User, required=False)
