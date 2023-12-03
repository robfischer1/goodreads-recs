import logging

import tensorflow as tf
import keras

from wrecksys.model import layers, metrics

logger = logging.getLogger(__name__)
@keras.saving.register_keras_serializable(package="GRU4Books")
class WreckSys(keras.Model):

    def __init__(self, model_config, *args, **kwargs):
        logger.debug("Creating new model.")
        super().__init__(*args, **kwargs)

        self._config = model_config
        self._vocab_size = 1 + self._config['vocab_size']
        emb_dims = self._config['embedding_dimensions']
        rnn_dims = self._config['rnn_dimensions']

        self._context_encoder = layers.ContextEncoder(self._vocab_size, emb_dims, rnn_dims)
        self._label_encoder = layers.BookEncoder(self._vocab_size, emb_dims)
        self._metrics = metrics.metrics_list([1, 5, 10, 100])

        self._vocabulary = {'label_id': tf.range(1, self._vocab_size)}

    @tf.function
    def train_step(self, data):
        y_true = data['label_id']

        with tf.GradientTape() as tape:
            y_pred = self(data, training=True)
            loss = self.compute_loss(y=y_true, y_pred=y_pred)

        gradients = tape.gradient(loss, self.trainable_variables)
        self.optimizer.apply_gradients(zip(gradients, self.trainable_variables))
        return {self.loss.name: loss}

    @tf.function
    def test_step(self, data):
        y_true = data['label_id']
        y_pred = self(data, training=False)
        loss = self.compute_loss(y=y_true, y_pred=y_pred)

        for metric in self._metrics:
            metric.update_state(y_true, y_pred)

        metric = {metric.name: metric.result() for metric in self.metrics}
        metric[self.loss.name] = loss
        return metric

    @property
    def metrics(self):
        return [m for m in self._metrics]

    def call(self, inputs: dict[str, tf.Tensor], training=None, mask=None) -> tf.Tensor:
        context_embeddings = self._context_encoder(inputs)
        label_embeddings = self._label_encoder(self._vocabulary)
        if keras.backend.ndim(label_embeddings) == 3:
            label_embeddings = tf.squeeze(label_embeddings, 1)
        return tf.matmul(context_embeddings, label_embeddings, transpose_b=True)

    @tf.function
    def serve(self, **kwargs):
        query = kwargs
        dotproduct = self(query)
        values, indices = tf.math.top_k(tf.squeeze(dotproduct), self._config['num_predictions'], sorted=True)
        ids = tf.identity(indices, name='top_recommendation_ids')
        scores = tf.identity(tf.math.sigmoid(values), name='top_recommendation_scores')
        return {'recommendation_ids': ids, 'recommendation_scores': scores}

    def get_config(self):
        base_config = super().get_config()
        config = {"model_config": self._config}
        return {**base_config, **config}
