import datetime

import simplejson
from flask import Flask, request, send_file, render_template
from flask_autodoc import Autodoc
from werkzeug import secure_filename
import util
import os

from upload import upload_file, upload_from_db, aact_db_upload

app = Flask(__name__)

init_status = "none"


@app.route('/')
def home():
    return "Welcome to Clarity NLP Ingestor"


@app.route('/upload', methods=['POST', 'GET'])
def upload():
    if request.method == 'GET':
        return render_template('solr_upload.html')

    elif request.method == 'POST':
        f = request.files['file']
        filepath = os.path.join('tmp', secure_filename(f.filename))
        f.save(filepath)
        msg = upload_file(util.solr_url, filepath)
        os.remove(filepath)
        return render_template('solr_upload.html', result=msg)

    return "ERROR. Contact Admin and try again later."


@app.route('/upload_from_db', methods=['GET'])
def db_to_solr():
    """Migrate data from DB to Solr."""
    if request.method == 'GET':
        msg = upload_from_db(util.conn_string, util.solr_url)
        return msg

    return "Couldn't migrate data."


@app.route('/upload_from_aact', methods=['GET'])
def aact_upload():
    """Migrate data from aact DB to Solr."""
    if request.method == 'GET':
        msg = aact_db_upload(util.solr_url)
        return msg

    return "Couldn't migrate data."


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5100, threaded=True)