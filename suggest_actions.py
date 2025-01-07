import pandas as pd
import random 
from QA_generation import words_hints
#from ql import q_table_df

def transform_hints(words_hints):
    hints_dict={}
    for i in words_hints:
        hints_dict.update({i[0].lower() :i[1].lower()})

    print("hints : " ,hints_dict)
    return hints_dict



#checking equality between two states
def is_equal(state,goal):
    if len(state)==len(goal):
        counter=0
        for i in goal:
            for j in state:
                if i[0]==j[0]:
                    if i[1:4]==j[1:4]:
                        counter+=1
                        break
        if counter==len(goal):
            return True
        else:
            return False
    else:
        return False

#suggest the action that has highest score
def get_actions(current_state,df,words_hints):


    hints=transform_hints(words_hints)

    update_score=-1
    #df = pd.read_csv('q_table.csv')
    #print(df)
    print('current_state : ',current_state)
   
    matches = df[df['states'].apply(lambda x: is_equal(x,current_state))]
    #print("matches : ",matches)
    matching_rows = matches.to_dict(orient='records')

    #print("match",matching_rows)
    
    filtered_match = {k: v for k, v in matching_rows[0].items() if isinstance(v, float)}


    print("filtered_match : ",filtered_match)

    max_value = max(filtered_match.values())
    max_keys = tuple(key for key, value in filtered_match.items() if value == max_value)
    if len(max_keys)==len(df.columns)-1:
        update_score=len(current_state)
        #print("print length" ,len(current_state),len(hints))
        if  len(current_state)==len(hints):
            return "Puzzle Completed",update_score
    #print(max_keys)

    #checking whether to update score or not
    for x in max_keys:
        if  x[0]==None:
            break
    else:
        update_score=len(current_state)

    result = random.choice(max_keys)

    
    #return suggestion
    
    if result[3]==0:
        orientation='horizontally'
    else:
        orientation='vertically'

    if result[0]!=None:
        return f"Place the word for '{hints[result[0]]}' at position {result[1]+1,result[2]+1} {orientation}",update_score
    
    else:
        return f'Remove the word at position {result[1]+1,result[2]+1} placed {orientation}',update_score
    

