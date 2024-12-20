from flask import Flask, render_template, redirect, url_for, request, flash, session    
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt
from sqlalchemy.dialects.sqlite import JSON  
from werkzeug.utils import secure_filename
import secrets


app = Flask(__name__)
app.secret_key = secrets.token_urlsafe(16)  
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads/'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)
    
class Album(db.Model):
    id = db.Column(db.Integer, primary_key=True)  
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True) 
    release_year = db.Column(db.Integer, nullable=True) 
    cover_image = db.Column(db.String(300), nullable=True)  
    songs = db.Column(JSON, nullable=True)
    ranking = db.Column(db.Integer, nullable=True)  


@app.route('/')
def home():
    top_albums = Album.query.order_by(Album.ranking.asc()).limit(4).all()
    return render_template('index.html', albums=top_albums)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/history')
def history():
    return render_template('history.html')

@app.route('/create_album', methods=['GET', 'POST'])
@login_required
def create_album():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        songs = request.form['songs']
        release_year = request.form['release_year']
        ranking = request.form['ranking']

        cover_image = request.files['cover_image']
        cover_image_filename = secure_filename(cover_image.filename)
        cover_image_filepath = app.config['UPLOAD_FOLDER'] + cover_image_filename
        cover_image.save(cover_image_filepath)

        new_album = Album(
            title=title,
            description=description,
            cover_image=cover_image_filepath,
            songs=songs,
            release_year=release_year,
            ranking=ranking
        )

        db.session.add(new_album)
        db.session.commit()

        return redirect(url_for('home'))  

    return render_template('create_album.html')  


@app.route('/albums')
def albums():
    all_albums = Album.query.all()
    return render_template('albums.html', albums=all_albums)

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
    session['user_id'] = None
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

@app.route('/albums_list', methods=['GET'])
@login_required  
def albums_list():
    albums = Album.query.all() 
    return render_template('albums_list.html', albums=albums)

@app.route('/delete_album/<int:album_id>', methods=['POST'])
@login_required  
def delete_album(album_id):
    album = Album.query.get_or_404(album_id) 
    db.session.delete(album) 
    db.session.commit()  
    flash('Album deleted successfully!', 'success')  
    return redirect(url_for('albums_list')) 

@app.route('/album/<int:album_id>', methods=['GET'])
def album(album_id):
    album = Album.query.get_or_404(album_id)  
    if not album:
        return "Album not found", 404
    return render_template('album.html', album=album)

@app.route('/edit_album/<int:album_id>', methods=['GET', 'POST'])
@login_required
def edit_album(album_id):
    album = Album.query.get_or_404(album_id)

    if request.method == 'POST':
        album.title = request.form['title']
        album.description = request.form['description']
        album.songs = request.form['songs']
        album.release_year = request.form['release_year']
        album.ranking = request.form['ranking']

        cover_image = request.files.get('cover_image')
        if cover_image:
            cover_image.save(f"static/uploads/{cover_image.filename}")
            album.cover_image = f"static/uploads/{cover_image.filename}"

        db.session.commit()

        return redirect(url_for('albums_list'))  

    return render_template('edit_album.html', album=album)

if __name__ == '__main__':
    with app.app_context():
        db.create_all() 
    app.run(port=5000, debug=True)


