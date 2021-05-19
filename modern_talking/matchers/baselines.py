from random import Random

from modern_talking.matchers import UntrainedMatcher
from modern_talking.model import Labels, Dataset, KeyPoint, Argument, Label


class AllMatcher(UntrainedMatcher):
    """
    Match arguments with key points if they share the same topic and stance.
    """

    name = "all"

    def predict(self, data: Dataset) -> Labels:
        return {
            (arg.id, kp.id): 1
            for (arg, kp) in data.argument_key_point_pairs
        }


class NoneMatcher(UntrainedMatcher):
    """
    Match no argument key point pair.
    """

    name = "none"

    def predict(self, data: Dataset) -> Labels:
        return {
            (arg.id, kp.id): 0
            for (arg, kp) in data.argument_key_point_pairs
        }


class RandomMatcher(UntrainedMatcher):
    """
    Match argument key point pairs randomly if they share topic and stance.
    """

    name = "random"
    random: Random

    def __init__(self, seed=None):
        self.random = Random(seed) if seed is not None else Random()

    def predict(self, data: Dataset) -> Labels:
        return {
            (arg.id, kp.id): self.random.uniform(0, 1)
            for (arg, kp) in data.argument_key_point_pairs
        }
