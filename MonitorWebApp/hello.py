from flask import Flask
app = Flask(__name__)
from OpenSSL import SSL
context = SSL.Context(SSL.SSLv23_METHOD)
context.use_privatekey_file('/etc/pki/tls/private/localhost.key')
context.use_certificate_file('/etc/pki/tls/certs/localhost.crt')

@app.route("/")
def hello():
    return "Hello World!"

if __name__ == "__main__":
	app.run(host='0.0.0.0', port=18181, ssl_context=context)
