import os.path

from flask import Flask, render_template
from flask_login import (LoginManager, current_user, login_required,
                         login_user, logout_user)
from werkzeug.utils import redirect

from data.db_session import create_session, global_init
from data.forms.LoginForm import LoginForm
from data.forms.RegisterForm import RegisterForm
from data.users import User

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'
app.config['UPLOAD_FOLDER'] = 'static/media/'
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 5120  # 5 GB
login_manager = LoginManager()
login_manager.init_app(app)
global_init('db/database.db')

DEBUG = True


@app.route('/')
def main():
    return render_template('main_page.html', title='Timetable',
                           current_user=current_user)


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
        user = db_sess.query(User).filter(
            User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form, current_user=current_user)
    return render_template('login.html', title='Авторизация', form=form,
                           current_user=current_user)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают",
                                   current_user=current_user)
        db_sess = create_session()
        if db_sess.query(User).filter(
                (User.email == form.email.data) |
                (User.nickname == form.nickname.data)).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть",
                                   current_user=current_user)
        user = User(
            nickname=form.nickname.data,
            email=form.email.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form,
                           current_user=current_user)


if __name__ == '__main__':
    if DEBUG:
        PORT = 5050
        HOST = '127.0.0.1'
    else:
        PORT = int(os.environ.get("PORT", 5000))
        HOST = '0.0.0.0'
    ADDRESS = HOST + ':' + str(PORT)
    app.run(host=HOST, port=PORT)
