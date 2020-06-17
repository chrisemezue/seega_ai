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
print("----Training model on all experience gathered----")
updated_agent_filename = 'agent/default_agent/agent2_2.hdf5'


lr = 0.0123
batch_size=500


#agent_white = load_policy_agent(h5file_dir=white_agent_dir)
#agent_black = load_policy_agent(h5file_dir=black_agent_dir)
experience_array=[]
main_dir = 'old_experience/old_exp2/'
exp_dirs = os.listdir(main_dir)
for exp_dir in exp_dirs:
    print(exp_dir)
    path = main_dir+exp_dir
    for file in os.listdir(path):
        filename=path+'/'+file
        experience_array.append(load_experience(h5py.File(filename)))

agent = load_policy_agent('agent/default_agent/agent1.hdf5')
exp_buffer = Experience_Collector()
final_buffer = exp_buffer.combine_buffer_array(experience_array)
print("Length of final buffer states: {}".format(final_buffer.states.shape))
#exp_buffer = self.load_experience(h5py.File(exp_filename))

#self.agent_white.train(exp_buffer,lr,batch_size)
agent.train(final_buffer,batch_size)
agent.serialize(updated_agent_filename)
