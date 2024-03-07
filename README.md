# WordleBot

This repository contains the code needed to access the New York Times daily Wordle puzzle and solve it via greedy search algorithm. 

## Key Takeaways

- **Performance**: Solves the Wordle Puzzle in 3.57 guesses on average, compared to [New York Times' best performing model's](https://www.nytimes.com/2022/08/17/upshot/wordle-wordlebot-new.html#:~:text=Only%20slightly.,more%20times%20in%20hard%20mode.) 3.40 guesses.
- **Technique**: WordleBot accesses the New York Times' website and navigates to the Wordle puzzle with `selenium` through the Chromium Browser. It chooses which word to guess based on the algorithm discussed below.
- **Efficiency Improvements**: WordleBot was optimized from its previous iterations using vectorized operations. Masking a `numpy` array, rather than iterating through a list, provided a 90% improvement in processing time. 

## Algorithm Design

WordleBot functions by iteratively reducing the number of possible answers. It looks to select the guess which maximally lowers this number in a single step. \

Specifically, it follows this process:

1) Assumes every word has the same probability of being the answer
2) Selects a word from the remaining possible answers

## Future Directions



## Dependencies

- `Python 3.9`
- `NumPy`
- `selenium`
- `time`

