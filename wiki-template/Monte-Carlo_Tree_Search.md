# Monte-Carlo Tree Search

# Table of Contents
- [Monte-Carlo Tree Search](#monte-carlo-tree-search)
  * [Motivation](#motivation)
  * [Application](#application)
  * [Trade-offs](#trade-offs)     
     - [Advantages](#advantages)
     - [Disadvantages](#disadvantages)
  * [Future improvements](#future-improvements)

## Monte-Carlo Tree Search
The MCTS Agent can be executed from the file myTeam_MCTS.py in the agents folder.
### Motivation  
Uncertainty Handling: MCTS is particularly effective in domains with uncertainty. For this particular game, the outcome of each move is not entirely predictable due to the ghosts’ locations are unknown when out of range and the enemy team will have completely different strategy. MCTS can model and exploit this uncertainty by running configurable simulations.
Adaptive Search: MCTS dynamically allocates more search effort to promising parts of the game tree. UCB is used to explore and exploit high-potential paths and avoid low-reward areas, allowing it to make better decisions for every move.
Real-time Play: MCTS fulfills the requirement of playing this Pac-man game, as it allows the AI to make decisions in a limited time frame. The algorithm will select, expand, simulate and backpropagate the tree repeatedly until the time limit of 1 second per move is reached and provide the most recommended action.

[Back to top](#table-of-contents)

### Application  
MCTS is used to predict the best move for an agent in the current state. When the function chooseAction() runs, a new search tree will be created with the current state as root node. MCTS will run with configurable threshold and parameters (including exploration constant, discount and learning rate) within the limited time frame. The MCT is designed and iterated using a linked list that contains [x, y, action, parent node, [next nodes], N, Q, layer], which are all the variables essential for calculating the best action and keep track of the search. When the iterations finish, the most suitable next move will be the action with the highest Q value. If there is a tie break, action is chosen randomly from the best moves. After the agent moves, the MCT is reset and will calculate the Q values under the current state.

[Back to top](#table-of-contents)

### Trade-offs  
#### *Advantages*  
The MCTS algorithm is adapted to handle different scenarios and objectives by adjusting how rewards are defined and used within the search. In the context of this Pac-man game, this configurability can be very valuable. By adjusting the weight of rewards, different agent will take responsibility of handling different major tasks while still considering helping other tasks when it’s convenient. For instance, an agent with high rewards for collecting food is more aggressive than an agent aiming to collect food, but it still can switch target to a food or a power capsule when no vulnerable enemy is found.

#### *Disadvantages*
While MCTS is a powerful technique to handle many scenarios, including capturing Pac-man enemy, avoiding invincible enemy and collecting food, its performance is not as good as other techniques when most food are collected and the enemies are not detected. Because the rest of the rewards are too far away when the agents’ using MCTS. Which heavily impact the agents’ performance in all games since it is crucial to collect the remaining food and return to the boundary faster than the enemy does to win the game. Even though MCTS may be efficient when there are many food around an agent, they are acting in a less intelligent way while approaching the end of the game. It would highly likely get surpassed by other agents that have even performance throughout the game. MCTS’s performance is compromised when dealing with problems that have long planning horizons, which is why the agent may wander aimlessly when the map around it is quite empty.

[Back to top](#table-of-contents)

### Future improvements  
As a result of reducing agent getting stuck at a dead end or make repetitive moves, e.g. not exiting the entrance quickly enough as the long corridor is far away from any rewards, the agents are not allowed to turn back when there are alternative actions. However, the turn back action may be the best action to make under certain scenarios such as getting chased by a ghost from ahead. Therefore, even though dead end detection is implemented in the algorithm and negative rewards are returned from simulating to an empty dead end, the performance of MCTS can be further improved by learning from past MCT and visited states instead of brutally forbidding the turn back action. 

[Back to top](#table-of-contents)
