import json

import mongoengine as db
from mongoengine_goodjson import *
from flask import Flask, Response, request, jsonify
from flask_cors import CORS

from models import Comment, Ticket, User

app = Flask(__name__)
# allow requests from client app
db.connect(db='CompanyShuttleDb', host='localhost', port=27017)
# creating api routes for the angular client

cors = CORS(app)


@app.route('/api/tickets', methods=['GET'])
def get_all_tickets():
    data = [json.loads(ticket.to_json(follow_reference=True)) for ticket in Ticket.objects()]
    return jsonify(data)


@app.route('/api/tickets/<string:ticket_id>', methods=['GET'])
def get_ticket(ticket_id):
    data = Ticket.objects(id=ticket_id).get()
    return jsonify(json.loads(data.to_json(follow_reference=True)))


@app.route('/api/tickets/create', methods=['POST'])
def create_ticket():
    Ticket.from_json(json.dumps(request.get_json())).save()
    return Response(status=200,
                    mimetype="application/json")


if __name__ == '__main__':
    app.run(port=5000, debug=True)
