class Body:
    def __init__(self, name: str = "auto") -> None:
        if name == "auto":
            name = f"Body_{id(self)}"
        self.name = name

        # === Body ===
        self._hp: int = 0
