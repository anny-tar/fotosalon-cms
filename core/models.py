from django.db import models


class SiteSettings(models.Model):
    site_name = models.CharField(
        max_length=255,
        verbose_name='Название сайта'
    )
    slogan = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Слоган'
    )
    logo = models.ImageField(
        upload_to='site/',
        blank=True,
        null=True,
        verbose_name='Логотип'
    )
    meta_title = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Meta title'
    )
    meta_description = models.TextField(
        blank=True,
        verbose_name='Meta description'
    )
    og_image = models.ImageField(
        upload_to='site/',
        blank=True,
        null=True,
        verbose_name='OG Image'
    )
    color_primary = models.CharField(
        max_length=7, default='#2563eb',
        verbose_name='Основной цвет'
    )
    color_primary_dark = models.CharField(
        max_length=7, default='#1d4ed8',
        verbose_name='Тёмный акцент'
    )
    color_accent = models.CharField(
        max_length=7, default='#f59e0b',
        verbose_name='Акцентный цвет'
    )
    color_bg = models.CharField(
        max_length=7, default='#f9fafb',
        verbose_name='Цвет фона'
    )
    color_card = models.CharField(
        max_length=7, default='#ffffff',
        verbose_name='Цвет карточек'
    )
    color_text = models.CharField(
        max_length=7, default='#111827',
        verbose_name='Основной цвет текста'
    )
    color_text_secondary = models.CharField(
        max_length=7, default='#6b7280',
        verbose_name='Вторичный цвет текста'
    )
    color_header_text = models.CharField(
        max_length=7, default='#ffffff',
        verbose_name='Цвет текста в шапке'
    )
    color_footer_text = models.CharField(
        max_length=7, default='#e5e7eb',
        verbose_name='Цвет текста в подвале'
    )

    class Meta:
        verbose_name = 'Настройки сайта'
        verbose_name_plural = 'Настройки сайта'

    def __str__(self):
        return self.site_name


class ContactItem(models.Model):
    TYPE_PHONE   = 'phone'
    TYPE_EMAIL   = 'email'
    TYPE_ADDRESS = 'address'
    TYPE_MAP     = 'map'
    TYPE_TEXT    = 'text'
    TYPE_SOCIAL  = 'social'

    TYPE_CHOICES = [
        (TYPE_PHONE,   'Телефон'),
        (TYPE_EMAIL,   'Email'),
        (TYPE_ADDRESS, 'Адрес'),
        (TYPE_MAP,     'Карта'),
        (TYPE_TEXT,    'Иное'),
        (TYPE_SOCIAL,  'Соцсеть'),
    ]

    TYPE_ICONS = {
        TYPE_PHONE:   '📞',
        TYPE_EMAIL:   '✉️',
        TYPE_ADDRESS: '📍',
        TYPE_MAP:     '🗺️',
        TYPE_TEXT:    '📝',
        TYPE_SOCIAL:  '🔗',
    }

    type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        verbose_name='Тип'
    )
    label = models.CharField(
        max_length=255,
        verbose_name='Описание',
        help_text='Например: Администратор, Главный офис, ВКонтакте'
    )
    value = models.TextField(
        verbose_name='Значение',
        help_text='Номер телефона, email, адрес, ссылка на карту или текст'
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name='Порядок'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Активен'
    )

    class Meta:
        verbose_name = 'Контактный элемент'
        verbose_name_plural = 'Контактные элементы'
        ordering = ['order', 'type']

    def __str__(self):
        return f'{self.get_type_display()} — {self.label}: {self.value[:50]}'

    @property
    def icon(self):
        return self.TYPE_ICONS.get(self.type, '•')


class SmtpSettings(models.Model):
    host = models.CharField(max_length=255, verbose_name='SMTP сервер')
    port = models.PositiveIntegerField(default=587, verbose_name='Порт')
    username = models.CharField(max_length=255, verbose_name='Логин')
    password = models.CharField(max_length=500, verbose_name='Пароль (зашифрован)')
    from_email = models.EmailField(verbose_name='Адрес отправителя')
    use_tls = models.BooleanField(default=True, verbose_name='Использовать TLS')
    class Meta:
        verbose_name = 'Настройки SMTP'
        verbose_name_plural = 'Настройки SMTP'

    def __str__(self):
        return f'{self.host}:{self.port}'


class EmailTemplate(models.Model):
    key = models.CharField(max_length=100, unique=True, verbose_name='Ключ шаблона')
    subject = models.CharField(max_length=255, verbose_name='Тема письма')
    body = models.TextField(verbose_name='Текст письма')

    class Meta:
        verbose_name = 'Шаблон email-уведомления'
        verbose_name_plural = 'Шаблоны email-уведомлений'

    def __str__(self):
        return self.key


class SectionTemplate(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название шаблона')
    template_name = models.CharField(max_length=255, verbose_name='Имя файла шаблона')
    description = models.TextField(blank=True, verbose_name='Описание')

    class Meta:
        verbose_name = 'Шаблон секции'
        verbose_name_plural = 'Шаблоны секций'

    def __str__(self):
        return self.name


class PageSection(models.Model):
    PAGE_CHOICES = [
        ('home', 'Главная страница'),
        ('about', 'О нас'),
    ]

    page = models.CharField(
        max_length=10, choices=PAGE_CHOICES, verbose_name='Страница'
    )
    template = models.ForeignKey(
        SectionTemplate, on_delete=models.PROTECT, verbose_name='Шаблон секции'
    )
    order = models.PositiveIntegerField(default=0, verbose_name='Порядок')
    is_active = models.BooleanField(default=True, verbose_name='Активна')
    content = models.JSONField(default=dict, blank=True, verbose_name='Содержимое секции')

    class Meta:
        verbose_name = 'Секция страницы'
        verbose_name_plural = 'Секции страниц'
        ordering = ['page', 'order']

    def __str__(self):
        return f'{self.get_page_display()} — {self.template.name} (порядок: {self.order})'