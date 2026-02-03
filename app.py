from flask import Flask, render_template, request, redirect, url_for
from extensions import db
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from datetime import datetime, timedelta
import os
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from models import User, Todo  # adjust import
"""
    Here, flask is the webapplication framework, just like Django for python
    flask_sqlalchemy lets you use SQLite for the database.
"""
app = Flask(__name__)  
app.config['SECRET_KEY'] = 'f9a8c2d7e3b14a9f0c7d2a6b9e5f1c3d'  
basedir = os.path.abspath(os.path.dirname(__file__)) 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'test.db')
db.init_app(app) 
with app.app_context(): 
    db.create_all()
"""
    The basedir and app.config and db is for database configuration
"""
login_manager = LoginManager() 
login_manager.init_app(app) 
login_manager.login_view = "login" # redirect here if not logged in 
@login_manager.user_loader 
def load_user(user_id): 
    return User.query.get(int(user_id))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # check if user exists
        if User.query.filter_by(username=username).first():
            error = "Username already taken" 
            return render_template('register.html', error=error, username=username)
        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    
    return render_template('register.html')
        
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            error = "Invalid Credentials, Try again." 
            return render_template('login.html', error=error, username=username)

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    if request.method == 'POST':
        task_content = request.form['content']
        new_task = Todo(content = task_content, user_id = current_user.id)
        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect(url_for('index'))
        except:
            return 'There was an issue adding your task'
    else:
        tasks = Todo.query.filter_by(user_id = current_user.id).order_by(Todo.date_created).all()
        return render_template("index.html", tasks = tasks)


@app.route('/delete/<int:id>')
def delete(id):
    """
    This part is to to delete stuff. This works like above, so not much to describe.
    """
    task_to_delete = Todo.query.get_or_404(id) #\retrieves the data by the id given

    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return "Error deleting the Task"


@app.route('/completed/<int:id>', methods = ['POST', 'GET'])
def task_completed(id):
    """
    This part is to to delete stuff. This works like above, so not much to describe.
    """
    task = Todo.query.get_or_404(id) #\retrieves the data by the id given

    try:
        task.task_completed = not task.task_completed
        db.session.commit()
        return redirect('/')
    except:
        return "Error deleting the Task"
    
@app.route('/update/<int:id>', methods = ['GET', 'POST'])
def update(id):
    task_to_update = Todo.query.get_or_404(id)
    if request.method == 'POST':
        task_to_update.content = request.form['content']
        try:
            db.session.commit()
            return redirect('/')
        except:
            return 'Update task error'
    else:
        return render_template('update.html', task = task_to_update)


@app.route('/selection', methods=['POST', 'GET'])
def selection():
    filter_option = request.args.get('filter', 'all')  # default to 'all'
    if filter_option == 'today':
        tasks = Todo.query.filter(
            Todo.date_created >= datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        ).filter_by(user_id = current_user.id).order_by(Todo.date_created).all()

    elif filter_option == 'completed':
        tasks = Todo.query.filter_by(user_id = current_user.id, task_completed=True).order_by(Todo.date_created).all()

    elif filter_option == 'pending':
        tasks = Todo.query.filter_by(user_id = current_user.id, task_completed=False).order_by(Todo.date_created).all()

    elif filter_option == 'all':
        tasks = Todo.query.filter_by(user_id=current_user.id).order_by(Todo.date_created).all()

    return render_template("index.html", tasks=tasks, current_filter=filter_option)

@app.route('/api/completed/<int:id>', methods=['POST'])
def api_task_completed(id):
    task = Todo.query.get_or_404(id)
    task.task_completed = not task.task_completed
    db.session.commit()
    return {"success": True, "completed": task.task_completed}

if __name__ == "__main__":
    app.run(debug=True, port=5000)