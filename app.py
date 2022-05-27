from flask import Flask, render_template
from flask_restful import Resource, Api

app = Flask(__name__)
api = Api(app)

@app.route("/")
def home():
    return render_template('index.html')

class HelloWorld(Resource):
    def get(self):
        return {'hello': 'world'}

api.add_resource(HelloWorld, '/hello')

if __name__ == '__main__':
    app.run(debug=True)