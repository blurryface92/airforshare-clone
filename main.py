from fileinput import filename
from flask import Flask, render_template, request, redirect, url_for,abort,flash,send_from_directory
from flask_sqlalchemy import SQLAlchemy
import os
from werkzeug.utils import secure_filename



app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'secret'
app.config['UPLOAD_FOLDER'] = 'files'
app.jinja_env.add_extension('jinja2.ext.loopcontrols')

db = SQLAlchemy(app)

class Text(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(200))
    def __repr__(self):
        return '<Text %r>' % self.text


class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(200))
    def __repr__(self):
        return '<File %r>' % self.filename

def create_db():
    db.create_all()

create_db()

@app.route('/')
def index():
    text = Text.query.all()
    file = File.query.all()
    return render_template('text.html', text=text, file=file)

@app.route('/text')
def text():
    text = Text.query.all()
    if not text:
        return render_template('text_edit.html', text=text)
    else:
        return render_template('text.html', text=text)


@app.route('/file')
def file():
    files = File.query.all()
    if not files:
        return render_template('file_upload.html', files=files)
    else:
        return render_template('file.html', files=files)

@app.route('/file/upload', methods=['GET', 'POST'])
def file_upload():
    file =  request.files['filename']
    if request.method == 'POST':
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        newfile = File(filename=file.filename)
        db.session.add(newfile)
        db.session.commit()
    else:
        return redirect(url_for('file'))
    files = File.query.all()
    return redirect(url_for('file', files=files))
    

@app.route('/text/upload', methods=['POST'])
def text_upload():
    if request.method == 'POST':
        text = request.form['text']
        if not text:
            flash('Please enter text')
            return redirect(url_for('text'))
        new_text = Text(text=text)
        db.session.add(new_text)
        db.session.commit()
    else:
        return redirect(url_for('text'))
    text = Text.query.all()
    return redirect(url_for('index', text=text))

@app.route('/file/delete/<int:id>', methods=['GET'])
def file_delete(id):
    file = File.query.get(id)
    if not file:
        abort(404)
    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
    db.session.delete(file)
    db.session.commit()
    return redirect(url_for('file'))

@app.route('/text/delete/<int:id>')
def text_delete(id):
    text = Text.query.get_or_404(id)
    db.session.delete(text)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/files/<path:filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

app.run(debug=True)