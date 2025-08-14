from django import forms
from .models import Tag

class TagForm(forms.ModelForm):
    emoji = forms.CharField(required=False, label="Emoji")
    icon = forms.CharField(required=False, label="Icon")
    bgColor = forms.CharField(required=False, initial="#00e5ff", label="Background Color")
    color = forms.CharField(required=False, initial="#000000", label="Text Color")
    iconColor = forms.CharField(required=False, initial="#000000", label="Icon Color")

    class Meta:
        model = Tag
        fields = ['name', 'description', 'icon_image', 'is_active', 'is_deleted']  # only real model fields

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.extra_fields:
            self.fields['emoji'].initial = self.instance.extra_fields.get('emoji', '📊')
            self.fields['icon'].initial = self.instance.extra_fields.get('icon', 'chart-line')
            self.fields['bgColor'].initial = self.instance.extra_fields.get('bgColor', '#00e5ff')
            self.fields['color'].initial = self.instance.extra_fields.get('color', '#000000')
            self.fields['iconColor'].initial = self.instance.extra_fields.get('iconColor', '#000000')

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.extra_fields = {
            **(instance.extra_fields or {}),
            'emoji': self.cleaned_data.get('emoji', '📊'),
            'icon': self.cleaned_data.get('icon', 'chart-line'),
            'bgColor': self.cleaned_data.get('bgColor', '#00e5ff'),
            'color': self.cleaned_data.get('color', '#000000'),
            'iconColor': self.cleaned_data.get('iconColor', '#000000')
        }
        if commit:
            instance.save()
        return instance