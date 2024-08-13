# Design Choices

The design choices are influenced by the techniques employed, including Q-learning, MCTS, A*, and multiplayer. The multiplayer approach is a flexible technique to effectively complementing the other three throughout the development process. It provides a solution to handle extreme cases and specify actions to remedy unforeseen conditions not accounted for in other designs.
In our testing, the use of the A* search and decision tree approach on the server consistently produced optimal results. Which also proves A* search is an efficient path finding algorithm for this particular problem.

More evaluations of the defensive and offensive agents per technique are introduced below.


## Evaluation

The Collector agent (MCTS) is crafted with a flexible reward system that serves the purpose of motivating or discouraging an agent to trigger various scenarios during the simulations. Designing an appropriate reward system is important for calculating the most suitable actions to accomplish tasks while steering clear of potential encounters with adversaries. However, MCTS comes with a relatively higher computational cost for storing MCT data and a longer time to run simulations and backpropagate. The implemented design could not provide optimal performance due to the game's time constraints. Therefore, repetitive actions are deliberately removed from the MCT expansion to make it more feasible for this problem. Additionally, empty dead-end detection is implemented to compensate for this design, even though it reduces agent mobility. Details provided in the MCTS section.

The second implemented technique, Q-learning, has significant potential to yield excellent results. However, in this particular project, the imperfect design of features may result in biases. As a consequence, the weights learned through feature and reward training cannot guarantee optimal performance for all scenarios. For instance, the approximate Q-learning agent lacks the ability to effectively evade enemy pursuit, leading to significantly reduced offensive efficiency. This may be a result of feature design limitations.

In contrast, A* provides optimal performance while adhering to the game rules. The A* agents adeptly avoid enemy defence agents and dynamically adjust their targets to maximize possible food capturing. The Defence A* agent also offers strong, reliable protection to the home territory by patrolling on the middle line and chase the attack enemy agent as it detected it. Furthermore, A* stands out for its time and space efficiency in automating the agent.


## Monte-Carlo Tree Search
In MCTS, the rewards system assigned to each agent is the most important element to distinguish their behavioural preference. The "getRewards()" function serves as a helper method designed to assign a rewards system to a given agent:

```python
# define rewards of different scenario for the collector agent
# even index agents are collectors who prefer collecting food, more aggressive
# odd index agents are collectors who prefer attack enemy when possible
# [food, power capsule, pacman enemy, invincible enemy, boundary]
def getRewards(self):
   if (self.index+1 // 2) == 1:
    return [120, 100, 80, -150, 0]
   else:
    return [80, 100, 120, -150, 0]

```

While both types of reward system have the same negative reward for getting captured by an invincible enemy,  the rewards for collecting food, collecting power capsule and capturing a Pac-man enemy are different. The rewards for returning to the boundary is 0 when initiated, which will gradually increase as the game progressed. This increment is aimed at motivating the agent to earn score by returning with the collected food.

## Offense
The offensive agent exhibits a more aggressive approach, prioritizing the collection of food and power capsules when multiple goals are in close proximity. These actions are considered of higher priority compared to eliminating vulnerable enemies. The offense agent is expected to be collecting food on the enemy’s side as its primary focus. Its defensive behaviour is mostly likely triggered when returning to the boundary and help capturing a detected Pac-man enemy. 

## Defense
The defence agent prefers to chase a detected vulnerable enemy as it results in higher rewards than collecting food. Since the environment is not fully observable, the defence agent would not exclusively stay on the boundary, but may also engage in lower-reward tasks such as collecting food to improve efficiency when no enemy is detected.


## A* Search

## Offense
The offense agent in heuristic approach (a* approach) is very aggressive, which have a good performance. The agent will chase the enemy ghost when it eat the capsule. Never the less the agent are flexible, it can avoid the chase by the enemy’s defense. Once it reaches the maximum capacity of its food load it will return to its base and attack again. 

## Defense

The defense agent will patrol along in the middle line. Once the agent detect the enemy pacman it will chase the pacman till the pacman been destroyed.

Both offense and defense agent will choose their action by selecting a target and using the a* search to find its shortest path to the target.


## Approximate Q-Learning 

## Offense 
The offense agent in approximate q learning approach has a lower performance than A* approach. The agent will attack and eat as much food as it can. While it has serious issue on the design of the feature. It ability of avoiding the chase of enemy agent is very weak it have a great possibility that been caught by enemy agent. 

## Defense
The defense agent in the veresion of  Approximate Q learning approach are same with the defense agent in A* approach.


[Back to top](#design-choices)

