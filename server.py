from flask import Flask, request, redirect, render_template, session, flash
from mysqlconnection import MySQLConnector
import re
import md5 
import os, binascii

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
app = Flask(__name__)
app.secret_key = "ThisIsSecret!"
mysql = MySQLConnector(app,'wall')

@app.route('/')
def index():                         # run query with query_db()
    return render_template('index.html') # pass data to our template




@app.route('/registration', methods=['POST'])
def createuser():
	password = request.form['password']
	salt= binascii.b2a_hex(os.urandom(15))
	hashed_pw = md5.new(password + salt).hexdigest()
	data = {
             'email': request.form['email'],
             'first_name': request.form['first_name'],
             'last_name': request.form['last_name'],
             'password': hashed_pw,
             'salt': salt
           }
	if len(request.form['email']) < 1:
		flash("You have to insert an e-mail")
	elif len(request.form['first_name']) < 1 or len(request.form['last_name']) < 1:
		flash("You forgot to put in a Name!")
	elif len(request.form['password']) < 1:
		flash("You need to put in a password!") 
	elif len(request.form['passwordconfirm']) < 1:
		flash("You need to confirm your password!") 
	elif not EMAIL_REGEX.match(request.form['email']):
		flash("Invalid Email Address!")
	elif mysql.query_db("SELECT * from users WHERE email LIKE :email", data):
		flash("e-mail already exists!")
	elif request.form['password'] != request.form['passwordconfirm']:
		flash("Password and Password Confirmation must be the same!")
        # Write query as a string. Notice how we have multiple values
    # we want to insert into our query.
    	query = "INSERT INTO users (first_name, last_name, email, password, salt, created_at, updated_at) VALUES (:first_name, :last_name, :email, :password, :salt,  NOW(), NOW())"
    # We'll then create a dictionary of data from the POST data received.

    # Run query, with dictionary values injected into the query.
    	mysql.query_db(query, data)
    	print len(request.form['email']), len(request.form['first_name']), len(request.form['last_name']), len(request.form['password']), len(request.form['passwordconfirm'])
        print len(request.form['password']) , len(request.form['passwordconfirm'])
   	return redirect('/')




@app.route('/login', methods=['POST'])
def login():
	email_id = request.form['email']
	password = request.form['password']
	query = "SELECT * FROM users WHERE email = :email"
	data = {'email': email_id,
			'password': password}
	login = mysql.query_db(query, data)
	session['id'] = login[0]['id']
	session['first_name'] = login[0]['first_name']
	session['last_name'] = login[0]['last_name']
	session['first_name'] = str(session['first_name'])
	session['last_name'] = str(session['last_name'])
	if len(login) != 0:
		encrypted_password = md5.new(password + login[0]['salt']).hexdigest()
		if login[0]['password'] == encrypted_password:
			return redirect('/wall')
		else:
			flash("Invalid Password!")
	else:
		flash("Invalid E-mail!")
	print session['first_name'], session['last_name']
	
	return redirect('/wall')




# THE WALL THE WALL THE WALL THE WALL THE WALL THE WALL 

@app.route('/wall')
def wall(): 
	query2 = "SELECT users.first_name, users.last_name, messages.message, messages.created_at, messages.id  FROM users JOIN messages ON users.id=messages.user_id"
	query = "SELECT  users.first_name, users.last_name, comments.comment, comments.created_at, comments.id, messages.id, comments.message_id  FROM users JOIN comments on comments.user_id = users.id JOIN messages on comments.message_id = messages.id"
	messages = mysql.query_db(query2)
	comments = mysql.query_db(query)
	return render_template('wall.html', all_messages=messages, all_comments=comments)



@app.route('/message', methods=['POST'])
def createmsg():
    # Write query as a string. Notice how we have multiple values
    # we want to insert into our query.
    query = "INSERT INTO messages (user_id, message, created_at) VALUES (:user_id, :message, NOW())"
    # We'll then create a dictionary of data from the POST data received.
    data = {
    		'user_id': session['id'],
            'message': request.form['message'],
           }
    # Run query, with dictionary values injected into the query.
    mysql.query_db(query, data)

    return redirect('/wall')


@app.route('/remove_message/<message_id>', methods=['POST'])
def delete(message_id):
    message_id = request.form['messagedel']
    query = "DELETE FROM messages WHERE messages.id = :message"
    data = {'message': message_id}
    mysql.query_db(query, data)
    return redirect('/wall')
    


@app.route('/comment', methods=['POST'])
def createcomment():
    # Write query as a string. Notice how we have multiple values
    # we want to insert into our query.
    query = "INSERT INTO comments (user_id, message_id, comment, created_at) VALUES (:user_id, :message_id, :comment, NOW())"
    # We'll then create a dictionary of data from the POST data received.
    data = {
             'comment': request.form['comment'],
             'user_id': session['id'],
             'message_id': request.form['message_id']
           }
    # Run query, with dictionary values injected into the query.
    mysql.query_db(query, data)
    
    return redirect('/wall')

@app.route('/logout', methods=['POST'])
def logout():
	session.clear()
	return redirect('/')








app.run(debug=True)