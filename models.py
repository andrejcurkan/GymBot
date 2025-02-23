# models.py
class Client:
    def __init__(self, chat_id, first_name, last_name, subscription_type, balance, is_wholesale):
        self.chat_id = chat_id
        self.first_name = first_name
        self.last_name = last_name
        self.subscription_type = subscription_type
        self.balance = balance
        self.is_wholesale = is_wholesale