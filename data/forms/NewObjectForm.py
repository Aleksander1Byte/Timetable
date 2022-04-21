from flask_wtf import FlaskForm
from wtforms import FileField, StringField, SubmitField, TextAreaField, \
    BooleanField, IntegerField, SelectField
from wtforms.validators import DataRequired, Length, NumberRange


class NewObjectForm(FlaskForm):
    from main import types, meanings
    name = StringField('Название',
                       validators=[DataRequired(), Length(max=300)])
    region_id = IntegerField('Номер региона расположения',
                             validators=[DataRequired(),
                                         NumberRange(min=1, max=94)])

    meaning_id = SelectField(f'Значение ({meanings})', choices=meanings.keys(),
                             validators=[DataRequired()])
    type_id = SelectField(f'Тип ({types})', choices=types.keys(),
                          validators=[DataRequired()])
    is_unesco = BooleanField('Находится в ЮНЕСКО')
    description = TextAreaField("Описание")
    video = FileField('Видео')
    picture = FileField("Картинка")
    submit = SubmitField('Загрузить')
