"""
=============================================================================
NeoNatal Watch AI — Autoencoder Architecture
=============================================================================
WHAT  : An Unsupervised Deep Learning model for Anomaly Detection.
WHY   : Instead of classifying "Normal vs Event" directly, an Autoencoder 
        learns to reconstruct ONLY normal vital sign patterns. When a 
        deterioration event occurs, it represents an "unseen" pattern. 
        The model will struggle to reconstruct it, resulting in a high 
        Reconstruction Error (MSE). This error acts as our risk score!
HOW   : Encoder (Compresses 30 time-steps down to a small vector)
        Decoder (Expands it back to 30 time-steps)
=============================================================================
"""

import tensorflow as tf
from tensorflow.keras import layers, models
import logging

logger = logging.getLogger("Autoencoder")

def build_autoencoder_model(
    sequence_length: int = 30,
    n_features: int = 6,
    learning_rate: float = 0.001
) -> tf.keras.Model:
    """
    Constructs a 1D Convolutional Autoencoder for time-series data.
    """
    logger.info("Building Conv1D Autoencoder Architecture...")
    
    inputs = layers.Input(shape=(sequence_length, n_features), name="ae_input")
    
    # ─── ENCODER (Compression) ──────────────────────────────────────────
    x = layers.Conv1D(filters=32, kernel_size=3, padding="same", activation="relu")(inputs)
    x = layers.MaxPooling1D(pool_size=2, padding="same")(x)
    
    x = layers.Conv1D(filters=16, kernel_size=3, padding="same", activation="relu")(x)
    encoded = layers.MaxPooling1D(pool_size=2, padding="same", name="bottleneck")(x)
    
    # ─── DECODER (Reconstruction) ───────────────────────────────────────
    x = layers.Conv1D(filters=16, kernel_size=3, padding="same", activation="relu")(encoded)
    x = layers.UpSampling1D(size=2)(x)
    
    x = layers.Conv1D(filters=32, kernel_size=3, padding="same", activation="relu")(x)
    x = layers.UpSampling1D(size=2)(x)
    
    # Ensure the output length matches the input length exactly.
    # Depending on the sequence length (e.g., 30), two UpSampling1D(2) on a padded MaxPool 
    # might result in length 32 instead of 30. We use a Cropping layer if needed.
    
    # Final layer to reconstruct original features
    decoded = layers.Conv1D(filters=n_features, kernel_size=3, padding="same", activation="linear", name="ae_output")(x)
    
    # Slice to match exact input length if padding caused an extension
    if decoded.shape[1] != sequence_length:
        crop_size = decoded.shape[1] - sequence_length
        decoded = layers.Cropping1D(cropping=(0, crop_size))(decoded)
        
    model = models.Model(inputs=inputs, outputs=decoded, name="NeoNatal_Autoencoder")
    
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=learning_rate),
        loss="mse"  # Mean Squared Error is the standard for reconstruction
    )
    
    return model

