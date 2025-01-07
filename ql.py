import copy
import numpy as np
from itertools import combinations,product
import pandas as pd



def execute_ql(list1,list2,goal):
    # Example lists
    
    #generate all possible actions using word list and position list checking their lengths
    def generate_combinations(list1, list2):
        combinations = []
        for word_tuple, space_tuple in product(list1, list2):
            if word_tuple[1] == space_tuple[3]:  # Check if word length matches space length
                combinations.append(word_tuple + space_tuple)
        return combinations



    combinationz= generate_combinations(list1, list2)



    #changing the positions integer to corresponsing letter in intersetions
    for i in combinationz:
        temp=[]
        for x in i[6]:
            if i[0]!=None:
                j=x[:]
                j[2]=i[0][j[2]]
                i[6]=j
                x=j[:]
            else:
                for n in x[-1]:
                    n[2]=None
            temp.append(x)
        i[6]=temp


    #for generating states (without removal  actions)
    actions_for_states=copy.deepcopy(combinationz)


    #actions including removal and no action
    action_space=list(combinationz)


    for i in list2:
        action_space.append([None,-1]+i)

    for i in action_space:
        temp=[]
        for x in i[6]:
            if i[0]!=None:
                pass
            else:
                x[2]=None
            temp.append(x)
        i[6]=temp



#generating states
    def generate_combinations(tuples_list):
        valid_combinations = []
        for r in range(0, len(tuples_list) + 1):
            for combination in combinations(tuples_list, r):
                combination=list(combination)
                #intersection list
                intersec=[]
                first_elements = set()
                third_fourth_fifth_set = []
                is_valid = True
                len_before=len(third_fourth_fifth_set)

                #validating every combination generated
                for tup in combination:
                    #words not repeated
                    if tup[0] in first_elements:
                        is_valid = False
                    else:
                        first_elements.add(tup[0])
                        #positions not repeated
                        if [tup[2],tup[3],tup[4]] in third_fourth_fifth_set:
                            is_valid = False
                        else:
                            third_fourth_fifth_set.append([tup[2],tup[3],tup[4]])
                            #intersections are valid or not
                            #appending valid interstions in the combination to the state
                            if tup[6]:
                                for temp in tup[6]:
                                    #if temp not in intersec:
                                    intersec.append(temp)
                            for i in range(len(intersec)):
                                for j in intersec[ i+1 :]:
                                    if intersec[i][:2]==j[:2] and intersec[i][2]!=j[2]:
                                        is_valid=False

                combination=[combination,]+[intersec,]
                if is_valid :
                    valid_combinations.append(combination)

        return valid_combinations

    combinationz= generate_combinations(actions_for_states)


    state_space=combinationz



    # Create a DataFrame with the specified number of rows and columns
    df = pd.DataFrame(index=range(len(state_space)), columns=[tuple([z[0],z[2],z[3]]) for z in action_space])


    #for x in state_space: print(x)

    # Fill the DataFrame with placeholder values (e.g., 0)
    df.fillna(0, inplace=True)

    #validating intersection
    def check_intersection(action,state):
        for x in action:
            for y in state:
                if x[:2] == y[:2] and x[2] != y[2]:
                    return False
        return True


    def check_equality(state, goal):
        state=state[0]
        goal=goal[0]
        #print("goal:",goal)
        #print('state:',state)
        counter=0
        if len(state)==len(goal):
            for i in goal:

                for j in state:

                    for x,y in zip(i[0:6],j[0:6]):
                        if x==y:
                            pass
                        else:
                            break
                    else:
                        sub_count=0
                        if len(i[6])==len(j[6]):
                            for m in i[6]:
                                for n in j[6]:
                                    for g,h in zip(m,n):
                                        if g==h:
                                            pass
                                        else:
                                            break
                                    else:
                                        sub_count+=1
                                        break
                            if len(i[6])==sub_count:
                                counter+=1
                                break

            if counter==len(goal):
                return True
            else:
                return False
        else:
            return False




    #reward table generation
    #iterating through the table
    for i in range(len(state_space)):
        for j in range(len(action_space)):
            state = state_space[i]
            action = action_space[j]
            #leaving No action column and empty state row
            if action!=None and len(state[0]):
                #leaving removal (only placing word)
                if action[0]!=None:
                    '''
                    if word in action exists in the state
                    if the position in action is occupied in state
                    if the value at intersections in the action are not the same in state
                    '''
                    if action[0] in [k[0] for k in state[0]] or\
                    action[2:4] in [k[2:4] for k in state[0]] or\
                    not check_intersection(action[6],state[1]):
                        df.iloc[i, j] = -1
                        continue
                #removal when the position is not filled in the state is invalid:
                elif action[0]==None:
                    if action[2:4] not in [k[2:4] for k in state[0]] :
                        df.iloc[i, j] = -1
                        continue


                #if any action from current state taken leads to goal  state , assign 100
                if df.iloc[i, j] ==0 :
                    temp_state=copy.deepcopy(state)

                    if action[0]==None:
                        for k in state[0]:
                            if action[2:5]==k[2:5]:
                                temp_state[0].remove(k)

                    elif action[0]!=None:
                        temp_state[0]+=[action]

                    if check_equality(temp_state, goal):
                        df.iloc[i, j] = 100
                        continue

            #from empty state no removal can be done
            elif len(state[0]) ==0 and action!=None and (action[0]==None):
                df.iloc[i, j] = -1
                continue


    # Export the DataFrame to a CSV file

    reward_table =df.values
    r_table_df=pd.DataFrame()
    r_table_df=copy.deepcopy(df)

    r_table_df.insert(0, 'states', [tuple(tuple([x[0],x[2],x[4]]) for x in y[0]) for y in state_space])

    #r_table_df.to_csv('actions_states_table.csv')
    #print("Table exported successfully as 'actions_states_table.csv'")

    #print(reward_table)


    #q-table generation
    #setting training episodes according to the words count
    if len(list1)>5:
        num_episodes=100000
    else:
        num_episodes = 10000
    # Define parameters
    gamma = 0.8  # Discount factor
    alpha = 0.9  # 0.7  Learning rate
    

    # Initialize Q-table with zeros
    num_states = len(state_space)
    num_actions = len(action_space)
    q_table = np.zeros((num_states, num_actions))

    max_epsilon = 1.0
    min_epsilon = 0.05
    decay_rate = 0.0005

    # Q-learning algorithm
    for episode in range(num_episodes):
        state = 0  # Start from the initial state
        done = False  # Flag to indicate if the episode is done
        epsilon = min_epsilon + (max_epsilon - min_epsilon)*np.exp(-decay_rate*episode)
        
        while not done:
            # Choose action using epsilon-greedy policy
            if np.random.rand() < epsilon:
            #if np.random.rand() < 0.5:
                action = np.argmax(q_table[state])
            else:
                action = np.random.choice(np.arange(num_actions))

            # Get reward for the chosen action
            reward = reward_table[state, action]

            if reward != -1:
                new_state=[[],[]]
                new_state[0]=copy.deepcopy(state_space[state][0])
                new_state[1]=copy.deepcopy(state_space[state][1])
                if action_space[action][0]!=None:

                    new_state[0]+=[action_space[action]]

                    for i in action_space[action][6]:
                            new_state[1]+=[i]

                else:

                    for i in state_space[state][0]:
                        if action_space[action][2:5]==i[2:5]:
                            #print(i[2:5],":",action_space[action][2:5])
                            new_state[0].remove(i)

                    for j in action_space[action][6]:
                        for i in state_space[state][1]:
                            if j[0:2]==i[0:2]:
                                new_state[1].remove(i)


                # Update Q-value using Bellman equation
                for i in range(len(state_space)):
                    if check_equality(new_state,state_space[i]):
                        next_state=i

                #print("after: ",new_state,"ind:",next_state)

                #next_state = state_space.index(new_state)
                #q_table[state, action] = alpha * (reward + gamma * np.max(q_table[next_state]) - q_table[state, action])
                q_table[state, action] =  round( alpha * (reward + gamma * np.max(q_table[next_state])) , 4)

                # Move to the next state
                state = next_state

                # Check if the goal state is reached
                if check_equality(state_space[state] , goal):
                    done = True
            else:
                # If the action is invalid, stay in the same state
                done = True

    # Print the learned Q-table
    #print("Learned Q-table:")
    print(q_table)

    print(action_space)
    q_table_df = pd.DataFrame(q_table, columns=[tuple([z[0],z[2],z[3],z[4]]) for z in action_space])
    q_table_df.insert(0, 'states', [tuple(tuple([x[0],x[2],x[3],x[4]]) for x in y[0]) for y in state_space])
    
    # Export the DataFrame to a CSV file
    #q_table_df.to_csv('q_table.csv', index=False)
    return q_table_df


