from wrecksys.utils import import_tensorflow
tf, keras = import_tensorflow()


@keras.saving.register_keras_serializable(package="GRU4Books")
class BookEncoder(keras.layers.Layer):

    def __init__(self, vocab_size, embedding_dim, name='label') -> None:
        super().__init__()
        self._vocab_size = vocab_size
        self._embedding_dim = embedding_dim
        self._embedding_layer = keras.layers.Embedding(
            self._vocab_size + 1,
            self._embedding_dim,
            embeddings_initializer=keras.initializers.truncated_normal(
                mean=0.0,
                stddev=1.0 / self._embedding_dim ** 0.5),
            mask_zero=True,
            name=f"{name}_embedding_layer")

    def call(self, inputs, *args, **kwargs) -> tf.Tensor:
        label = inputs['label_id']

        if isinstance(label, tf.SparseTensor):
            label = tf.sparse.to_dense(label)

        label_embedding = self._embedding_layer(label)

        if keras.backend.ndim(label_embedding) == 3:
            label_embedding = tf.squeeze(label_embedding)

        return label_embedding

    def get_config(self):
        config = {
            "vocab_size": self._vocab_size,
            "embedding_dim": self._embedding_dim,
        }
        return config


@keras.saving.register_keras_serializable(package="GRU4Books")
class RatingEncoder(BookEncoder):

    def __init__(self, vocab_size, embedding_dim, rnn_dim):
        super().__init__(vocab_size, embedding_dim, 'context')
        self._rnn_dim = rnn_dim
        self._rnn_layer = keras.layers.GRU(rnn_dim)

    def call(self, inputs: dict[str, tf.Tensor], *args, **kwargs) -> tf.Tensor:
        context = inputs['context_id']
        if isinstance(context, tf.SparseTensor):
            context = tf.sparse.to_dense(context)

        context_shape = context.shape.as_list()
        context_embed = self._embedding_layer(context)
        context_masks = self._embedding_layer.compute_mask(context)

        rating = inputs['context_rating']
        if isinstance(rating, tf.SparseTensor):
            rating = tf.sparse.to_dense(rating)
        rating_embed = tf.expand_dims(rating, -1)

        embedding = tf.concat([context_embed, rating_embed], -1)

        mask_shape = [1] + context_shape[1:]
        mask = tf.ones(shape=mask_shape) * tf.cast(context_masks, 'float32')
        mask = tf.expand_dims(mask, -1)
        embedding = embedding * mask

        return self._rnn_layer(embedding)

    def get_config(self):
        config = {
            "vocab_size": self._vocab_size,
            "embedding_dim": self._embedding_dim,
            "rnn_dim": self._rnn_dim
        }
        return config


@keras.saving.register_keras_serializable(package="GRU4Books")
class ContextEncoder(keras.layers.Layer):

    def __init__(self, vocab_size, embedding_dim, rnn_dim):
        super().__init__(name='context_encoder')

        self._vocab_size = vocab_size
        self._embedding_dim = embedding_dim
        self._rnn_dim = rnn_dim
        self._feature_encoder = RatingEncoder(vocab_size, embedding_dim, rnn_dim)

        self._hidden_layers = []
        self._hidden_layer_dims = [8, 4]
        for i, d in enumerate(self._hidden_layer_dims):
            self._hidden_layers.append(
                keras.layers.Dense(
                    units=d,
                    name=f"hidden_layer_{i}",
                    activation=tf.nn.relu
                )
            )

        self._hidden_layers.append(
            keras.layers.Dense(
                units=self._embedding_dim,
                name="projection_layer",
                activation=tf.nn.relu
            )
        )

    def call(self, inputs: dict[str, tf.Tensor], *args, **kwargs) -> tf.Tensor:
        feature = {
            k: tf.expand_dims(v, 0) if v.shape.ndims == 1 else v
            for k, v in inputs.items()
        }

        context_embedding = self._feature_encoder(feature)

        for layer in self._hidden_layers:
            context_embedding = layer(context_embedding)

        return context_embedding

    def get_config(self):
        config = {
            "vocab_size": self._vocab_size,
            "embedding_dim": self._embedding_dim,
            "rnn_dim": self._rnn_dim
        }
        return config


# noinspection PyMethodOverriding
@keras.saving.register_keras_serializable(package="GRU4Books")
class Recommendation(keras.layers.Layer):
    def __init__(self,
                 loss: keras.losses.Loss,
                 metrics: keras.callbacks.CallbackList,
                 name='prediction_layer') -> None:
        super().__init__(name=name)
        self._loss = loss
        self._metrics = metrics

    def call(self,
             label_embeddings: tf.Tensor,
             context_embeddings: tf.Tensor,
             compute_metrics: bool = False) -> tf.Tensor:

        args = {'y_true': label_embeddings, 'y_pred': context_embeddings}
        loss = self._loss(**args)
        if not compute_metrics:
            return loss

        update_ops = []
        for metric in self._metrics:
            update_ops.append(metric.update_state(**args))

        with tf.control_dependencies(update_ops):
            return tf.identity(loss)

    def get_config(self):
        config = {
            "loss": self._loss,
            "metrics": self._metrics,
            "name": self.name
        }
        return config
