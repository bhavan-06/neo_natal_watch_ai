"""
=============================================================================
NeoNatal Watch AI — CNN-LSTM Architecture
=============================================================================
WHAT  : Defines a Hybrid Deep Learning Model combining CNN and LSTM.
WHY   : 
  - CNN (Convolutional Neural Network) excels at finding sudden, local 
    patterns (e.g., a sudden spike in Heart Rate).
  - LSTM (Long Short-Term Memory) excels at tracking long-term trends 
    over time (e.g., a slow, steady decline in Oxygen).
HOW   : 
  Input -> 1D Convolution -> Pooling -> LSTM -> Dense -> Sigmoid (Probability)
=============================================================================
"""

import tensorflow as tf
from tensorflow.keras import layers, models, regularizers
import logging

logger = logging.getLogger("CNN_LSTM")

def build_cnn_lstm_model(
    sequence_length: int = 30,
    n_features: int = 6,
    cnn_filters: list = [32, 64],
    cnn_kernel_size: int = 3,
    lstm_units: int = 64,
    dropout_rate: float = 0.3,
    learning_rate: float = 0.001
) -> tf.keras.Model:
    """
    Constructs and compiles the CNN-LSTM hybrid model.
    
    Parameters
    ----------
    sequence_length : Number of time steps in each window (e.g., 30 minutes).
    n_features      : Number of vital signs (e.g., 6).
    cnn_filters     : List of filter sizes for Conv1D layers.
    cnn_kernel_size : Size of the sliding window the CNN looks at.
    lstm_units      : Number of hidden units in the LSTM layer.
    dropout_rate    : Fraction of neurons to drop (prevents overfitting).
    learning_rate   : Adam optimizer learning rate.
    
    Returns
    -------
    model : Compiled Keras model.
    """
    logger.info("Building CNN-LSTM Architecture...")
    
    # Input Layer: expects 3D tensor (batch_size, sequence_length, n_features)
    inputs = layers.Input(shape=(sequence_length, n_features), name="vital_signs_input")
    
    x = inputs
    
    # Spatial/Local Pattern Extraction (CNN Block)
    for i, filters in enumerate(cnn_filters):
        x = layers.Conv1D(
            filters=filters, 
            kernel_size=cnn_kernel_size, 
            padding="same", 
            activation="relu",
            name=f"conv1d_{i+1}"
        )(x)
        x = layers.BatchNormalization(name=f"batch_norm_conv_{i+1}")(x)
        # We only pool if we have enough sequence length left
        if x.shape[1] > 2: 
            x = layers.MaxPooling1D(pool_size=2, name=f"max_pool_{i+1}")(x)
        x = layers.Dropout(dropout_rate, name=f"dropout_conv_{i+1}")(x)

    # Temporal/Sequential Pattern Extraction (LSTM Block)
    # The LSTM reads the sequence of features extracted by the CNN
    x = layers.LSTM(
        units=lstm_units, 
        return_sequences=False, # We only want the final prediction for the window
        kernel_regularizer=regularizers.l2(0.001),
        name="lstm_1"
    )(x)
    
    x = layers.BatchNormalization(name="batch_norm_lstm")(x)
    x = layers.Dropout(dropout_rate + 0.1, name="dropout_lstm")(x)
    
    # Fully Connected Block
    x = layers.Dense(32, activation="relu", name="dense_1")(x)
    x = layers.Dropout(dropout_rate, name="dropout_dense")(x)
    
    # Output Layer (Sigmoid for binary classification: 0 = Normal, 1 = Event)
    outputs = layers.Dense(1, activation="sigmoid", name="deterioration_probability")(x)
    
    model = models.Model(inputs=inputs, outputs=outputs, name="NeoNatal_CNN_LSTM")
    
    # We use PR-AUC as our primary metric inside Keras
    metrics_list = [
        tf.keras.metrics.AUC(curve='PR', name='pr_auc'),
        tf.keras.metrics.AUC(curve='ROC', name='roc_auc'),
        tf.keras.metrics.Recall(name='recall'),
        tf.keras.metrics.Precision(name='precision')
    ]
    
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=learning_rate),
        loss=tf.keras.losses.BinaryCrossentropy(),
        metrics=metrics_list
    )
    
    return model

