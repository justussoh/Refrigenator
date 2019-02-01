import datetime #date time functions
from ocr import *

class Fridge:
    def __init__(self):
        self.foods = []

        #Values initialised for demonstration
        self.categories = {"FRUITS": ["APPLE", "ORANGE", "BANANA", "Others"], "VEGETABLES": ["TOMATO", "POTATO", "CABBAGE", "SPINACH", "Others"], "MEAT": ["BEEF", "PORK", "CHICKEN", "Others"],
                           "DAIRY PRODUCTS": ["MILK", "CHOCOLATE MILK", "CHEESE", "Others"], "OTHERS": ["DRINKS", "CURRY", "Others"]}

        self.items = {"APPLE": "FRUITS", "ORANGE": "FRUITS", "BANANA": "FRUITS", "TOMATO": "VEGETABLES", "POTATO": "VEGETABLES", "CABBAGE": "VEGETABLES",
                      "SPINACH": "VEGETABLES", "BEEF": "MEAT", "PORK": "MEAT", "CHICKEN": "MEAT", "MILK": "DAIRY PRODUCTS", "CHOCOLATE MILK": "DAIRY PRODUCTS",
                      "CHEESE": "DAIRY PRODUCTS", "DRINKS": "OTHERS"}

    ## GETTERS
    def get_food(self):
        return self.foods

    def get_food_names(self):
        return list(map(lambda x: x.get_name(), self.get_food()))

    def get_expired(self):
        return list(filter(lambda x: x.get_status(), self.get_food()))

    def get_not_expired(self):
        return list(filter(lambda x: not x.get_status(), self.get_food()))

    def get_category(self, category):
        #List out all the food belonging to a category
        #This is for /add - when adding a food belonging to a category,
        #it will pull out the past options as an option list
        return self.categories[category]

    def get_object_by_id(self, id):
        for food in self.get_food():
            if food.get_id() == id:
                return food

    ## SETTERS
    def add_entry_to_cat(self, name, category):
        #Adds new names to existing categories
        self.categories[category].insert(-1,name)
        self.items[name] = category

    def add_food(self, other):
        #For /add command. Takes in a food object and adds it to the fridge
        #Check if there are existing food with the same name as the added food
        # if other.get_name() in self.get_food_names():
        #     existing = list(filter(lambda x: x.get_name() == other.get_name(),
        #                            self.get_food()))
        #     # If yes, loop through all the food with the same name
        #     for food in existing:
        #         print("ALERT!")
        #         """
        #         INSERT CODE HERE - call a function that triggers an alert
        #         prompt if the previous entry had been consumed
        #         if yes: call remove_food
        #         """
        #         pass
        self.foods.append(other)

    def remove_food(self, id):
        ##For the /remove command. Takes in the id, removes item from fridge
        food_obj = self.get_object_by_id(id)
        self.foods.remove(food_obj)

    def sort_by_expiry(self):
        self.foods.sort(key = lambda x: x.get_expiry_date())

    def add_bulk(self, lst):
        res = []
        for word in lst:
            if word in self.items:
                res.append((word, self.items[word]))
        return res

    def clear(self):
        #For the /clear command - Resets the whole fridge (Probably need some confirmation
        #prompt
        self.foods.clear()

    def print_by_category(self, category):
        ##For the /remove command - Returns a list that can be printed as options
        filtered = list(filter(lambda x: x.get_category() == category, self.get_food()))
        ids = list(map(lambda x: x.get_id(), filtered))
        return ids

    def daily_update(self):
        text = ""
        expired_food = list(filter(lambda x: x.get_status(), self.get_food()))
        if expired_food: #If there is expired food
            text += "The following food are expired:\nName of food - Expired by"
            for food in self.get_expired():
                text += (food.get_name() + " - " + str(-1 * food.get_remaining_days()) + "\n")
            text += "\n"

        expiring = list(filter(lambda x: 0 <= x.get_remaining_days() <= 2,
                        self.get_food())) #List of food that are not expired
        if expiring: #If there are expiring things
            text += "Following things are expiring within 2 days:\n"
            text += "Name of food - Days before expiry\n"
            for food in expiring:
                text += (food.get_name() + " - " + str(food.get_remaining_days()) + "\n")
        return text

    def print_full_fridge(self):
        if not self.get_food():
            return "Fridge is empty"
        ## For the /display command - Shows all the food in the fridge
        self.sort_by_expiry()
        expired_food = self.get_expired() #List of expired food
        text = ""

        if expired_food: #If there is expired food
            text += "The following food are expired:\nName of food - Expired by"
            for food in self.get_expired():
                text += (food.get_name() + " - " + str(-1 * food.get_remaining_days()) + "\n")
            text += "\n"

        not_expired = self.get_not_expired() #List of food that are not expired
        if not_expired: #If there are non-expired food
            text += "Remaining food:\n"
            text += "Name of food - Days before expiry\n"
            for food in self.get_not_expired():
                text += (food.get_name() + " - " + str(food.get_remaining_days()) + "\n")
        return text

class Food:
    def __init__(self, name, expiry, category):
        #Contains name, category, date_entered, date_expiring (based on expiry),
        #days_left, expired_status (boolean T/F)

        self.name = name
        self.category = category

        today = datetime.datetime.now() #Unformatted date
        year = str(today.year)
        month = str(today.month)
        day = str(today.day)
        hour = str(today.hour)
        minute = today.minute
        if minute < 10:
            minute = "0" + str(minute)
        else:
            minute = str(minute)

        self.id = f"{name} bought on {day}/{month}/{year[2:]} {hour}:{minute}"

        self.start_date = today
        expiry = today + datetime.timedelta(days = expiry)
        year_expiry = expiry.year
        month_expiry = expiry.month
        day_expiry = expiry.day

        self.expiry_date = datetime.datetime(year_expiry, month_expiry, day_expiry, 23, 59)

        self.days_left = self.expiry_date - self.start_date #How many days left before expiry
        self.alert_days = 2 #No of days ahead to warn about expiring food
        self.expired = False #Is food expired?

    def get_name(self):
        return self.name

    def get_expiry_date(self):
        return self.expiry_date

    def get_category(self):
        return self.category

    def get_id(self):
        return self.id

    def get_remaining_days(self):
        #Need some way to active this command
        today = datetime.datetime.now()
        self.days_left = (self.get_expiry_date() - today).days
        if self.days_left < 0:
            self.expired = True
        return self.days_left

    def get_status(self):
        return self.expired



##
##
##tomato = Food("TOMATO", 0, 'FRUITS')
##potato = Food("POTATO", 3, 'VEGETABLES')
##fridge = Fridge()
##fridge.add_food(tomato)
##fridge.add_food(potato)
##potato2 = Food("POTATO", 4, 'VEGETABLES')
##lettuce = Food("LETTUCE", 2, 'VEGETABLES')
##spinach = Food("SPINACH", 7, "VEGETABLES")
##fridge.add_food(potato2)
##fridge.add_food(lettuce)
##fridge.add_food(spinach)
