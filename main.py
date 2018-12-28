from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import json
import boto3
import uuid
import os
from werkzeug.utils import secure_filename
app = Flask(__name__)
UPLOAD_FOLDER='./tmp'
ALLOWED_EXTENSIONS = set(['png', 'PNG', 'JPG', 'jpg', 'JPEG', 'jpeg'])

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/new', methods=['GET', 'POST'])
def index():
    #split into to sections: POST for saving the articles to DB and GET for getting the portal
    if request.method == "POST":
        #debug statements
        print(request.form)
        print(request.files)
        data = request.form
        #if statement for new images
        #TODO: expand to allow old images
        if 'image' not in request.files:
            print('no file')
        else:
            file = request.files['image']

            #just in case no file is submitted (again)
            if file.filename == '':
                return redirect(url_for('listArticles'))
            
            #now if it's the real deal
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                savePath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(savePath)
                bucket = "jackson56a4fac2-0705-4d37-88d6-8582757e9b8c"
                
                boto3.client('s3').upload_file(Filename=savePath, Bucket=bucket,Key='Pictures/' + filename)
                #save picture into picture db
                conn = sqlite3.connect('static/articles.db')
                tmpLink = 'https://s3.us-east-2.amazonaws.com/jackson56a4fac2-0705-4d37-88d6-8582757e9b8c/Pictures/' + filename
                cursor = conn.execute('insert into images(name, link, date) values(?, ?, datetime("now"))', (filename, tmpLink,))
                conn.commit()
                conn.close()
        
        #checking publishing status
        pub = False;
        if 'no_pub' in data.keys():
            pub = False
        else:
            pub = True
        
        #connecting and committing to the database
        conn = sqlite3.connect('static/articles.db')
        cursor = conn.execute('insert into articles (headline, byline, section, body, datePub, photo, publish) values(?,?,?,?,strftime("%Y-%m-%d %H-%M","now"), ?, ?)', (data['headline'], data['byline'], data['section'], data['content'], tmpLink, pub,))
        conn.commit()
        conn.close()

        return render_template('index.html')
    else:
        return render_template('index.html')


@app.route('/edit', methods=['POST'])
def edit():
    data = json.loads(request.data.decode('utf-8'))
    conn = sqlite3.connect('static/articles.db')
    cursor = conn.execute('update articles set headline=?, byline=?, section=?, body=? where ROWID=?', (data['headline'], data['byline'], data['section'], data['body'], data['id'],))
    conn.commit()
    conn.close()
    return ":)"

@app.route('/edit/<id>', methods=['GET', 'POST'])
def editSpecific(id):
    if request.method == 'POST':
        data = json.loads(request.data.decode('utf-8'))
        conn = sqlite3.connect('static/articles.db')
        cursor = conn.execute('update articles set headline=?, byline=?, section=?, body=?', (data['headline'], data['byline'], data['section'], data['body'],))
        conn.commit()
        conn.close()
        print('POST!')
        return redirect(url_for('listArticles'))
    else:
        conn = sqlite3.connect('static/articles.db')
        cursor = conn.execute('select rowid, * from articles where ROWID=?', (id,))
        for row in cursor:
            article = row
        conn.close()
        return render_template('edit.html', id=article[0], headline=article[1], byline=article[2], section=article[3], body=article[4], pub=article[6])


@app.route('/data')
def listArticlesJSON():
    conn = sqlite3.connect('static/articles.db')
    cursor = conn.execute('select rowid, * from articles')
    ret = []
    for row in cursor:
        insertDict = {}
        insertDict["headline"] = row[1]
        insertDict["id"] = row[0]
        ret.append(insertDict)
    ret2 = {}
    ret2["data"] = ret
    retJSON = json.dumps(ret2)
    return retJSON

@app.route('/a')
def listArticles():
    return render_template('listArticles.html')

@app.route('/a/<articleID>')
def article(articleID):
    conn = sqlite3.connect('static/articles.db')
    cursor = conn.execute('select * from articles where ROWID=?', (articleID,))
    body = ""
    for row in cursor:
        body = row
    conn.close()
    print(body[4])
    if body[6] == True:
        return render_template('article.html', headline=body[0], byline=body[1], body=body[3], img=body[4])
    else:
        return redirect(url_for('listArticles'))


