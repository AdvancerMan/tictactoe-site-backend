from django import forms


class PageCountForm(forms.Form):
    page = forms.IntegerField(min_value=1, required=False)
    count = forms.IntegerField(min_value=1, max_value=100, required=False)

    def clean_page(self):
        return int(self.data.get('page', 1))

    def clean_count(self):
        return int(self.data.get('count', 10))


class GameForm(forms.Form):
    width = forms.IntegerField(min_value=1, max_value=1000)
    height = forms.IntegerField(min_value=1, max_value=1000)
    win_threshold = forms.IntegerField(min_value=1, max_value=1000)
    owner_color = forms.RegexField(r'^#[0-9a-fA-F]{6}$')
