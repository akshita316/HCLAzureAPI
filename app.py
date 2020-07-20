
import os, uuid
from flask import Flask, request, render_template
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from werkzeug.utils import secure_filename
from flask import send_file

app = Flask(__name__)

# Retrieve the connection string for use with the application. The storage
# connect_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
connect_str = 'DefaultEndpointsProtocol=https;AccountName=fhirtestingstore;AccountKey=E/bxDh1TGeGnkNT7Y2OVEzE2zmZgpkQ5t9F0suURT7f3FF0kBW4Yu+afr/q28gz9THNbm3zSwfoTeZUXW99vuQ==;EndpointSuffix=core.windows.net'
# print(connect_str)

local_path = "./uploads"

@app.route('/')
def landingPage():
    return render_template('LandingPage.html')

#
# @app.route('/uploader',meth)
# def upload_file():
#     return render_template('index.html')

@app.route('/downloadFile')
def index():
    path = "FileTOUpload.xlsx"
    return send_file(path, as_attachment=True)

@app.route('/uploader', methods=['GET','POST'])
def upload_files():
    if request.method == 'GET':
        return render_template('index.html')
    if request.method == 'POST':
        file = request.files['file']
        filename = secure_filename(file.filename)
        file_extension = filename.rsplit('.', 1)[1]
        print(file_extension)
        file.save(os.path.join(local_path, filename))

        local_file_name = filename
        upload_file_path = os.path.join(local_path, local_file_name)
        try:
            print("Azure Blob storage v12")
            # Create the BlobServiceClient object which will be used to create a container client
            blob_service_client = BlobServiceClient.from_connection_string(connect_str)

            # Create a unique name for the container
            container_name = "container" + str(uuid.uuid4()) + file_extension

            # Create the container
            container_client = blob_service_client.create_container(container_name)

            # Create a blob client using the local file name as the name for the blob
            blob_client = blob_service_client.get_blob_client(container=container_name, blob=local_file_name)

            print("\nUploading to Azure Storage as blob:\n\t" + local_file_name)

            # Upload the created file
            with open(upload_file_path, "rb") as data:
                blob_client.upload_blob(data)

        except Exception as ex:
            print('Exception:')
            print(ex)
    return 'file uploaded successfully'


if __name__ == '__main__':
    app.run(debug=True)