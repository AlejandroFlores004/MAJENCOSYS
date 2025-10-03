from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views    
from .views import startpage, dashboard, loginPage, database_tools, download_backup, userInfo, logoutUser, dashboardProject
from .forms import CustomSetPasswordForm,CustomPasswordResetForm

urlpatterns = [
    # ---- Rutas principales ----
    path('', startpage, name='startpage'),
    path('dashboard/', dashboard, name='dashboard'),
    path('login/', loginPage, name='log'),
    path('logout/', logoutUser, name='logout'),
    path('admon_usuarios/', include('user.urls'), name='user'),
    path("herramientas_basedatos/", database_tools, name="database_tools"),
    path("herramientas_basedatos/download/", download_backup, name="download_backup"),
    path('admon_project',include('project.urls'),name='project'),
    path('usuario_informacion', userInfo, name="infoUser"),
    path('dashboard/project/<int:pk>/', dashboardProject, name='dashboardProject'),
    path('dashboard/project/<int:pk>/catalogos/', include('activity_catalogs.urls'), name='activity_catalogs'),
    path('dashboard/project/<int:pk>/infraestructura/', include('activity_infraestructura.urls'), name='activity_infraestructura'),
    path('dashboard/project/<int:pk>/alcantarillado/', include('activity_alcantarillado.urls'), name='activity_alcantarillado'),
    path('dashboard/project/<int:pk>/obras_mitigacion/', include('activity_obras_mitigacion.urls'), name='activity_obras_mitigacion'),
    path('dashboard/project/<int:pk>/creacion_mantenimiento_red_vial/', include('activity_cmrv.urls'), name='activity_cmrv'),
    

    # ---- Rutas para el cambio de contraseña ----
     path('reset-password/', 
          auth_views.PasswordResetView.as_view(template_name='registration/password_reset_form.html',
          form_class=CustomPasswordResetForm), 
          name='password_reset'),
     path('reset-password/done/', 
          auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), 
          name='password_reset_done'),
     path('reset-password/<uidb64>/<token>/',
          auth_views.PasswordResetConfirmView.as_view(
          template_name='registration/password_reset_confirm.html',
          form_class=CustomSetPasswordForm),
          name='password_reset_confirm'),
     path('reset-password/complete/', 
          auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), 
          name='password_reset_complete'),

     # ---- Administradores de apps ----
    path('admon_usuarios/',include('user.urls'),name='user'),
    path('admon_project/', include('project.urls')),


]
  

