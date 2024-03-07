# WordleBot

This repository contains the code needed to access the New York Times daily Wordle puzzle and solve it via greedy search algorithm. 

## Key Takeaways

- **Performance**: Solves the Wordle Puzzle in 3.6 guesses on average, compared to [New York Times' best performing model's](https://www.nytimes.com/2022/08/17/upshot/wordle-wordlebot-new.html#:~:text=Only%20slightly.,more%20times%20in%20hard%20mode.) 3.4 guesses.
- **Technique**: WordleBot accesses the New York Times' website and navigates to the Wordle puzzle with `selenium` through the Chromium Browser. It chooses which word to guess based on the algorithm discussed below.
- **Efficiency Improvements**: WordleBot was optimized from its previous iterations using vectorized operations. Masking a `numpy` array, rather than iterating through a list, provided a 90% improvement in processing time. 

## Algorithm Design

WordleBot functions via the following steps:

1) t
2) c

## Future Directions



## Dependencies

- `Python 3.9`
- `NumPy`
- `selenium`
- `time`

