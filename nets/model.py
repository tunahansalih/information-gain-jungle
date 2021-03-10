from enum import Enum

import tensorflow as tf
from tensorflow.keras.layers import BatchNormalization

from nets.layers import InformationGainRoutingBlock, RandomRoutingBlock, ConvolutionalBlock, RoutingMaskLayer, \
    DenseRoutingMaskLayer


class Routing(Enum):
    NO_ROUTING = 0
    RANDOM_ROUTING = 1
    INFORMATION_GAIN_ROUTING = 2


class InformationGainRoutingModel(tf.keras.models.Model):

    def __init__(self, config):
        super(InformationGainRoutingModel, self).__init__()

        self.conv_block_0 = ConvolutionalBlock(filters=config["CNN_0"], kernel_size=(5, 5), padding="same")
        if config["USE_ROUTING"]:
            self.routing_block_0 = InformationGainRoutingBlock(routes=config["NUM_ROUTES_0"])
            self.random_routing_block_0 = RandomRoutingBlock(routes=config["NUM_ROUTES_0"])
            self.routing_mask_layer_0 = RoutingMaskLayer(routes=config["NUM_ROUTES_0"],
                                                         gumbel=config["ADD_GUMBEL_NOISE"])
        self.batch_norm_0 = BatchNormalization()

        self.conv_block_1 = ConvolutionalBlock(filters=config["CNN_1"], kernel_size=(5, 5), padding="same")
        if config["USE_ROUTING"]:
            self.routing_block_1 = InformationGainRoutingBlock(routes=config["NUM_ROUTES_1"])
            self.random_routing_block_1 = RandomRoutingBlock(routes=config["NUM_ROUTES_1"])
            self.routing_mask_layer_1 = RoutingMaskLayer(routes=config["NUM_ROUTES_1"],
                                                         gumbel=config["ADD_GUMBEL_NOISE"])
        self.batch_norm_1 = BatchNormalization()

        self.conv_block_2 = ConvolutionalBlock(filters=config["CNN_2"], kernel_size=(5, 5), padding="same")
        self.batch_norm_2 = BatchNormalization()

        self.flatten = tf.keras.layers.Flatten()

        self.fc_0 = tf.keras.layers.Dense(1024, activation=tf.nn.relu)
        self.do_0 = tf.keras.layers.Dropout(config["DROPOUT_RATE"])
        self.fc_1 = tf.keras.layers.Dense(512, activation=tf.nn.relu)
        self.do_1 = tf.keras.layers.Dropout(config["DROPOUT_RATE"])
        self.fc_2 = tf.keras.layers.Dense(config["NUM_CLASSES"])

    def call(self, inputs, routing: Routing, temperature=1, is_training=True):
        x = self.conv_block_0(inputs)
        x = self.batch_norm_0(x, training=is_training)

        if routing == Routing.RANDOM_ROUTING:
            routing_0 = self.random_routing_block_0(x)
        elif routing == Routing.INFORMATION_GAIN_ROUTING:
            routing_0 = self.routing_block_0(x, is_training=is_training) / temperature
        elif routing == Routing.NO_ROUTING:
            routing_0 = None
        else:
            routing_0 = None

        x = self.conv_block_1(x)
        if routing_0 is not None:
            x = self.routing_mask_layer_0(x, routing_0, is_training=is_training)
        x = self.batch_norm_1(x, training=is_training)

        if routing == Routing.RANDOM_ROUTING:
            routing_1 = self.random_routing_block_1(x)
        elif routing == Routing.INFORMATION_GAIN_ROUTING:
            routing_1 = self.routing_block_1(x, is_training=is_training) / temperature
        elif routing == Routing.NO_ROUTING:
            routing_1 = None
        else:
            routing_1 = None

        x = self.conv_block_2(x)
        if routing_1 is not None:
            x = self.routing_mask_layer_1(x, routing_1, is_training=is_training)
        x = self.batch_norm_2(x, training=is_training)

        x = self.flatten(x)

        x = self.fc_0(x)
        if is_training:
            x = self.do_0(x)
        x = self.fc_1(x)
        if is_training:
            x = self.do_1(x)
        x = self.fc_2(x)

        return routing_0, routing_1, x


class InformationGainRoutingLeNetModel(tf.keras.models.Model):

    def __init__(self, config):
        super(InformationGainRoutingLeNetModel, self).__init__()

        self.conv_block_0 = ConvolutionalBlock(filters=config["CNN_0"], kernel_size=(5, 5), padding="same")
        if config["USE_ROUTING"]:
            self.routing_block_0 = InformationGainRoutingBlock(routes=config["NUM_ROUTES_0"])
            self.random_routing_block_0 = RandomRoutingBlock(routes=config["NUM_ROUTES_0"])
            self.routing_mask_layer_0 = RoutingMaskLayer(routes=config["NUM_ROUTES_0"],
                                                         gumbel=config["ADD_GUMBEL_NOISE"])

        self.conv_block_1 = ConvolutionalBlock(filters=config["CNN_1"], kernel_size=(5, 5), padding="same")
        if config["USE_ROUTING"]:
            self.routing_block_1 = InformationGainRoutingBlock(routes=config["NUM_ROUTES_1"])
            self.random_routing_block_1 = RandomRoutingBlock(routes=config["NUM_ROUTES_1"])
            self.routing_mask_layer_1 = DenseRoutingMaskLayer(routes=config["NUM_ROUTES_1"],
                                                              gumbel=config["ADD_GUMBEL_NOISE"])

        self.flatten = tf.keras.layers.Flatten()

        self.fc_0 = tf.keras.layers.Dense(500, activation=tf.nn.relu)
        self.do_0 = tf.keras.layers.Dropout(config["DROPOUT_RATE"])
        self.fc_1 = tf.keras.layers.Dense(config["NUM_CLASSES"])

    def call(self, inputs, routing: Routing, temperature=1, is_training=True):
        x = self.conv_block_0(inputs)

        if routing == Routing.RANDOM_ROUTING:
            routing_0 = self.random_routing_block_0(x)
        elif routing == Routing.INFORMATION_GAIN_ROUTING:
            routing_0 = self.routing_block_0(x, is_training=is_training) / temperature
        elif routing == Routing.NO_ROUTING:
            routing_0 = None
        else:
            routing_0 = None

        x = self.conv_block_1(x)
        if routing_0 is not None:
            x = self.routing_mask_layer_0(x, routing_0, is_training=is_training)

        if routing == Routing.RANDOM_ROUTING:
            routing_1 = self.random_routing_block_1(x)
        elif routing == Routing.INFORMATION_GAIN_ROUTING:
            routing_1 = self.routing_block_1(x, is_training=is_training) / temperature
        elif routing == Routing.NO_ROUTING:
            routing_1 = None
        else:
            routing_1 = None

        x = self.flatten(x)

        x = self.fc_0(x)
        if routing_1 is not None:
            x = self.routing_mask_layer_1(x, routing_1, is_training=is_training)

        if is_training:
            x = self.do_0(x)
        x = self.fc_1(x)

        return routing_0, routing_1, x
