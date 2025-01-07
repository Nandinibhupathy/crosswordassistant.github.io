# vi: set ft=python sts=4 ts=4 sw=4 et:

import random
import re
import time
import string
from copy import copy as duplicate


class Crossword(object):
    def __init__(self, cols, rows, empty='-', maxloops=2000, available_words=[]):
        self.cols = cols
        self.rows = rows
        self.empty = empty
        self.maxloops = maxloops
        self.available_words = available_words
        self.randomize_word_list()
        self.current_word_list = []
        self.clear_grid()
        self.debug = 0
        self.word_details=[]
        self.grids=[]
        self.start_col=0
        self.start_row=0

    def clear_grid(self):
        """Initialize grid and fill with empty character."""
        self.grid = []
        for i in range(self.rows):
            ea_row = []
            for j in range(self.cols):
                ea_row.append(self.empty)
            self.grid.append(ea_row)

    def randomize_word_list(self):
        """Reset words and sort by length."""
        temp_list = []
        for word in self.available_words:
            if isinstance(word, Word):
                temp_list.append(Word(word.word, word.clue))
            else:
                temp_list.append(Word(word[0], word[1]))
        # randomize word list
        random.shuffle(temp_list)
        # sort by length
        temp_list.sort(key=lambda i: len(i.word), reverse=True)
        self.available_words = temp_list

    def compute_crossword(self, time_permitted=1.00, spins=2):
        copy = Crossword(self.cols, self.rows, self.empty,
                         self.maxloops, self.available_words)

        count = 0
        time_permitted = float(time_permitted)
        start_full = float(time.time())

        # only run for x seconds
        while (float(time.time()) - start_full) < time_permitted or count == 0:
            self.debug += 1
            copy.randomize_word_list()
            copy.current_word_list = []
            copy.clear_grid()

            x = 0
            # spins; 2 seems to be plenty
            while x < spins:
                for word in copy.available_words:
                    if word not in copy.current_word_list:
                        copy.fit_and_add(word)
                x += 1
            #print(copy.solution())
            #print(len(copy.current_word_list), len(self.current_word_list), self.debug)
            # buffer the best crossword by comparing placed words
            if len(copy.current_word_list) > len(self.current_word_list):
                self.current_word_list = copy.current_word_list
                self.grid = copy.grid
            count += 1
        return
    
    def suggest_coord(self, word):
        #count = 0
        coordlist = []
        glc = -1
        
        # cycle through letters in word
        for given_letter in word.word:
            glc += 1
            rowc = 0
            # cycle through rows
            for row in self.grid:
                rowc += 1
                colc = 0
                # cycle through letters in rows
                for cell in row:
                    colc += 1
                    # check match letter in word to letters in row
                    if given_letter == cell:
                        # suggest vertical placement
                        try:
                            # make sure we're not suggesting a starting point off the grid
                            if rowc - glc > 0:
                                # make sure word doesn't go off of grid
                                if ((rowc - glc) + word.length) <= self.rows:
                                    coordlist.append([colc, rowc-glc, 1, colc+(rowc-glc),0])
                        except:
                            pass

                        # suggest horizontal placement
                        try:
                            # make sure we're not suggesting a starting point off the grid
                            if colc - glc > 0:
                                # make sure word doesn't go off of grid
                                if ((colc - glc) + word.length) <= self.cols:
                                    coordlist.append([colc-glc, rowc, 0, rowc+(colc-glc),0])
                        except:
                            pass

        # example: coordlist[0] = [col, row, vertical, col + row, score]
        #print(word.word)
        #print(coordlist)
        new_coordlist = self.sort_coordlist(coordlist, word)

        #print(new_coordlist)

        return new_coordlist


    def sort_coordlist(self, coordlist, word):
        """Give each coordinate a score, then sort."""
        new_coordlist = []
        for coord in coordlist:
            col, row, vertical = coord[0], coord[1], coord[2]
            # checking scores
            coord[4] = self.check_fit_score(col, row, vertical, word)
            # 0 scores are filtered
            if coord[4]:
                new_coordlist.append(coord)
        # randomize coord list; why not?
        random.shuffle(new_coordlist)
        # put the best scores first
        new_coordlist.sort(key=lambda i: i[4], reverse=True)
        return new_coordlist

    def fit_and_add(self, word):
        """Doesn't really check fit except for the first word;
        otherwise just adds if score is good.
        """
        fit = False
        count = 0
        coordlist = self.suggest_coord(word)

        while not fit and count < self.maxloops:
            # this is the first word: the seed
            if len(self.current_word_list) == 0:
                # top left seed of longest word yields best results (maybe override)
                vertical, col, row = random.randrange(0, 2), 1, 1


                # optional center seed method, slower and less keyword placement
                if vertical:
                    col = int(round((self.cols+1)/2, 0))
                    row = int(round((self.rows+1)/2, 0)) - int(round((word.length+1)/2, 0))
                else:
                    col = int(round((self.cols+1)/2, 0)) - int(round((word.length+1)/2, 0))
                    row = int(round((self.rows+1)/2, 0))
                '''
                # completely random seed method
                col = random.randrange(1, self.cols + 1)
                row = random.randrange(1, self.rows + 1)
                '''

                if self.check_fit_score(col, row, vertical, word):
                    fit = True
                    self.set_word(col, row, vertical, word, force=True)

            # a subsquent words have scores calculated
            else:
                try:
                    col, row, vertical = coordlist[count][0], coordlist[count][1], coordlist[count][2]
                # no more cordinates, stop trying to fit
                except IndexError:
                    return

                # already filtered these out, but double check
                if coordlist[count][4]:
                    fit = True
                    self.set_word(col, row, vertical, word, force=True)

            count += 1

        return

    def check_fit_score(self, col, row, vertical, word):
        """Return score: 0 signifies no fit, 1 means a fit, 2+ means a cross.
        The more crosses the better.
        """
        if col < 1 or row < 1:
            return 0

        # give score a standard value of 1, will override with 0 if collisions detected
        count, score = 1, 1
        for letter in word.word:
            try:
                active_cell = self.get_cell(col, row)
            except IndexError:
                return 0

            if active_cell == self.empty or active_cell == letter:
                pass
            else:
                return 0

            if active_cell == letter:
                score += 1

            if vertical:
                # check surroundings
                if active_cell != letter: # don't check surroundings if cross point
                    if not self.check_if_cell_clear(col+1, row): # check right cell
                        return 0

                    if not self.check_if_cell_clear(col-1, row): # check left cell
                        return 0

                if count == 1: # check top cell only on first letter
                    if not self.check_if_cell_clear(col, row-1):
                        return 0

                if count == len(word.word): # check bottom cell only on last letter
                    if not self.check_if_cell_clear(col, row+1):
                        return 0
            else: # else horizontal
                # check surroundings
                if active_cell != letter: # don't check surroundings if cross point
                    if not self.check_if_cell_clear(col, row-1): # check top cell
                        return 0

                    if not self.check_if_cell_clear(col, row+1): # check bottom cell
                        return 0

                if count == 1: # check left cell only on first letter
                    if not self.check_if_cell_clear(col-1, row):
                        return 0

                if count == len(word.word): # check right cell only on last letter
                    if not self.check_if_cell_clear(col+1, row):
                        return 0

            if vertical: # progress to next letter and position
                row += 1
            else: # else horizontal
                col += 1

            count += 1

        return score

    def set_word(self, col, row, vertical, word, force=False):
        """Set word in the grid, and adds word to word list."""
        if force:
            word.col = col
            word.row = row
            word.vertical = vertical
            self.current_word_list.append(word)

            for letter in word.word:
                self.set_cell(col, row, letter)
                if vertical:
                    row += 1
                else:
                    col += 1

        return

    def set_cell(self, col, row, value):
        self.grid[row-1][col-1] = value

    def get_cell(self, col, row):
        return self.grid[row-1][col-1]

    def check_if_cell_clear(self, col, row):
        try:
            cell = self.get_cell(col, row)
            if cell == self.empty:
                return True
        except IndexError:
            pass
        return False


    def solution(self):
      """Return solution grid with only rows and columns that have letters."""
      outStr = ""
      # Create a list to track which columns have letters
      column_has_letters = [any(self.grid[r][c] != self.empty for r in range(self.rows)) for c in range(self.cols)]
      
      for r in range(self.rows):
          # Check if the row has any letters
          if any(cell != self.empty for cell in self.grid[r]):
          
              for c in range(self.cols):
                  # Check if the column has any letters before adding its content to the output string
                  if column_has_letters[c]:
                      
                      outStr += '%s ' % self.grid[r][c]
              outStr += '\n'
      return outStr



    def word_find(self):
        """Return solution grid."""
        outStr = ""
        for r in range(self.rows):
            for c in self.grid[r]:
                if c == self.empty:
                    outStr += '%s ' % string.ascii_lowercase[random.randint(0,len(string.ascii_lowercase)-1)]
                else:
                    outStr += '%s ' % c
            outStr += '\n'
        return outStr

    def order_number_words(self):
        """Orders words and applies numbering system to them."""
        self.current_word_list.sort(key=lambda i: (i.col + i.row))
        count, icount = 1, 1
        for word in self.current_word_list:
            word.number = count
            if icount < len(self.current_word_list):
                if word.col == self.current_word_list[icount].col and word.row == self.current_word_list[icount].row:
                    pass
                else:
                    count += 1
            icount += 1

    def find_intersections(self):
      intersections = []
      grid=self.grid
      # Iterate through each cell in the grid
      for r in range(len(grid)):
          for c in range(len(grid[r])):
              # Check if the cell is not empty and not a black cell
              if grid[r][c] != '-' and grid[r][c] != ' ':
                  # Check if the cell has both vertical and horizontal neighbors
                  has_horizontal_neighbor = (c > 0 and grid[r][c - 1] != '-' and grid[r][c - 1] != ' ') or \
                                            (c < len(grid[r]) - 1 and grid[r][c + 1] != '-' and grid[r][c + 1] != ' ')
                  has_vertical_neighbor = (r > 0 and grid[r - 1][c] != '-' and grid[r - 1][c] != ' ') or \
                                          (r < len(grid) - 1 and grid[r + 1][c] != '-' and grid[r + 1][c] != ' ')
                  if has_horizontal_neighbor and has_vertical_neighbor:
                      intersections.append((r-self.start_row-1, c-self.start_col-1))

      return intersections


    def get_word_intersections(self,word_details, intersections):
      # Determine the orientation of the word
      orientation = word_details['orientation']
      start=word_details['start_coordinates']
      # Iterate over intersections
      for intersection in intersections:
          row, col = intersection
          if orientation == 0 and row==start[0] and col in range(start[1],start[1]+word_details['length']):
              # If the intersection is in the same row and word is horizontal
              inter=list(intersection)
              inter.append(col-start[1])
              word_details['intersections'].append(inter)
          elif orientation == 1 and col==start[1] and row in range(start[0],start[0]+word_details['length']):
              # If the intersection is in the same column and word is vertical
              inter=list(intersection)
              inter.append(row-start[0])
              word_details['intersections'].append(inter)


      return word_details

    def get_grid(self):
      """Return solution grid with only rows and columns that have letters."""
      outStr = []
      # Create a list to track which columns have letters
      r_flag=0
      c_flag=0
      column_has_letters = [any(self.grid[r][c] != self.empty for r in range(self.rows)) for c in range(self.cols)]
      for r in range(self.rows):
          temp_row=[]
          # Check if the row has any letters
          if any(cell != self.empty for cell in self.grid[r]):
              if r_flag==0: 
                  self.start_row=r-1
                  r_flag=1
              for c in range(self.cols):
                  # Check if the column has any letters before adding its content to the output string
                  if column_has_letters[c]:
                      if c_flag==0: 
                        self.start_col=c-1
                        c_flag=1
                      temp_row.append(self.grid[r][c])
              outStr.append(temp_row)
      return outStr

    def get_puzzle(self):
        puzzle=[]
        grids=self.get_grid()
        for i in grids:
          temp=[]
          for j in i:
            if j!='-':
              temp.append(1)
            else:
              temp.append(0)
          puzzle.append(temp)
        return puzzle

    def word_bank(self):
        outStr = ''
        temp_list = duplicate(self.current_word_list)
        # randomize word list
        random.shuffle(temp_list)
        for word in temp_list:
            outStr += '%s\n' % word.word
        return outStr


    def pass_to_function(self):
        intersec=self.find_intersections()
        word_details = []
        start_r=self.start_row
        start_c=self.start_col
        orient_dict={'down':1,'across':0}
        for word in self.current_word_list:

            word_details.append({
                "word": word.word,
                "length": len(word.word),
                "start_coordinates": (word.row-2-start_r, word.col-2-start_c),
                "orientation": orient_dict[word.down_across()],
                "intersections": []
            })
        for x in word_details:
            word_intersec=self.get_word_intersections(x,intersec)
            x['intersections']=word_intersec['intersections']
        self.word_details=word_details
        #return word_details
    
    def get_list2(self):
        word_details=self.word_details
        result=[]
        for i in word_details:
            temp=[i['start_coordinates'][0],i['start_coordinates'][1],i['orientation'],i['length'],i['intersections']]
            result.append(temp)
        return result

    def get_list1(self):
        word_details=self.word_details
        result=[]
        for i in word_details:
            temp=[i['word'],i['length']]
            result.append(temp)
        return result

    def get_goal(self):
        word_details=self.word_details
        result=[[],[]]
        for i in word_details:
            temp_inter=[]
            for x in i['intersections']:
                temp_inter.append([x[0],x[1],i['word'][x[2]]])
            temp=[i['word'],i['length'],i['start_coordinates'][0],i['start_coordinates'][1],i['orientation'],i['length'],temp_inter]
            result[0].append(temp)
        return result
    
    def get_lists(self):
        list_1=self.get_list1()
        list_2=self.get_list2()
        goal=self.get_goal()
        return list_1,list_2,goal
    
    def get_words(self):
        outStr = []
        temp_list = duplicate(self.current_word_list)

        for word in temp_list:
            outStr.append(word.word)
        return outStr
        


class Word(object):
    def __init__(self, word=None, clue=None):
        self.word = re.sub(r'\s', '', word.lower())
        self.clue = clue
        self.length = len(self.word)
        # the below are set when placed on board
        self.row = None
        self.col = None
        self.vertical = None
        self.number = None

    def down_across(self):
        """Return down or across."""
        if self.vertical:
            return 'down'
        else:
            return 'across'

    def __repr__(self):
        return self.word


#start_full = float(time.time())
'''
word_list = [
    ['formal', 'The dried, orange yellow plant used to as dye and as a cooking spice.'],
    ['nickel', 'Dark, sour bread made from coarse ground rye.'],
    ['worship', 'An agent, such as yeast, that cause batter or dough to rise..'],
    ['conda', 'Musical conclusion of a movement or composition.'],
    ['paladium', 'A heroic champion or paragon of chivalry.'],
    ['symposium', 'Shifting the emphasis of a beat to the normally weak beat.'],
    ['pigeon', 'A large bird of the ocean having a hooked beek and long, narrow wings.'],
    ['harmonium', 'Musical instrument with 46 or more open strings played by plucking.'],
    ['pista', 'A solid cylinder or disk that fits snugly in a larger cylinder and moves under pressure as in an engine.'],
    ['camel', 'A smooth chery candy made from suger, butter, cream or milk with flavoring.'],
    ['coral', 'A rock-like deposit of organism skeletons that make up reefs.'],
    ['dawn', 'The time of each morning at which daylight begins.'],
    ['pitch', 'A resin derived from the sap of various pine trees.'],
    ['ford', 'A long, narrow, deep inlet of the sea between steep slopes.'],
    ['lip', 'Either of two fleshy folds surrounding the mouth.'],
    ['lime', 'The egg-shaped citrus fruit having a green coloring and acidic juice.'],
    ['mistress','A mass of fine water droplets in the air near or in contact with the ground.'],
    ['plague', 'A widespread affliction or calamity.'],
    ['yarning', 'A strand of twisted threads or a long elaborate narrative.'],
    ['snickers', 'A snide, slightly stifled laugh.'],
]
'''



'''
word_list=[ ['rose', 'flower'], ['emerald', 'gem'], ['fame', 'popular'], ['watch', 'time'], ['water', 'bottle'], ['ball', 'kick'],['importance',''],['messenger','']]

#word_list=[['honey', 'bee'], ['rose', 'flower'], ['emerald', 'gem'], ['fame', 'popular']]

a = Crossword(30, 30, '-', 5000, word_list)
a.compute_crossword(2)
a.grids=a.get_grid()
a.pass_to_function()


print(a.solution())
print(a.word_details)
print(a.get_lists())
#print(a.get_puzzle())
#print(a.get_words())
#print(a.solution())
#print(a.get_puzzle())
#print(a.word_details)
print(len(a.current_word_list), 'out of', len(word_list))
#end_full = float(time.time())
#print(end_full - start_full)
#print(a.get_lists())
'''

