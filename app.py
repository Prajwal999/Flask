from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
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
    date_created = db.Column(db.DateTime, default = datetime.timezone.utc)

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
    task_to_delete = Todo.query.get_or_404(id) #Takes retrieves the data by the id given

    try:
        db.session.delete(task_to_delete)
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

if __name__ == "__main__":
    app.run(debug=True)