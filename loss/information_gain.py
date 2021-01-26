import tensorflow as tf


def entropy(prob_distribution):
    log_prob = tf.math.log(prob_distribution + tf.keras.backend.epsilon())
    prob_log_prob = prob_distribution * log_prob
    entropy_val = -1.0 * tf.reduce_sum(prob_log_prob)
    return entropy_val


def entropy_stable(prob_distribution):
    x = tf.reshape(prob_distribution, -1)
    exp = tf.math.exp(x)
    sum_exp = tf.math.reduce_sum(exp)
    log_sum_exp = tf.math.log(sum_exp)

    return (-1 * (1 / sum_exp) * tf.reduce_sum(exp * x)) + ((log_sum_exp / sum_exp) * tf.reduce_sum(exp))


def information_gain_loss_fn(p_c_given_x_2d, p_n_given_x_2d, balance_coefficient=1.0):
    p_n_given_x_3d = tf.expand_dims(input=p_n_given_x_2d, axis=1)
    p_c_given_x_3d = tf.expand_dims(input=p_c_given_x_2d, axis=2)
    non_normalized_joint_xcn = p_n_given_x_3d * p_c_given_x_3d
    # Calculate p(c,n)
    marginal_p_cn = tf.reduce_mean(non_normalized_joint_xcn, axis=0)
    # Calculate p(n)
    marginal_p_n = tf.reduce_sum(marginal_p_cn, axis=0)
    # Calculate p(c)
    marginal_p_c = tf.reduce_sum(marginal_p_cn, axis=1)
    # Calculate entropies

    # entropy_p_cn, log_prob_p_cn = entropy(prob_distribution=marginal_p_cn)
    # entropy_p_n, log_prob_p_n = entropy(prob_distribution=marginal_p_n)
    # entropy_p_c, log_prob_p_c = entropy(prob_distribution=marginal_p_c)

    entropy_p_cn = entropy(prob_distribution=marginal_p_cn)
    entropy_p_n = entropy(prob_distribution=marginal_p_n)
    entropy_p_c = entropy(prob_distribution=marginal_p_c)

    # Calculate the information gain
    information_gain = (balance_coefficient * entropy_p_n) + entropy_p_c - entropy_p_cn
    information_gain = -1.0 * information_gain
    return information_gain