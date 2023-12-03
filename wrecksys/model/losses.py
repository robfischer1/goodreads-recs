#   Copyright 2021 The TensorFlow Authors. All Rights Reserved.
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.


#
#   From: https://github.com/tensorflow/examples/tree/master/lite/examples/recommendation/ml
#   Included without modification under the assumption that they know something I don't
#   about the built-in Keras loss layers.
#

import tensorflow as tf
import keras


class GlobalSoftmax(keras.losses.Loss):
    """Compute softmax over similarities.

  This loss function computes softmax over similarities between context and
  full vocab label embeddings, considering full label vocab non-label
  predictions as negatives. This is currently the default loss in the model.
  """

    def __init__(self, name='Global_Softmax_Cross_Entropy', **kwargs):
        super(GlobalSoftmax, self).__init__(name=name, **kwargs)

    @tf.function
    def call(self, y_true: tf.Tensor, y_pred: tf.Tensor):
        """Compute softmax loss with full vocab labels as negatives.

    Args:
      y_true: the true labels with shape [batch_size, 1].
      y_pred: the pre-calculated similarities matrix with shape [batch_size,
        label_embedding_vocab_size]

    Returns:
      The softmax loss with full vocab labels as negatives.
    """
        logits = keras.backend.cast(y_pred, 'float32')
        # Compose a metric to tell which column represents the similarity between
        # the example and the label. For each row, only the item at index of the
        # label of that example will be set as 1.
        full_labels = tf.one_hot(
            tf.transpose(y_true)[0], tf.shape(logits)[1], dtype=tf.dtypes.float32)
        batch_loss = tf.nn.softmax_cross_entropy_with_logits(
            labels=full_labels, logits=logits)
        loss = tf.reduce_mean(batch_loss)
        return loss
