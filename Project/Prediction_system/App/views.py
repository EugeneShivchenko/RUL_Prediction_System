import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from Prediction_system import renderers
from .forms import DatasetForm, ML_modelForm, ReportForm, ScalerForm
from .models import ML_model, Engine, Scaler
from io import BytesIO
from tensorflow import keras
from translate import Translator
import joblib
import datetime
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
import pandas as pd
import numpy as np
import base64
import os
import json

# Создавайте свои представления здесь.
def home(request):
    """
    Принимает объект HttpRequest. Если пользователь авторизован, то перенаправляет в личный кабинет.
    Иначе выводит главную страницу.
    """
    if request.user.is_authenticated:
        return redirect('account')
    else:
        return render(request, 'home.html')

@login_required
def account(request):
    """Принимает объект HttpRequest. Выводит личный кабинет."""
    return render(request, 'account_base.html')

@login_required
def upload_dataset(request):
    """Принимает объект HttpRequest. Позволяет через форму загружать в систему датасет."""
    if request.method == 'POST':
        form = DatasetForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            dataset_name = form.cleaned_data['dataset_location'].name
            serial_number = form.cleaned_data['serial'].serial_id
            base_path = os.getcwd()
            dataset_path = os.path.join(base_path, 'media', 'datasets', dataset_name)
            index_names = ['Двигатель', 'Цикл']
            setting_names = [f'Условие_{i}' for i in range(1, 4)]
            sensor_names = [f'Датчик_{i}' for i in range(1, 22)]
            col_names = index_names + setting_names + sensor_names
            dataset = pd.read_csv(dataset_path, sep='\s+', names=col_names,
                                  keep_default_na=False, na_values=['failure'])
            request.session['serial_number'] = serial_number
            request.session['dataset'] = dataset.to_json()
            request.session['duplicates_deleted'] = False
            request.session['missing_values_handled'] = False
            request.session['unimportant_features_deleted'] = False
            request.session['high_correlation_features_deleted'] = False
            request.session['dataset_is_scaled'] = False
            request.session['data_is_not_empty'] = False
            request.session['no_report'] = True
            notification = f'Датасет для двигателя с серийным номером {serial_number} загружен успешно!'
            notification_message = {'notification': notification}
            return render(request, 'account_notification.html', context=notification_message)
    else:
        form = DatasetForm()
    return render(request, 'dataset_form.html', {'form': form})

@login_required
def show_dataset(request):
    """Принимает объект HttpRequest. Выводит на экран загруженный датасет в виде таблицы."""
    try:
        dataset = pd.read_json(request.session['dataset'])
        dataset_table = dataset.to_html(classes='table table-bordered border-black', col_space=50,
                                        index=False, justify='center', show_dimensions=True)
        message = {'dataset_table': dataset_table}
        return render(request, 'account_show_dataset.html', context=message)
    except Exception:
        notification = 'Пожалуйста, загрузите датасет.'
        notification_message = {'notification': notification}
        return render(request, 'account_notification.html', context=notification_message)

@login_required
def show_statistics(request):
    """Принимает объект HttpRequest. Выводит на экран статистику по загруженному датасету в виде таблицы."""
    try:
        dataset = pd.read_json(request.session['dataset'])
        statistics = dataset.describe().T
        statistics_table = statistics.to_html(classes='table table-bordered border-black',
                                              col_space=50, justify='center')
        message = {'statistics_table': statistics_table}
        return render(request, 'account_show_statistics.html', context=message)
    except Exception:
        notification = 'Пожалуйста, загрузите датасет.'
        notification_message = {'notification': notification}
        return render(request, 'account_notification.html', context=notification_message)

@login_required
def delete_duplicates(request):
    """Принимает объект HttpRequest. Удаляет из загруженного датасета повторяющиеся строки."""
    try:
        dataset = pd.read_json(request.session['dataset'])
        length_dataset = len(dataset.index)
        dataset.drop_duplicates(inplace=True)
        dataset.reset_index(drop=True, inplace=True)
        length_dataset_without_duplicates = len(dataset)
        length_difference = length_dataset - length_dataset_without_duplicates
        message = {'length_difference': length_difference}
        request.session['dataset'] = dataset.to_json()
        request.session['duplicates_deleted'] = True
        return render(request, 'account_delete_duplicates.html', context=message)
    except Exception:
        notification = 'Пожалуйста, загрузите датасет.'
        notification_message = {'notification': notification}
        return render(request, 'account_notification.html', context=notification_message)

@login_required
def handle_missing_values(request):
    """Принимает объект HttpRequest. Заполняет пропущенные значения в загруженном датасете."""
    try:
        dataset = pd.read_json(request.session['dataset'])
        dataset.replace(to_replace='failure', value=np.nan, inplace=True)
        missing_values_count = dataset.isnull().sum().sum()
        if missing_values_count != 0:
            dataset.interpolate(inplace=True, limit_direction='both')
        message = {'missing_values_count': missing_values_count}
        request.session['dataset'] = dataset.to_json()
        request.session['missing_values_handled'] = True
        return render(request, 'account_handle_missing_values.html', context=message)
    except Exception:
        notification = 'Пожалуйста, загрузите датасет.'
        notification_message = {'notification': notification}
        return render(request, 'account_notification.html', context=notification_message)

@login_required
def delete_unimportant_features(request):
    """Принимает объект HttpRequest. Удаляет из загруженного датасета неинформативные признаки."""
    try:
        dataset = pd.read_json(request.session['dataset'])
        correlation_matrix = dataset.corr(numeric_only=True)
        nan_columns = list(correlation_matrix[correlation_matrix.isna().all(axis=1)].index)
        count_nan_columns = len(nan_columns)
        if count_nan_columns != 0:
            dataset.drop(labels=nan_columns, axis=1, inplace=True)
        message = {'count_nan_columns': count_nan_columns, 'nan_columns': nan_columns}
        request.session['dataset'] = dataset.to_json()
        request.session['unimportant_features_deleted'] = True
        return render(request, 'account_delete_unimportant_features.html', context=message)
    except Exception:
        notification = 'Пожалуйста, загрузите датасет.'
        notification_message = {'notification': notification}
        return render(request, 'account_notification.html', context=notification_message)

@login_required
def plot_heatmap(request):
    """Принимает объект HttpRequest. Выполняет построение матрицы корреляций."""
    try:
        if request.session['duplicates_deleted'] and \
        request.session['missing_values_handled'] and \
        request.session['unimportant_features_deleted']:
            dataset = pd.read_json(request.session['dataset'])
            list_of_columns = []
            correlation_matrix = dataset.corr(numeric_only=True)
            filtered_correlation_matrix = correlation_matrix[((correlation_matrix >= 0.95) |
                                                            (correlation_matrix <= -0.95)) &
                                                            (correlation_matrix != 1)]
            high_correlation_columns = filtered_correlation_matrix.unstack().sort_values().drop_duplicates()
            for i in range(len(high_correlation_columns.index)):
                if high_correlation_columns.index[i][0] != 'Цикл':
                    list_of_columns.append(high_correlation_columns.index[i][0])
            count_of_columns = len(list_of_columns)
            plt.rc('xtick', labelsize=16)
            plt.rc('ytick', labelsize=16)
            img = BytesIO()
            plt.figure(figsize=(20, 20))
            sns.heatmap(correlation_matrix, vmin=-1, vmax=1, cmap='coolwarm', annot=True, fmt='.2f',
                        annot_kws={'size': 14}, linewidths=0.5, cbar_kws={'shrink': 0.5}, square=True)
            plt.xticks(rotation=45)
            plt.savefig(img, format='webp', bbox_inches='tight', pad_inches=0.5)
            plt.close()
            img.seek(0)
            plot_url = base64.b64encode(img.getvalue()).decode('utf8')
            message = {'list_of_columns': list_of_columns,
                       'count_of_columns': count_of_columns,
                       'plot_url': plot_url}
            request.session['list_of_columns'] = list_of_columns
            return render(request, 'account_plot_heatmap.html', context=message)
        else:
            notification = 'Пожалуйста, обработайте пропуски, удалите дубликаты и неинформативные признаки.'
            notification_message = {'notification': notification}
            return render(request, 'account_notification.html', context=notification_message)
    except Exception:
        notification = 'Пожалуйста, загрузите датасет.'
        notification_message = {'notification': notification}
        return render(request, 'account_notification.html', context=notification_message)

@login_required
def delete_high_correlation_features(request):
    """Принимает объект HttpRequest. Удаляет из загруженного датасета высококоррелирующие признаки."""
    try:
        dataset = pd.read_json(request.session['dataset'])
        columns = request.session['list_of_columns']
        dataset.drop(labels=columns, axis=1, inplace=True)
        request.session['dataset'] = dataset.to_json()
        request.session['high_correlation_features_deleted'] = True
        notification = 'Удаление высококоррелирующих признаков из датасета выполнено успешно!'
        notification_message = {'notification': notification}
        return render(request, 'account_notification.html', context=notification_message)
    except Exception:
        notification = 'Пожалуйста, загрузите датасет.'
        notification_message = {'notification': notification}
        return render(request, 'account_notification.html', context=notification_message)

@login_required
def plot_line_plot(request):
    """Принимает объект HttpRequest. Выполняет построение линейных графиков."""
    try:
        if request.session['duplicates_deleted'] and \
        request.session['missing_values_handled']:
            dataset = pd.read_json(request.session['dataset'])
            list_of_plots = []
            plt.rc('axes', labelsize=19)
            plt.rc('xtick', labelsize=16)
            plt.rc('ytick', labelsize=16)
            x = dataset['Цикл']
            for column in dataset:
                img = BytesIO()
                plt.figure(figsize=(22, 7))
                if column == 'Двигатель' or column == 'Цикл':
                    continue
                y = dataset[column]
                plt.plot(x, y, linewidth=2.2, color='SteelBlue')
                plt.xlabel('Полетный цикл')
                plt.ylabel(column)
                plt.grid(True)
                plt.savefig(img, format='webp')
                plt.close()
                img.seek(0)
                plot_url = base64.b64encode(img.getvalue()).decode('utf8')
                list_of_plots.append(plot_url)
            message = {'list_of_plots': list_of_plots}
            return render(request, 'account_plot_plots.html', context=message)
        else:
            notification = 'Пожалуйста, обработайте пропуски и удалите дубликаты.'
            notification_message = {'notification': notification}
            return render(request, 'account_notification.html', context=notification_message)
    except Exception:
        notification = 'Пожалуйста, загрузите датасет.'
        notification_message = {'notification': notification}
        return render(request, 'account_notification.html', context=notification_message)

@login_required
def plot_box_plot(request):
    """Принимает объект HttpRequest. Выполняет построение диаграмм размаха."""
    try:
        if request.session['duplicates_deleted'] and \
        request.session['missing_values_handled']:
            dataset = pd.read_json(request.session['dataset'])
            list_of_plots = []
            plt.rc('axes', titlesize=19)
            plt.rc('xtick', labelsize=16)
            plt.rc('ytick', labelsize=16)
            for column in dataset:
                img = BytesIO()
                plt.figure(figsize=(22, 7))
                if column == 'Двигатель' or column == 'Цикл':
                    continue
                plt.boxplot(dataset[column])
                plt.title(column)
                plt.savefig(img, format='webp')
                plt.close()
                img.seek(0)
                plot_url = base64.b64encode(img.getvalue()).decode('utf8')
                list_of_plots.append(plot_url)
            message = {'list_of_plots': list_of_plots}
            return render(request, 'account_plot_plots.html', context=message)
        else:
            notification = 'Пожалуйста, обработайте пропуски и удалите дубликаты.'
            notification_message = {'notification': notification}
            return render(request, 'account_notification.html', context=notification_message)
    except Exception:
        notification = 'Пожалуйста, загрузите датасет.'
        notification_message = {'notification': notification}
        return render(request, 'account_notification.html', context=notification_message)

@login_required
def select_scaler(request):
    """Принимает объект HttpRequest. Позволяет через форму выбирать нужный масштабатор."""
    if request.method == 'POST':
        form = ScalerForm(request.POST)
        if form.is_valid():
            scaler_name = form.cleaned_data['scalers_names']
            scaler = Scaler.objects.get(scaler_name=scaler_name)
            relative_path = str(scaler.scaler_location).lstrip('scalers/')
            base_path = os.getcwd()
            scaler_path = os.path.join(base_path, 'media', 'scalers', relative_path)
            notification = f'{scaler_name} выбран успешно!'
            message = {'notification': notification}
            request.session['scaler_path'] = scaler_path
            return render(request, 'account_notification.html', context=message)
    else:
        form = ScalerForm()
    return render(request, 'scaler_form.html', {'form': form})

@login_required
def scale_dataset(request):
    """Принимает объект HttpRequest. Масштабирует загруженный датасет."""
    try:
        if request.session['duplicates_deleted'] and \
        request.session['missing_values_handled'] and \
        request.session['unimportant_features_deleted'] and \
        request.session['high_correlation_features_deleted']:
            dataset = pd.read_json(request.session['dataset'])
            robust_scaler = joblib.load(request.session['scaler_path']) 
            scaled_dataset = robust_scaler.transform(dataset)
            scaled_df = pd.DataFrame(scaled_dataset, columns=dataset.columns)
            dataset_table = scaled_df.to_html(classes='table table-bordered border-black', col_space=50,
                                            index=False, justify='center', show_dimensions=True)
            message = {'dataset_table': dataset_table}
            request.session['scaled_dataset'] = json.dumps(scaled_dataset.tolist())
            request.session['dataset_is_scaled'] = True
            return render(request, 'account_scale_dataset.html', context=message)
        else:
            notification = 'Пожалуйста, обработайте пропуски, удалите дубликаты, ' \
                           'неинформативные и высококоррелирующие признаки.'
            notification_message = {'notification': notification}
            return render(request, 'account_notification.html', context=notification_message)
    except Exception:
        notification = 'Пожалуйста, загрузите датасет или выберите подходящий масштабатор.'
        notification_message = {'notification': notification}
        return render(request, 'account_notification.html', context=notification_message)

@login_required
def select_ml_model(request):
    """Принимает объект HttpRequest. Позволяет через форму выбирать нужную модель МО."""
    if request.method == 'POST':
        form = ML_modelForm(request.POST)
        if form.is_valid():
            ml_model_name = form.cleaned_data['ml_models_names']
            ml_model = ML_model.objects.get(ml_model_name=ml_model_name)
            relative_path = str(ml_model.ml_model_location).lstrip('models/')
            base_path = os.getcwd()
            ml_model_path = os.path.join(base_path, 'media', 'models', relative_path)
            notification = f'{ml_model_name} выбрана успешно!'
            message = {'notification': notification}
            request.session['ml_model_path'] = ml_model_path
            return render(request, 'account_notification.html', context=message)
    else:
        form = ML_modelForm()
    return render(request, 'ml_model_form.html', {'form': form})

@login_required
def calculate_rul(request):
    """Принимает объект HttpRequest. Рассчитывает остаточный ресурс для авиадвигателя."""
    try:
        if request.session['duplicates_deleted'] and \
        request.session['missing_values_handled'] and \
        request.session['unimportant_features_deleted'] and \
        request.session['high_correlation_features_deleted'] and \
        request.session['dataset_is_scaled']:
            data_list = json.loads(request.session['scaled_dataset'])
            scaled_dataset = np.array(data_list)
            scaled_dataset_reshaped = scaled_dataset.reshape(scaled_dataset.shape[0],
                                                             1,
                                                             scaled_dataset.shape[1])
            ml_model_loaded = keras.models.load_model(request.session['ml_model_path'])
            rul = np.ravel(ml_model_loaded.predict(scaled_dataset_reshaped))[-1]
            rul = round(rul, 2)
            engine = Engine.objects.get(serial_id=request.session['serial_number'])
            engine.rul = float(rul)
            engine.save(update_fields=['rul'])
            message = {'total_rul': rul}
            request.session['data_is_not_empty'] = True
            return render(request, 'account_calculate_rul.html', context=message)
        else:
            notification = 'Пожалуйста, обработайте пропуски, удалите дубликаты, ' \
                           'неинформативные и высококоррелирующие признаки, отмасштабируйте датасет.'
            notification_message = {'notification': notification}
            return render(request, 'account_notification.html', context=notification_message)
    except Exception:
        notification = 'Пожалуйста, загрузите датасет или выберите подходящую модель МО.'
        notification_message = {'notification': notification}
        return render(request, 'account_notification.html', context=notification_message)
    
@login_required
def pdf_report(request):
    """Принимает объект HttpRequest. Формирует контекст для заполнения шаблона отчета."""
    translator= Translator(from_lang='russian', to_lang='english')
    executor = f'{request.user.first_name} {request.user.last_name}'
    engine = Engine.objects.get(serial_id=request.session['serial_number'])
    tail_number = engine.tail_number
    engine_name = engine.engine_name
    rul = engine.rul
    date_and_time = datetime.datetime.now()
    report_number = f"{tail_number} {request.session['serial_number']} {date_and_time}"
    report_number = report_number.replace('-', '').replace(':', '').replace('.', '').replace(' ', '')
    data = {'report_number': report_number,
            'executor': translator.translate(executor),
            'tail_number': tail_number,
            'engine_name': engine_name,
            'serial_number': request.session['serial_number'],
            'rul': rul,
            'date_and_time': date_and_time.strftime('%d %B %Y %H:%M:%S')}
    request.session['no_report'] = False
    request.session['report_number'] = report_number
    return renderers.render_to_pdf('report.html', report_number, data)
    
@login_required
def create_report(request):
    """Принимает объект HttpRequest. Выводит на экран заполненный отчет в формате PDF."""
    try:
        notification = 'Пожалуйста, выполните расчет остаточного ресурса двигателя, ' \
                       'прежде чем создавать отчет.'
        notification_message = {'data_is_not_empty': request.session['data_is_not_empty'],
                                'notification': notification}
        return render(request, 'account_create_report.html', context=notification_message)
    except Exception:
        notification = 'Пожалуйста, выполните расчет остаточного ресурса двигателя, ' \
                       'прежде чем создавать отчет.'
        notification_message = {'notification': notification}
        return render(request, 'account_notification.html', context=notification_message)

@login_required
def save_report(request):
    """Принимает объект HttpRequest. Позволяет через форму сохранять в системе отчет."""
    try:
        if request.session['no_report']:
            notification = 'Пожалуйста, выполните расчет остаточного ресурса двигателя и создайте отчет.'
            notification_message = {'notification': notification}
            return render(request, 'account_notification.html', context=notification_message)
        else:
            if request.method == 'POST':
                form = ReportForm(request.POST, request.FILES)
                if form.is_valid():
                    form.save()
                    notification = f"Отчет No. {request.session['report_number']} сохранен успешно!"
                    notification_message = {'notification': notification}
                    return render(request, 'account_notification.html', context=notification_message)
            else:
                data = {'report_id': request.session['report_number'],
                        'user': request.user.id,
                        'serial': request.session['serial_number']}
                form = ReportForm(data)
            return render(request, 'report_form.html', {'form': form})
    except Exception:
        notification = 'Пожалуйста, выполните расчет остаточного ресурса двигателя и создайте отчет.'
        notification_message = {'notification': notification}
        return render(request, 'account_notification.html', context=notification_message)