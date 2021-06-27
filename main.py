from datetime import datetime
import os

from flask import Flask, render_template, request, redirect, url_for, session
from passlib.hash import pbkdf2_sha256

from model import Task, User

app = Flask(__name__)
#app.secret_key = b'\x9d\xb1u\x08%\xe0\xd0p\x9bEL\xf8JC\xa3\xf4J(hAh\xa4\xcdw\x12S*,u\xec\xb8\xb8'
app.secret_key = os.environ.get('SECRET_KEY').encode()

@app.route('/all')
def all_tasks():
    return render_template('all.jinja2', tasks=Task.select())

@app.route('/create', methods=['GET', 'POST'])
def create_task():
    if 'username' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        new_task = Task(name=request.form['name'])
        new_task.save()
        return redirect(url_for('all_tasks'))
    return render_template('create.jinja2')

@app.route('/login', methods=['GET', 'POST'])
def login():
    # If the user is attempting to submit the login form (method is POST)
    #    Find a user from the database that matches the username provided in the form submission
    #    If you find such a user and their password matches the provided password:
    #        Then log the user in by settings session['username'] to the users name
    #        And redirect the user to the list of all tasks
    #    Else:
    #        Render the login.jinja2 template and include an error message 
    # Else the user is just trying to view the login form
    #    so render the login.jinja2 template
    if request.method == 'POST':
        user = User.select().where(User.name == request.form['name']).get()
        if user and pbkdf2_sha256.verify(request.form['password'], user.password):
            session['username'] = user.name
            return redirect(url_for('all_tasks'))
        return render_template('login.jinja2', error="Wrong username or password")
    return render_template('login.jinja2')
@app.route('/incomplete', methods=['GET', 'POST'])
def incomplete_tasks():
    # If the visitor is not logged in as a user:
        # Then redirect them to the login page
    if 'username' not in session:
        return redirect(url_for('login'))

    # If the request method is POST
        # Then retrieve the username from the session and find the associated user
        # Retrieve the task_id from the form submission and use it to find the associated task
        # Update the task to indicate that it has been completed at datetime.now() by the current user
    # Retrieve a list of all incomplete tasks
    # Render the incomplete.jinja2 template, injecting in the list of all incomplete tasks
    if request.method == 'POST':
        user = User.select().where(User.name == session['username']).get()
        Task.update(performed = datetime.now(), performed_by = user)\
            .where(Task.id == request.form['task_id'])\
            .execute()
    return render_template('incomplete.jinja2', tasks=Task.select().where(Task.performed.is_null()))
        
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)