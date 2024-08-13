import json


def createTeam(firstIndex, secondIndex, isRed,
               first='Attack_Agent', second='Semi_Attack_Defence_Agent'):
    """
  This function should return a list of two agents that will form the
  team, initialized using firstIndex and secondIndex as their agent
  index numbers.  isRed is True if the red team is being created, and
  will be False if the blue team is being created.

  As a potentially helpful development aid, this function can take
  additional string-valued keyword arguments ("first" and "second" are
  such arguments in the case of this function), which will come from
  the --redOpts and --blueOpts command-line arguments to capture.py.
  For the nightly contest, however, your team will be created without
  any extra arguments, so you should make sure that the default
  behavior is what you want for the nightly contest.
  """

    # The following line is an example only; feel free to change it.
    return [eval(first)(firstIndex), eval(second)(secondIndex)]



##########
# Agents #
##########

MAX_CAPACITY = 4
TIMELIMIT = 10
A = 0.3
G = 0.8

###########
# Q_learning Agent
############

def get_weight(file_name):
    weight_data = [1, 1, 1]
    with open(file_name, 'r', encoding='utf-8') as weight_file:
        weight_data = json.load(weight_file)['feature_weight']
    return weight_data


class q_attack_agent(CaptureAgent):

    ## get the number of enemy food at the begging of the game
    def get_num_food(self, gameState):
        food_list = self.getFood(gameState).asList()
        number_food = len(food_list)
        return number_food

    """
    check whether the  agent is a ghost or a pacman
    """

    def get_agent_mode(self, gameState, enemy_index):
        # true = pacman  false = ghost
        if enemy_index is not None:
            result = gameState.getAgentState(enemy_index).isPacman
        else:
            result = gameState.getAgentState(self.index).isPacman
        return result

    def getBoundary(self, gameState):
        boundary_location = []
        height = gameState.data.layout.height
        width = gameState.data.layout.width
        for i in range(height):
            if self.red:
                j = int(width / 2) - 1
            else:
                j = int(width / 2)
            if not gameState.hasWall(j, i):
                boundary_location.append((j, i))
        return boundary_location

    def registerInitialState(self, gameState):
        CaptureAgent.registerInitialState(self, gameState)
        ## get the initial number of enemy's food
        self.total_food_initial = self.get_num_food(gameState)
        ## get the feature weight and set the weight to the agent
        weight = get_weight("agents/t_096/weight.json")
        self.feature_weight = weight
        ## current carrying food
        self.last_remaining_food = 0
        self.boundary = self.getBoundary(gameState)
        self.carrying = 0

    def feature_calculator(self, action, gameState):
        feature_list = []
        current_food_condition = self.getFood(gameState).asList()
        current_location = gameState.getAgentPosition(self.index)
        #########
        food_list = self.getFood(gameState).asList()
        current_food_remaining = len(food_list)
        #########
        next_state = gameState.generateSuccessor(self.index, action)
        next_location = next_state.getAgentPosition(self.index)
        next_food_condition = self.getFood(next_state).asList()
        next_number_food = len(next_food_condition)
        if (current_food_remaining > 2):
            ### food carrying
            dx, dy = game.Actions.directionToVector(action)
            x, y = gameState.getAgentState(self.index).getPosition()
            new_x, new_y = int(x + dx), int(y + dy)
            cache_carry = self.carrying
            if self.getFood(gameState)[new_x][new_y]:
                cache_carry += 1
            print("self.total_food_initial")
            print(self.total_food_initial)
            print("cache. carry")
            print(cache_carry)
            feature_list.append(1 / ((self.total_food_initial + 2) - cache_carry))
        else:
            feature_list.append(1 / self.total_food_initial + 2)

        ### number of food gain 看：到下一个state food 能多拿几个
        gain_food = self.last_remaining_food - next_number_food

        feature_list.append(1 / (self.total_food_initial - gain_food + 1))

        ### disntance to food 对于现在这个state
        min_dis = 100000000
        for next_food in next_food_condition:
            next_distance = self.getMazeDistance(next_location, next_food)
            if next_distance < min_dis:
                min_dis = next_distance

        feature_list.append(1 / (min_dis + 1))

        return feature_list

    def q_calculator(self, action, gameState):
        feature = self.feature_calculator(action, gameState)
        #####
        # 检查weight feature 长度
        #####
        q = 0
        for f_index in range(len(feature)):
            q += self.feature_weight[f_index] * feature[f_index]
        return q

    def get_best_action(self, begin_time, gameState, legal_action, return_action):
        iter_Q = -1000000000
        result_action = return_action
        for action in legal_action:
            time_gap = time.time() - begin_time
            if time_gap > TIMELIMIT:
                print("run out of time")
                break
            current_q = self.q_calculator(action, gameState)
            print(current_q)
            if (current_q > iter_Q):
                iter_Q = current_q
                result_action = action
        return result_action, iter_Q

    def adjuest_weight_file(self,file_name,R_NQ_OQ,feature_list):
        for i in range(len(feature_list)):
            self.feature_weight[i] = A *R_NQ_OQ * feature_list[i]
        with open(file_name,'w',encoding='utf-8') as weight_file:
            json.dump({'feature_weight':self.feature_weight},weight_file,indent=5,ensure_ascii=False)

    def chooseAction(self, gameState):
        # get the initial information for decision
        self_index = self.index
        self_location = gameState.getAgentPosition(self_index)
        enemy_index = self.getOpponents(gameState)  # get the enemy index
        capsules = self.getCapsules(gameState)  # get the list of capsules
        food_list = self.getFood(gameState).asList()
        current_mode = self.get_agent_mode(gameState, None)
        current_food_remaining = len(food_list)
        if (current_food_remaining > 2):
            begin_time = time.time()
            agent_mode = self.get_agent_mode(gameState, None)
            if not agent_mode:
                self.last_remaining_food = self.get_num_food(gameState)
            legal_actions = gameState.getLegalActions(self.index)
            return_action = legal_actions[0]

            if len(legal_actions) > 1:
                return_action,old_Q = self.get_best_action(begin_time, gameState, legal_actions, return_action)
                self.old_q =old_Q
            print(return_action)
            ####################

            dx, dy = game.Actions.directionToVector(return_action)
            x, y = gameState.getAgentState(self.index).getPosition()
            new_x, new_y = int(x + dx), int(y + dy)
            if self.getFood(gameState)[new_x][new_y]:
                self.carrying += 1
            elif (new_x, new_y) in self.boundary:
                self.carrying = 0

            ####################
            reward = self.carrying
            next_state = gameState.generateSuccessor(self.index, return_action)
            old_q = self.old_q

            next_action_list = next_state.getLegalActions(self.index)
            start_action = next_action_list[0]
            next_action, new_Q = self.get_best_action(begin_time, gameState, next_action_list, start_action)
            feature_list  = self.feature_calculator(legal_actions, gameState)
            R_NQ_OQ =  reward + (G*new_Q - old_q)

            self.adjuest_weight_file(self, "agents/t_096/weight.json", R_NQ_OQ, feature_list)



            return return_action
        else:  # when the number of eaten food have reach the goal go back to home and avoid the defence
            self.current_target = self.getClosestPos(gameState, self.boundary)
            self.return_permission = True
            enemy_location_list = self.get_enemyloc_list(gameState, enemy_index)
            problem = PositionSearchProblem(gameState, self.current_target, self.index, enemy_location_list)

            # the path finding logic(line 266 to line 284) is same as the sample/baselineTeam line 110 to line 124
            # author: University of Melbourne COMP90054 staff team
            # find a path
            path = self.aStarSearch(problem)
            if path == []:
                actions = gameState.getLegalActions(self.index)
                return random.choice(actions)
            else:
                action = path[0]
                dx, dy = game.Actions.directionToVector(action)
                x, y = gameState.getAgentState(self.index).getPosition()
                new_x, new_y = int(x + dx), int(y + dy)
                if (new_x, new_y) == self.current_target:
                    self.current_target = None
                if self.getFood(gameState)[new_x][new_y]:
                    self.carrying += 1
                elif (new_x, new_y) in self.boundary:
                    self.carrying = 0
                return path[0]

    def get_enemyloc_list(self, gameState, enemy_index):
        enemy_location_list = []
        for enemy_id in enemy_index:
            enemy_location = gameState.getAgentState(enemy_id).getPosition()
            # pacman = true ghost = false
            enemy_mode = self.get_agent_mode(gameState, enemy_id)
            if not enemy_mode and enemy_location is not None:
                exact_enemy_loc = form_enemy_location(enemy_location)
                enemy_location_list.append(exact_enemy_loc)
        return enemy_location_list

        # The method getClosestPos is same as the method getClosestPos in sample/baselineTeam
        # author: University of Melbourne COMP90054 staff team

    def getClosestPos(self, gameState, pos_list):
        min_length = 9999
        min_pos = None
        my_local_state = gameState.getAgentState(self.index)
        my_pos = my_local_state.getPosition()
        for pos in pos_list:
            temp_length = self.getMazeDistance(my_pos, pos)
            if temp_length < min_length:
                min_length = temp_length
                min_pos = pos
        return min_pos

        # The method  aStarSearch is same as the method aStarSearch in sample/baselineTeam
        # author: University of Melbourne COMP90054 staff team

    def aStarSearch(self, problem):
        """Search the node that has the lowest combined cost and heuristic first."""

        from util import PriorityQueue
        myPQ = util.PriorityQueue()
        startState = problem.getStartState()

        startNode = (startState, '', 0, [])
        heuristic = problem._manhattanDistance
        myPQ.push(startNode, heuristic(startState))
        visited = set()
        best_g = dict()
        while not myPQ.isEmpty():
            node = myPQ.pop()
            state, action, cost, path = node

            if (not state in visited) or cost < best_g.get(str(state)):
                visited.add(state)
                best_g[str(state)] = cost
                if problem.isGoalState(state):
                    path = path + [(state, action)]
                    actions = [action[1] for action in path]
                    del actions[0]
                    return actions
                for succ in problem.getSuccessors(state):
                    succState, succAction, succCost = succ
                    newNode = (succState, succAction, cost + succCost, path + [(node, action)])
                    myPQ.push(newNode, heuristic(succState) + cost + succCost)
        return []


"""
generate the int tuple enemy location
"""


def form_enemy_location(enemy_location):
    x_loc, y_loc = enemy_location
    return int(x_loc), int(y_loc)


"""
check whether there is a enemy agent around(with in 5 step)
"""


def enemy_around(enemy_location):
    if enemy_location is None:
        return False
    else:
        return True

