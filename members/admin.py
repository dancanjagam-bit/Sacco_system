from django.contrib import admin
from .models import Member, Loan, Transaction


# =========================
# TRANSACTION INLINE (inside Loan)
# =========================
class TransactionInline(admin.TabularInline):
    model = Transaction
    extra = 0
    fields = ("amount", "type", "date")
    readonly_fields = ("date",)


# =========================
# MEMBER ADMIN
# =========================
@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "email", "national_id", "balance")
    search_fields = ("name", "phone", "email", "national_id")


# =========================
# LOAN ADMIN
# =========================
@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ("member", "amount", "balance", "status", "date_applied")
    list_filter = ("status", "date_applied")
    search_fields = ("member__name", "member__phone", "member__email")
    inlines = [TransactionInline]


# =========================
# TRANSACTION ADMIN
# =========================
@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("member", "amount", "type", "loan", "date")
    list_filter = ("type", "date")
    search_fields = ("member__name", "member__phone", "member__email")
