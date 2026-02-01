from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import os
"""
    Here, flask is the webapplication framework, just like Django for python
    flask_sqlalchemy lets you use SQLite for the database.
"""
app = Flask(__name__)     #We created the instance of Flask called app
basedir = os.path.abspath(os.path.dirname(__file__)) 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'test.db')
db = SQLAlchemy(app)
"""
    The basedir and app.config and db is for database configuration
"""

#A table called Todo is made in the database
class Todo(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    content = db.Column(db.String(200), nullable = False)
    date_created = db.Column(db.DateTime, default = datetime.now())
    task_completed = db.Column(db.Boolean, default = False)

    def __repr__(self):
    # __repr__ → defines how the object is represented when printed. Example: <Task 1>.
        return '<Task %r>' % self.id

# Here, route() is a decorator used in Flask to tell Flask which URL to trigger
#We added methods to accept both GET and POST request. 
@app.route('/', methods = ['POST', 'GET'])
def index():
    #Here, code is divided to POST and GET Methods
    #If the method is POST, then it will add new contents to the database
    if request.method == 'POST':
        task_content = request.form['content'] #grabs the text input from the form field named "content"
        new_task = Todo(content = task_content) #creates a new todo object, meaning it creates a new row for new task

        try:
            db.session.add(new_task) #adds the new_task to the database session
            db.session.commit() #saves the added object permanently
            return redirect('/') #reloads the homepage to show the updated list
        except:
            return 'There was an Issue adding your Thing'
    #Here, the else represents the GET part.
    else:
        tasks = Todo.query.order_by(Todo.date_created).all() #This fetches all the database contents
        return render_template("index.html", tasks = tasks) #This passes tasks to HTML Template to display it


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
        ).order_by(Todo.date_created).all()

    elif filter_option == 'completed':
        tasks = Todo.query.filter_by(task_completed=True).order_by(Todo.date_created).all()

    elif filter_option == 'pending':
        tasks = Todo.query.filter_by(task_completed=False).order_by(Todo.date_created).all()

    elif filter_option == 'all':
        tasks = Todo.query.order_by(Todo.date_created).all()

    return render_template("index.html", tasks=tasks, current_filter=filter_option)

@app.route('/api/completed/<int:id>', methods=['POST'])
def api_task_completed(id):
    task = Todo.query.get_or_404(id)
    task.task_completed = not task.task_completed
    db.session.commit()
    return {"success": True, "completed": task.task_completed}

if __name__ == "__main__":
    app.run(debug=True, port=5000)