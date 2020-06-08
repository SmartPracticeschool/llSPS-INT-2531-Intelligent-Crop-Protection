import cv2
import numpy as np
import datetime
import json
from watson_developer_cloud import VisualRecognitionV3
import ibm_boto3
from ibm_botocore.client import Config, ClientError
from cloudant.client import Cloudant
from cloudant.error import CloudantException
from cloudant.result import Result, ResultByKey
import requests
face_classifier=cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
eye_classifier=cv2.CascadeClassifier("haarcascade_eye.xml")
COS_ENDPOINT = "https://s3.jp-tok.objectstorage.softlayer.net" # Current list avaiable at https://control.cloud-object-storage.cloud.ibm.com/v2/endpoints
COS_API_KEY_ID = "G_bbpn-FeZZD1zO29WhpIfYVYTTwKbXWc0FBzPVIj4wb" # eg "W00YiRnLW4a3fTjMB-odB-2ySfTrFBIQQWanc--P3byk"
COS_AUTH_ENDPOINT = "https://iam.cloud.ibm.com/identity/token"
COS_RESOURCE_CRN = "crn:v1:bluemix:public:cloud-object-storage:global:a/574e776671f7408abab5d179ac0aa6c7:0fe39ae2-2f1a-4e42-b18c-6d4c1e996798::" # eg "crn:v1:bluemix:public:cloud-object-storage:global:a/3bf0d9003abfb5d29761c3e97696b71c:d6f04d83-6c4f-4a62-a165-696756d63903::"
cos = ibm_boto3.resource("s3",
    ibm_api_key_id=COS_API_KEY_ID,
    ibm_service_instance_id=COS_RESOURCE_CRN,
    ibm_auth_endpoint=COS_AUTH_ENDPOINT,
    config=Config(signature_version="oauth"),
    endpoint_url=COS_ENDPOINT
)
client = Cloudant("c50bd8d6-cabd-419a-9484-ec2fc5101e2c-bluemix", "1e1c2e03ac0376a1c7174435a75ad92d61a01baec66998ac6db78996eb520a9d", url="https://c50bd8d6-cabd-419a-9484-ec2fc5101e2c-bluemix:1e1c2e03ac0376a1c7174435a75ad92d61a01baec66998ac6db78996eb520a9d@c50bd8d6-cabd-419a-9484-ec2fc5101e2c-bluemix.cloudantnosqldb.appdomain.cloud")
client.connect()
database_name = "smartsecurity"
my_database = client.create_database(database_name)
def multi_part_upload(bucket_name, item_name, file_path):
    try:
        part_size = 1024 * 1024 * 5
        file_threshold = 1024 * 1024 * 15
        transfer_config = ibm_boto3.s3.transfer.TransferConfig(
            multipart_threshold=file_threshold,
            multipart_chunksize=part_size
        )
        with open(file_path, "rb") as file_data:
            cos.Object(bucket_name, item_name).upload_fileobj(
                Fileobj=file_data,
                Config=transfer_config
            )
    except ClientError as be:
        print("CLIENT ERROR: {0}\n".format(be))
    except Exception as e:
        print("Unable to complete multi-part upload: {0}".format(e))
video=cv2.VideoCapture(0)
while True:
    check,frame=video.read()
    gray=cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces=face_classifier.detectMultiScale(gray,1.3,5)
    eyes=eye_classifier.detectMultiScale(gray,1.3,5)
    for(x,y,w,h) in faces:
        cv2.rectangle(frame, (x,y), (x+w,y+h), (127,0,255), 2)
        cv2.imshow('Face detection', frame)
        picname=datetime.datetime.now().strftime("%y-%m-%d-%H-%M-%S")
        cv2.imwrite(picname+".jpg",frame)
        multi_part_upload("techtycoons", picname+".jpg", picname+".jpg")
        json_document={"link":COS_ENDPOINT+"/"+"techtycoons"+"/"+picname+".jpg"}
        new_document = my_database.create_document(json_document)
        if new_document.exists():
            visual_recognition = VisualRecognitionV3(
                '2018-03-19',
                iam_apikey='g2HkZiqZ3dDrwxjIQR0Guj-Cddq70UhtHNnQMN_nPsSN')
            with open(picname+'.jpg', 'rb') as images_file:
                classes = visual_recognition.classify(
                    images_file,
                    threshold='0.6',
                    classifier_ids='animalsandbirds_977755542').get_result()
            #print(json.dumps(classes, indent=2))
            l=json.dumps(classes, indent=2)
            k=json.loads(l)
            p=k['images'][0]['classifiers'][0]['classes'][0]['class']
            print(p)
           
            url = "https://www.fast2sms.com/dev/bulk"
            querystring = {"authorization":"IoHyB4PlVJYumgFxfk0CT87tcihAnRdSqva21QebwKjNOL9G6rxOElgJ3oR0F9BCWSa4HX6MYPeGwcdA","sender_id":"FSTSMS","message":p+" is at the field","language":"english","route":"p","numbers":"9440443739,9440580362"}
            headers = {
                         'cache-control': "no-cache"
            }
            response = requests.request("GET", url, headers=headers, params=querystring)
            print(response.text)
           
    for(ex,ey,ew,eh) in eyes:
        cv2.rectangle(frame, (ex,ey), (ex+ew,ey+eh), (127,0,255), 2)
        cv2.imshow('Face detection', frame)
    Key=cv2.waitKey(1)
    if Key==ord('q'):
        video.release()
        cv2.destroyAllWindows()
        break  
