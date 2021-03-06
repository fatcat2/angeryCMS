# import libraries
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user
import sqlite3
import json
import os

# import helper library

app = Flask(__name__)

import sqlite3
import boto3
import os
from werkzeug.utils import secure_filename
from main import app
ALLOWED_EXTENSIONS = set(['png', 'PNG', 'JPG', 'jpg', 'JPEG', 'jpeg'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



def processImage(request):
    tmpLink = ""
    if 'image' not in request.files:
        print('no file')
        return ""
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
        conn.execute('insert into images(name, link, date) values(?, ?, datetime("now"))', (filename, tmpLink,))
        conn.commit()

    return tmpLink

#app = Flask(__name__)
UPLOAD_FOLDER='./tmp'
ALLOWED_EXTENSIONS = set(['png', 'PNG', 'JPG', 'jpg', 'JPEG', 'jpeg'])
app.secret_key = '_5#y2L"F4Q8z\n\xec]/'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
login_manager = LoginManager(app)

@app.route('/test')
def testPage():
    conn = sqlite3.connect('static/articles.db')
    cursor = conn.execute('select rowid, * from articles where publish=1 ORDER BY datePub DESC limit 10')
    tmpList = []

    for row in cursor:
        tmpList.append(row)

    initialList = []
    initialList.append(tmpList.pop(0))
    initialList.append(tmpList.pop(0))
    print(initialList);
    return render_template('homepage.html', bigBox=initialList[1])

@app.route('/', methods=['GET', 'POST'])
def homepage():
    conn = sqlite3.connect('static/articles.db')
    cursor = conn.execute('select rowid, * from articles where publish=1 ORDER BY datePub DESC limit 10')
    tmpList = []

    for row in cursor:
        tmpList.append(row)

    return render_template('homepage.html', bigBox=tmpList.pop(0))


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/new', methods=['GET', 'POST'])
@login_required
def index():
    #split into to sections: POST for saving the articles to DB and GET for getting the portal
    if request.method == "POST":
        tmpLink = processImage(request)
        data = request.form
        print(data.keys())
        tmpList = [];
        for key in data.keys():
            tmpList.append(key)
        #checking publishing status
        pub = False;
        if 'no_pub' in tmpList:
            pub = False
        else:
            pub = True

        #connecting and committing to the database
        conn = sqlite3.connect('static/articles.db')
        conn.execute('insert into articles (headline, byline, section, body, datePub, photo, publish, tagline) values(?,?,?,?,strftime("%Y-%m-%d %H-%M","now"), ?, ?, ?)', (data['headline'], data['byline'], data['section'], data['content'], tmpLink, pub, data['tagline'],))
        conn.commit()
        conn.close()

        return render_template('index.html')
    else:
        return render_template('index.html')


@app.route('/edit', methods=['POST'])
@login_required
def edit():
    # See if image needs to be put in database
    tmpLink = processImage(request)
    data = request.form
    #checking publishing status
    pub = False;
    if 'no_pub' in data.keys():
        print(data.keys())
        pub = False
    else:
        print("Pub is true")
        print(data['pub'])
        pub = True

    conn = sqlite3.connect('static/articles.db')
    conn.execute('update articles set headline=?, byline=?, section=?, body=?, publish=?, photo=? where ROWID=?', (data['headline'], data['byline'], data['section'], data['body'], pub, tmpLink, data['id']))
    conn.commit()
    conn.close()
    return ":)"

@app.route('/edit/<articleID>', methods=['GET'])
@login_required
def editSpecific(articleID):
    conn = sqlite3.connect('static/articles.db')
    cursor = conn.execute('select rowid, * from articles where ROWID=?', (articleID,))
    articleTMP = []
    for row in cursor:
        articleTMP.append(row)
    if(len(articleTMP) == 0):
        conn.close()
        return redirect(url_for('listArticles'))
    conn.close()
    article = articleTMP[0]
    print(article)
    return render_template('edit.html', id=articleID, headline=article[1], byline=article[2], section=article[3], body=article[4], image=article[5], pub=article[7])


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
@login_required
def listArticles():
    return render_template('listArticles.html')

@app.route('/a/<articleID>')
def article(articleID):
    conn = sqlite3.connect('static/articles.db')
    cursor = conn.execute('select rowid, * from articles where ROWID=?', (articleID,))
    body = ""
    for row in cursor:
        body = row
    conn.close()
    print(body[4])
    if body[7] == True:
        return render_template('article.html', articleID=body[0], headline=body[1], byline=body[2], body=body[4], img=body[5], tagline=body[8])
    else:
        return redirect(url_for('listArticles'))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        form = request.form
        user = form['username']
        conn = sqlite3.connect('static/users.db')
        cursor = conn.execute('select * from users where username=?', (user,))

        tmpLoginList = []
        for row in cursor:
            tmpLoginList.append(row)
        conn.close()
        if(len(tmpLoginList) <= 0):
            return redirect(url_for("homepage"))

        maybeUser = tmpLoginList[0]
        maybeUserHash = generate_password_hash(maybeUser[2])
        if (len(tmpLoginList) > 0) and (maybeUser[0] == user) and (check_password_hash(maybeUserHash, form['password'])):
            #success
            print("success")
            login_user(User(maybeUser[0], maybeUser[2], maybeUser[1], maybeUser[4], maybeUser[3]), remember=True)
            return redirect(url_for("listArticles"))
        else:
            return redirect(url_for("homepage"))
    else:
        return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("homepage"))

@login_manager.user_loader
def load_user(user_id):
    conn = sqlite3.connect('static/users.db')
    cursor = conn.execute('select * from users where username=?', (user_id,))
    userList = []
    for r in cursor:
        userList.append(r)
    maybeUser = userList.pop(0)
    return User(maybeUser[0], maybeUser[2], maybeUser[1], maybeUser[4], maybeUser[3])

@app.errorhandler(401)
def page_not_found(e):
    return redirect(url_for("login"))

class User:
    def __init__(self, username, password, email, fullName, authLevel):
        self.username = username
        self.password = password
        self.email = email
        self.fullName = fullName
        self.authLevel = authLevel
        self.authenticated = True
    @classmethod
    def is_active(cls):
        return True

    def get_id(self):
        return self.username

    def is_authenticated(self):
        return self.authenticated

    @classmethod
    def is_anonymous(cls):
        return False


# run the app.
if __name__ == "__main__":
    #application.debug = True
    application.run()
