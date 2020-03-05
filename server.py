# Haikusaare web server

from flask import Flask, request, abort, send_from_directory, render_template_string
from haikusaare import Haikusaare
from os.path import isfile

app = Flask(__name__)
generator = Haikusaare()

def from_file(filename):
    with open(filename, encoding='utf-8') as file:
        contents = file.read()
    return contents

main_page = from_file('front/main.html')
haikusaare_page = from_file('front/haikusaare.html')
haikusaare_parimad_page = from_file('front/parimad.html')

hostname = from_file('conf/hostname').strip()
besthaikus = [[line.strip() for line in haiku.strip().split('\n')]
              for haiku in from_file('pearls.txt').strip().split('#')]

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

@app.route('/haikusaare/parimad')
def haikusaare_parimad_page_address():
    return render_template_string(haikusaare_parimad_page, haikus=besthaikus)

@app.route('/haikusaare/haiku')
def get_haiku():
    if 'insp' in request.args:
        return generator.generate_haiku(request.args['insp'])
    else:
        return generator.generate_haiku('')

if __name__ == '__main__':
    app.run(host=hostname)
