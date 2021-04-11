from flask import Flask, render_template, request
from werkzeug.utils import secure_filename

app = Flask(__name__)


@app.route("/")
def hello():
    return ("Hello")


@app.route('/form')
def form():
    return render_template('form.html')


@app.route('/upload', methods=['POST', 'GET'])
def upload():
    if request.method == 'POST':
        if 'cdc_file' not in request.files:
            print('No file part')
        else:
            print('file found')
        f = request.files['cdc_file']
        print(type(f))
        print(f.read())
        # with open(f, "r")as _file:
        #     all_lines = _file.readlines()
        #     for line in all_lines:
        #         print(line)
        # # f.save(secure_filename(f.filename))
        return "File saved successfully"


if __name__ == '__main__':
    app.run(debug=True)
