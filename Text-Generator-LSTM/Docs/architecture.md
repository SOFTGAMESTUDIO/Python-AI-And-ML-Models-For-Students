# Neural Architecture: LSTM Text Generator

This document provides a conceptual understanding of the internal processes driving the text generation engine.

## 1. Sequence Tokenization and Padding
Deep learning networks cannot process raw English letters directly. 
1. **Tokenization**: We scan `data/input.txt` to identify all unique words, assembling a vocabulary dictionary. Each word is assigned an integer (e.g. `{"the": 1, "learning": 2}`).
2. **Sequencing**: We transform sentences into arrays of numbers.
3. **Padding**: LSTMs require fixed-width inputs. We use a context window of length 10. If the context is shorter than 10 words, we prepend it with `0`s (left-padding) so the tensor remains structurally sound without violating semantic sequences.

## 2. Keras Model Architecture

The core of `src/model.py` leverages three key dense operations inside a Sequential pipeline.

```python
Model: "sequential"
┌─────────────────────────────────┬────────────────────────┬───────────────┐
│ Layer (type)                    │ Output Shape           │       Param # │
├─────────────────────────────────┼────────────────────────┼───────────────┤
│ embedding (Embedding)           │ (None, 10, 64)         │        23,744 │
├─────────────────────────────────┼────────────────────────┼───────────────┤
│ lstm (LSTM)                     │ (None, 128)            │        98,816 │
├─────────────────────────────────┼────────────────────────┼───────────────┤
│ dropout (Dropout)               │ (None, 128)            │             0 │
├─────────────────────────────────┼────────────────────────┼───────────────┤
│ dense (Dense)                   │ (None, 371)            │        47,859 │
└─────────────────────────────────┴────────────────────────┴───────────────┘
```

### The Embedding Layer
Integer representations are sparse and disconnected. The `Embedding` layer maps the sparse integer IDs into a dense, 64-dimensional float vector. It allows the model to map the semantic distance between words (e.g., bringing "king" and "queen" closer together mathematically).

### The Long Short-Term Memory (LSTM) Layer
Standard Recurrent Neural Networks suffer from "vanishing gradients" when reading long sentences. The LSTM explicitly features internal "Gates" (Forget, Input, and Output gates).
It uses a 128-unit structure to process the 10 words linearly, deciding which contextual rules to carry forward into its hidden state, and which context points to selectively discard.

### Regularization: Dropout
We insert a `Dropout` function that randomly zeroes out signals (20% by default) during training. This mathematically prevents the LSTM from strictly "memorizing" individual sentences from `input.txt`.

### The Softmax Output (Dense Layer)
The final stage is a dense matrix matching the exact size of the vocabulary. It uses a `softmax` activation to scale the output vector into a valid probability distribution equalling `1.0`. The word with the highest probability peak becomes the model's predicted next word.

## 3. Stochastic Sampling (Temperature)
During inference, blindly picking the `argmax()` (the highest probability) results in boring, repetitive loops. To counter this, `src/generate.py` scales the logits using a `temperature` variable. Lower temperatures sharpen the distribution (making the model play it safe), while higher temperatures flatten the distribution (forcing the model to pick rare, surprising words).
