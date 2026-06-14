from django.urls import path, include
from django.contrib import admin
from django.urls import path, include
from members.views import home
from rest_framework import routers
from members.views_api import MemberViewSet, TransactionViewSet, LoanViewSet

router = routers.DefaultRouter()
router.register(r'members', MemberViewSet)
router.register(r'transactions', TransactionViewSet)
router.register(r'loans', LoanViewSet)

urlpatterns = [
    path('', home),  # root path
    path('api/', include(router.urls)),
    path('admin/', admin.site.urls),
    path("members/", include("members.urls")),
]
