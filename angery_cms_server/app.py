import json
import os

from flask import Flask, render_template, request, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user

from angery_cms_server.helpers.helperMain import allowed_file, processImage, auth

app = Flask(__name__)

ALLOWED_EXTENSIONS = set(["png", "PNG", "JPG", "jpg", "JPEG", "jpeg"])
app.config["UPLOAD_FOLDER"] = "./tmp"
login_manager = LoginManager(app)


@app.route("/test")
def testPage():
    return render_template("homepage.html", bigBox=initialList[1])


@app.route("/", methods=["GET", "POST"])
def homepage():

    return render_template("homepage.html", bigBox=tmpList.pop(0))


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/new", methods=["GET", "POST"])
@login_required
def index():
    # split into to sections: POST for saving the articles to DB and GET for getting the portal
    if request.method == "POST":
        tmpLink = processImage(request)
        data = request.form
        print(data.keys())
        tmpList = []
        for key in data.keys():
            tmpList.append(key)
        # checking publishing status
        pub = False
        if "no_pub" in tmpList:
            pub = False
        else:
            pub = True

        return render_template("index.html")
    else:
        return render_template("index.html")


@app.route("/edit", methods=["POST"])
@login_required
def edit():
    # See if image needs to be put in database
    tmpLink = processImage(request)
    data = request.form
    # checking publishing status
    pub = False
    if "no_pub" in data.keys():
        print(data.keys())
        pub = False
    else:
        print("Pub is true")
        print(data["pub"])
        pub = True

    return ":)"


@app.route("/edit/<articleID>", methods=["GET"])
@login_required
def editSpecific(articleID):
    return render_template(
        "edit.html",
        id=articleID,
        headline=article[1],
        byline=article[2],
        section=article[3],
        body=article[4],
        image=article[5],
        pub=article[7],
    )


@app.route("/data")
def listArticlesJSON():
    return retJSON


@app.route("/a")
@login_required
def listArticles():
    return render_template("listArticles.html")


@app.route("/a/<articleID>")
def article(articleID):
    return False


@app.route("/login", methods=["GET", "POST"])
def login():
    data = request.form
    return auth(data["username"], data["password"])


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("homepage"))


@login_manager.user_loader
def load_user(user_id):
    conn = sqlite3.connect("static/users.db")
    cursor = conn.execute("select * from users where username=?", (user_id,))
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
    # application.debug = True
    application.run()
