from flask import Flask, request, render_template, abort
from flask_sqlalchemy import SQLAlchemy

import os, io, time, random, string


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
db = SQLAlchemy(app)




@app.template_filter()
def elapsedtime(timestamp):
    timestamp = time.time() - timestamp
    if timestamp > (3600 * 24):
        return str(int(timestamp // (3600 * 24))) + " days"
    elif timestamp > 3600:
        return str(int(timestamp // 3600)) + " hours"
    elif timestamp > 60:
        return str(int(timestamp // 60)) + " minutes"
    else:
        return str(timestamp) + " seconds"




def uuid():
    return ''.join([random.choice(string.ascii_letters+string.digits+'-_') for ch in range(12)])


#for somewhat reason, Flask.redirect is not working!
def redirect(url, code):
    return f'<meta http-equiv="refresh" content="0;URL=\'{url}\'" />'



class Code(db.Model):
    uuid = db.Column(db.String(12), primary_key=True, unique=True)
    code = db.Column(db.String(524288), nullable=False)
    lang = db.Column(db.String(8), nullable=False)
    note = db.Column(db.String(256), nullable=True)
    timestamp = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return '<Code %r>' % self.uuid





@app.route("/")
def home():
    recents = (Code.query.order_by(Code.timestamp.desc()).limit(10).all() or [])
    
    return render_template("home.html", recents=recents)
  


@app.route("/code/delete/")
def deleteCode():
    return ""



@app.route("/code/update/")
def updateCode():
    return ""



@app.route("/code/")
def codeList():
    codes = (Code.query.order_by(Code.timestamp.desc()).all() or [])
    return render_template("code_list.html", codes=codes)



@app.route("/code/new/", methods=["GET", "POST"])
def addCode():

    if request.method == "POST":
        note = request.form.get("note")
        code = (request.form.get("code") or request.files.get("file").read().decode("utf-8") or None)
        lang = (request.form.get("lang") or request.files.get("file").filename.split(".")[-1] or "plaintext")
        
        if not code:
            return "Either a code string or a file must be sent. Found None.", 400
            
        if len(list(code)) > 5120:
            return "Code size is larger than 5KB.", 400
        
        code_instance = Code(uuid=uuid(), code=code, lang=lang, note=note, timestamp=time.time())
        db.session.add(code_instance)
        db.session.commit()
        
        return redirect(f"/view/{code_instance.uuid}", 201)
        
    
    if request.method == "GET":
        return render_template("add_code.html")
  
  

@app.route("/view/<codeid>/")
def codeView(codeid):
    code_instance = Code.query.filter_by(uuid=codeid).first()
    
    if code_instance == None:
      abort(404)
    
    return render_template("code.html", code=code_instance)




@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html')





if __name__ == "__main__":
    app.run("0.0.0.0", (os.environ.get("PORT") or 3000), debug=True)