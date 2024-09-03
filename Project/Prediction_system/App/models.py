from django.db import models
from django.conf import settings
from django.core.validators import FileExtensionValidator

# Создавайте свои модели здесь.
class Engine(models.Model):
    """
    Модель для представления авиадвигателя.
    
    Поля:
        engine_name (CharField): хранит название авиадвигателя.
        serial_id (CharField): хранит серийный номер авиадвигателя.
        tail_number (CharField): хранит бортовой номер ВС.
        rul (DecimalField): хранит значение остаточного ресурса авиадвигателя.
    """
    engine_name = models.CharField(max_length=50,
                                   verbose_name='Название двигателя')
    serial_id = models.CharField(primary_key=True,
                                 max_length=50,
                                 verbose_name='Серийный номер двигателя')
    tail_number = models.CharField(max_length=20,
                                   verbose_name='Бортовой номер ВС')
    rul = models.DecimalField(null=True,
                              blank=True,
                              max_digits=6,
                              decimal_places=2,
                              verbose_name='Остаточный ресурс')
    
    class Meta:
        """
        Содержит метаданные, которые определяют поведение модели.

        Атрибуты:
            verbose_name (str): человекочитаемое название модели.
            verbose_name_plural (str): множественное человекочитаемое название модели.
        """
        verbose_name = 'двигатель'
        verbose_name_plural = 'двигатели'
    
    def __str__(self):
        """Определяет, с каким именем объект будет отображаться в панели администрирования."""
        return str(self.serial_id)

class Report(models.Model):
    """
    Модель для представления отчета.
    
    Поля:
        report_id (CharField): хранит ID отчета.
        user (ForeignKey): хранит ID пользователя.
        serial (ForeignKey): хранит серийный номер авиадвигателя.
        upload_date (DateTimeField): хранит дату и время загрузки отчета.
        report_location (FileField): хранит путь расположения отчета.
    """
    report_id = models.CharField(primary_key=True,
                                 max_length=100,
                                 verbose_name='ID отчета')
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.PROTECT,
                             verbose_name='ID пользователя')
    serial = models.ForeignKey(Engine,
                               on_delete=models.CASCADE,
                               verbose_name='Серийный номер двигателя')
    upload_date = models.DateTimeField(auto_now_add=True,
                                       verbose_name='Дата и время загрузки')
    report_location = models.FileField(upload_to='reports/',
                                       verbose_name='Расположение отчета',
                                       validators=[FileExtensionValidator(['pdf'])])

    class Meta:
        """
        Содержит метаданные, которые определяют поведение модели.

        Атрибуты:
            verbose_name (str): человекочитаемое название модели.
            verbose_name_plural (str): множественное человекочитаемое название модели.
        """
        verbose_name = 'отчет'
        verbose_name_plural = 'отчеты'

    def __str__(self):
        """Определяет, с каким именем объект будет отображаться в панели администрирования."""
        return str(self.report_id)

class ML_model(models.Model):
    """
    Модель для представления модели МО.
    
    Поля:
        ml_model_id (BigAutoField): хранит ID модели МО.
        ml_model_name (CharField): хранит название модели МО.
        ml_model_location (FileField): хранит путь расположения модели МО.
    """
    ml_model_id = models.BigAutoField(auto_created=True,
                                      primary_key=True,
                                      verbose_name='ID модели машинного обучения')
    ml_model_name = models.CharField(max_length=50,
                                     verbose_name='Название модели машинного обучения')
    ml_model_location = models.FileField(upload_to='models/',
                                         verbose_name='Расположение модели машинного обучения',
                                         validators=[FileExtensionValidator(['h5'])])

    class Meta:
        """
        Содержит метаданные, которые определяют поведение модели.

        Атрибуты:
            verbose_name (str): человекочитаемое название модели.
            verbose_name_plural (str): множественное человекочитаемое название модели.
        """
        verbose_name = 'модель машинного обучения'
        verbose_name_plural = 'модели машинного обучения'

    def __str__(self):
        """Определяет, с каким именем объект будет отображаться в панели администрирования."""
        return str(self.ml_model_name)

class Dataset(models.Model):
    """
    Модель для представления датасета.
    
    Поля:
        dataset_id (BigAutoField): хранит ID датасета.
        serial (ForeignKey): хранит серийный номер авиадвигателя.
        upload_date (DateTimeField): хранит дату и время загрузки датасета.
        dataset_location (FileField): хранит путь расположения датасета.
    """
    dataset_id = models.BigAutoField(auto_created=True,
                                     primary_key=True,
                                     verbose_name='ID датасета')
    serial = models.ForeignKey(Engine,
                               on_delete=models.CASCADE,
                               verbose_name='Серийный номер двигателя')
    upload_date = models.DateTimeField(auto_now_add=True,
                                       verbose_name='Дата и время загрузки')
    dataset_location = models.FileField(upload_to='datasets/',
                                        verbose_name='Расположение датасета',
                                        validators=[FileExtensionValidator(['txt'])])

    class Meta:
        """
        Содержит метаданные, которые определяют поведение модели.

        Атрибуты:
            verbose_name (str): человекочитаемое название модели.
            verbose_name_plural (str): множественное человекочитаемое название модели.
        """
        verbose_name = 'датасет'
        verbose_name_plural = 'датасеты'

    def __str__(self):
        """Определяет, с каким именем объект будет отображаться в панели администрирования."""
        return str(self.dataset_id)

class Scaler(models.Model):
    """
    Модель для представления масштабатора.
    
    Поля:
        scaler_id (BigAutoField): хранит ID масштабатора.
        scaler_name (CharField): хранит название масштабатора.
        scaler_location (FileField): хранит путь расположения масштабатора.
    """
    scaler_id = models.BigAutoField(auto_created=True,
                                    primary_key=True,
                                    verbose_name='ID масштабатора')
    scaler_name = models.CharField(max_length=50,
                                   verbose_name='Название масштабатора')
    scaler_location = models.FileField(upload_to='scalers/',
                                       verbose_name='Расположение масштабатора',
                                       validators=[FileExtensionValidator(['joblib'])])

    class Meta:
        """
        Содержит метаданные, которые определяют поведение модели.

        Атрибуты:
            verbose_name (str): человекочитаемое название модели.
            verbose_name_plural (str): множественное человекочитаемое название модели.
        """
        verbose_name = 'масштабатор'
        verbose_name_plural = 'масштабаторы'

    def __str__(self):
        """Определяет, с каким именем объект будет отображаться в панели администрирования."""
        return str(self.scaler_name)