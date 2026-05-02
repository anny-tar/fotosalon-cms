from django.db import models


class ProductCategory(models.Model):
    name = models.CharField(
        max_length=255,
        verbose_name='Название категории'
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='Slug'
    )

    class Meta:
        verbose_name = 'Категория товаров'
        verbose_name_plural = 'Категории товаров'

    def __str__(self):
        return self.name


class Product(models.Model):
    article = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Артикул'
    )
    name = models.CharField(
        max_length=500,
        verbose_name='Название'
    )
    category = models.ForeignKey(
        ProductCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Категория'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Описание'
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Цена'
    )
    image = models.ImageField(
        upload_to='products/images/',
        blank=True,
        null=True,
        verbose_name='Фото'
    )
    thumbnail = models.ImageField(
        upload_to='products/thumbnails/',
        blank=True,
        null=True,
        verbose_name='Миниатюра'
    )
    quantity = models.PositiveIntegerField(
        default=0,
        verbose_name='Количество на складе'
    )
    min_quantity = models.PositiveIntegerField(
        default=1,
        verbose_name='Минимальный остаток'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Активен'
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name='Порядок'
    )

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ['order', 'name']

    def __str__(self):
        return f'{self.article} — {self.name}'

    @property
    def is_in_stock(self):
        return self.quantity > 0

    @property
    def is_low_stock(self):
        """Остаток достиг или ниже минимального порога."""
        return self.quantity <= self.min_quantity