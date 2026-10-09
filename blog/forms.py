from django import forms
from django.contrib.auth import get_user_model
from .models import BlogComment

User = get_user_model()


class BlogCommentForm(forms.ModelForm):
    class Meta:
        model = BlogComment
        fields = ["author_name", "author_email", "comment"]
        widgets = {
            "author_name": forms.TextInput(
                attrs={
                    "class": "form-input",
                    "placeholder": "Your Name or Handle",
                    "required": "required",
                }
            ),
            "author_email": forms.EmailInput(
                attrs={
                    "class": "form-input",
                    "placeholder": "Your Email (optional, never shared)",
                }
            ),
            "comment": forms.Textarea(
                attrs={
                    "class": "form-textarea",
                    "rows": 4,
                    "placeholder": "Join the discussion... Share your thoughts, questions, or insights.",
                    "required": "required",
                }
            ),
        }
        labels = {
            "author_name": "Name",
            "author_email": "Email (Optional)",
            "comment": "Comment",
        }


class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-input",
                "placeholder": "Username",
                "autofocus": True,
            }
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-input",
                "placeholder": "Password",
            }
        )
    )


class RegisterForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-input",
                "placeholder": "Create a secure password",
            }
        ),
        min_length=6,
        help_text="At least 6 characters.",
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-input",
                "placeholder": "Confirm password",
            }
        )
    )

    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name"]
        widgets = {
            "username": forms.TextInput(
                attrs={
                    "class": "form-input",
                    "placeholder": "Choose a username",
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": "form-input",
                    "placeholder": "Your email address",
                }
            ),
            "first_name": forms.TextInput(
                attrs={
                    "class": "form-input",
                    "placeholder": "First name (optional)",
                }
            ),
            "last_name": forms.TextInput(
                attrs={
                    "class": "form-input",
                    "placeholder": "Last name (optional)",
                }
            ),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password_confirm and password != password_confirm:
            self.add_error("password_confirm", "Passwords do not match.")

        return cleaned_data
