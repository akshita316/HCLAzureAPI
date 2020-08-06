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

# Create the BlobServiceClient object which will be used to create a container client
blob_service_client = BlobServiceClient.from_connection_string(connect_str)

local_path = "./uploads"
# download_path = "./downloads"


@app.route('/')
def landingPage():
    return render_template('LandingPage.html')


@app.route('/downloader', methods=['GET', 'POST'])
def download():
    if request.method == 'GET':
        return "you requested for downloader API"
    if request.method == "POST":
        container_name = request.form['container']
        download_loc = request.form['download path']
        blob_value = request.form.getlist('blob_list')
        for file_name in blob_value:
            blob_client = blob_service_client.get_blob_client(container=container_name, blob=file_name)
            full_path_to_file2 = os.path.join(download_loc, str.replace(
                file_name, '.txt', '_DOWNLOADED.txt'))
            print("\nDownloading blob to " + full_path_to_file2)
            with open(full_path_to_file2, "wb") as my_blob:
                my_blob.writelines([blob_client.download_blob().readall()])
    return str(blob_value)


@app.route('/downloadFile', methods=['GET', 'POST'])
def getDownloadPage():
    if request.method == "GET":
        return render_template("downloadPage.html")

    if request.method == 'POST':

        container_name = request.form['container_var']
        print("\nList blobs in the container")
        container = blob_service_client.get_container_client(container=container_name)
        generator = container.list_blobs()
        arr = []
        for blob in generator:
            # print("\t Blob name: " + blob.name)
            arr.append(blob.name)
        # print(arr)
        return render_template('dropdown.html', var=arr, container=container_name)


@app.route('/uploader', methods=['GET', 'POST'])
def upload_files():
    if request.method == 'GET':
        return render_template('index.html')
    if request.method == 'POST':
        uploaded_file = request.files.getlist("file[]")
        try:
            print("Azure Blob storage v12")

            # Create a unique name for the container
            container_name = "container" + str(uuid.uuid4())

            # Create the container
            blob_service_client.create_container(container_name)

            for file in uploaded_file:
                filename = secure_filename(file.filename)
                # file_extension = filename.rsplit('.', 1)[1]
                print(filename)
                file.save(os.path.join(local_path, filename))

                local_file_name = filename
                upload_file_path = os.path.join(local_path, local_file_name)

                # Create a blob client using the local file name as the name for the blob
                blob_client = blob_service_client.get_blob_client(container=container_name, blob=local_file_name)

                print("\nUploading to Azure Storage as blob:\n\t" + local_file_name)

                # Upload the created file
                with open(upload_file_path, "rb") as data:
                    blob_client.upload_blob(data)

            # List the blobs in the container
            print("\nList blobs in the container")
            container = blob_service_client.get_container_client(container=container_name)
            generator = container.list_blobs()
            arr = []
            for blob in generator:
                print("\t Blob name: " + blob.name)
                arr.append(blob.name)

            return render_template('result.html', var=arr)

        except Exception as ex:
            print('Exception:')
            print(ex)


if __name__ == '__main__':
    app.run(debug=True)
