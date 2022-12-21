from lib2to3.pygram import pattern_grammar
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('mapeamento/', views.mapeamento, name="mapeamento"),
    path('sobre-os-ods/', views.sobre_ods, name="sobre-ods"),
    path('sobre-a-ferramenta/', views.sobre_ferramenta, name="sobre-a-ferramenta"),
    path('sobre-nos/', views.sobre_nos, name="sobre-nos"),
    path('noticias/', views.noticias, name="noticias"),
    path('upload/', views.upload, name="upload"),
    path('resultado-csv/', views.map_csv, name="resultado-csv"),
    path('resultado-pdf/', views.map_pdf, name="resultado-pdf"),
    path('contact/', views.contact, name='contact'),
]