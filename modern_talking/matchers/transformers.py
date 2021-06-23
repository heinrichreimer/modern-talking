from pathlib import Path
from typing import List, Optional

from nlpaug.augmenter.word import WordAugmenter, SynonymAug
from pandas import DataFrame
from simpletransformers.classification import ClassificationModel
from simpletransformers.config.model_args import ClassificationArgs
from torch.cuda import is_available as is_cuda_available

from modern_talking.matchers import Matcher, UnknownLabelPolicy
from modern_talking.model import Dataset, Labels, LabelledDataset, \
    ArgumentKeyPointPair


class TransformersMatcher(Matcher):
    model_type: str
    model_name: str
    augment: int
    unknown_label_policy: UnknownLabelPolicy

    model: ClassificationModel

    def __init__(
            self,
            model_type: str,
            model_name: str,
            augment: int = 0,
            unknown_label_policy: UnknownLabelPolicy = UnknownLabelPolicy.skip,
    ):
        self.model_type = model_type
        self.model_name = model_name
        self.augment = augment
        self.unknown_label_policy = unknown_label_policy

    @property
    def name(self) -> str:
        augment_suffix = f"-augment-{self.augment}" \
            if self.augment > 0 else ""
        unknown_label_policy_suffix = "-relaxed" \
            if self.unknown_label_policy == UnknownLabelPolicy.relaxed \
            else "-strict" \
            if self.unknown_label_policy == UnknownLabelPolicy.strict \
            else ""
        return f"transformers" \
               f"-{self.model_type}" \
               f"-{self.model_name}" \
               f"{augment_suffix}" \
               f"{unknown_label_policy_suffix}"

    def prepare(self) -> None:
        base_dir = (Path(__file__).parent.parent.parent
                    / "data" / "cache" / self.name)

        args = ClassificationArgs()
        args.cache_dir = str((base_dir / "cache").absolute())
        args.output_dir = str((base_dir / "out").absolute())
        args.overwrite_output_dir = True
        args.tensorboard_dir = str((base_dir / "runs").absolute())
        args.best_model_dir = str((base_dir / "best_model").absolute())
        args.regression = True
        args.gradient_accumulation_steps = 16
        args.evaluate_during_training = True

        self.model = ClassificationModel(
            model_type=self.model_type,
            model_name=self.model_name,
            num_labels=1,
            args=args,
            use_cuda=is_cuda_available(),
        )

    def train(
            self,
            train_data: LabelledDataset,
            dev_data: LabelledDataset,
            checkpoint_path: Path,
    ):
        # Load data.
        train_df = _text_pair_df(
            train_data,
            self.augment,
            self.unknown_label_policy,
        )
        train_df.sample(frac=1, random_state=1234)
        dev_df = _text_pair_df(
            dev_data,
            self.augment,
            self.unknown_label_policy,
        )
        dev_df.sample(frac=1, random_state=1234)

        # Train model.
        self.model.train_model(train_df, eval_df=dev_df)

    def predict(self, data: Dataset) -> Labels:
        # Load data.
        pairs = _arg_kp_pairs(data)
        inputs = [[arg.text, kp.text] for arg, kp in pairs]

        # Predict labels.
        predictions, _ = self.model.predict(inputs)

        # Return predictions.
        return {
            (arg.id, kp.id): float(label)
            for (arg, kp), label in zip(pairs, predictions)
        }


def _text_pair_df(
        data: LabelledDataset,
        augment: int,
        unknown_label_policy: UnknownLabelPolicy,
) -> DataFrame:
    pairs = _arg_kp_pairs(data)
    if unknown_label_policy == UnknownLabelPolicy.skip:
        pairs = [
            (arg, kp)
            for (arg, kp) in pairs
            if (arg.id, kp.id) in data.labels.keys()
        ]
    df = DataFrame(columns=["text_a", "text_b", "labels"])

    augmenter: Optional[WordAugmenter] = SynonymAug("wordnet") \
        if augment >= 2 else None
    for arg, kp in pairs:
        current_arg_texts = [arg.text]
        current_kp_texts = [kp.text]
        if augmenter is not None:
            current_arg_texts.extend(augmenter.augment(arg.text, n=augment))
            current_kp_texts.extend(augmenter.augment(kp.text, n=augment))
        for arg_text, kp_text in zip(current_arg_texts, current_kp_texts):
            label: float
            if (arg.id, kp.id) not in data.labels.keys():
                if unknown_label_policy == UnknownLabelPolicy.strict:
                    label = 0
                elif unknown_label_policy == UnknownLabelPolicy.relaxed:
                    label = 1
                else:
                    raise Exception("Broken unknown label policy.")
            else:
                label = data.labels[arg.id, kp.id]
            df.append(
                {
                    "text_a": arg_text,
                    "text_b": kp_text,
                    "labels": label
                },
                ignore_index=True,
            )
    return df


def _arg_kp_pairs(data: Dataset) -> List[ArgumentKeyPointPair]:
    pairs = [
        (arg, kp)
        for arg in data.arguments
        for kp in data.key_points
        if arg.topic == kp.topic and arg.stance == kp.stance
    ]
    return pairs