from argparse import ArgumentParser, Namespace

from modern_talking.data import download_kpa_2021_data
from modern_talking.evaluation import Metric
from modern_talking.evaluation.f_measure import F1Score, MacroF1Score
from modern_talking.evaluation.manual_errors import ManualErrors
from modern_talking.evaluation.map import MeanAveragePrecision
from modern_talking.evaluation.precision import Precision, MacroPrecision
from modern_talking.evaluation.recall import Recall, MacroRecall
from modern_talking.matchers import UnknownLabelPolicy, Matcher
from modern_talking.pipeline import Pipeline

metrics = [
    MeanAveragePrecision(),
    Precision(),
    MacroPrecision(),
    Recall(),
    MacroRecall(),
    F1Score(),
    MacroF1Score(),
    ManualErrors(),
]


def _prepare_parser(parser: ArgumentParser) -> None:
    matcher_parsers = parser.add_subparsers(dest="matcher")
    parser.add_argument(
        dest="metric",
        type=str,
        choices=[metric.name for metric in metrics],
    )

    all_parser = matcher_parsers.add_parser("all")
    _prepare_all_parser(all_parser)

    none_parser = matcher_parsers.add_parser("none")
    _prepare_none_parser(none_parser)

    random_parser = matcher_parsers.add_parser("random")
    _prepare_random_parser(random_parser)

    term_overlap_parser = matcher_parsers.add_parser("term-overlap")
    _prepare_term_overlap_parser(term_overlap_parser)

    bilstm_parser = matcher_parsers.add_parser("bilstm-glove")
    _prepare_bilstm_parser(bilstm_parser)

    transformers_parser = matcher_parsers.add_parser("transformers")
    _prepare_transformers_parser(transformers_parser)

    parser.add_argument(
        "--test-unknown",
        dest="test_known",
        action="store_false",
        default=False,
    )
    parser.add_argument(
        "--test-known",
        dest="test_unknown",
        action="store_true",
        default=False,
    )


def _prepare_all_parser(parser: ArgumentParser) -> None:
    pass


def _prepare_none_parser(parser: ArgumentParser) -> None:
    pass


def _prepare_random_parser(parser: ArgumentParser) -> None:
    parser.add_argument(
        "--seed",
        dest="seed",
        type=int,
    )


def _prepare_term_overlap_parser(parser: ArgumentParser) -> None:
    parser.add_argument(
        "--stemming",
        dest="stemming",
        action="store_true",
    )
    parser.add_argument(
        "--stop-words",
        dest="stop_words",
        action="store_true",
    )
    parser.add_argument(
        "--custom-stop-words",
        dest="custom_stop_words",
        action="store_true",
    )
    parser.add_argument(
        "--synonyms",
        dest="synonyms",
        action="store_true",
    )
    parser.add_argument(
        "--antonyms",
        dest="antonyms",
        action="store_true",
    )
    parser.add_argument(
        "--language",
        dest="language",
        type=str,
        default="english",
    )


def _prepare_bilstm_parser(parser: ArgumentParser) -> None:
    parser.add_argument(
        "--units",
        dest="units",
        type=int,
        default=16,
        help="Number of units in each BiLSTM module."
    )
    parser.add_argument(
        "--layers", "--depth",
        dest="layers",
        type=int,
        default=1,
        help="Number of BiLSTM layers."
    )
    parser.add_argument(
        "--max-length",
        dest="max_length",
        type=int,
        default=256,
    )
    parser.add_argument(
        "--dropout",
        dest="dropout",
        type=float,
        default=0.3,
    )
    parser.add_argument(
        "--learning-rate", "--learn",
        dest="learning_rate",
        type=float,
        default=1e-5,
    )
    parser.add_argument(
        "--weight-decay", "--decay",
        dest="weight_decay",
        type=float,
        default=1e-4,
    )
    parser.add_argument(
        "--shuffle",
        dest="shuffle",
        type=int,
        default=1000,
    )
    parser.add_argument(
        "--batch-size", "--batch",
        dest="batch_size",
        type=int,
        default=16,
    )
    parser.add_argument(
        "--epochs",
        dest="epochs",
        type=int,
        default=10,
    )
    parser.add_argument(
        "--early-stopping",
        dest="early_stopping",
        action="store_true",
    )
    parser.add_argument(
        "--augment",
        dest="augment",
        type=int,
        default=0,
    )
    parser.add_argument(
        "--unknown-label-policy", "--unknown-label", "--label-policy",
        dest="unknown_label_policy",
        type=UnknownLabelPolicy,
        choices=list(UnknownLabelPolicy),
        default=UnknownLabelPolicy.skip,
    )
    parser.add_argument(
        "--strict",
        dest="unknown_label_policy",
        action="store_const",
        const=UnknownLabelPolicy.strict,
    )
    parser.add_argument(
        "--relaxed",
        dest="unknown_label_policy",
        action="store_const",
        const=UnknownLabelPolicy.relaxed,
    )


def _prepare_transformers_parser(parser: ArgumentParser) -> None:
    parser.add_argument(
        "--model-type", "--type",
        dest="model_type",
        type=str,
        default="bert",
    )
    parser.add_argument(
        "--model-name", "--name",
        dest="model_name",
        type=str,
        default="bert-base-uncased",
    )
    parser.add_argument(
        "--augment",
        dest="augment",
        type=int,
        default=0,
    )
    parser.add_argument(
        "--unknown-label-policy", "--unknown-label", "--label-policy",
        dest="unknown_label_policy",
        type=UnknownLabelPolicy,
        choices=list(UnknownLabelPolicy),
        default=UnknownLabelPolicy.skip,
    )
    parser.add_argument(
        "--strict",
        dest="unknown_label_policy",
        action="store_const",
        const=UnknownLabelPolicy.strict,
    )
    parser.add_argument(
        "--relaxed",
        dest="unknown_label_policy",
        action="store_const",
        const=UnknownLabelPolicy.relaxed,
    )


def train_eval(matcher: Matcher, metric: Metric, test_known: bool) -> None:
    """
    Train/evaluate matcher.
    """
    print(f"Train/evaluate matcher '{matcher.name}' "
          f"with metric '{metric.name}'.")
    if not test_known:
        print("Use validation set for testing.")

    # Download datasets.
    download_kpa_2021_data()

    # Execute pipeline.
    pipeline = Pipeline(matcher, metric)
    result = pipeline.train_evaluate(ignore_test=not test_known)

    print(f"Final score for metric {metric.name} "
          f"on test dataset: {result:.4f}")


def train_eval_cli(args: Namespace) -> None:
    test_known: bool = args.test_known

    metric: Metric = next(filter(lambda m: m.name == args.metric, metrics))

    matcher: Matcher

    if args.matcher == "all":
        from modern_talking.matchers.baselines import AllMatcher
        matcher = AllMatcher()

    elif args.matcher == "none":
        from modern_talking.matchers.baselines import NoneMatcher
        matcher = NoneMatcher()

    elif args.matcher == "random":
        from modern_talking.matchers.baselines import RandomMatcher
        matcher = RandomMatcher(
            seed=args.seed
        )

    elif args.matcher == "term-overlap":
        from modern_talking.matchers.term_overlap import TermOverlapMatcher
        matcher = TermOverlapMatcher(
            stemming=args.stemming,
            stop_words=args.stop_words,
            custom_stop_words=args.custom_stop_words,
            synonyms=args.synonyms,
            antonyms=args.antonyms,
            language=args.language,
        )
    elif args.matcher == "bilstm-glove":
        from modern_talking.matchers.bilstm import BidirectionalLstmMatcher
        matcher = BidirectionalLstmMatcher(
            units=args.units,
            layers=args.layers,
            max_length=args.max_length,
            dropout=args.dropout,
            learning_rate=args.learning_rate,
            weight_decay=args.weight_decay,
            shuffle=args.shuffle,
            batch_size=args.batch_size,
            epochs=args.epochs,
            early_stopping=args.early_stopping,
            augment=args.augment,
            unknown_label_policy=args.unknown_label_policy,
        )
    elif args.matcher == "transformers":
        from modern_talking.matchers.transformers import TransformersMatcher
        matcher = TransformersMatcher(
            model_type=args.model_type,
            model_name=args.model_name,
            augment=args.augment,
            unknown_label_policy=args.unknown_label_policy,
        )
    else:
        raise Exception("Invalid matcher.")

    train_eval(matcher, metric, test_known)


if __name__ == "__main__":
    argument_parser: ArgumentParser = ArgumentParser()
    _prepare_parser(argument_parser)
    train_eval_cli(argument_parser.parse_args())