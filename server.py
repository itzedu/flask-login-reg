from flask import Flask, render_template, redirect, request, flash, session
from flask_bcrypt import Bcrypt
from mysqlconnection import connectToMySQL
import re	# the regex module

# create a regular expression object that we'll use later   
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$') 

app = Flask(__name__)
app.secret_key = "My very secret key that everybody knows"
bcrypt = Bcrypt(app)

@app.route("/ninjas")
def index():
    if not 'user_id' in session:
        flash('Please login first. You are not allowed into my website just yet')
        return redirect('/ninjas/new')
    else:
        mysql = connectToMySQL("dojo-schema")
        all_ninjas = mysql.query_db("SELECT * FROM ninjas;")

        mysql = connectToMySQL("dojo-schema")

        data = {
            "id": session['user_id']
        }

        query = "SELECT id, first_name, last_name FROM ninjas WHERE id = %(id)s;"
        user = mysql.query_db(query, data)[0]

        return render_template("ninjas/index.html", all_ninjas=all_ninjas, user=user)

@app.route("/ninjas/new")
def new_ninja():
    return render_template("ninjas/new.html")

@app.route("/ninjas", methods=["POST"])
def create_ninja():
    errors = False

    if len(request.form['first_name']) < 1:
        errors = True
        flash("First name is required")
    if len(request.form['last_name']) < 1:
        errors = True
        flash("Last name is required")
    if len(request.form['password']) < 1:
        errors = True
        flash("Password is required")
    if not EMAIL_REGEX.match(request.form['email']):
        errors = True
        flash("Email is not in a valid format")

    if errors:
        return redirect('/ninjas/new')
    else:
        # if everything is good. execute the code below
        hashed_password = bcrypt.generate_password_hash(request.form['password'])

        data = { 
            'first_name' : request.form['first_name'],
            'last_name' : request.form['last_name'],
            'email' : request.form['email'],
            'password' : hashed_password
        }

        mysql = connectToMySQL("dojo-schema")
        query = "INSERT INTO ninjas (first_name, last_Name, email, password, created_at, updated_at) VALUES (%(first_name)s, %(last_name)s, %(email)s, %(password)s, NOW(), NOW())"
        mysql.query_db(query, data)

        return redirect("/ninjas")

@app.route("/login", methods=["POST"])
def login():
    mysql = connectToMySQL("dojo-schema")
    query = "SELECT * FROM ninjas WHERE email = %(email)s;"
    potential_user = mysql.query_db(query, request.form)

    if potential_user:
        # found user!
        user = potential_user[0]
        if bcrypt.check_password_hash(user["password"], request.form["password"]):
            session["user_id"] = user["id"]
            return redirect("/ninjas")
        else:
            flash("Invalid Credentials")
            return redirect("/ninjas/new")
    else:
        flash("Invalid Credentials")
        return redirect("/ninjas/new")
    return redirect("/ninjas")


@app.route("/ninjas/delete/<ninja_id>")
def delete_ninja(ninja_id):
    mysql = connectToMySQL("dojo-schema")
    data = {
        "id" : ninja_id,
    }
    query = "DELETE FROM ninjas WHERE id = %(id)s"
    mysql.query_db(query, data)
    return redirect("/ninjas")


if __name__ == "__main__":
    app.run(debug=True)
