from django.urls import path
from . import views
urlpatterns = [
    path('', frontend),  # root serves React dashboard
    path('api/', include(router.urls)),
    path('admin/', admin.site.urls),
    path("bank/callback/", views.bank_callback, name="bank_callback"),
    path("mpesa/callback/", views.mpesa_callback, name="mpesa_callback"),
    path("mpesa/repay/", views.mpesa_repay_callback, name="mpesa_repay_callback"),
    path("deposit/", views.deposit, name="deposit"),
    path("balance/<str:phone>/", views.balance, name="balance"),
    path("loan/apply/", views.apply_loan, name="apply_loan"),
    path("loan/approve/<int:loan_id>/", views.approve_loan, name="approve_loan"),
    path("loan/repay/", views.repay_loan, name="repay_loan"),
]

