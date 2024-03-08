# WordleBot

This repository contains the code needed to access the New York Times daily Wordle puzzle and solve it via semi-greedy search algorithm. 

## Key Takeaways

- **Performance**: Solves the Wordle Puzzle in 3.54 guesses on average, compared to [New York Times' best performing model's](https://www.nytimes.com/2022/08/17/upshot/wordle-wordlebot-new.html#:~:text=Only%20slightly.,more%20times%20in%20hard%20mode.) 3.40 guesses. For reference, [the average wordle user takes 3.92 guesses](https://www.forbes.com/sites/mattgardner1/2022/03/05/wordle-stats-reveal-10-best-countries-and-america-misses-out/?sh=659172502d62). 
- **Technique**: WordleBot accesses the New York Times' website and navigates to the Wordle puzzle with `selenium` through the Chromium Browser. It chooses which word to guess based on the algorithm discussed below.
- **Efficiency Improvements**: WordleBot was optimized from its previous iterations using vectorized operations. Masking a `numpy` array, rather than iterating through a list, provided a 90% improvement in processing time. 

## Algorithm Design

WordleBot functions by iteratively reducing the number of possible answers. It looks to select the guess which maximally lowers this number in a single step. 

Specifically, it follows this process:

1) Considers only the remaining possible answers, the words which could be the answer based on the information it has gathered so far. 
2) Assumes all of these words have the same probability of being the answer
3) Selects a word to guess, "W"
4) Selects an answer, "A"
5) Counts the number of remaining possible answers if it had guessed word "W" and the answer had been "A"
6) Repeats step 5 for all answers, and averages the number of remaining possible answers for word "W"
7) Repeats steps 4-6 for all guessable words
8) Selects the word "W" with the lowest averages number of remaining possible answers
9) Guesses word "W" and gets feedback (i.e., which letters are black/green/yellow) from the New York Times website
10) Subsets the remaining possible answers based on this feedback and repeats steps 1-9

In doing so, it is able to solve all Wordle answers in 6 guesses or fewer, marking a 100% success rate.

## Future Directions

Reinforcement learning seems to be a promising machine learning approach which could solve the Wordle puzzle stochastically. Based on preliminary research, it seems that training such an algorithm requires millions of cycles and resulting models take 4 guesses on average, worse than our deterministic approach. For my next steps, I would like to combine the two and see if I can leverage the reinforcement learning model's ability to look more than one step ahead in further improving the semi-greedy search algorithm, which only sees one state in front of its current one. 

## Dependencies

- `Python 3.9`
- `NumPy`
- `selenium`
- `time`

