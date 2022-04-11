from django.urls import path
from .views import *


urlpatterns = [
    path("login", UserView.as_view()),
    path("get_transactions", TransactionView.as_view()),
    path("add_transaction", TransactionView.as_view()),
    path("mark_paid", TransactionView.as_view()),
    path("credit_score", UserView.as_view()),
]
