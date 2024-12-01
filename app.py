from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a secure secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"

# User model for authentication
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)
    
class Album(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Home Route
@app.route('/')
def home():
    return render_template('index.html')

# About Route
@app.route('/about')
def about():
    return render_template('about.html')

# History Route
@app.route('/history')
def history():
    return render_template('history.html')

# Albums Route
@app.route('/albums')
def albums():
    albums = Album.query.all()
    return render_template('albums.html', albums=albums)

# Add Login System Routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('home'))
        flash('Invalid credentials.', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('home'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(username=username, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Account created successfully! You can now log in.', 'success')
        return redirect(url_for('login'))
    return render_template('signup.html')

# Protect Album Management Routes with Login Required
@app.route('/album/new', methods=['GET', 'POST'])
@login_required
def new_album():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        new_album = Album(title=title, description=description)
        db.session.add(new_album)
        db.session.commit()
        flash('Album created successfully!', 'success')
        return redirect(url_for('albums'))
    return render_template('new_album.html')

@app.route('/album/<int:album_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_album(album_id):
    album = Album.query.get_or_404(album_id)
    if request.method == 'POST':
        album.title = request.form['title']
        album.description = request.form['description']
        db.session.commit()
        flash('Album updated successfully!', 'success')
        return redirect(url_for('albums'))
    return render_template('edit_album.html', album=album)

@app.route('/album/<int:album_id>/delete', methods=['POST'])
@login_required
def delete_album(album_id):
    album = Album.query.get_or_404(album_id)
    db.session.delete(album)
    db.session.commit()
    flash('Album deleted successfully!', 'success')
    return redirect(url_for('albums'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Creates tables if they don't exist
    app.run(debug=True)
