from django.contrib import admin
from .models import Member, Loan, Transaction

class TransactionInline(admin.TabularInline):
    model = Transaction
    extra = 0   # don’t show empty rows by default
    fields = ("amount", "source", "date")  # columns to display
    readonly_fields = ("date",)  # date auto-set, not editable

@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "email", "national_id", "balance")
    search_fields = ("name", "phone", "email", "national_id")

@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ("member", "amount", "balance", "status", "date_applied", "date_updated")
    list_filter = ("status", "date_applied")
    search_fields = ("member__name", "member__phone", "member__email")
    inlines = [TransactionInline]   # 👈 show transactions inline

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("member", "amount", "source", "loan", "date")
    list_filter = ("source", "date")
    search_fields = ("member__name", "member__phone", "member__email")

