#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import *
import os
from werkzeug import secure_filename
import csv
import MySQLdb
import shutil
import datetime
from dbconnect import connection
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://ian:rognarock@mysql.default.svc.cluster.local/iandb'
db = SQLAlchemy(app)
UPLOAD_FOLDER = '.'
ALLOWED_EXTENSIONS = set(['csv'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

mydb = MySQLdb.connect(host='mysql.default.svc.cluster.local',
    user='ian',
    passwd='rognarock',
    db='iandb')
cursor = mydb.cursor()

def delete_item(ids):
    cursor.execute("DELETE FROM item WHERE ID = (%s)", (ids, ))
    mydb.commit()
#    cursor.close()

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)

def remove_file(filename):
    if os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], filename)):
      os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    else:
        pass
    
def upload_data(filename):
    csv_data = csv.reader(file(filename))
    for row in csv_data:

        cursor.execute('INSERT INTO item(Sku, \
                      Name, Price )' \
                      'VALUES("%s", "%s", "%s")',
                      row)
    mydb.commit()
#    cursor.close()

def save_rename(filename):
    shutil.move(os.path.join(app.config['UPLOAD_FOLDER'], filename), 'uploaded/'+filename + datetime.datetime.now().strftime("%Y%m%d-%H%M%S") + '.csv')

@app.route('/del')
def index():
    items = Item.query.all()
    return render_template_string('''<ul>{% for item in items %}
        <li>{{ item.name }} -
        <form method=post action="{{ url_for('delete', id=item.id) }}">
            <button type=submit>delete</button>
        </form></li>
    {% endfor %}</ul>''', items=items)

@app.route('/<int:id>/delete', methods=['GET', 'POST'])
def delete(id):
    delete_item(id)
    return redirect(url_for('index'))


@app.route("/test")
def hello(name=None):
    
    return render_template('hello.html', name=name)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = file.filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            upload_data(filename)
            save_rename(filename)
            remove_file(filename)
            return redirect(url_for('upload_file'))
        else:
            return '''
            <!doctype html>
            <title>Upload new File</title>
            <h1>File Select Error!</h1>
            <a href="/file">file</a>
            '''
    return '''
    <!doctype html>
    <h1>List of saved csv</h1>
    <a href="/list">show_list</a>
    <h1>Show Data from Database</h1>
    <a href="/dashboard">show_data_from_database</a>
    <h1>Delete selected row</h1>
    <a href="/del">delete_row_from_database</a>
    <h1>Upload new File</h1>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
    '''

@app.route('/dashboard/')       
def display_deals():

    c, conn = connection()

    query = "SELECT * from item"
    c.execute(query)

    data = c.fetchall()

    conn.close()

    return render_template("dashboard.html", data=data)

@app.route('/list')
def dir_listing():

    # Joining the base and the requested path
    abs_path = os.path.join(app.config['UPLOAD_FOLDER'], 'uploaded')

    # Return 404 if path doesn't exist
    if not os.path.exists(abs_path):
        return abort(404)

    # Check if path is a file and serve
    if os.path.isfile(abs_path):
        return send_file(abs_path)

    # Show directory contents
    files = os.listdir(abs_path)
    return render_template('files.html', files=files)


if __name__ == "__main__":
    app.run(host= '0.0.0.0', debug=True)
