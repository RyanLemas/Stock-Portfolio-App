from django.urls import path
from django.contrib.auth.views import LogoutView
from .views import stock_operations,portfolio_list


urlpatterns = [
    path('', portfolio_list, name='default_view'),
    #path('', stock_operations, name='default_view'),
    #path('accounts/stock_operations/', stock_operations, name='stock_operations_list'),
    path('portfolio_list/', portfolio_list, name='portfolio'),
    path('stock_operations/', stock_operations, name='stock_operations'),
    path('accounts/portfolio_list/', portfolio_list, name='portfolio_list'),
]