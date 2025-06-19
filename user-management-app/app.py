from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-for-testing')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://postgres:postgres@db:5432/usermanagement')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    
    def __repr__(self):
        return f'<User {self.username}>'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('user_login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.password == password:  # In production, use proper password hashing
            login_user(user)
            return redirect(url_for('user_page'))
        else:
            flash('Invalid username or password')
    
    return render_template('user_login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/user')
@login_required
def user_page():
    users = User.query.all()
    return render_template('user_page.html', users=users)

@app.route('/user/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_user(id):
    user = User.query.get_or_404(id)
    
    if request.method == 'POST':
        user.username = request.form.get('username')
        user.email = request.form.get('email')
        
        db.session.commit()
        flash('User updated successfully')
        return redirect(url_for('user_page'))
    
    return render_template('edit_user.html', user=user)

@app.route('/user/add', methods=['GET', 'POST'])
@login_required
def add_user():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        
        new_user = User(username=username, password=password, email=email)
        db.session.add(new_user)
        db.session.commit()
        
        flash('User added successfully')
        return redirect(url_for('user_page'))
    
    return render_template('edit_user.html', user=None)

@app.route('/user/delete/<int:id>')
@login_required
def delete_user(id):
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    
    flash('User deleted successfully')
    return redirect(url_for('user_page'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', debug=True)
