from django.contrib.auth.decorators import login_required
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

# Маршруты для личного кабинета
urlpatterns = [path('account/plot-heatmap/delete-high-correlation-features/',
                    views.delete_high_correlation_features, name='delete_high_correlation_features'),
               path('account/create-report/pdf-report/', views.pdf_report, name='pdf_report'),
               path('account/upload-dataset/', views.upload_dataset, name='upload_dataset'),
               path('account/show-dataset/', views.show_dataset, name='show_dataset'),
               path('account/show-statistics/', views.show_statistics, name='show_statistics'),
               path('account/delete-duplicates/', views.delete_duplicates, name='delete_duplicates'),
               path('account/handle-missing-values/',
                    views.handle_missing_values, name='handle_missing_values'),
               path('account/delete-unimportant-features/',
                    views.delete_unimportant_features, name='delete_unimportant_features'),
               path('account/plot-heatmap/', views.plot_heatmap, name='plot_heatmap'),
               path('account/plot-line-plot/', views.plot_line_plot, name='plot_line_plot'),
               path('account/plot-box-plot/', views.plot_box_plot, name='plot_box_plot'),
               path('account/select-scaler/', views.select_scaler, name='select_scaler'),
               path('account/scale-dataset/', views.scale_dataset, name='scale_dataset'),
               path('account/select-ml-model/', views.select_ml_model, name='select_ml_model'),
               path('account/calculate-rul/', views.calculate_rul, name='calculate_rul'),
               path('account/create-report/', views.create_report, name='create_report'),
               path('account/save-report/', views.save_report, name='save_report'),
               path('account/', views.account, name='account'),
               path('logout/', login_required(auth_views.LogoutView.as_view()), name='logout'),
               path('login/', auth_views.LoginView.as_view(), name='login'),
               path('', views.home, name='home'),]