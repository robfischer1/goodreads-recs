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
"""Customized metrics."""

#
#   Original version from: https://github.com/tensorflow/examples/tree/master/lite/examples/recommendation/ml
#   Added metric_list() for use in model.model_builder
#

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import keras
import tensorflow as tf


def metrics_list(top_k: list[int]):
    # global_metrics = []
    global_metrics = [GlobalRecall(name=f'Global_Recall/Top_{k}', top_k=k) for k in top_k]
    # global_metrics.append(GlobalMeanRank(name='Global_Mean_Rank'))
    # batch_metrics = []
    batch_metrics = [BatchRecall(name=f'Batch_Recall/Top_{k}', top_k=k) for k in top_k]
    batch_metrics.append(BatchMeanRank(name='Batch_Mean_Rank'))
    return global_metrics + batch_metrics


def _get_batch_similarities(batch_label, full_vocab_similarities):
    return tf.gather(
        full_vocab_similarities, tf.transpose(batch_label)[0], axis=1)


class BatchRecall(keras.metrics.Recall):
    """Compute batch recall for top_k."""

    def update_state(self, y_true, y_pred, sample_weight=None):
        """Update state of the metric.

        Args:
          y_true: the true labels with shape [batch_size, 1].
          y_pred: model output, which is the similarity matrix with shape
            [batch_size, label_embedding_vocab_size] between context and full vocab
            label embeddings.
          sample_weight: Optional weighting of each example. Defaults to 1.
        """
        label_indices = tf.eye(
            tf.shape(y_pred)[0], tf.shape(y_pred)[0], dtype=tf.dtypes.float32)
        # Since tf.keras default recall metric only accept predicted values in
        # range [0, 1], so use tf.nn.softmax to preprocess.
        normalized_logits = tf.nn.softmax(_get_batch_similarities(y_true, y_pred))
        super().update_state(label_indices, normalized_logits, sample_weight)


class GlobalRecall(keras.metrics.Recall):
    """Compute global recall for top_k."""

    def update_state(self, y_true, y_pred, sample_weight=None):
        """Update state of the metric.

        Args:
          y_true: the true labels with shape [batch_size, 1].
          y_pred: model output, which is the similarity matrix with shape
            [batch_size, label_embedding_vocab_size] between context and full vocab
            label embeddings.
          sample_weight: Optional weighting of each example. Defaults to 1.
        """
        label_indices = tf.one_hot(
            tf.transpose(y_true)[0], tf.shape(y_pred)[1], dtype=tf.dtypes.float32)
        # Since tf.keras default recall metric only accept predicted values in
        # range [0, 1], so use tf.nn.softmax to preprocess.
        normalized_logits = tf.nn.softmax(y_pred)
        super().update_state(label_indices, normalized_logits, sample_weight)


class BatchMeanRank(keras.metrics.Mean):
    """Keras metric computing mean rank of correct label within batch."""

    # noinspection PyMethodOverriding
    def update_state(self, y_true, y_pred,
                     sample_weight=None):  # pytype: disable=signature-mismatch  # overriding-parameter-count-checks
        """Update state of the metric.

        Args:
          y_true: the true labels with shape [batch_size, 1].
          y_pred: model output, which is the similarity matrix with shape
            [batch_size, label_embedding_vocab_size] between context and full vocab
            label embeddings. Hence, to compute batch mean rank, the default global
            similarities will be converted to batch similarities first with shape
            [batch_size, batch_size].
          sample_weight: Optional weighting of each example. Defaults to 1.
        """
        similarities = _get_batch_similarities(y_true, y_pred)
        # Get the ranks of the correct label for each context.
        batch_size = tf.shape(similarities)[0]
        label_indices = tf.expand_dims(tf.range(batch_size), -1)

        # Get the indices of similar labels in sorted order for each context.
        sorted_similarities = tf.argsort(
            similarities, axis=-1, direction='DESCENDING')

        ranks = tf.where(tf.equal(sorted_similarities, label_indices))[:, -1]
        ranks = keras.backend.cast(ranks, 'float32')
        super().update_state(ranks, sample_weight=sample_weight)


class GlobalMeanRank(keras.metrics.Mean):
    """Keras metric computing mean rank of correct label globally."""

    # noinspection PyMethodOverriding
    def update_state(self, y_true, y_pred,
                     sample_weight=None):  # pytype: disable=signature-mismatch  # overriding-parameter-count-checks
        """Update state of the metric.

        Args:
          y_true: the true labels with shape [batch_size, 1].
          y_pred: model output, which is the similarity matrix with shape
            [batch_size, label_embedding_vocab_size] between context and full vocab
            label embeddings.
          sample_weight: Optional weighting of each example. Defaults to 1.
        """

        similarities = y_pred
        label_indices = tf.expand_dims(tf.cast(y_true, dtype=tf.int32), -1)

        # Get the indices of similar labels in sorted order for each context.
        sorted_similarities = tf.argsort(
            similarities, axis=-1, direction='DESCENDING')

        ranks = tf.where(tf.equal(sorted_similarities, label_indices))[:, -1]
        ranks = keras.backend.cast(ranks, 'float32')
        super().update_state(ranks, sample_weight=sample_weight)
