from dataclasses import dataclass

@dataclass
class BaseTemplate:
    template: str
    def format(self, **kwargs):
        return self.format(**kwargs)