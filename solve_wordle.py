'''
Accesses the New York Times Wordle Site and solves the daily Wordle puzzle based on a greedy search algorithm.
'''

#Wordle dependencies
import numpy as np

#NYT dependencies
import time
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

#read in all 2315 possible Wordle answers
with open('answers.txt', 'r') as all_possible_guesses_file:
    all_possible_guesses = [g.strip() for g in all_possible_guesses_file.readlines()]
all_possible_guesses = np.asarray([list(w) for w in all_possible_guesses]) #convert to array for faster operations



class NYT:
    """Tools to solve the current Wordle by accessing the NYT Wordle website"""

    #convert info from NYT website to numeric form for WordleBot to read
    color_dict = {'absent': 0, 'present': 1, 'correct': 2, 'empty': -1}

    @classmethod
    def load_wordle_site(cls):
        """Open Wordle site"""
        cls.chrome = Chrome()
        cls.chrome.get('https://www.nytimes.com/games/wordle/index.html')
        play_button = cls.chrome.find_element(By.XPATH, '//button[text()="Play"]')
        play_button.click()

        #close tutorial popup
        tutorial_exit_path = (By.XPATH, '//button[@class="Modal-module_closeIcon__TcEKb"]')
        close_tutorial = WebDriverWait(cls.chrome, 10).until(EC.presence_of_element_located(tutorial_exit_path))
        close_tutorial.click()
        time.sleep(2) #gives time for closing animation to complete 

    @classmethod
    def send_guess(cls, guess: np.array):
        """Reformat guess from an array to string, send it to Wordle website"""
        guess = ''.join([letter for letter in guess])
        actions = ActionChains(cls.chrome)
        actions.send_keys(guess)
        actions.send_keys(Keys.RETURN)
        actions.perform()
        time.sleep(2) #gives time for typing animation to complete 

    @classmethod
    def get_feedback(cls, guess_idx: int) -> np.array:
        """Read Wordle website to determine which letters from a guess are black/yellow/green"""
        feedback_tiles = cls.chrome.find_elements(By.XPATH, '//div[@class="Tile-module_tile__UWEHN"]')
        feedback_colors = [tile.get_attribute("data-state") for tile in feedback_tiles]
        feedback = np.asarray([cls.color_dict[color] for color in feedback_colors])
        feedback = feedback[5*guess_idx:5*(guess_idx+1)] #only consider row we just guessed in
        return feedback
    
    @classmethod
    def solve(cls):
        """Solves today's Wordle!"""
        cls.load_wordle_site()
        guess, remaining_words = np.asarray(list('raise')), all_possible_guesses #initialize first guess and all words that can be guessed
        #submit guess, update remaining words based on feedback, get new guess 
        for guess_idx in range(6):
            cls.send_guess(guess)
            feedback = cls.get_feedback(guess_idx)
            guess, remaining_words = WordleBot.get_best_guess(guess, feedback, remaining_words)



class WordleBot:
    """Tools to solve the Wordle via deterministic greedy search algorithm"""

    @staticmethod
    def get_compatible_words(guess: np.array, feedback: np.array, remaining_words: np.array) -> np.array:
        """
        Given a list of possible answers ('remaining_words'), a word that was just guessed ('guess') and feedback for
        each letter of that guess ('feedback') e.g. black/yellow/green, what answers are still possible ('mask')?
        """
        #boolean array for which words in remaining_words are still possible answers
        mask = np.ones(remaining_words.shape[0], dtype=bool) 
        #iterate through each letter of guess with its corresponding feedback color
        for idx,(letter,color) in enumerate(zip(guess,feedback)):
            if color == 0: #black
                #count number of times this black letter also appears as a yellow or green elsewhere in the word
                num_yellows = np.count_nonzero(guess[feedback==1] == letter) 
                num_greens = np.count_nonzero(guess[feedback==2] == letter)  
                #if this black letter is not green or yellow elsewhere, remove any word which has the letter
                if num_greens==0 and num_yellows==0:
                    updated_mask = np.all(remaining_words != letter,axis=1)
                    mask = np.logical_and(mask, updated_mask)
                #if this black letter is yellow elsewhere
                if num_yellows >= 1: 
                    #remove words with this letter if it appears in the spot where it is black
                    remove_black = remaining_words[:,idx] != letter
                    #count number of times each word has this letter in places that are not green or the current index
                    included_idx = np.logical_and(np.arange(5) != idx, feedback!=2)
                    count_yellows = np.count_nonzero(remaining_words[:,included_idx] == letter,axis=1) 
                    #keep only words which have this letter the same number of times (excluding greens) as the letter is yellow in this guess (we know no word can have this letter a greater number of times because it is also black at least once)
                    proper_number_of_yellows = count_yellows==num_yellows
                    updated_mask = np.logical_and(proper_number_of_yellows,remove_black)  
                    mask = np.logical_and(mask, updated_mask)
                #if this black letter is green elsewhere and not yellow elsewhere
                elif num_greens >= 1:
                    #remove all words with this letter except for where it is green 
                    not_green_idx = ~np.logical_and(feedback==2, guess==letter) 
                    updated_mask = np.all(remaining_words[:,not_green_idx] != letter, axis=1)
                    mask = np.logical_and(mask, updated_mask) 
            elif color == 1: #yellow
                #remove words with this letter if it appears in the spot where it is yellow (yellow letters must appear ELSEWHERE or they would be green)
                remove_identical = remaining_words[:,idx] != letter
                #count number of yellows in this word
                num_yellows = np.count_nonzero(guess[feedback==1] == letter)
                #count number of times each word has this letter in places that are not green
                count_yellows = np.count_nonzero(remaining_words[:,feedback!=2] == letter,axis=1)
                #keep only words which have this letter the same number of times or greater (excluding greens) as the letter is yellow in this guess (the answer could have this letter more than once, information we will not gain if our guess only had it once)
                proper_number_of_yellows = count_yellows>=num_yellows
                updated_mask = np.logical_and(proper_number_of_yellows,remove_identical)
                mask = np.logical_and(mask,updated_mask)
            elif color == 2: #green
                #remove all words that don't have this letter at the same spot
                updated_mask = remaining_words[:,idx] == letter
                mask = np.logical_and(mask,updated_mask)
        return mask

    @staticmethod
    def get_feedback(guess: np.array, answer: np.array) -> np.array:
        """Given the correct answer and a guess, what would the feedback for each letter be (e.g., black, yellow, green)"""
        #start feedback as all black, update accordingly
        feedback = np.zeros(5) 
        #if a letter is in our guess and answer at the same index, it is green
        feedback[guess == answer] = 2
        #only consider letters that are not green
        subset_idx = np.where(feedback != 2)
        subset = guess[subset_idx]
        #yellow letters are ones which appear in the answer and word but not at the same place
        yellow_letters = subset[np.in1d(subset, answer[subset_idx])]
        for letter in set(yellow_letters):
            #only make the first N occurences of this letter in our guess yellow, where N = number of times the letter appears in the answer
            num_yellows = np.count_nonzero(letter == answer[subset_idx]) 
            location = np.where(subset == letter)[0][:num_yellows]
            feedback[subset_idx[0][location]] = 1
        return feedback

    @staticmethod
    def get_num_compatible_words(guess: np.array, answer_array: np.array) -> np.array:
        """Given an array of possible answers and 1 guess, returns how many compatible words would be left for each answer if 'guess' was guessed"""
        #get feedback for all answers in 'answer_array' given 'guess' was guessed, lambda function used to switch arguments as np.apply_along_axis requires iterable argument to be given first
        feedback_array = np.apply_along_axis(lambda x,y: WordleBot.get_feedback(y,x), 1, answer_array, guess)
        #get number of compatible words for every answer given 'guess' and feedback for that guess
        func = lambda x,y,z: np.count_nonzero(WordleBot.get_compatible_words(y,x,z))
        return np.apply_along_axis(func, 1, feedback_array, guess, answer_array)

    @staticmethod
    def solve(guess: np.array, answer: np.array, all_possible_guesses: np.array) -> int:
        """
        Solves the Wordle given a first guess ('guess'), the answer ('answer') and a list of possible answers (all_possible_guesses). 
        Answer is used to return feedback after each new guess, the guessing algorithm itself does not have access to this information. 
        The list of possible answers is what the guessing algorithm is allowed to select from. Returns the number of guesses it takes.
        """
        remaining_words = all_possible_guesses.copy()
        for guess_idx in range(6): #only get 6 guesses
            if all(guess == answer): #if guess is correct return how many guesses it took to get there
                return guess_idx+1
            #subset remaining words to only include compatible words (those which are possible answers)
            feedback = WordleBot.get_feedback(guess, answer)
            possible_answers = WordleBot.get_compatible_words(guess, feedback, remaining_words)
            remaining_words = remaining_words[possible_answers]
            #given the current possible answers (remaining_words), how many possible answers are left for every possible guess/answer combination
            num_possible_answers = np.apply_along_axis(WordleBot.get_num_compatible_words, 1, remaining_words, remaining_words)
            #average the number of possible answers left for each guess and select the best guess (where the fewest average possible answers remaining is)
            average_possible_answers = np.mean(num_possible_answers, axis=1)
            guess = remaining_words[np.argmin(average_possible_answers)]
            #if there are 3-20 possible answers left and they share more than half their letters on average
            if len(remaining_words) > 2 and len(remaining_words) <= 20:
                shared_letters = np.mean(np.count_nonzero(guess == remaining_words, axis=1)) 
                if shared_letters >= 3:
                    #perform the same guessing algorithm as before but allow it to select a guess from all possible guesses, rather than just the remaining words
                    num_possible_answers = np.apply_along_axis(WordleBot.get_num_compatible_words, 1, all_possible_guesses, remaining_words)
                    average_possible_answers = np.mean(num_possible_answers, axis=1)
                    guess = all_possible_guesses[np.argmin(average_possible_answers)]

    @staticmethod
    def get_best_guess(guess: np.array, feedback: np.array, remaining_words: np.array) -> tuple:
        """
        Finds the best guess based on the last word guessed, the feedback recieved and the previously remaining words.
        Returns the best guess and new remaining words. 
        """
        #subset remaining words to only include compatible words (those which are possible answers)
        possible_answers = WordleBot.get_compatible_words(guess, feedback, remaining_words)
        remaining_words = remaining_words[possible_answers]
        #given the current possible answers (remaining_words), how many possible answers are left for every possible guess/answer combination
        num_possible_answers = np.apply_along_axis(WordleBot.get_num_compatible_words, 1, remaining_words, remaining_words)
        #average the number of possible answers left across each guess and select the best guess (where the fewest average possible answers remaining is)
        average_possible_answers = np.mean(num_possible_answers, axis=1)
        guess = remaining_words[np.argmin(average_possible_answers)]
        return guess, remaining_words
