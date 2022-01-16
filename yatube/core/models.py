from django.db import models


class CreatedModel(models.Model):
    '''Абстрактная модель добавляет дату создания'''
    created = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True
    )
    text = models.TextField(
        'Текст',
    )

    class Meta:
        abstract = True
