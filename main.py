import os
from pkgutil import iter_modules
from flask import Flask, request, render_template
from google.cloud import storage
from google.cloud import vision

app = Flask(__name__, template_folder='template')

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "anjalee-cloud-work-space-ca1fff86b175.json"


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        print("Data Received")
    return render_template('index.html')


# lable detection
@app.route('/animal-label-detection', methods=['GET', 'POST'])
def animalLabelDetection():


    image_uri = 'gs://anjalee_cloud_work_space/animaImg.jpg'

    client = vision.ImageAnnotatorClient()
    image = vision.Image()
    image.source.image_uri = image_uri

    response = client.label_detection(image=image)

    print('Labels (and confidence score):')

    labels = response.label_annotations
    labelName = []
    labelScore = []

    for label in labels:
        resultV = label.description
        labelName.append(resultV)
        resultS = '%.2f%%' % (label.score*100.)
        labelScore.append(resultS)

    return render_template('animal-label-detection.html', labelName=labelName, labelScore=labelScore)


# object detection
@app.route('/animal-object-detection', methods=['GET', 'POST'])
def animalObjectDetection():

    image_uri = 'gs://anjalee_cloud_work_space/animaImg.jpg'

    client = vision.ImageAnnotatorClient()
    image = vision.Image()
    image.source.image_uri = image_uri
    response = client.object_localization(image=image)
    objects = response.localized_object_annotations
    objectName = []
    objectScore = []

    for obj in objects:
        resultN = obj.name
        objectName.append(resultN)
        resultS = '%.2f%%' % (obj.score*100.)
        objectScore.append(resultS)

    return render_template('animal-object-detection.html', labelName=objectName, labelScore=objectScore)


# detect cat or dog
@app.route('/animal-list', methods=['GET', 'POST'])
def animalList():

    cat = []
    dog = []

    bucket_name = "anjalee_cloud_work_space"
    storage_client = storage.Client()
    blobs = storage_client.list_blobs(bucket_name)

    for blob in blobs:
        imageUri = ("gs://anjalee_cloud_work_space/"+blob.name)

        client = vision.ImageAnnotatorClient()
        image = vision.Image()

        image.source.image_uri = imageUri
        objects = client.object_localization(
            image=image).localized_object_annotations

        len(objects)

        for object_ in objects:

            if object_.name == "Cat" and object_.score > 0.80:
                cat.append('Img Name: {} , Confidence: {}'.format(
                    blob.name, '%.2f%%' % (object_.score*100.)))

            if object_.name == "Dog" and object_.score > 0.80:
                dog.append('Img Name: {} , Confidence: {}'.format(
                    blob.name, '%.2f%%' % (object_.score*100.)))

    return render_template('animal-list.html', cat=cat, dog=dog)


@app.route('/animal-img-list', methods=['GET', 'POST'])
def animalImgList():

    catUrl = []
    dogUrl = []

    bucket_name = "anjalee_cloud_work_space"
    storage_client = storage.Client()
    blobs = storage_client.list_blobs(bucket_name)

    for blob in blobs:
        imageUri = ("gs://anjalee_cloud_work_space/"+blob.name)
        publicImgUri = (
            'https://storage.googleapis.com/anjalee_cloud_work_space/'+blob.name)

        client = vision.ImageAnnotatorClient()
        image = vision.Image()

        image.source.image_uri = imageUri
        objects = client.object_localization(
            image=image).localized_object_annotations

        len(objects)

        for object_ in objects:

            if object_.name == "Cat" and object_.score > 0.80:
                catUrl.append(publicImgUri)

            if object_.name == "Dog" and object_.score > 0.80:
                dogUrl.append(publicImgUri)

    return render_template('animal-img-list.html', catUrl=catUrl, dogUrl=dogUrl)


if __name__ == "__main__":
    app.run(debug=True, threaded=True)
