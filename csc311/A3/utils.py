import numpy as np


def load_data(filename, load2=True, load3=True):
    """Loads data for 2's and 3's
    Inputs:
    filename: Name of the file.
    load2: If True, load data for 2's.
    load3: If True, load data for 3's.
    """
    assert (load2 or load3), "At least one dataset must be loaded."
    data = np.load(filename)
    if load2 and load3:
        inputs_train = np.hstack((data['train2'], data['train3']))
        inputs_valid = np.hstack((data['valid2'], data['valid3']))
        inputs_test = np.hstack((data['test2'], data['test3']))
        target_train = np.hstack((np.zeros((1, data['train2'].shape[1])), np.ones((1, data['train3'].shape[1]))))
        target_valid = np.hstack((np.zeros((1, data['valid2'].shape[1])), np.ones((1, data['valid3'].shape[1]))))
        target_test = np.hstack((np.zeros((1, data['test2'].shape[1])), np.ones((1, data['test3'].shape[1]))))
    else:
        if load2:
            inputs_train = data['train2']
            target_train = np.zeros((1, data['train2'].shape[1]))
            inputs_valid = data['valid2']
            target_valid = np.zeros((1, data['valid2'].shape[1]))
            inputs_test = data['test2']
            target_test = np.zeros((1, data['test2'].shape[1]))
        else:
            inputs_train = data['train3']
            target_train = np.zeros((1, data['train3'].shape[1]))
            inputs_valid = data['valid3']
            target_valid = np.zeros((1, data['valid3'].shape[1]))
            inputs_test = data['test3']
            target_test = np.zeros((1, data['test3'].shape[1]))

    return inputs_train.T, inputs_valid.T, inputs_test.T, target_train.T, target_valid.T, target_test.T
