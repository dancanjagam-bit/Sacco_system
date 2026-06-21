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

    def loan_limit(self):
        return self.total_savings() * 3

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

    last_interest_date = models.DateField(null=True, blank=True)

    disbursed_at = models.DateTimeField(null=True, blank=True)

    def total_repaid(self):
        return sum(r.amount for r in self.repayments.all())
    def save(self, *args, **kwargs):
        if not self.pk:   # when loan is first created
            self.balance = self.amount
            self.last_interest_date = self.date_applied.date()
        super().save(*args, **kwargs)
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
    def save(self, *args, **kwargs):
        is_new = self.pk is None  # check if this is first time saving

        super().save(*args, **kwargs)

        # Only apply loan deduction ONCE (when repayment is first created)
        if is_new:
            self.loan.balance -= self.amount

            if self.loan.balance <= 0:
                self.loan.balance = 0
                self.loan.status = "REPAID"

            self.loan.save()
    def __str__(self):
        return f"Repayment {self.amount} (Loan {self.loan.id})"


# =========================
# TRANSACTION LEDGER (IMPORTANT)
# =========================
class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ("DEPOSIT", "Deposit"),
        ("WITHDRAW", "Withdraw"),
        ("LOAN_DISBURSEMENT", "Loan Disbursement"),
        ("LOAN_REPAYMENT", "Loan Repayment"),
        ("INTEREST", "Interest Accrual"),
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
        ("member", "Member"),
        ("teller", "Teller"),
        ("manager", "Manager"),
        ("admin", "Admin"),
    )

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile"
    )

    phone = models.CharField(
        max_length=15,
        blank=True
    )

    national_id = models.CharField(
        max_length=20,
        #unique=True,
        null=True,
        blank=True
    )

    member_number = models.CharField(
        max_length=20,
        #unique=True,
        null=True,
        blank=True
    )

    address = models.TextField(
        blank=True
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default="member"
    )

    is_verified = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def save(self, *args, **kwargs):
        if not self.member_number:
            last_id = Profile.objects.count() + 1
            self.member_number = f"SACCO{last_id:05d}"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} ({self.role})"
