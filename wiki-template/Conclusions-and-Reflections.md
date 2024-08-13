## Challenges  
Computational Efficiency and Aimless Wandering: MCTS faced the challenge of getting stuck in infinite loops and exhibiting aimless wandering behavior. These were addressed by integrating A* search to encourage more decisive movements.

Balance Between Offense and Defense: A* faced a challenge in balancing offense and defense. An agent had to be re-developed from an agent with aggressive actions to a fully defensive agent in response to the game state.

Redundant Actions: MCTS, in combination with A*, struggled with escaping enemy chases effectively. Improvements such as empty dead end detection were made to overcome this challenge.

Bias in Reward Structure: The Approximate Q-Learning Agent was not fully optimized, inevitably resulting in a bias in reward selection. Which could not ensure the calculation accurately improve the agent's performance and objectives.

Adaptability to Different Game Scenarios: All agents faced the challenge of adapting to various game scenarios. This required the introduction of flexible parameters, logic, and enhanced adaptability. Furthermore, there is more can be improved in the future.


## Conclusions and Learnings
In the quest to master the Pac-Man game, multiple AI techniques have been employed, each evolving over time to address a series of challenges. These techniques include Monte-Carlo Tree Search (MCTS), A* search, and Approximate Q-Learning, each demonstrating its unique strengths and adaptability.

### Monte-Carlo Tree Search
The MCTS Agent, initially driven solely by MCTS, embarked on a journey of development and improvement. Challenges encountered included issues like high computational cost and aimless wandering. To overcome these challenges, it incorporated A* search and prohibiting turn-back action to help Pac-Man act more decisively, avoiding aimless wanderings. The configuration of parameters and the flexibility to adapt to different games allowed the agent to further enhance its performance. A flexible reward structure ensured the agent could accommodate both defensive and aggressive strategies.

### A* Search
The A* Agent underwent two major iterations, initially as an offense and defense agent. The first version displayed a mix of aggression and defense, with a focus on crossing the middle line and choosing targets based on distance. The logic was then fine-tuned in the second version, which abandoned aggressive actions and adopted a more defensive posture. The enhancements aimed to optimize path selection, especially in complex environments.

### Approximate Q-Learning
The Approximate Q-Learning Agent's journey was marked by the introduction of additional features and rewards. It initially struggled to escape enemy chases and had a bias in reward selection. Improvements came in the form of two new features, distance to food, and the number of foods carried, to enable better target selection. These enhancements facilitated the agent's ability to improve its food carrying capacity and choose actions that maintain or increase food collection.


In summary, the progress of these Pac-Man AI agents shows how AI improvement is an ongoing process. Each method addressed particular problems related to navigation, adaptability, or responsiveness. Combining different approaches and adjusting the settings played a crucial role in making Pac-Man AI smarter and better at playing the game.

[Back to top](#challenges)