from flask import render_template, redirect, url_for, request
from application import app, db,bcrypt
from application.models import Films, Users, Collection
from application.forms import FilmsForm, CollectionForm, RegistrationForm, LoginForm, UpdateAccountForm, EditFilmsForm
from flask_login import login_user, current_user, logout_user, login_required

@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html', title='Home Page')

@app.route('/about')
def about():
    return render_template('about.html', title='About Page')

@app.route('/catalogue', methods=['GET', 'POST'])
def catalogue():
    filmData = Films.query.all()
    return render_template('catalogue.html', title='catalogue Page', films=filmData)

@app.route('/catalogue/<film>/add', methods=['GET','POST'])
def add_collection(film):
    userID = int(current_user.id)
    ownData = Collection.query.filter_by(user_id = userID).all()
    filmOwn = Collection(
        user_id = userID,
        films_id = film
    )
    db.session.add(filmOwn)
    db.session.commit()
    return redirect(url_for('collection'))


@app.route('/add_movie', methods=['GET', 'POST'])
@login_required
def add_movie():
    form = FilmsForm()
    if form.validate_on_submit():
        filmData = Films(
                title=form.title.data,
                year=form.year.data,
                age=form.age.data,
                director=form.director.data,
                genre=form.genre.data,
                formating=form.formating.data,
                description=form.description.data,
                code=form.code.data
        )

        db.session.add(filmData)
        db.session.commit()

        return redirect(url_for('home'))
    else:
        print(form.errors)

    return render_template('add_movie.html', title='add_movie', form=form)

@app.route('/catalogue/<film>/edit_movie', methods=['GET', 'POST'])
@login_required
def edit_movie(film):
    form = EditFilmsForm()
    currentMovie = Films.query.filter_by(id=film).first()
    print("mOVIE CONTENT: ", currentMovie)
    if form.validate_on_submit():
        currentMovie.title.data = form.title.data
        currentMovie.year.data = form.year.data
        currentMovie.age.data = form.age.data
        currentMovie.director.data = form.director.data
        currentMovie.genre.data = form.genre.data
        currentMovie.formating.data = form.formating.data
        currentMovie.description.data = form.description.data
        currentMovie.code.data = form.code.data
        db.session.commit()
        return redirect(url_for('collection'))
    elif request.method =='GET':
        form.title.data = currentMovie.title.data 
        form.year.data = currentMovie.year.data
        form.age.data = currentMovie.age.data
        form.director.data = currentMovie.director.data
        form.genre.data = currentMovie.genre.data
        form.formating.data = currentMovie.formating.data
        form.description.data = currentMovie.description.data
        form.code.data = currentMovie.code.data
    return render_template('edit_movie.html', title='Edit Page', form=form)

@app.route('/collection', methods=['GET', 'POST'])
@login_required
def collection():
    userID = int(current_user.id)
    myFilms = Collection.query.filter_by(user_id = userID).all()
    
    return render_template('collection.html', title='collection', films=myFilms)

@app.route('/collection/<film>/delete', methods=['GET', 'POST'])
@login_required
def remove_collection(film):
    userID = int(current_user.id)
    myFilms = Collection.query.filter_by(user_id=userID).filter_by(films_id=film)
    for film in myFilms:
        db.session.delete(film)
    db.session.commit()
    return redirect(url_for('collection'))

#-----------------------------------------------------------------------------------------------
#--- USERS -------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hash_pw=bcrypt.generate_password_hash(form.password.data)

        user=Users(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data, 
            password=hash_pw
            )

        db.session.add(user)
        db.session.commit()

        return redirect(url_for('catalogue'))
    return render_template('register.html', title='Register', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(
                user,
                remember=form.remember.data
            )
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            else:
                return redirect(url_for('home'))

    return render_template('login.html', title='Login Page', form=form)

@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.email = form.email.data
        db.session.commit()
        return redirect(url_for('account'))
    elif request.method =='GET':
        form.first_name =  current_user.first_name
        form.last_name = current_user.last_name
        form.email = current_user.email
    return render_template('account.html', title='Account Page', form=form)

@app.route('/account/delete', methods=['GET', 'POST'])
@login_required
def account_delete():
    user = current_user.id
    account = Users.query.filter_by(id=user).first()
    owned = Collection.query.filter_by(user_id=user).all()
    logout_user()
    for films in owned:
        db.session.delete(films)
    db.session.delete(account)
    db.session.commit()
    return redirect(url_for('register'))
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hash_pw=bcrypt.generate_password_hash(form.password.data)
        user=Users(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data, 
            password=hash_pw
            )

        db.session.add(user)
        db.session.commit()

        return redirect(url_for('catalogue'))
    return render_template('register.html', title='Register', form=form)

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    return redirect(url_for('login'))

#-----------------------------------------------------------------------------------------------
#--- USERS - END -------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------