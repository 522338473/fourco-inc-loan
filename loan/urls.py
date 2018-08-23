from django.urls import path

from loan.views import login, banner, product
from loan.common import *

handler404 = page_not_found
urlpatterns = [
    path('login', login.login, name='login'),
    path('send/code', login.sendCode, name='sendCode'),
    path('u/user/<int:uid>', login.editUserInfo, name='editUserInfo'),
    path('u/user/<int:uid>/detail', login.getUserInfo, name='getUserInfo'),
    path('banner/list', banner.getBannerList, name='bannerList'),
    path('u/banner/<int:bannerId>', banner.getBannerDetail, name='getBannerDetail'),
    path('u/product/list', product.getProductList, name='getProductList'),
    path('u/product/<int:productId>/detail', product.getProductDetail, name='getProductDetail'),
    path('u/recommend/statistics', product.recommendStatistics, name='recommendStatistics'),
]
