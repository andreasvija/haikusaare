# Haikusaare web server

from flask import Flask, request, abort, send_from_directory
from haikusaare import Haikusaare
from os.path import isfile

app = Flask(__name__)
generator = Haikusaare()

def from_file(filename):
    with open(filename, encoding='utf-8') as file:
        page = file.read()
    return page

main_page = from_file('front/main.html')
haikusaare_page = from_file('front/haikusaare.html')

hostname = from_file('conf/hostname').strip()

@app.route('/')
@app.route('/index.html')
def main_page_address():
    return main_page

@app.route('/front/<filename>')
def send_file(filename):
    if isfile('front/'+filename):
        return send_from_directory('front/', filename=filename, as_attachment=True)
    else:
        abort(404)

@app.route('/haikusaare')
def haikusaare_page_address():
    return haikusaare_page

@app.route('/haikusaare/haiku')
def get_haiku():
    if 'insp' in request.args:
        return generator.generate_haiku(request.args['insp'])
    else:
        return 'Faulty GET request.'

if __name__ == '__main__':
    app.run(host=hostname)