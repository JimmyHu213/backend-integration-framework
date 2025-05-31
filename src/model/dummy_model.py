from dataclasses import dataclass


@dataclass
class DummyModel:
    """
    A dummy model class that serves as a placeholder for actual model implementations.
    It can be used for testing or as a base class for more complex models.
    """

    name: str = "DummyModel"
    version: str = "1.0"

    def predict(self, input_data):
        """
        A dummy prediction method that returns a fixed response.
        :param input_data: The input data for prediction.
        :return: A fixed response indicating the prediction.
        """
        return f"Prediction from {self.name} (version {self.version})"

    def train(self, training_data):
        """
        A dummy training method that simulates training on the provided data.
        :param training_data: The data to train on.
        :return: A fixed response indicating the training completion.
        """
        return f"Training completed on {self.name} with provided data."
