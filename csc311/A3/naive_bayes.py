from __future__ import absolute_import
from __future__ import print_function
from future.standard_library import install_aliases

install_aliases()
import numpy as np
import os
import gzip
import struct
import array
import matplotlib.pyplot as plt
import matplotlib.image
from urllib.request import urlretrieve


def download(url, filename):
    if not os.path.exists('data'):
        os.makedirs('data')
    out_file = os.path.join('data', filename)
    if not os.path.isfile(out_file):
        urlretrieve(url, out_file)


def mnist():
    base_url = 'http://yann.lecun.com/exdb/mnist/'

    def parse_labels(filename):
        with gzip.open(filename, 'rb') as fh:
            magic, num_data = struct.unpack(">II", fh.read(8))
            return np.array(array.array("B", fh.read()), dtype=np.uint8)

    def parse_images(filename):
        with gzip.open(filename, 'rb') as fh:
            magic, num_data, rows, cols = struct.unpack(">IIII", fh.read(16))
            return np.array(array.array("B", fh.read()), dtype=np.uint8).reshape(num_data, rows, cols)

    for filename in ['train-images-idx3-ubyte.gz',
                     'train-labels-idx1-ubyte.gz',
                     't10k-images-idx3-ubyte.gz',
                     't10k-labels-idx1-ubyte.gz']:
        download(base_url + filename, filename)

    train_images = parse_images('data/train-images-idx3-ubyte.gz')
    train_labels = parse_labels('data/train-labels-idx1-ubyte.gz')
    test_images = parse_images('data/t10k-images-idx3-ubyte.gz')
    test_labels = parse_labels('data/t10k-labels-idx1-ubyte.gz')

    return train_images, train_labels, test_images[:1000], test_labels[:1000]


def load_mnist():
    partial_flatten = lambda x: np.reshape(x, (x.shape[0], np.prod(x.shape[1:])))
    one_hot = lambda x, k: np.array(x[:, None] == np.arange(k)[None, :], dtype=int)
    train_images, train_labels, test_images, test_labels = mnist()
    train_images = (partial_flatten(train_images) / 255.0 > .5).astype(float)
    test_images = (partial_flatten(test_images) / 255.0 > .5).astype(float)
    train_labels = one_hot(train_labels, 10)
    test_labels = one_hot(test_labels, 10)
    N_data = train_images.shape[0]

    return N_data, train_images, train_labels, test_images, test_labels


def plot_images(images, ax, ims_per_row=5, padding=5, digit_dimensions=(28, 28),
                cmap=matplotlib.cm.binary, vmin=None, vmax=None):
    """Images should be a (N_images x pixels) matrix."""
    N_images = images.shape[0]
    N_rows = np.int32(np.ceil(float(N_images) / ims_per_row))
    pad_value = np.min(images.ravel())
    concat_images = np.full(((digit_dimensions[0] + padding) * N_rows + padding,
                             (digit_dimensions[1] + padding) * ims_per_row + padding), pad_value)
    for i in range(N_images):
        cur_image = np.reshape(images[i, :], digit_dimensions)
        row_ix = i // ims_per_row
        col_ix = i % ims_per_row
        row_start = padding + (padding + digit_dimensions[0]) * row_ix
        col_start = padding + (padding + digit_dimensions[1]) * col_ix
        concat_images[row_start: row_start + digit_dimensions[0],
        col_start: col_start + digit_dimensions[1]] = cur_image
        cax = ax.matshow(concat_images, cmap=cmap, vmin=vmin, vmax=vmax)
        plt.xticks(np.array([]))
        plt.yticks(np.array([]))
    return cax


def save_images(images, filename, **kwargs):
    fig = plt.figure(1)
    fig.clf()
    ax = fig.add_subplot(111)
    plot_images(images, ax, **kwargs)
    fig.patch.set_visible(False)
    ax.patch.set_visible(False)
    plt.savefig(filename)


def train_mle_estimator(train_images, train_labels):
    """ Inputs: train_images, train_labels
        Returns the MLE estimators theta_mle and pi_mle"""

    pi_mle = sum(train_labels) / sum(sum(train_labels))
    ones = np.ones((train_images.shape[1], train_labels.shape[0]))
    theta_mle = (train_images.T.dot(train_labels)) / ones.dot(train_labels)

    # This is not a good algorithm.
    # theta = []
    # for i in range(train_labels.shape[1]):  # 10
    #     class_sum = sum(train_labels)[i]
    #     class_column = []
    #     for j in range(train_images.shape[1]):  # 784
    #         sum_feature_j = 0
    #         for k in range(train_images.shape[0]):  # 60000
    #             if train_labels[k][i] == 1:
    #                 sum_feature_j += train_images[k][j]
    #         class_column.append(sum_feature_j / class_sum)
    #     theta.append(class_column)
    # theta_mle = np.array(theta).T

    return theta_mle, pi_mle


def train_map_estimator(train_images, train_labels):
    """ Inputs: train_images, train_labels
        Returns the MAP estimators theta_map and pi_map"""

    pi_map = sum(train_labels) / sum(sum(train_labels))
    ones = np.ones((train_images.shape[1], train_labels.shape[0]))
    theta_map = ((train_images.T.dot(train_labels)) + 2) / (ones.dot(train_labels) + 4)

    # This is not a good algorithm.
    # theta = []
    # for i in range(train_labels.shape[1]):  # 10
    #     class_sum = sum(train_labels)[i]
    #     class_column = []
    #     for j in range(train_images.shape[1]):  # 784
    #         sum_feature_j = 0
    #         for k in range(train_images.shape[0]):  # 60000
    #             if train_labels[k][i] == 1:
    #                 sum_feature_j += train_images[k][j]
    #         class_column.append((sum_feature_j + 2) / (class_sum + 4))
    #     theta.append(class_column)
    # theta_map = np.array(theta).T

    return theta_map, pi_map


def log_likelihood(images, theta, pi):
    """ Inputs: images, theta, pi
        Returns the matrix 'log_like' of loglikehoods over the input images where
    log_like[i,c] = log p (c |x^(i), theta, pi) using the estimators theta and pi.
    log_like is a matrix of num of images x num of classes
    Note that log likelihood is not only for c^(i), it is for all possible c's."""

    factor_matrix = np.zeros((pi.shape[0], pi.shape[0]))
    np.fill_diagonal(factor_matrix, np.log(pi))
    log_like = images.dot(np.log(theta)) + (1 - images).dot(np.log(1 - theta)) + \
        np.ones((images.shape[0], theta.shape[1])).dot(factor_matrix)

    return log_like


def predict(log_like):
    """ Inputs: matrix of log likelihoods
    Returns the predictions based on log likelihood values"""

    predictions = np.argmax(log_like, axis=1)

    return predictions


def accuracy(log_like, labels):
    """ Inputs: matrix of log likelihoods and 1-of-K labels
    Returns the accuracy based on predictions from log likelihood values"""

    acc = np.mean(predict(log_like) == np.argmax(labels, axis=1))

    return acc


def image_sampler(theta, pi, num_images):
    """ Inputs: parameters theta and pi, and number of images to sample
    Returns the sampled images"""

    random_classes = np.random.choice(10, num_images, p=pi)
    random_probs = theta.T[random_classes]
    sampled_images = np.random.binomial(1, random_probs)

    return sampled_images


def main():
    N_data, train_images, train_labels, test_images, test_labels = load_mnist()

    # Fit MLE and MAP estimators
    theta_mle, pi_mle = train_mle_estimator(train_images, train_labels)
    theta_map, pi_map = train_map_estimator(train_images, train_labels)

    # Find the log likelihood of each data point
    loglike_train_mle = log_likelihood(train_images, theta_mle, pi_mle)
    loglike_train_map = log_likelihood(train_images, theta_map, pi_map)

    avg_loglike_mle = np.sum(loglike_train_mle * train_labels) / N_data
    avg_loglike_map = np.sum(loglike_train_map * train_labels) / N_data

    print("Average log-likelihood for MLE is ", avg_loglike_mle)
    print("Average log-likelihood for MAP is ", avg_loglike_map)

    train_accuracy_map = accuracy(loglike_train_map, train_labels)
    loglike_test_map = log_likelihood(test_images, theta_map, pi_map)
    test_accuracy_map = accuracy(loglike_test_map, test_labels)

    print("Training accuracy for MAP is ", train_accuracy_map)
    print("Test accuracy for MAP is ", test_accuracy_map)

    # Plot MLE and MAP estimators
    save_images(theta_mle.T, 'mle.png')
    save_images(theta_map.T, 'map.png')

    # Sample 10 images
    sampled_images = image_sampler(theta_map, pi_map, 10)
    save_images(sampled_images, 'sampled_images.png')


if __name__ == '__main__':
    main()
