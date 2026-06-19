from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from django.views.generic import TemplateView
from members.views_auth import MyTokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView

from members.views_api import (
    MemberViewSet,
    TransactionViewSet,
    LoanViewSet,
    SavingsViewSet,
)

router = routers.DefaultRouter()
router.register(r'members', MemberViewSet)
router.register(r'transactions', TransactionViewSet)
router.register(r'loans', LoanViewSet)
router.register(r'savings', SavingsViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name="index.html")),

    path('api/login/', MyTokenObtainPairView.as_view(), name='login'),
    path('api/token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
