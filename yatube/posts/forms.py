from django import forms

from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'cols': 40,
                'rows': 10,
            }),
            'group': forms.Select(attrs={
                'name': 'group',
                'class': 'form-control',
                'id': 'id_group'
            })
        }
        help_texts = {
            'text': 'Текст поста',
            'group': 'Группа, к которой будет относиться пост',
            'image': 'Изображение, прикрепленное к посту',
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text', )
        help_texts = {
            'post': 'Пост, к которому относится комментарий',
            'author': 'Автор комментария',
            'text': 'Текст комментария',
            'created': 'Дата создания комментария'
        }
