from flask import Flask, render_template, request, redirect
import json
import pymongo

app = Flask(__name__)

with open('tickets.json') as json_file:
    data = json.load(json_file)

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["CompanyShuttleDb"]
mycol = mydb["tickets"]

@app.route('/', methods = ['GET'])
def index():
    data = mycol.find()
    return render_template('ticket/ticket-list.html', tickets = data)

@app.route('/tickets/<int:id>', methods = ['GET'])
def get_ticket(id):
    query = {
        "id": id
    }
    tic = mycol.find_one(query)
    return render_template('ticket/ticket-details.html', ticket = tic)

@app.route('/tickets', methods = ['POST'])
def add_ticket():
    body = request.get_json()
    mycol.insert_one(body)
    return redirect('/')

@app.route('/tickets/<int:id>', methods = ['DELETE'])
def delete_ticket(id):
    query = {
        "id": id
    }
    mycol.delete_one(query)
    return redirect('/')



if __name__ == '__main__':
    app.run(port=5000, debug='true')