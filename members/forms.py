from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Task, Comment, UserProfile, Category

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        
    def save(self, commit=True):
        user = super(UserRegisterForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['bio', 'profile_picture']
        widgets = {
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'bio': 'О себе',
            'profile_picture': 'Фото профиля',
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make fields not required
        self.fields['bio'].required = False
        self.fields['profile_picture'].required = False
        
        # Add Bootstrap form control classes
        for field_name in self.fields:
            self.fields[field_name].widget.attrs.update({'class': 'form-control'})

class TaskForm(forms.ModelForm):
    observer = forms.ModelChoiceField(
        queryset=User.objects.all(),
        required=False,
        label="Наблюдатель",
        help_text="Этот пользователь будет получать уведомления об обновлениях этой задачи."
    )
    
    class Meta:
        model = Task
        fields = ['title', 'description', 'due_date', 'status', 'priority', 'assigned_to', 'category']
        widgets = {
            'due_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
        labels = {
            'title': 'Название',
            'description': 'Описание',
            'due_date': 'Срок',
            'status': 'Статус',
            'priority': 'Приоритет',
            'assigned_to': 'Назначить',
            'category': 'Категория',
        }
    
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)  # Store request if provided
        super().__init__(*args, **kwargs)
        if self.instance.pk and self.instance.observers.exists():
            self.fields['observer'].initial = self.instance.observers.first()
            
        # Add Bootstrap form control classes
        for field_name in self.fields:
            field = self.fields[field_name]
            css_class = 'form-control'
            if isinstance(field.widget, forms.Select):
                css_class = 'form-select'
            elif isinstance(field.widget, forms.Textarea):
                css_class = 'form-control'
            
            field.widget.attrs.update({'class': css_class})
    
    def save(self, commit=True):
        task = super().save(commit=False)
        if commit:
            task.save()
            task.observers.clear()
            if self.cleaned_data.get('observer'):
                task.observers.add(self.cleaned_data['observer'])
        return task

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }
        labels = {
            'text': 'Комментарий',
        }

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description', 'color']
        widgets = {
            'color': forms.TextInput(attrs={'type': 'color'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }
        labels = {
            'name': 'Название',
            'description': 'Описание', 
            'color': 'Цвет',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap form control classes
        for field_name in self.fields:
            if field_name != 'color':  # Skip color field as it has custom attributes
                self.fields[field_name].widget.attrs.update({'class': 'form-control'})
