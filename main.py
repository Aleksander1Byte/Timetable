import os.path
from functools import wraps
from random import shuffle

from flask import Flask, render_template, request
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from flask_restful import Api
from requests import delete
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import abort
from werkzeug.utils import redirect

import data.forms.NewObjectForm as nof
from data.db_session import global_init
from data.forms.LoginForm import LoginForm
from data.forms.RegisterForm import RegisterForm
from data.meaning import Meaning, Type
from data.resources.objects_resources import *
from data.users import User

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'
app.config['UPLOAD_FOLDER'] = 'static/media/'
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 5120  # 5 GB
login_manager = LoginManager()
login_manager.init_app(app)
global_init('db/database.db')

api = Api(app)
api.add_resource(ObjectsListResource, '/api/objects')
api.add_resource(ObjectsResource, '/api/objects/<int:object_id>')

types = {1: 'Памятник', 2: 'Ансамбль', 3: 'Достопримечательное место'}
meanings = {1: 'Местное', 2: 'Региональное', 3: 'Федеральное'}

DEBUG = True


@app.route('/')
def main():
    db_sess = create_session()
    objects = db_sess.query(Object).all()
    shuffle(objects)
    return render_template(
        'main_page.html',
        title='Timetable',
        current_user=current_user,
        objects=objects[:8],
    )


def admin_only(func):
    @wraps(func)
    def check(*args, **kwargs):
        if current_user is None:
            abort(405)
        if not current_user.is_admin:
            abort(405)
        return func(*args, **kwargs)

    return check


@app.route('/search', methods=['GET'])
def search():
    db_sess = create_session()
    query = request.args.get("search_query")
    obj = db_sess.query(Object).filter(Object.name.like(f'%{query}%')).first()
    if obj is None:
        return redirect('/')
    return redirect(f'/obj/{obj.id}')


@app.route('/super_ultra_mega_secret')
@login_required
def get_admin():
    db_sess = create_session()
    user = db_sess.query(User).get(current_user.id)
    if user.is_admin:
        user.is_admin = False
    else:
        user.is_admin = True
    db_sess.commit()
    return f'Удивительно! Ваши права перевернулись на {user.is_admin}'


@app.route('/list')
def full_list():
    db_sess = create_session()
    objects = db_sess.query(Object).all()
    context = {'objects': objects}
    return render_template('full_list.html', current_user=current_user, **context)


@app.route('/obj/delete/<int:id>', methods=['GET', 'POST'])
@admin_only
def delete_object(id):
    delete(f'http://{ADDRESS}/api/objects/{id}')
    return redirect('/')


@app.route('/obj/<int:id>', methods=['GET', 'POST'])
def view_object(id):
    db_sess = create_session()
    obj = db_sess.query(Object).get(id)
    if obj is None:
        abort(404)
        return
    context = {'obj': obj}
    if request.method == 'POST':
        if 'comment' in request.form:  # комментарий
            text = request.form.get('comment')
            if text is None or text == '':
                return render_template(
                    'view_object.html', current_user=current_user, **context
                )
            comment = Comments(creator_id=current_user.id, post_id=id, text=text)
            db_sess.add(comment)
            db_sess.commit()
        else:  # удаление комментария
            comment_id = list(request.form.keys())[0]
            comment = db_sess.query(Comments).get(comment_id)
            db_sess.delete(comment)
            db_sess.commit()

    return render_template('view_object.html', current_user=current_user, **context)


@app.route('/obj/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_only
def edit_object(id):
    db_sess = create_session()
    obj = db_sess.query(Object).get(id)
    form = nof.NewObjectForm()
    if request.method == 'GET':
        form.name.data = obj.name
        form.region_id.data = obj.region_id
        form.description.data = obj.description
        form.is_unesco.data = obj.is_unesco
    if form.validate_on_submit():
        delete(f'http://{ADDRESS}/api/objects/{id}')
        video = request.files['video'] if 'video' in request.files else None
        picture = request.files['picture'] if 'picture' in request.files else None
        db_sess = create_session()
        obj = Object(
            id=id,
            name=form.name.data,
            description=form.description.data.capitalize(),
            region_id=form.region_id.data,
            meaning_id=form.meaning_id.data,
            type_id=form.type_id.data,
            is_unesco=form.is_unesco.data,
        )
        obj.set_paths(video, picture)
        db_sess.add(obj)
        db_sess.commit()
        return redirect(f'/obj/{id}')
    return render_template(
        'new_object.html',
        title='Timetable - edit',
        current_user=current_user,
        form=form,
        obj=obj,
    )


@app.route('/add', methods=['GET', 'POST'])
@login_required
@admin_only
def add_object():
    form = nof.NewObjectForm()
    if form.validate_on_submit():
        video = request.files['video'] if 'video' in request.files else None
        picture = request.files['picture'] if 'picture' in request.files else None
        db_sess = create_session()
        obj = Object(
            name=form.name.data,
            description=form.description.data.capitalize(),
            region_id=form.region_id.data,
            meaning_id=form.meaning_id.data,
            type_id=form.type_id.data,
            is_unesco=form.is_unesco.data,
        )

        obj.set_paths(video, picture)

        db_sess.add(obj)
        db_sess.commit()
        return redirect('/')
    return render_template(
        'new_object.html',
        title='Timetable - upload',
        current_user=current_user,
        form=form,
        obj=None,
    )


@login_manager.user_loader
def load_user(user_id):
    db_sess = create_session()
    return db_sess.query(User).get(user_id)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template(
            'login.html',
            message="Неправильный логин или пароль",
            form=form,
            current_user=current_user,
        )
    return render_template(
        'login.html', title='Авторизация', form=form, current_user=current_user
    )


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template(
                'register.html',
                title='Регистрация',
                form=form,
                message="Пароли не совпадают",
                current_user=current_user,
            )
        db_sess = create_session()
        if (
            db_sess.query(User)
            .filter(
                (User.email == form.email.data) | (User.nickname == form.nickname.data)
            )
            .first()
        ):
            return render_template(
                'register.html',
                title='Регистрация',
                form=form,
                message="Такой пользователь уже есть",
                current_user=current_user,
            )
        user = User(nickname=form.nickname.data, email=form.email.data)
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template(
        'register.html', title='Регистрация', form=form, current_user=current_user
    )


def setup_db():
    db_sess = create_session()
    try:
        for key_t in types:
            new_type = Type(id=key_t, text=types[key_t])
            db_sess.add(new_type)

        for key_m in meanings:
            new_meaning = Meaning(id=key_m, text=meanings[key_m])
            db_sess.add(new_meaning)

        db_sess.commit()
    except IntegrityError:
        print('База данных уже наполнена стандатрными значениями')
        return


if __name__ == '__main__':
    setup_db()
    if DEBUG:
        PORT = 5050
        HOST = '127.0.0.1'
    else:
        PORT = int(os.environ.get("PORT", 5000))
        HOST = '0.0.0.0'
    ADDRESS = HOST + ':' + str(PORT)
    app.run(host=HOST, port=PORT)
