import numpy as np
import h5py
import pickle


class Experience_Buffer():
    def __init__(self,states,actions,rewards,advantages):
        self.states = states
        self.actions = actions
        self.rewards = rewards
        self.advantages = advantages

    def serialize(self,h5file):
        """This is to create the h5file and store the states,actions and rewards to it"""
        h5file.create_group('experience')
        h5file['experience'].create_dataset('states', data=self.states)
        h5file['experience'].create_dataset('actions', data=self.actions)
        h5file['experience'].create_dataset('rewards', data=self.rewards)
        h5file['experience'].create_dataset('advantages', data=self.advantages)
    def load_experience(self,h5file):
        """This loads the experience from the h5file"""
        return Experience_Buffer(states=h5file['experience']['states'],actions=h5file['experience']['actions'],rewards=h5file['experience']['rewards'],advantages=h5file['experience']['advantages']
        )





