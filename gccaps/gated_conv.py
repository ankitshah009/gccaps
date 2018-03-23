from keras.layers import Activation
from keras.layers import BatchNormalization
from keras.layers import Dropout
from keras.layers import Conv2D
from keras.layers import MaxPooling2D
from keras.layers import Multiply


def block(x, n_filters=64, pool_size=(2, 2), dropout_rate=0.2):
    """Apply two gated convolutions followed by a max-pooling operation.

    Batch normalization and dropout are applied for regularization.

    Args:
        x (tensor): Input tensor to transform.
        n_filters (int): Number of filters for each gated convolution.
        pool_size (int or tuple): Pool size of max-pooling operation.
        dropout_rate (float): Fraction of units to drop.

    Returns:
        A Keras tensor of the resulting output.
    """
    x = GatedConv(n_filters, padding='same')(x)
    x = BatchNormalization(axis=-1)(x)
    x = Dropout(rate=dropout_rate)(x)

    x = GatedConv(n_filters, padding='same')(x)
    x = BatchNormalization(axis=-1)(x)
    x = Dropout(rate=dropout_rate)(x)

    return MaxPooling2D(pool_size=pool_size)(x)


class GatedConv(Conv2D):
    """A Keras layer implementing gated convolutions [1]_.

    Args:
        n_filters (int): Number of output filters.
        kernel_size (int or tuple): Size of convolution kernel.
        strides (int or tuple): Strides of the convolution.
        padding (str): One of ``'valid'`` or ``'same'``.
        kwargs: Other layer keyword arguments.

    References:
        .. [1] Y. N. Dauphin, A. Fan, M. Auli, and D. Grangier,
               "Language modeling with gated convolutional networks,"
               ArXiv e-prints, 2016.
    """
    def __init__(self, n_filters=64, kernel_size=(3, 3),
                 strides=(1, 1), padding='valid', **kwargs):
        super(GatedConv, self).__init__(filters=n_filters*2,
                                        kernel_size=kernel_size,
                                        strides=strides,
                                        padding=padding,
                                        **kwargs)

        self.n_filters = n_filters

    def call(self, inputs):
        """Apply gated convolution."""
        output = super(GatedConv, self).call(inputs)

        n_filters = self.n_filters
        linear = Activation('linear')(output[:, :, :, :n_filters])
        sigmoid = Activation('sigmoid')(output[:, :, :, n_filters:])

        return Multiply()([linear, sigmoid])

    def compute_output_shape(self, input_shape):
        """Compute shape of layer output."""
        output_shape = super(GatedConv, self).compute_output_shape(input_shape)
        return tuple(output_shape[:3]) + (self.n_filters,)

    def get_config(self):
        """Return the config of the layer."""
        config = super(GatedConv, self).get_config()
        config['n_filters'] = self.n_filters
        del config['filters']
        return config