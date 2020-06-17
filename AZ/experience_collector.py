import numpy as np
import h5py as hp
from experience_buffer import Experience_Buffer
"""
This to keep track of all the decisions from the current game episode until it is complete.
"""
class Experience_Collector():
    def __init__(self):
        self.states=[]
        self.actions = []
        self.rewards = []
        self.advantage=[]
        self.current_episode_states = []
        self.current_episode_actions = []
        self.current_episode_estimated_values = []


    def begin_episode(self):
        self.current_episode_actions = []
        self.current_episode_states = []
        self.current_episode_estimated_values = []

    def record_decision(self,state,action,estimated_value):
        self.current_episode_actions.append(action)
        self.current_episode_states.append(state)
        self.current_episode_estimated_values.append(estimated_value)

    def complete_episode(self,reward):

        num_game_states = len(self.current_episode_states)
        self.states+=self.current_episode_states
        self.actions += self.current_episode_actions
        #this is giving the same reward to the whole decisions made in the game
        #In the future, will need to be changed
        #print("LENGTH OF GAME STATES:    {}".format(num_game_states))
        #assert(len(reward) == num_game_states)
        #self.rewards+=reward
        #reward_to_tanh = np.tanh(reward)
        #reward_to_tanh = reward_to_tanh.tolist()
        reward = [reward for i in range(num_game_states)]
        self.rewards += reward

        for i in range(num_game_states):
            advantage = reward[i] - self.current_episode_estimated_values[i]
            self.advantage.append(advantage)

        self.current_episode_actions = []
        self.current_episode_states = []
        self.current_episode_estimated_values = []
    def get_states(self):
        return self.states
    def get_actions(self):
        return self.actions
    def get_rewards(self):
        return self.rewards
    def get_advantages(self):
        return self.advantage
    def to_buffer(self):
        return Experience_Buffer(states = np.array(self.states), actions = np.array(self.actions), rewards = np.array(self.rewards),advantages=np.array(self.advantage))

    def combine_experience(self, experience_dict_black, experience_dict_white):
        combined_state = []
        combined_action = []
        combined_reward = []
        combined_advantage = []
        """
        Each of them is of the form [states, actions, rewards]
        """
        #Append state, action and reward for Experience 1
        for s1 in experience_dict_black['states']:
            combined_state.append(s1)
        for a1 in experience_dict_black['actions']:
            combined_action.append(a1)
        for r1 in experience_dict_black['rewards']:
            combined_reward.append(r1)
        for ad1 in experience_dict_black['advantages']:
            combined_advantage.append(ad1)

        print("Length BEFORE: {}   {}    {}".format(len(combined_state),len(combined_action),len(combined_reward)))
        #Append state,action and reward for Experience 2
        for e2 in experience_dict_white['states']:
            combined_state.append(e2)
        for a2 in experience_dict_white['actions']:
            combined_action.append(a2)
        for r2 in experience_dict_white['rewards']:
            combined_reward.append(r2)
        for ad2 in experience_dict_white['advantages']:
            combined_advantage.append(ad2)


        print("Length AFTER: {}   {}    {}".format(len(combined_state), len(combined_action), len(combined_reward)))
        print(np.asarray(combined_state).shape)
        print(np.asarray(combined_action).shape)
        print(np.asarray(combined_reward).shape)
        print(np.asarray(combined_advantage).shape)
        return Experience_Buffer(states=np.array(combined_state), actions=np.array(combined_action), rewards=np.array(combined_reward), advantages=np.array(combined_advantage))

    def combine_buffer_array(self,buffer_array):
        length_buffer = len(buffer_array)
        combined_state = np.concatenate((buffer_array[0].states),axis=0)
        #print(combined_state.shape)
        #print(buffer_array[1].states.shape)
        for i in range(1,length_buffer):
            state = np.concatenate((buffer_array[i].states),axis=0)
            combined_state=np.concatenate((combined_state,state),axis=0)
        #states = [c.states for c in buffer_array]
        #combined_state = np.concatenate((states),axis=0)
        combined_action = np.concatenate([c.actions for c in buffer_array])
        combined_reward = np.concatenate([c.rewards for c in buffer_array])
        combined_advantage = np.concatenate([c.advantages for c in buffer_array])
        return Experience_Buffer(combined_state,combined_action,combined_reward,combined_advantage)


