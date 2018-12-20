from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import json
app = Flask(__name__)

@app.route('/new', methods=['GET', 'POST'])
def index():
    if request.method == "POST":
        data = json.loads(request.data.decode('utf-8'))
        conn = sqlite3.connect('static/articles.db')
        cursor = conn.execute('insert into articles (headline, byline, section, body, datePub) values(?,?,?,?,strftime("%Y-%m-%d %H-%M","now"))', (data['headline'], data['byline'], data['section'], data['body'],))
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
        return render_template('edit.html', id=article[0], headline=article[1], byline=article[2], section=article[3], body=article[4])


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
    return render_template('article.html', headline=body[0], byline=body[1], body=body[3])


