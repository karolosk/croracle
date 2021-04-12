from flask import Flask, render_template, request, flash
from werkzeug.utils import secure_filename
import os

ALLOWED_EXTENSIONS = {'csv'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def hello():
    return render_template("home.html")


@app.route('/form')
def form():
    return render_template('form.html')


@app.route('/upload', methods=['POST', 'GET'])
def upload():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'cdc_file' not in request.files:
            flash('No file part')
        file = request.files['cdc_file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            with open(f'uploads/{filename}', "rb", newline=None) as filet:
                f = filet.readlines()
                os.remove(f'uploads/{filename}')
                for a in f:
                    print(a)

            # return redirect(url_for('download_file', name=filename))
        # if 'cdc_file' not in request.files:
        #     print('No file part')
        # else:
        #     print('file found')
        # f = request.files['cdc_file']
        # print(type(f))
        # print(f.read)
        # with open(f, "r")as _file:
        #     all_lines = _file.readlines()
        #     for line in all_lines:
        #         print(line)
        # # f.save(secure_filename(f.filename))
        return "File saved successfully"


if __name__ == '__main__':
    app.run(debug=True)
