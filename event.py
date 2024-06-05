import random

class Event:
    def execute(self, GS, PS, parent):
        raise NotImplementedError("Subclasses should implement this method")

    def show_message(self, parent, title, message):
        parent.display_event_message(title, message)

class NewCoinEvent(Event):
    def execute(self, GS, PS, parent):
        coin_name = f"Coin{len(GS.coins) + 1}"
        GS.add_new_coin(coin_name)
        self.show_message(parent, "New Coin", f"A new coin {coin_name} has been listed!")

class SuddenRiseEvent(Event):
    def execute(self, GS, PS, parent):
        if not GS.coins:
            return
        coin = random.choice(GS.coins)
        if not coin.delisted:
            coin.apply_price_modifier(1.5)
            self.show_message(parent, "Sudden Rise", f"The coin {coin.name} has suddenly risen by 50%!")

class SuddenFallEvent(Event):
    def execute(self, GS, PS, parent):
        if not GS.coins:
            return
        coin = random.choice(GS.coins)
        if not coin.delisted:
            coin.apply_price_modifier(0.5)
            self.show_message(parent, "Sudden Fall", f"The coin {coin.name} has suddenly fallen by 50%!")

class DelistEvent(Event):
    def execute(self, GS, PS, parent):
        if not GS.coins:
            return
        coin = random.choice(GS.coins)
        if not coin.delisted:
            coin.delisted = True
            coin.prices[1][-1] = 0
            self.show_message(parent, "Delisted", f"The coin {coin.name} has been delisted!")

class EventSystem:
    def __init__(self, GS, PS, config_loader):
        self.GS = GS
        self.PS = PS
        self.config_loader = config_loader
        self.event_interval = int(config_loader.get_setting('Events', 'EventInterval'))
        self.events = []
        self.day_counter = 0
        self.load_events()

    def load_events(self):
        self.add_event(NewCoinEvent(), float(self.config_loader.get_setting('Events', 'NewCoinProbability')))
        self.add_event(SuddenRiseEvent(), float(self.config_loader.get_setting('Events', 'SuddenRiseProbability')))
        self.add_event(SuddenFallEvent(), float(self.config_loader.get_setting('Events', 'SuddenFallProbability')))
        self.add_event(DelistEvent(), float(self.config_loader.get_setting('Events', 'DelistProbability')))

    def add_event(self, event, probability):
        self.events.append((event, probability))

    def check_for_event(self, parent):
        self.day_counter += 1
        if self.day_counter % self.event_interval == 0:
            event = self.select_event()
            if event:
                event.execute(self.GS, self.PS, parent)

    def select_event(self):
        total = sum(prob for _, prob in self.events)
        r = random.uniform(0, total)
        upto = 0
        for event, prob in self.events:
            if upto + prob >= r:
                return event
            upto += prob
        return None
