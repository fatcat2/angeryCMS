from flask import Flask, render_template, request
import sqlite3
import markdown
import json
app = Flask(__name__)

@app.route('/new', methods=['GET', 'POST'])
def index():
    if request.method == "POST":
        data = json.loads(request.data)
        print(data)

        conn = sqlite3.connect('static/articles.db')
        cursor = conn.execute('insert into articles (headline, byline, section, body, datePub) values(?,?,?,?,strftime("%Y-%m-%d %H-%M","now"))', (data['headline'], data['byline'], data['section'], data['body'],))
        conn.commit()
        conn.close()

        return render_template('index.html')
    else:
        return render_template('index.html')

@app.route('/a/<articleID>')
def article(articleID):
    conn = sqlite3.connect('static/articles.db')
    cursor = conn.execute('select * from articles where ROWID=?', (articleID,))
    body = ""
    for row in cursor:
        body = row
    conn.close()
    return render_template('article.html', headline=body[0], byline=body[1], body=body[3])


