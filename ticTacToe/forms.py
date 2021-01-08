from django import forms
from django.core.exceptions import ValidationError

from ticTacToe.models import Game


class PageCountForm(forms.Form):
    page = forms.IntegerField(min_value=1, required=False)
    count = forms.IntegerField(min_value=1, max_value=100, required=False)

    def clean_page(self):
        return int(self.data.get('page', 1))

    def clean_count(self):
        return int(self.data.get('count', 10))


class GameForm(forms.ModelForm):
    owner_color = forms.RegexField(r'^#[0-9a-fA-F]{6}$')

    def clean(self):
        cleaned_data = super(GameForm, self).clean()
        width = cleaned_data.get('width', 0)
        height = cleaned_data.get('height', 0)
        win_threshold = cleaned_data.get('win_threshold', 0)

        if win_threshold > width or win_threshold > height:
            raise ValidationError(
                "Win threshold should not be more than width and height"
            )

        return cleaned_data

    class Meta:
        model = Game
        fields = ['width', 'height', 'win_threshold', 'owner_color']


class JoinForm(forms.Form):
    color = forms.RegexField(r'^#[0-9a-fA-F]{6}$')


class TurnForm(forms.Form):
    i = forms.IntegerField(min_value=0, max_value=99)
    j = forms.IntegerField(min_value=0, max_value=99)


class HistorySuffixForm(forms.Form):
    start_index = forms.IntegerField(min_value=0, max_value=9999)


class MyGamesForm(forms.Form):
    finished = forms.NullBooleanField()
