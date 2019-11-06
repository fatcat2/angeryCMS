import os
from datetime import datetime

from google.cloud import storage
from werkzeug.utils import secure_filename


ALLOWED_EXTENSIONS = set(["png", "PNG", "JPG", "jpg", "JPEG", "jpeg"])
BUCKET_NAME = os.getenv("BUCKET_NAME")


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def unique_file_naming(filename):
    today = datetime.today()
    return "{}{}{}{}{}{}{}_{}".format(
        today.year,
        today.month,
        today.day,
        today.hour,
        today.minute,
        today.second,
        today.microsecond,
        filename,
    )


def processImage(request):
    tmpLink = ""
    if "image" not in request.files:
        print("no file")
        return ""
    else:
        file = request.files["image"]

    # just in case no file is submitted (again)
    if file.filename == "":
        return redirect(url_for("listArticles"))

    # now if it's the real deal
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        savePath = os.path.join("/tmp", filename)
        file.save(savePath)

        storage_client = storage.Client()
        bucket = storage_client.get_bucket(BUCKET_NAME)
        new_file = bucket.blob(filename)
        blob.upload_from_filename(savePath)

    return tmpLink
