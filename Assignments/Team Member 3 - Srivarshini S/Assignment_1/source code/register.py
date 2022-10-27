from flask import Flask,render_template,request 
app=Flask(__name__)
@app.route("/") 
def home():
 return render_template("register.html") 
@app.route("/register",methods=["POST","GET"]) 
def register():
 if request.method=="POST": 
   username=request.form.get('username') 
   email=request.form.get('email') 
   phone=request.form.get('phone')
   return render_template("home.html",username=username,email=email,phone=phone)

if __name__ == '__main__':
    app.run(debug=True)
