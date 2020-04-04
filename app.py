import json

import mongoengine as db
from flask import Flask, Response, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token
from flask_bcrypt import Bcrypt

from models import Ticket, User, Comment

app = Flask(__name__)
db.connect(db='CompanyShuttleDb', host='localhost', port=27017)
jwt = JWTManager(app)
bcrypt = Bcrypt(app)
app.config['JWT_SECRET_KEY'] = 'secret'

cors = CORS(app)


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
    return jsonify(json.loads(c.to_json()))


@app.route('/api/tickets/create', methods=['POST'])
def create_ticket():
    Ticket.from_json(json.dumps(request.get_json())).save()
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


if __name__ == '__main__':
    app.run(port=5000, debug=True)
