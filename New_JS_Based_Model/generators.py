# generators.py

from model import StarCoder, ModelBase

def model_factory(model_name: str, port: str = "") -> ModelBase:
    if "starcoder" in model_name.lower():
        return StarCoder(port)
    else:
        raise ValueError(f"Model {model_name} is not supported.")
