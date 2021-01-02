from django import forms


class PageCountForm(forms.Form):
    page = forms.IntegerField(min_value=1, required=False)
    count = forms.IntegerField(min_value=1, max_value=100, required=False)

    def clean_page(self):
        return int(self.data.get('page', 1))

    def clean_count(self):
        return int(self.data.get('count', 10))


class GameForm(forms.Form):
    width = forms.IntegerField(min_value=1, max_value=100)
    height = forms.IntegerField(min_value=1, max_value=100)
    win_threshold = forms.IntegerField(min_value=1, max_value=100)
    owner_color = forms.RegexField(r'^#[0-9a-fA-F]{6}$')


class JoinForm(forms.Form):
    color = forms.RegexField(r'^#[0-9a-fA-F]{6}$')


class TurnForm(forms.Form):
    i = forms.IntegerField(min_value=0, max_value=99)
    j = forms.IntegerField(min_value=0, max_value=99)


class HistorySuffixForm(forms.Form):
    start_index = forms.IntegerField(min_value=0, max_value=9999)
