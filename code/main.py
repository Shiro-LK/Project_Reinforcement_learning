# Utilisation de OpenAI Gym pour avoir l'agent

import gym
import time
from DQL import DQLAgent
from preprocess import preprocess
from keras.models import load_model
import pandas as pd
import numpy as np

env = gym.make('Breakout-v0')
state_size = env.observation_space.shape
action_size = env.action_space.n
agent = DQLAgent(state_size, action_size)

######## A changer
file = 'fourth_model'
restart = False

if __name__ == '__main__':
    nb_episode = 1000000
    batch_size = 32
    history = [0, 0, 0, 0]
    save_models_each = 300
    no_training_steps = 50000
    allow_replay = False
    load_model_from_file = file
    average_score = 0
    list_average_score = []
    repeat_action = 4

    if not restart:
        # On charge le dernier modele
        agent.continue_model(load_model_from_file)
        # Et les resultats
        save_average_score = pd.read_csv('output/' + file + '.csv')
    else:
        save_average_score = pd.DataFrame({'Episode': [0],
                                           'Average_score': [0]})

    for episode in range(nb_episode):
        print('Debut du ' + str(episode) + ' episode')
        state = env.reset()
        history = np.stack((state,state,state,state),axis=0)
        compteur = 0
        score = 0
        done = False
        prepross_history = preprocess(history)
        while not done:
            compteur += 1
            # Uncomment to unable rendering
            # env.render()
            # slepp is needed to correct an issue with pyglet/ mac os only ?
            # time.sleep(0.1)

            # on cherche la meilleure action

            action = agent.act(prepross_history)

            save_state = prepross_history

            # On la fait
            for action in range(repeat_action):
                next_state_not_processed, reward, done, info = env.step(action)
                score += reward

                history[0:3] = history[1:4]
                history[3] = next_state_not_processed

                next_state = preprocess(history)
                prepross_history = next_state
                # On la sauvegarde
                agent.add_to_memory(state=save_state, action=action, reward=reward, next_state=next_state, terminal=done)
                state = next_state

            if allow_replay:
                agent.replay(batch_size)
        message = 'Agent has reached the end in {} steps with score {}'.format(compteur, score)
        print(message)
        average_score += score
        if episode % save_models_each == 0 and episode != 0:
            agent.save('output/backup.h5')
            list_average_score.append((episode, average_score / save_models_each))
            save_average_score.loc[save_average_score.index[-1] + 1] = np.array(list_average_score[-1])
            save_average_score.to_csv('output/' + file + 'backup.csv')
            print('Le score moyen sur les {} derniers episode etait {}'.format(save_models_each,average_score))
            average_score = 0
        if no_training_steps > 0:
            no_training_steps -= compteur
        else:
            allow_replay = True
    save_average_score.to_csv('output/' + file + '.csv')
    agent.save('output/' + file + '.h5')
