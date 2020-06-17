import numpy as np
from experience_collector import Experience_Collector
import keras
from dlgo import kerasutil
import importlib
import h5py
from game_state import Game_State
from keras import optimizers
import pickle
import os
import matplotlib.pyplot as plt

#This is to define the PolicyAgent for SeegaAI
#The SeegaAgent is responsibe for selecting moves
# according to the model and changing its behaviour in response to its experience

class SeegaAgent():
    def __init__(self,model,encoder):
        self.model = model
        self.encoder = encoder

    """
    game_state is a dictionary that contains:ff
    board
    player
    step
    """

    def train(self,experience,batch_size,epoch,n):

        self.model.compile(loss=["categorical_crossentropy","mse"],optimizer=optimizers.adam(),loss_weights=[1.0,0.5])

        experience_states,policy_target, value_target = self.prepare_experience_data(experience,self.encoder.num_moves())
        history = self.model.fit(experience_states,[policy_target,value_target],epochs=epoch, batch_size=batch_size)

        #print(history.history)
        train_save = 'loss_plot/train_fig_{}'.format(n)
        #test_save = 'test_fig_{}'.format(n)
        # Plot training & validation accuracy values
        plt.plot(history.history['loss'])
        #plt.plot(history.history['val_acc'])
        plt.title('Model loss')
        plt.ylabel('Loss')
        plt.xlabel('Epoch')
        plt.savefig(train_save)





    def select_move(self,game_state):
        board_tensor = self.encoder.board_encode(game_state['board'], game_state['player'], game_state['step'])
        game_STATE = Game_State(game_state['board'],game_state['player'],game_state['step'])
        actions,values = self.model.predict(board_tensor)
        prob_move = self.clip_probability(actions[0])
        estimated_value = values[0][0]

        #Choose a move from the probability output of moves from the model
        num_moves = self.encoder.num_moves()
        #print("NUM OF MOVES: ----------------------------{}".format(num_moves))
        candidates = np.arange(num_moves)
        ranked_moves = np.random.choice(candidates,num_moves,replace=False,p=prob_move)
        #print("RANKED MOVES:--------------------------{}".format(ranked_moves))
        for point in ranked_moves:
            move = self.encoder.decode_point_index(point)
            if game_STATE.is_valid_move(move, game_state['board'],game_state['player'],game_state['step']):
                if self.collector is not None:
                    self.collector.record_decision(state=board_tensor,action=point,estimated_value=estimated_value)
                    return move


    def prepare_experience_data(self, experience, num_moves):
        """This takes the experience buffer"""
        experience_size = experience.states.shape[0]

        experience_states = np.concatenate((experience.states),axis=0)
        policy_target = np.zeros((experience_size,num_moves))
        value_target = np.zeros((experience_size,1))
        #print(experience_states.shape)
        #print(experience.states.shape)
        #print(num_moves)
        #target_vectors = np.zeros((experience_size, num_moves))
        for i in range(experience_size):
            action = experience.actions[i]
            reward = experience.rewards[i]
            policy_target[i][action] = experience.advantages[i]
            value_target[i] = reward
        return experience.states,policy_target, value_target

    def clip_probability(self,original_prob):
        #This is to make sure that the probabilities from the model don't go pushed all the way to 0 or 1
        min_p = 1e-6
        max_p = 1-min_p
        clipped_probs = np.clip(original_prob,min_p,max_p)
        clipped_probs = clipped_probs / np.sum(clipped_probs)
        return clipped_probs

    def set_collector(self,collector):
        """This sets the Experience_Collector which wll take the states and actions for the gamee"""
        self.collector = collector


    def load_policy_agent(self,h5file_dir):
        h5file = h5py.File(h5file_dir, 'r')
        model = kerasutil.load_model_from_hdf5_group(h5file['model'])
        encoder_name = h5file['encoder'].attrs['name']
        board_width = h5file['encoder'].attrs['board_width']
        board_height = h5file['encoder'].attrs['board_height']
        encoder = self.get_encoder_by_name(encoder_name,board_height)
        return SeegaAgent(model,encoder)


    def serialize(self,h5file_dir):

        if os.path.isfile(h5file_dir):
            os.remove(h5file_dir)
        with h5py.File(h5file_dir,'a') as h5file:
        #This saves encoding details and the model to a h5py file
            h5file.create_group('encoder')
            h5file['encoder'].attrs['name'] = self.encoder.name()
            h5file['encoder'].attrs['board_width'] = self.encoder.board_width()
            h5file['encoder'].attrs['board_height'] = self.encoder.board_height()
            h5file.create_group('model')
            kerasutil.save_model_to_hdf5_group(self.model,h5file['model'])
        """
        serial = {
            'encoder' : self.encoder.name(),
            'encoder_board_width': self.encoder.board_width(),
            'encoder_board_height': self.encoder.board_height(),



        }
        """
    def get_encoder_by_name(self, name, board_size):
        module = importlib.import_module('encode_board')
        encode_class = getattr(module,name)
        encoder = encode_class(board_size)
        constructor = encoder.create(board_size)
        return constructor

