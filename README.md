## Steps to Run Project:
***
1. Clone this Git repo
2. Make sure you have installed `docker` and `docker-compose`
3. Build docker-compose `docker-compose build`
4. Run docker container `docker-compose up -d`
5. Now, server is up and available at http://0.0.0.0:8000/
---

## API endpoints:
***
> Postman collection is available in Repo for testing

APIs ~~are~~ were live at `http://0.0.0.0:8000/`

1. `/api/login` :  It accepts username and password and returns true if exists
2. `/api/get_transactions` : fetches all the transactions for the user (he can be either borrower or lender).
3. `/api/add_transaction` :  it accepts { user_id, transaction_id (random hash), transaction_type (borrow/lend), transaction_amount (negative, positive), transaction_date, transaction_status (paid/unpaid), transaction_with (user_id) }
4. `/api/mark_paid` : it accepts transaction id  and changes transaction status.
5. `api/credit_score` :  it sends the user’s credit score based on his/her transaction history.


## Users details for testing
***

|Name|Username|Password|
|----|--------|--------|
|John|john|john|
|Bob|bob|bob|
|Adam|adam|adam|

- Use theses creds in login API and you will get user ids. You can use user id to add transaction, get transactions and get the credit score.
- You can get transaction id from get transaction API response and use transaction id to mark transaction paid using API.