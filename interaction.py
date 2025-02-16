class Interaction:
    def __init__(self, user=None, llm=None):
        self.user = user
        self.llm = llm

    def __str__(self): # Optional: for simple debugging/printing
        user_text = f"User: {self.user}" if self.user else ""
        llm_text = f"Llama: {self.llm}" if self.llm else ""
        return user_text + "\n" + llm_text

    def getUserStr(self):
        return self.user

    def getLLMStr(self):
        return self.llm