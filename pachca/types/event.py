class Event:
    type:str
    event:str

    def __init__(self, type:str, event:str):
        self.type = type
        self.event = event

    def _is_valid_operand(self, other):
        return (hasattr(other, "type") and
                hasattr(other, "event"))

    def __eq__(self, other):
        if not self._is_valid_operand(other):
            return NotImplemented
        return (self.type == other.type and
                self.event == other.event)
        