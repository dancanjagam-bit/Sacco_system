from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


# =========================
# MEMBER MODEL
# =========================
class Member(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15, unique=True)
    email = models.EmailField(unique=True)
    national_id = models.CharField(max_length=20, unique=True)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def total_savings(self):
        return sum(s.amount for s in self.savings.all())

    def total_loans(self):
        return sum(l.balance for l in self.loans.all())

    def __str__(self):
        return f"{self.name} ({self.phone})"


# =========================
# SAVINGS MODEL
# =========================
class Savings(models.Model):
    member = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name="savings"
    )

    amount = models.DecimalField(max_digits=12, decimal_places=2)

    source = models.CharField(max_length=50, default="Cash Deposit")

    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.member.name} - {self.amount}"


# =========================
# LOAN MODEL
# =========================
class Loan(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('REPAID', 'Repaid'),
    )

    member = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name="loans"
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    interest_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=10.00
    )

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="PENDING"
    )

    date_applied = models.DateTimeField(default=timezone.now)

    date_updated = models.DateTimeField(auto_now=True)

    def total_repaid(self):
        return sum(r.amount for r in self.repayments.all())

    def __str__(self):
        return f"{self.member.name} - Loan {self.amount} [{self.status}]"

# =========================
# LOAN REPAYMENT MODEL
# =========================
class LoanRepayment(models.Model):
    loan = models.ForeignKey(
        Loan,
        on_delete=models.CASCADE,
        related_name="repayments"
    )

    amount = models.DecimalField(max_digits=12, decimal_places=2)

    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Repayment {self.amount} (Loan {self.loan.id})"


# =========================
# TRANSACTION LEDGER (IMPORTANT)
# =========================
class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ("DEPOSIT", "Deposit"),
        ("LOAN_REPAYMENT", "Loan Repayment"),
    ]

    member = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name="transactions"
    )

    loan = models.ForeignKey(
        Loan,
        on_delete=models.CASCADE,
        related_name="transactions",
        null=True,
        blank=True
    )

    amount = models.DecimalField(max_digits=12, decimal_places=2)

    type = models.CharField(
        max_length=20,
        choices=TRANSACTION_TYPES,
        default="DEPOSIT"
    )

    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.member.name} - {self.type} {self.amount}"

class Profile(models.Model):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('member', 'Member'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='member')

    def __str__(self):
        return f"{self.user.username} - {self.role}"
