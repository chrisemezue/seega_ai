import numpy as np
from keras.models import Sequential
import tensorflow as tf
from keras import models, layers
from keras import optimizers
from keras.preprocessing.image import ImageDataGenerator
from keras.layers import Dense, Dropout
from keras.utils import to_categorical
from keras.datasets import mnist
from keras.utils.vis_utils import model_to_dot
from keras.models import load_model
from IPython.display import SVG
from sklearn.preprocessing import StandardScaler, Normalizer
import numpy as np
from sklearn import preprocessing
from PIL import Image
import matplotlib
from sklearn.metrics import roc_curve, auc, f1_score
import matplotlib.pyplot as plt
import livelossplot
import h5py as h5py
from keras.layers.normalization import BatchNormalization
from sklearn.model_selection import train_test_split
from seega_agent import SeegaAgent
from encode_board import SeegaEncoder_Board
from experience_collector import Experience_Collector
from experience_buffer import Experience_Buffer
from dlgo import kerasutil
import importlib
import os



def load_policy_agent(h5file_dir):
    h5file = h5py.File(h5file_dir, 'r')
    model = kerasutil.load_model_from_hdf5_group(h5file['model'])
    encoder_name = h5file['encoder'].attrs['name']
    board_width = h5file['encoder'].attrs['board_width']
    board_height = h5file['encoder'].attrs['board_height']
    encoder = get_encoder_by_name(encoder_name, board_height)
    return SeegaAgent(model, encoder)

def get_encoder_by_name(name, board_size):
    module = importlib.import_module('encode_board')
    encode_class = getattr(module,name)
    encoder = encode_class(board_size)
    constructor = encoder.create(board_size)
    return constructor


def load_experience(h5file):
    """This loads the experience from the h5file"""
    return Experience_Buffer(states=h5file['experience']['states'],actions=h5file['experience']['actions'],rewards=h5file['experience']['rewards'], advantages=h5file['experience']['advantages']
    )
def train(n,batch_number,epoch):
    print("----Training model on all experience gathered----")
    old_agent_filename='agent/old_agent2/agent2.hdf5'
    updated_agent_filename = 'agent/new_agent2/agent2.hdf5'
    for_archive = 'agent/agent2_archive/agent2_{}.hdf5'.format(n)
    #batch_size=1000
    batch_size = batch_number
    #agent_white = load_policy_agent(h5file_dir=white_agent_dir)
    #agent_black = load_policy_agent(h5file_dir=black_agent_dir)
    experience_array=[]
    main_dir = 'experience/'
    exp_dirs = os.listdir(main_dir)
    for exp_dir in exp_dirs:
        print(exp_dir)
        path = main_dir+exp_dir
        for file in os.listdir(path):
            filename=path+'/'+file
            experience_array.append(load_experience(h5py.File(filename)))

    old_agent = load_policy_agent(updated_agent_filename)
    old_agent.serialize(old_agent_filename)

    agent = load_policy_agent(updated_agent_filename)
    exp_buffer = Experience_Collector()
    final_buffer = exp_buffer.combine_buffer_array(experience_array)
    print("Length of final buffer states: {}".format(final_buffer.states.shape))
    #exp_buffer = self.load_experience(h5py.File(exp_filename))

    #self.agent_white.train(exp_buffer,lr,batch_size)
    agent.train(final_buffer,batch_size,epoch,n)

    agent.serialize(updated_agent_filename)
    agent.serialize(for_archive)

"""
#datasets = datasets.reshape((int(datasets.shape[0]/num_encoded_layers),num_rows,num_cols,num_encoded_layers))
label = to_categorical(label)

X, X_test, y, y_test = train_test_split(datasets,label, test_size=0.05)
X_train, X_valid, y_train, y_valid = train_test_split(X,y, test_size=0.03)

print("Shape of board dataset: {}".format(datasets.shape))
print("Shape of label dataset: {}".format(label.shape))

input_shape = (num_rows,num_cols,num_encoded_layers,)

# Build and train neural network

model = models.Sequential()
model.add(layers.Conv2D(100, (2, 2),padding='same', data_format="channels_last", input_shape=input_shape))
#model.add(BatchNormalization())
#model.add(layers.MaxPooling2D((2, 2)))
model.add(layers.Conv2D(100,(2,2),padding='same', activation='relu'))
#model.add(layers.MaxPooling2D((1, )))
model.add(layers.Conv2D(128, (2,2),padding='same', activation='relu'))
# model.add(BatchNormalization())
#model.add(layers.MaxPooling2D((2, 2)))
model.add(layers.Conv2D(256,(2,2), activation='relu'))
model.add(layers.Conv2D(512,(2,2), activation='relu'))
# model.add(BatchNormalization())
#model.add(layers.MaxPooling2D((2, 2)))
model.add(layers.Flatten())
#model.add(layers.Dropout(0.5))
#model.add(layers.Dense(100, activation='relu'))
# model.add(BatchNormalization())
#model.add(layers.Dropout(0.2))
model.add(layers.Dense(25, activation='sigmoid'))
model.add(layers.Dense(num_classes, activation='softmax'))
model.summary()
# Compile model
model.compile(loss='categorical_crossentropy', optimizer=optimizers.adam(), metrics=['accuracy'])

# Now we fit the preprocessed image, stored in the generator, into the model

history = model.fit(X_train, y_train,epochs=10, validation_data=[X_valid, y_valid],batch_size=batch_size)

# We can save our model after training
model.save('seega_model_NEW_ENCODING.h5')

test_loss,score = model.evaluate(X_test,y_test)
print("Accuracy on test data: {}".format(score))

# cnn.summary()
# Now let's plot the loss and accuracy of the model over the training and validation data during training

acc = history.history['acc']
val_acc = history.history['val_acc']
loss = history.history['loss']
val_loss = history.history['val_loss']

epochs = range(1, len(acc) + 1)

plt.plot(epochs, acc, 'bo', label='Training accuracy')
plt.plot(epochs, val_acc, 'b', label='Validation accuracy')
plt.title('Training and validation accuracy')
plt.legend()

plt.figure()

plt.plot(epochs, loss, 'bo', label='Training loss')
plt.plot(epochs, val_loss, 'b', label='Validation loss')
plt.title('Training and validation loss')
plt.legend()

plt.show()


# test_loss, test_acc = model.evaluate(X_test,y_test)
# print(str(test_acc))

"""