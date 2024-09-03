from django import forms
from .models import Dataset, ML_model, Report, Scaler

class DatasetForm(forms.ModelForm):
    """Класс для определения формы загрузки датасета."""
    class Meta:
        """
        Содержит метаданные, используемые для настройки различных аспектов формы.

        Атрибуты:
            model: устанавливает связь формы с моделью Dataset.
            labels: устанавливает человекочитаемые названия полей в форме.
            fields: определяет поля для отображения в форме.
        """
        model = Dataset
        labels = {'dataset_location': ''}
        fields = ['serial', 'dataset_location']

class ML_modelForm(forms.Form):
    """
    Класс для определения формы выбора модели МО.

    Поля:
        ml_models_names (ModelChoiceField): хранит список с названиями моделей МО.
    """
    ml_models_names = forms.ModelChoiceField(queryset=ML_model.objects.all().order_by('ml_model_name'),
                                             label='Название:')

class ReportForm(forms.ModelForm):
    """Класс для определения формы загрузки отчета."""
    class Meta:
        """
        Содержит метаданные, используемые для настройки различных аспектов формы.

        Атрибуты:
            model: устанавливает связь формы с моделью Report.
            labels: устанавливает человекочитаемые названия полей в форме.
            widgets: устанавливает классы виджетов, которые будут использоваться при рендеринге полей.
            help_text: устанавливает вспомогательный текст для полей в форме.
            fields: определяет поля для отображения в форме.
        """
        model = Report
        labels = {'report_location': ''}
        widgets = {'report_id': forms.HiddenInput(),
                   'user': forms.HiddenInput(),
                   'serial': forms.HiddenInput()}
        help_text = {'report_id': '', 'user': '', 'serial': ''}
        fields = ['report_id', 'user', 'serial', 'report_location']

class ScalerForm(forms.Form):
    """
    Класс для определения формы выбора масштабатора.

    Поля:
        scalers_names (ModelChoiceField): хранит список с названиями масштабаторов.
    """
    scalers_names = forms.ModelChoiceField(queryset=Scaler.objects.all().order_by('scaler_name'),
                                           label='Название:')