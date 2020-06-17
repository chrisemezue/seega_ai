import os
import shutil
import seega_ai
import seega_ai2
import seega_agent
import train_seega2
import multiprocessing as mp

"""
This is where we bring the various functions together into a full package.

This package
-collects all the game experience
-then uses the experience to train the Seega Agent
-then plays a game of 100 games ; new SeegaAI vs old SeegaAI.
-   If new SeegaAI wins more than 60 of the games, then we move on with the new one, else, we use the old SeegaAI

"""


def get_expereience(ts, t):
    print("----------------GETTING EXPERIENCE-----------------")
    s = 'python ai_game_cli.py -ai0 seega_ai2 -ai1 seega_ai2 -train_samples {} -instance {}'.format(ts, t)
    os.system(s)


def agent_train(n, batch_size,epoch):
    print("----------------TRAINING MODEL ON EXPERIENCE---------------")
    train_seega2.train(n, batch_size,epoch)


def agent_test(n, ts):
    print("------------------TESTING TRAINED MODEL AGAINST OLD MODEL-------------")
    '''This is where we play the new and old agent to ascertain the level of improvement of the new agent'''
    if n == 'black':
        t = 'python ai_game.py -ai0 seega_ai2 -ai1 seega_aiold -train_samples {}'.format(
            ts)  # New agent is BLACK, Old agent is WHITE
    if n == 'white':
        t = 'python ai_game.py -ai0 seega_aiold -ai1 seega_ai2 -train_samples {}'.format(
            ts)  # New agent is WHITE, Old agent is BLACK
    os.system(t)


def review(ts, n):
    print("------------------MAKING DECISION-----------------")
    archive_test = 'agent_test_result_archive.txt'
    '''Check the scores, use the old or new model based on result and go back to getting experience'''
    score_array = []  # format: NEW, OLD, OLD, NEW
    f = open("agent_test_result.txt", "r")
    f1 = f.readlines()
    for x in f1:
        score_array = score_array + x.split(':')

    f.close()
    if len(score_array) == 5:
        score_array = score_array[:-1]  # to remove the last : in the agent_test result
    #print(score_array)
    #print(len(score_array))
    assert (len(score_array) == 4)
    score_new_1st_round = int(score_array[0])
    score_old_1st_round = int(score_array[1])
    score_new_2nd_round = int(score_array[3])
    score_old_2nd_round = int(score_array[2])

    # string_score = [str(s) for s in score_array]

    # print(score_new_2nd_round)
    # print(score_new_1st_round)
    # print(ts)
    if ((score_new_1st_round / (score_new_1st_round + score_old_1st_round)) >= 0.6 or (
            score_new_2nd_round / (score_new_2nd_round + score_old_2nd_round)) >= 0.6):
        s = 'Round {}: '.format(n) + 'New model used ' + ' '.join(score_array)

    else:
        # If we are to use old model
        old_agent_filename = 'agent/old_agent2/agent2.hdf5'
        new_agent_filename = 'agent/new_agent2/agent2.hdf5'
        os.replace(old_agent_filename, new_agent_filename)

        s = '{}th round: '.format(n) + 'New model not used' + ' '.join(score_array)

    # Update Statistics report
    with open(archive_test, 'a+') as f:
        f.write(s + "\n")
        f.close()
    os.remove("agent_test_result.txt")


if __name__ == '__main__':
    train_samples = 500
    test_samples = 100
    batch_size = 32000
    epoch=10
    total = 10
    for i in range(total):
        print("--------------{} OF {}----------".format(i + 1, total))

        # Using multiprocessing for parallel computing

        cores = mp.cpu_count()
        #print("Number of cores: {}".format(cores))
        pool = mp.Pool(cores)

        # arg for experience:
        exp_args = [(train_samples, 0), (train_samples, 1), (train_samples, 2), (train_samples, 3)]
        results = pool.starmap(get_expereience, exp_args)

        # get_expereience(train_samples,0)
        #train on experience
        agent_train(i,batch_size,epoch)

        #test trained model
        test_args= [('black', test_samples),('white', test_samples)]
        test_results = pool.starmap(agent_test,test_args)

        #make decision on test results
        review(test_samples, i)

