from django.shortcuts import render

# Create your views here.
import requests
import json
from .models import Member, Transaction, Loan
import base64
from datetime import datetime
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.shortcuts import render

def frontend(request):
    return render(request, "index.html")

def home(request):
    return HttpResponse("Welcome to the SACCO System API")

# --- Bank Callback (Deposit) ---
@csrf_exempt
def bank_callback(request):
    """
    Simulated callback from bank API when deposit is made.
    Expected JSON:
    {
      "account_number": "123456789",
      "reference": "0722000000",   # member phone or ID
      "amount": 5000,
      "narration": "Deposit via Bank"
    }
    """
    data = json.loads(request.body)
    phone = data.get("reference")
    amount = float(data.get("amount"))

    try:
        member = Member.objects.get(phone=phone)
        member.balance += amount
        member.save()

        Transaction.objects.create(member=member, amount=amount, source="Bank")

        return JsonResponse({"message": "Bank deposit successful", "balance": member.balance})
    except Member.DoesNotExist:
        return JsonResponse({"error": "Member not found"}, status=404)


# --- Generate Access Token ---
def get_access_token():
    consumer_key = "YOUR_CONSUMER_KEY"
    consumer_secret = "YOUR_CONSUMER_SECRET"
    url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    response = requests.get(url, auth=(consumer_key, consumer_secret))
    return response.json()["access_token"]

# --- Initiate STK Push ---
@csrf_exempt
def stk_push(request):
    data = request.json if hasattr(request, "json") else request.POST
    phone = data.get("phone")
    amount = int(data.get("amount"))

    access_token = get_access_token()
    headers = {"Authorization": f"Bearer {access_token}"}

    shortcode = "YOUR_PAYBILL"
    passkey = "YOUR_PASSKEY"
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    password = base64.b64encode((shortcode + passkey + timestamp).encode()).decode()

    payload = {
        "BusinessShortCode": shortcode,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone,
        "PartyB": shortcode,
        "PhoneNumber": phone,
        "CallBackURL": "https://yourdomain.com/members/mpesa/callback/",
        "AccountReference": "SACCO Deposit",
        "TransactionDesc": "Deposit to SACCO"
    }

    response = requests.post("https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest",
                             json=payload, headers=headers)

    return JsonResponse(response.json())

# --- Handle Callback ---
@csrf_exempt
def mpesa_callback(request):
    data = json.loads(request.body)
    phone = data["Body"]["stkCallback"]["CallbackMetadata"]["Item"][4]["Value"]
    amount = data["Body"]["stkCallback"]["CallbackMetadata"]["Item"][0]["Value"]

    try:
        member = Member.objects.get(phone=phone)
        member.balance += amount
        member.save()

        Transaction.objects.create(member=member, amount=amount, source="M-Pesa STK")

        return JsonResponse({"message": "Deposit successful", "balance": member.balance})
    except Member.DoesNotExist:
        return JsonResponse({"error": "Member not found"}, status=404)


# --- Get Access Token ---
def get_access_token():
    consumer_key = "YOUR_CONSUMER_KEY"
    consumer_secret = "YOUR_CONSUMER_SECRET"
    url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    response = requests.get(url, auth=(consumer_key, consumer_secret))
    return response.json()["access_token"]

# --- M-Pesa Callback (Deposit) ---
@csrf_exempt
def mpesa_callback(request):
    data = json.loads(request.body)
    phone = data["Body"]["stkCallback"]["CallbackMetadata"]["Item"][4]["Value"]
    amount = data["Body"]["stkCallback"]["CallbackMetadata"]["Item"][0]["Value"]

    try:
        member = Member.objects.get(phone=phone)
        member.balance += amount
        member.save()

        Transaction.objects.create(member=member, amount=amount, source="M-Pesa")

        return JsonResponse({"message": "Deposit successful", "balance": member.balance})
    except Member.DoesNotExist:
        return JsonResponse({"error": "Member not found"}, status=404)

# --- M-Pesa Callback (Loan Repayment) ---
@csrf_exempt
def mpesa_repay_callback(request):
    data = json.loads(request.body)
    phone = data["Body"]["stkCallback"]["CallbackMetadata"]["Item"][4]["Value"]
    amount = data["Body"]["stkCallback"]["CallbackMetadata"]["Item"][0]["Value"]

    try:
        member = Member.objects.get(phone=phone)
        loan = Loan.objects.filter(member=member, status="APPROVED").last()
        if not loan:
            return JsonResponse({"error": "No active loan"}, status=404)

        loan.balance -= amount
        if loan.balance <= 0:
            loan.status = "REPAID"
            loan.balance = 0
        loan.save()

        Transaction.objects.create(member=member, amount=amount, source="Loan Repayment")

        return JsonResponse({"message": "Repayment successful", "remaining_balance": loan.balance, "status": loan.status})
    except Member.DoesNotExist:
        return JsonResponse({"error": "Member not found"}, status=404)


@csrf_exempt
def deposit(request):
    if request.method == "POST":
        data = json.loads(request.body)
        phone = data.get("phone")
        amount = float(data.get("amount"))

        try:
            member = Member.objects.get(phone=phone)
            member.balance += amount
            member.save()

            Transaction.objects.create(member=member, amount=amount, source="Deposit")

            return JsonResponse({"message": "Deposit successful", "balance": member.balance})
        except Member.DoesNotExist:
            return JsonResponse({"error": "Member not found"}, status=404)

@csrf_exempt
def balance(request, phone):
    try:
        member = Member.objects.get(phone=phone)
        return JsonResponse({"name": member.name, "balance": member.balance})
    except Member.DoesNotExist:
        return JsonResponse({"error": "Member not found"}, status=404)
@csrf_exempt
def apply_loan(request):
    if request.method == "POST":
        data = json.loads(request.body)
        phone = data.get("phone")
        amount = float(data.get("amount"))

        try:
            member = Member.objects.get(phone=phone)

            # Simple eligibility check: must have at least 50% of loan amount in savings
            if member.balance < (amount * 0.5):
                return JsonResponse({"error": "Insufficient savings for loan eligibility"}, status=400)

            loan = Loan.objects.create(member=member, amount=amount, balance=amount, status="PENDING")
            return JsonResponse({"message": "Loan application submitted", "loan_id": loan.id, "status": loan.status})
        except Member.DoesNotExist:
            return JsonResponse({"error": "Member not found"}, status=404)


@csrf_exempt
def approve_loan(request, loan_id):
    try:
        loan = Loan.objects.get(id=loan_id)
        loan.status = "APPROVED"
        loan.save()
        return JsonResponse({"message": "Loan approved", "loan_id": loan.id, "status": loan.status})
    except Loan.DoesNotExist:
        return JsonResponse({"error": "Loan not found"}, status=404)


@csrf_exempt
def repay_loan(request):
    if request.method == "POST":
        data = json.loads(request.body)
        loan_id = data.get("loan_id")
        amount = float(data.get("amount"))

        try:
            loan = Loan.objects.get(id=loan_id)
            if loan.status != "APPROVED":
                return JsonResponse({"error": "Loan not active"}, status=400)

            loan.balance -= amount
            if loan.balance <= 0:
                loan.status = "REPAID"
                loan.balance = 0
            loan.save()

            return JsonResponse({"message": "Repayment successful", "remaining_balance": loan.balance, "status": loan.status})
        except Loan.DoesNotExist:
            return JsonResponse({"error": "Loan not found"}, status=404)
