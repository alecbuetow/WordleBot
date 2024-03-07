'''
All functions found here are optimized versions of those found in readable_functions.py. Please check there for documentation.
Variables were declared as infrequently as possible to minimize execution time, since training the Recurrent Neural Network
requires millions of trials, and get_compatible_words() is the function responsible for creating the feature space in each trial. 
'''

import numpy as np

class WordleBot:

    @staticmethod
    def get_compatible_words(guess, feedback, remaining_words):
        mask = np.ones(remaining_words.shape[0], dtype=bool)
        for idx,(letter,color) in enumerate(zip(guess,feedback)):
            if color == 0:
                num_yellows, num_greens = np.count_nonzero(guess[feedback==1] == letter), np.count_nonzero(guess[feedback==2] == letter)         
                if num_greens==0 and num_yellows==0:
                    mask = np.logical_and(mask,np.all(remaining_words != letter,axis=1))
                if num_yellows >= 1:          
                    mask = np.logical_and(mask,np.logical_and(np.count_nonzero(remaining_words[:,np.logical_and(np.arange(5) != idx, feedback!=2)] == letter,axis=1)==num_yellows,remaining_words[:,idx] != letter))
                elif num_greens >= 1: 
                    mask = np.logical_and(mask, np.all(remaining_words[:,~np.logical_and(feedback==2, guess==letter)] != letter, axis=1)) 
            elif color == 1:   
                mask = np.logical_and(mask,np.logical_and(np.sum(remaining_words[:,feedback!=2] == letter,axis=1)>=np.count_nonzero(guess[feedback==1] == letter),remaining_words[:,idx] != letter))
            elif color == 2:
                mask = np.logical_and(mask,remaining_words[:,idx] == letter)
        return mask

    @staticmethod
    def get_feedback(guess, answer):
        feedback = np.zeros(5)
        feedback[guess == answer] = 2
        subset_idx = np.where(feedback != 2)
        subset = guess[subset_idx]
        yellow_letters = subset[np.in1d(subset, answer[subset_idx])]
        for letter in set(yellow_letters):
            feedback[subset_idx[0][np.where(subset == letter)[0][:np.count_nonzero(letter == answer[subset_idx])]]] = 1 
        return feedback

    @staticmethod
    def get_num_compatible_words(guess, answer_array):
        return np.apply_along_axis(lambda x,y,z: np.count_nonzero(WordleBot.get_compatible_words(y,x,z)), 1, np.apply_along_axis(lambda x,y: WordleBot.get_feedback(y,x), 1, answer_array, guess), guess, answer_array)

    @staticmethod
    def solve(guess, answer, all_possible_guesses):
        remaining_words = all_possible_guesses.copy()
        for guess_idx in range(6):
            if all(guess == answer):
                return guess_idx+1
            remaining_words = remaining_words[WordleBot.get_compatible_words(guess, WordleBot.get_feedback(guess, answer), remaining_words)]
            guess = remaining_words[np.argmin(np.mean(np.apply_along_axis(WordleBot.get_num_compatible_words, 1, remaining_words, remaining_words), axis=1))]
            if len(remaining_words) > 2 and len(remaining_words) <= 20 and np.mean(np.count_nonzero(guess == remaining_words, axis=1)) >= 3:
                guess = all_possible_guesses[np.argmin(np.mean(np.apply_along_axis(WordleBot.get_num_compatible_words, 1, all_possible_guesses, remaining_words), axis=1))]