from flask import Flask,render_template

app = Flask(__name__)


@app.route('/')
def homePage():
    return render_template('index.html')

# @app.route('/UploadFile',methods="PUT")
# def uploadFile():
#

if __name__ == '__main__':
    app.run()
