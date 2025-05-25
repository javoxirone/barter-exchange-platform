from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse


class Ad(models.Model):
    CATEGORY_CHOICES = [
        ('electronics', 'Электроника'),
        ('clothing', 'Одежда'),
        ('books', 'Книги'),
        ('home', 'Товары для дома'),
        ('sport', 'Спорт и отдых'),
        ('toys', 'Игрушки'),
        ('other', 'Другое'),
    ]

    CONDITION_CHOICES = [
        ('new', 'Новый'),
        ('like_new', 'Как новый'),
        ('good', 'Хорошее'),
        ('fair', 'Удовлетворительное'),
        ('poor', 'Плохое'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    title = models.CharField(max_length=255, verbose_name='Заголовок')
    description = models.TextField(verbose_name='Описание')
    image_url = models.ImageField(upload_to="ads/", blank=True, null=True, verbose_name='URL изображения')
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, verbose_name='Категория')
    condition = models.CharField(max_length=30, choices=CONDITION_CHOICES, verbose_name='Состояние')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации')

    class Meta:
        verbose_name = 'Объявление'
        verbose_name_plural = 'Объявления'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('ad_detail', args=[str(self.id)])


class ExchangeProposal(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидает'),
        ('accepted', 'Принято'),
        ('rejected', 'Отклонено'),
    ]

    ad_sender = models.ForeignKey(Ad, on_delete=models.CASCADE, related_name='sent_proposals',
                                  verbose_name='Отправитель')
    ad_receiver = models.ForeignKey(Ad, on_delete=models.CASCADE, related_name='received_proposals',
                                    verbose_name='Получатель')
    comment = models.TextField(blank=True, null=True, verbose_name='Комментарий')
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='pending',
                              verbose_name='Статус')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        verbose_name = 'Предложение обмена'
        verbose_name_plural = 'Предложения обмена'
        ordering = ['-created_at']

    def __str__(self):
        return f"Обмен {self.ad_sender} на {self.ad_receiver}"