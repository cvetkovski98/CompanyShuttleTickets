import json

import mongoengine as db
from flask import Flask, Response, request, jsonify, copy_current_request_context
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token
from flask_bcrypt import Bcrypt
from flask_mail import Mail, Message
from models import Ticket, User, Comment
import threading

app = Flask(__name__)
db.connect(db='CompanyShuttleDb', host='localhost', port=27017)
jwt = JWTManager(app)
bcrypt = Bcrypt(app)
app.config['JWT_SECRET_KEY'] = 'secret'

cors = CORS(app)
# email setup
app.config["MAIL_SERVER"] = 'smtp.gmail.com'
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USE_SSL"] = False
app.config["MAIL_USERNAME"] = 'companyshuttleapp@gmail.com'
app.config["MAIL_PASSWORD"] = '<pw>'
app.config["MAIL_DEFAULT_SENDER"] = 'companyshuttleapp@gmail.com'
app.config["MAIL_MAX_EMAILS"] = None
app.config["MAIL_ASCII_ATTACHMENTS"] = False

mail = Mail(app)


@app.route('/api/tickets', methods=['GET'])
def get_all_tickets():
    data = [json.loads(ticket.to_json(follow_reference=True)) for ticket in Ticket.objects()]
    return jsonify(data)


@app.route('/api/tickets/<string:ticket_id>', methods=['GET'])
def get_ticket(ticket_id):
    data = Ticket.objects(id=ticket_id).get()
    return jsonify(json.loads(data.to_json(follow_reference=True)))


@app.route('/api/users')
def get_field_agents():
    role_type = request.args.get('role_type')
    data = [json.loads(ticket.to_json(follow_reference=True)) for ticket in User.objects(role=role_type)]
    data_dict = data
    for user in data_dict:
        del (user['password'])
    return jsonify(data_dict)


@app.route('/api/tickets/comment/<string:ticket_id>', methods=['POST'])
def add_comment(ticket_id):
    c = Comment().from_json(json.dumps(request.get_json()))
    t = Ticket.objects(id=ticket_id).get()
    t.comments.append(c)
    t.status = c.statusChangedTo
    t.assignee = c.assignee
    t.save()
    user_dict = json.loads(t.created_by.to_json())
    receivers = ['cvetkovski98@gmail.com', 'stboki77@gmail.com']
    message_text = user_dict['name'] + " " + user_dict[
        'surname'] + " just commented on " + t.title + " and updated status to " + t.status
    title = "[" + t.title + "] Comment added"
    send_mail_async(receivers, title, message_text)
    return jsonify(json.loads(c.to_json()))


@app.route('/api/tickets/create', methods=['POST'])
def create_ticket():
    receiving_dict = request.get_json()
    if receiving_dict['assignee'] is None:
        receiving_dict['assignee'] = None
    t = Ticket(
        id=receiving_dict['id'],
        title=receiving_dict['title'],
        content=receiving_dict['content'],
        timestamp=receiving_dict['timestamp'],
        status=receiving_dict['status'],
        created_by=receiving_dict['created_by'],
        comments=receiving_dict['comments'],
        assignee=receiving_dict['assignee']
    )
    # t.assignee = None
    print(t)
    t.save(cascade=False)
    user_dict = json.loads(t.created_by.to_json())
    receivers = ['cvetkovski98@gmail.com', 'stboki77@gmail.com']
    message_text = user_dict['name'] + " " + user_dict[
        'surname'] + " created a new ticket with title " + t.title + " and status " + t.status
    send_mail_async(receivers, 'Ticket created', message_text)
    return Response(status=200,
                    mimetype='application/json')


@app.route('/api/user/register', methods=['POST'])
def register_user():
    user_data = request.get_json()
    User(
        id=user_data['id'],
        name=user_data['name'],
        surname=user_data['surname'],
        email=user_data['email'],
        password=bcrypt.generate_password_hash(user_data['password']).decode('utf-8'),
        role=user_data['role'],
        address=user_data['address']
    ).save()
    return Response(status=200,
                    mimetype='application/json')


@app.route('/api/user/login', methods=['POST'])
def login():
    request_data = request.get_json()
    email = request_data['email']
    password = request_data['password']
    data = User.objects(email=email).get()
    user_dict = json.loads(data.to_json())
    if bcrypt.check_password_hash(user_dict['password'], password):
        del (user_dict['password'])
        access_token = create_access_token(identity=user_dict)
        return jsonify({'token': access_token})
    else:
        return jsonify({"error": "wrong"})


def send_mail_async(receiver, subject, body, sender=None):
    """

    :param receiver: list of emails to send message to
    :param subject: the subject of the email
    :param body: the body of the email
    :param sender: (optional) who sends the mail
    :return:
    """
    if sender is None:
        sender = app.config['MAIL_DEFAULT_SENDER']

    message = Message(subject=subject, recipients=receiver, body=body, sender=sender)

    @copy_current_request_context
    def send_message(m):
        mail.send(m)

    sender = threading.Thread(name='mail_sender', target=send_message, args=(message,))
    sender.start()


if __name__ == '__main__':
    app.run(port=5000, debug=True)
