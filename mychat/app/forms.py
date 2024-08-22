from django import forms

class ScraperForm(forms.Form):
    url = forms.URLField(label='Nhập URL:')
    save_path = forms.CharField(label='Chọn đường dẫn lưu:')
    start_page = forms.IntegerField(label='Bắt đầu từ trang:')