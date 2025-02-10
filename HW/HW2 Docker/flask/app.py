from flask import Flask, make_response, request
import os


app = Flask(__name__)
val = os.getenv('PORT') #importing port env variable


@app.route('/')
def hello():
   response = make_response(
       {
           'response': 'Hello, World!',
           'status': 200
       }
   )
   return response


#2. Route w/Get Parameter
@app.route('/repeat', methods=['GET'])
def part2():
   input = request.args.get('input')
   response = make_response (
       {
           'body': input,
           'status': 200
       }
   )
   return response


#3. Health function (Expose on endpoints)
@app.route('/health')
@app.route('/healthcheck')
def healthcheck():
   response = make_response(
       {
           'body': 'OK',
           'status': 200
       }
   )
   return response


#4. Infinite loop endpoint
@app.route('/4ever')
def loop():
   i = -1;
   while i < 0:
       i = i - 1 ;


if __name__ == '__main__':
   # By default flask is only accessible from localhost.
   # Set this to '0.0.0.0' to make it accessible from any IP address
   # on your network (not recommended for production use)
   app.run(host='0.0.0.0', port = val, debug=True, threaded=False)
