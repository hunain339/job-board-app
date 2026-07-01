from django import forms
from .models import Job


class JobPostForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = [
            'title', 'description', 'job_type', 'experience_level',
            'location', 'is_remote', 'salary_min', 'salary_max',
            'required_skills', 'category'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 8}),
            'is_remote': forms.CheckboxInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            if field != 'is_remote':
                self.fields[field].widget.attrs.update({
                    'class': 'w-full px-4 py-3 border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-indigo-600'
                })
            else:
                self.fields[field].widget.attrs.update({'class': 'rounded'})
