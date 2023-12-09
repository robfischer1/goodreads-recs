import pathlib
from datetime import datetime

from wrecksys.utils import import_tensorflow
tf, keras = import_tensorflow()


class SaveCheckpoint(keras.callbacks.Callback):
    def __init__(self, checkpoint_manager):
        super().__init__()
        self.checkpoint_manager = checkpoint_manager

    # noinspection PyProtectedMember
    def on_epoch_end(self, epoch, logs=None):
        step = int(self.checkpoint_manager._step_counter)
        self.checkpoint_manager.save(checkpoint_number=step)


def callback_list(model: keras.Model, model_dir: pathlib.Path) -> list:
    logs_dir = model_dir / 'logs/' / datetime.now().strftime("%Y%m%d-%H%M%S")
    checkpoint_dir = model_dir / 'checkpoints/'

    logs_dir.parent.mkdir(exist_ok=True)
    checkpoint_dir.parent.mkdir(exist_ok=True)

    stop_early = keras.callbacks.EarlyStopping(monitor='Global_Softmax_Cross_Entropy', patience=3)
    save_tensorboard = keras.callbacks.TensorBoard(log_dir=logs_dir, histogram_freq=1)

    """checkpoint = tf.train.Checkpoint(
        model=model,
        opt=model.optimizer)
    checkpoint_manager = tf.train.CheckpointManager(
        checkpoint=checkpoint,
        directory=checkpoint_dir,
        max_to_keep=1,
        step_counter=model.optimizer.iterations,
        checkpoint_interval=0)
    save_checkpoint = SaveCheckpoint(checkpoint_manager)"""

    #return keras.callbacks.CallbackList([stop_early, save_tensorboard, save_checkpoint])
    return [stop_early, save_tensorboard] # , save_checkpoint]
