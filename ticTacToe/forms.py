from django import forms


class PageCountForm(forms.Form):
    page = forms.IntegerField(min_value=1, required=False)
    count = forms.IntegerField(min_value=1, max_value=100, required=False)

    def clean_page(self):
        return int(self.data.get('page', 1))

    def clean_count(self):
        return int(self.data.get('count', 10))
