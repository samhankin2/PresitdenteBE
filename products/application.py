from flask import Flask
from flask_restful import Resource, Api
from flask_socketio import SocketIO

app = Flask(__name__)
api = Api(app)
socketio = SocketIO(app, cors_allowed_origins="*")

class Product(Resource):
    def get(self):
        socketio.emit('okay', {'data': 42})
        return {
            "product":[
                "ice-cre",
                "this has updated",
                "fruit"
                "ice-cream",
                "chocolasdasdate",
                "fruit",
                "Apex Legends"
            ]
        }


api.add_resource(Product, '/')

@socketio.on('test')
def handle_message(data):
    socketio.emit('okay', {'data': 42})
    print('received messag' + data, flush=True)

@socketio.on('message')
def handle_message(data):
    print(data)
    socketio.emit('message', data)
    print('received messag' + data, flush=True)



if __name__ == '__main__':
    # socketio.run(app, debug=True)
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)

    # app.run(host='0.0.0.0', port=5000, debug=True)