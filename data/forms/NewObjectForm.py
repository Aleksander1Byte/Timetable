from flask_wtf import FlaskForm
from wtforms import FileField, StringField, SubmitField, TextAreaField, \
    BooleanField
from wtforms.validators import DataRequired, Length


class NewObjectForm(FlaskForm):
    from main import types, meanings
    name = StringField('Название',
                       validators=[DataRequired(), Length(max=300)])
    region_id = StringField('Номер региона расположения',
                            validators=[DataRequired()])
    meaning_id = StringField(f'ID значения ({meanings})',
                             validators=[DataRequired()])
    type_id = StringField(f'ID типа ({types})', validators=[DataRequired()])
    is_unesco = BooleanField('Находится в ЮНЕСКО')
    description = TextAreaField("Описание")
    video = FileField('Видео')
    picture = FileField("Картинка")
    submit = SubmitField('Загрузить')
