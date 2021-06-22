from os import environ

from tensorflow import distribute, config, tpu


def is_running_on_colab():
    return 'COLAB_GPU' in environ


def gpu_count() -> int:
    return int(environ['COLAB_GPU'])


def setup_colab_tpu():
    """
    Setup TPUs for usage in Google Colab, only if running on Colab.
    """
    if not is_running_on_colab() or gpu_count() >= 1:
        # Skip setup because either not running on Colab or on GPU environment.
        return

    # Special resolver for Google Colaboratory.
    resolver = distribute.cluster_resolver.TPUClusterResolver(tpu='')
    config.experimental_connect_to_cluster(resolver)
    tpu.experimental.initialize_tpu_system(resolver)