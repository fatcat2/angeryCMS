import sqlite3
import boto3
import os

def processImage(request):
    data = request.form
    tmpLink = ""
    if 'image' not in request.files:
        print('no file')
        return tmpLink = ""
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
