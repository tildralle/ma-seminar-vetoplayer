class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class Sprayer(Colors):
    def __init__(self):
        super().__init__()
        self.colors = Colors.__dict__

    def dye(self, message, color):
        dyed_message = f"{self.colors[color]}{message}{self.ENDC}"
        return dyed_message

    def fail(self, message):
        dyed_message = f"{self.FAIL}{message}{self.ENDC}"
        return dyed_message

    def success(self, message):
        dyed_message = f"{self.OKGREEN}{message}{self.ENDC}"
        return dyed_message