"""
=============================================================================
NeoNatal Watch AI — Transformer Architecture
=============================================================================
WHAT  : A Time-Series Transformer using Self-Attention.
WHY   : Unlike LSTMs (which process data sequentially and can "forget" older 
        events), Transformers look at the entire 30-minute window at once.
        The Multi-Head Attention mechanism learns exactly *which* specific 
        minutes are most critical to predicting deterioration, regardless
        of when they occurred in the window.
=============================================================================
"""

import tensorflow as tf
from tensorflow.keras import layers, models
import logging

logger = logging.getLogger("Transformer")

def transformer_encoder(inputs, head_size, num_heads, ff_dim, dropout=0.3):
    """
    Creates a single Transformer Encoder block.
    """
    # 1. Self-Attention
    x = layers.LayerNormalization(epsilon=1e-6)(inputs)
    x = layers.MultiHeadAttention(
        key_dim=head_size, num_heads=num_heads, dropout=dropout
    )(x, x)
    x = layers.Dropout(dropout)(x)
    res = layers.Add()([x, inputs])

    # 2. Feed-Forward Network
    x = layers.LayerNormalization(epsilon=1e-6)(res)
    x = layers.Conv1D(filters=ff_dim, kernel_size=1, activation="relu")(x)
    x = layers.Dropout(dropout)(x)
    x = layers.Conv1D(filters=inputs.shape[-1], kernel_size=1)(x)
    return layers.Add()([x, res])

def build_transformer_model(
    sequence_length: int = 30,
    n_features: int = 6,
    head_size: int = 32,
    num_heads: int = 4,
    ff_dim: int = 64,
    num_transformer_blocks: int = 2,
    mlp_units: list = [64, 32],
    dropout: float = 0.3,
    learning_rate: float = 0.001
) -> tf.keras.Model:
    """
    Constructs the Time-Series Transformer model.
    """
    logger.info("Building Transformer Architecture...")
    inputs = layers.Input(shape=(sequence_length, n_features), name="vital_signs_input")
    
    # ─── 1. Projection & Positional Embedding ────────────────────────────
    # Project the 6 vital signs into a richer embedded space
    x = layers.Conv1D(filters=ff_dim, kernel_size=1, padding="same")(inputs)
    
    # Since attention is permutation invariant, we must add positional information.
    # We add a learnable positional embedding for the 30 time steps.
    positional_embedding = layers.Embedding(input_dim=sequence_length, output_dim=ff_dim)
    positions = tf.range(start=0, limit=sequence_length, delta=1)
    pos_emb = positional_embedding(positions)
    x = x + pos_emb
    
    # ─── 2. Transformer Blocks ───────────────────────────────────────────
    for _ in range(num_transformer_blocks):
        x = transformer_encoder(x, head_size, num_heads, ff_dim, dropout)

    # ─── 3. Global Pooling & MLP ─────────────────────────────────────────
    # Compress the sequence down to a single vector
    x = layers.GlobalAveragePooling1D(data_format="channels_last")(x)
    
    for dim in mlp_units:
        x = layers.Dense(dim, activation="relu")(x)
        x = layers.Dropout(dropout)(x)
        
    # Output layer
    outputs = layers.Dense(1, activation="sigmoid", name="deterioration_probability")(x)
    
    model = models.Model(inputs=inputs, outputs=outputs, name="NeoNatal_Transformer")
    
    # Metrics
    metrics_list = [
        tf.keras.metrics.AUC(curve='PR', name='pr_auc'),
        tf.keras.metrics.AUC(curve='ROC', name='roc_auc'),
        tf.keras.metrics.Recall(name='recall'),
        tf.keras.metrics.Precision(name='precision')
    ]
    
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=learning_rate),
        loss="binary_crossentropy",
        metrics=metrics_list
    )
    
    return model

