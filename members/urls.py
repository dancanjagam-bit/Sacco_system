from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

# 🔐 JWT imports (NEW)
from members.views_auth import MyTokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView

from sacco_system.views import (
    frontend,
    bank_callback,
    mpesa_callback,
    mpesa_repay_callback,
    deposit,
    balance,
    apply_loan,
    approve_loan,
    repay_loan,
)

from members.views_api import (
    MemberViewSet,
    TransactionViewSet,
    LoanViewSet,
    SavingsViewSet,
)

# DRF router for API endpoints
router = DefaultRouter()
router.register(r'members', MemberViewSet)
router.register(r'transactions', TransactionViewSet)
router.register(r'loans', LoanViewSet)
router.register(r'savings', SavingsViewSet)

urlpatterns = [
    path('', frontend, name="frontend"),

    # =========================
    # 🔐 AUTH (NEW JWT ROUTES)
    # =========================
    path('api/login/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # =========================
    # 📡 API ROUTES
    # =========================
    path('api/', include(router.urls)),

    # =========================
    # 🛡️ ADMIN
    # =========================
    path('admin/', admin.site.urls),

    # =========================
    # 💳 SACCO CALLBACKS
    # =========================
    path("bank/callback/", bank_callback, name="bank_callback"),
    path("mpesa/callback/", mpesa_callback, name="mpesa_callback"),
    path("mpesa/repay/", mpesa_repay_callback, name="mpesa_repay_callback"),

    # =========================
    # 💰 SACCO CORE ACTIONS
    # =========================
    path("deposit/", deposit, name="deposit"),
    path("balance/<str:phone>/", balance, name="balance"),

    path("loan/apply/", apply_loan, name="apply_loan"),
    path("loan/approve/<int:loan_id>/", approve_loan, name="approve_loan"),
    path("loan/repay/", repay_loan, name="repay_loan"),
]
