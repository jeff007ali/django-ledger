from datetime import datetime
from django.test import TestCase
from api.models import Transactions, Users
from api.utils import TransactionUtility, UsersUtility


class LedgerTestCases(TestCase):
    def setUp(self):
        jeff_user = Users.objects.create(
            name="Jeff", username="jeff", password="jeff")
        ali_user = Users.objects.create(
            name="Ali", username="ali", password="ali")
        Users.objects.create(
            name="Jafar", username="jafar", password="jafar")
        Transactions.objects.create(transaction_from=jeff_user,
                                    transaction_with=ali_user,
                                    transaction_amount=1500.0,
                                    transaction_status="paid",
                                    transaction_date=TransactionUtility().get_datetime_obj(
                                        "2022-04-10"),
                                    reason="food")
        Transactions.objects.create(transaction_from=ali_user,
                                    transaction_with=jeff_user,
                                    transaction_amount=600.0,
                                    transaction_status="paid",
                                    transaction_date=TransactionUtility().get_datetime_obj(
                                        "2022-04-10"),
                                    reason="travel")
        Transactions.objects.create(transaction_from=jeff_user,
                                    transaction_with=ali_user,
                                    transaction_amount=300.0,
                                    transaction_status="unpaid",
                                    transaction_date=TransactionUtility().get_datetime_obj(
                                        "2022-04-10"),
                                    reason="travel")

    def test_login_success(self):
        user = Users.objects.filter(username="jeff", password="jeff")
        actual = UsersUtility().login("jeff", "jeff")
        expected = {
            "name": user[0].name,
            "balance": user[0].balance,
            "user_id": str(user[0].id),
            "code": 200
        }
        self.assertEqual(actual, expected)

    def test_login_failure(self):
        actual = UsersUtility().login("jeff1", "jeff1")
        expected = {"message": "Wrong username or password!", "code": 401}
        self.assertEqual(actual, expected)

    def test_login_blank(self):
        actual = UsersUtility().login("", "")
        expected = {"message": "Wrong username or password!", "code": 401}
        self.assertEqual(actual, expected)

    def test_get_credit_score_success(self):
        user = Users.objects.filter(username="jeff")
        actual = UsersUtility().get_credit_score(str(user[0].id))
        expected = {"credit_score": 100, "code": 200}
        self.assertEqual(actual, expected)

    def test_get_credit_score_failure(self):
        actual = UsersUtility().get_credit_score("")
        expected = {"message": "Please provide user id", "code": 400}
        self.assertEqual(actual, expected)

    def test_calculate_lend_score(self):
        actual = UsersUtility().calculate_lend_score(1500.0)
        self.assertEqual(actual, 50)

    def test_calculate_borrow_score(self):
        actual = UsersUtility().calculate_borrow_score(600.0)
        self.assertEqual(actual, 50)

    def test_get_transactions_by_user_id_success(self):
        jeff_user = Users.objects.filter(username="jeff")
        ali_user = Users.objects.filter(username="ali")

        actual = TransactionUtility(
        ).get_transactions_by_user_id(str(jeff_user[0].id))

        for x in actual["transactions"]:
            del x["transaction_id"]

        expected = {
            "user_id": str(jeff_user[0].id),
            "transactions": [
                {
                    "transaction_date": "2022-04-10",
                    "transaction_from": str(jeff_user[0].id),
                    "transaction_with": str(ali_user[0].id),
                    "transaction_status": "paid",
                    "transaction_amount": 1500.0,
                    "transaction_type": "lend",
                    "reason": "food"
                },
                {
                    "transaction_date": "2022-04-10",
                    "transaction_from": str(jeff_user[0].id),
                    "transaction_with": str(ali_user[0].id),
                    "transaction_status": "unpaid",
                    "transaction_amount": 300.0,
                    "transaction_type": "lend",
                    "reason": "travel"
                },
                {
                    "transaction_date": "2022-04-10",
                    "transaction_from": str(jeff_user[0].id),
                    "transaction_with": str(ali_user[0].id),
                    "transaction_status": "paid",
                    "transaction_amount": 600.0,
                    "transaction_type": "borrow",
                    "reason": "travel"
                }
            ],
            "code": 200
        }
        self.assertEqual(actual, expected)

    def test_get_transactions_by_user_id_failure(self):
        jafar_user = Users.objects.filter(username="jafar")

        actual = TransactionUtility(
        ).get_transactions_by_user_id(str(jafar_user[0].id))

        expected = {
            "message": "There is no transactions for given user id", "code": 404}
        self.assertEqual(actual, expected)

    def test_format_datetime(self):
        actual = TransactionUtility().format_datetime(datetime.now())
        expected = datetime.now().strftime("%Y-%m-%d")
        self.assertEqual(actual, expected)

    def test_get_datetime_obj(self):
        date_str = datetime.now().strftime("%Y-%m-%d")
        actual = TransactionUtility().get_datetime_obj(date_str)
        expected = datetime.strptime(date_str, "%Y-%m-%d")
        self.assertEqual(actual, expected)

    def test_add_transaction_success(self):
        jeff_user = Users.objects.filter(username="jeff")
        ali_user = Users.objects.filter(username="ali")

        jeff_balance = jeff_user[0].balance
        ali_balance = ali_user[0].balance

        actual = TransactionUtility().add_transaction(str(jeff_user[0].id), str(
            ali_user[0].id), 400.0, "lend", "paid", "2022-04-10", "food")

        new_jeff_balance = jeff_user[0].balance
        new_ali_balance = ali_user[0].balance

        self.assertEqual(jeff_balance - 400.0, new_jeff_balance)
        self.assertEqual(ali_balance + 400.0, new_ali_balance)

        transaction_id = actual["message"].split(" - ")[1]
        expected = {
            "message": "Transaction successfully added - {}".format(transaction_id), "code": 200}
        self.assertEqual(actual, expected)

    def test_add_transaction_failiure_blank_parameter(self):
        actual = TransactionUtility().add_transaction(
            "", "", 400.0, "lend", "paid", "2022-04-10", "food")

        expected = {
            "message": "Please provide transaction from user id", "code": 400}
        self.assertEqual(actual, expected)

    def test_add_transaction_failiure_user_does_not_exists(self):
        jeff_user = Users.objects.filter(username="jeff")

        actual = TransactionUtility().add_transaction(
            str(jeff_user[0].id), "64bf6cc4-0ed9-4e52-a450-605574334641", 400.0, "lend", "paid", "2022-04-10", "food")

        expected = {
            "message": "Transaction With User does not exist", "code": 404}
        self.assertEqual(actual, expected)

    def test_mark_transaction_paid_success(self):
        transaction = Transactions.objects.filter(transaction_status="unpaid")
        transaction_id = str(transaction[0].id)
        actual = TransactionUtility().mark_transaction_paid(transaction_id)

        expected = {
            "message": "Transaction successfully updated - {}".format(transaction_id), "code": 200}
        self.assertEqual(actual, expected)

    def test_mark_transaction_paid_failure_blank_parameter(self):
        actual = TransactionUtility().mark_transaction_paid("")

        expected = {"message": "Please provide transaction id", "code": 400}
        self.assertEqual(actual, expected)

    def test_mark_transaction_paid_failure_transaction_does_not_exists(self):
        actual = TransactionUtility().mark_transaction_paid(
            "64bf6cc4-0ed9-4e52-a450-605574334641")

        expected = {
            "message": "Given transaction id does not exists", "code": 404}
        self.assertEqual(actual, expected)
