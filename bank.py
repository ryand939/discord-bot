from config import BotConfig

class Bank():
    
    # bank class that makes use of my config.py file and has more specific features

    def __init__(self):
        self.bank = BotConfig("./resources/storage/economy.json")

    def withdraw(self, guildID, userID, amount):
        balance = self.bank.get(str(guildID), str(userID))
        if balance is None or (balance - amount) < 0:
            return False
        else:
            # has enough balance
            self.bank.set(str(guildID), str(userID), amount * (-1), relative=True)
            return True

    def deposit(self, guildID, userID, amount):
            self.bank.set(str(guildID), str(userID), amount, relative=True)


    def balance(self, guildID, userID):
        balance = self.bank.get(str(guildID), str(userID))
        if balance is None: balance = 0
        return balance

    def remove(self, guildID, userID):
        self.bank.clear(str(guildID), str(userID))

    def leaderboard(self, guildID):
        return self.bank.sorted_list(str(guildID))

