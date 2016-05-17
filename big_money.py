''' big_money.py

A program playing the arcade game Big Money. The game has to 
be started and the game window has to be visible on the screen 
through out the whole game play. Certain external images of 
the game (see below) have to be provided. The program uses 
them to locate the game window and some of the game attributes 
on the screen.
'''

import os
import time
import pyautogui
import numpy as np
import cv2


def main():
    '''Executes the game. 
    '''
    pyautogui.FAILSAFE = True
    big_money = BigMoney()
    big_money.play()

   
class BigMoney:

    def __init__(self):
        '''Prepares for the game start.

        Loads images of the game and computes region coordinates
        of important game attributes.
        '''
        self.dir_imgs = os.path.expanduser('~') + '/Images/Game_Big_Money/'
        self.path_area = self.dir_imgs + 'area_of_interest.bmp'
        self.path_grid = self.dir_imgs + 'grid.bmp'
        self.path_next_row =  self.dir_imgs + 'next_row.bmp'
        self.path_update_bar =  self.dir_imgs + 'update_bar.bmp'
        self.path_level = self.dir_imgs + 'level.bmp'
        self.path_bag = self.dir_imgs + 'bag.bmp'
        self.path_game_over = self.dir_imgs + 'game_over.bmp'
        self.path_number_bar = self.dir_imgs + 'number_bar.bmp'
        self.path_0 = self.dir_imgs + '0.bmp'
        self.path_1 = self.dir_imgs + '1.bmp'
        self.path_2 = self.dir_imgs + '2.bmp'
        self.path_3 = self.dir_imgs + '3.bmp'
        self.path_4 = self.dir_imgs + '4.bmp'
        self.path_5 = self.dir_imgs + '5.bmp'
        self.path_6 = self.dir_imgs + '6.bmp'
        self.path_7 = self.dir_imgs + '7.bmp'
        self.path_8 = self.dir_imgs + '8.bmp'
        self.path_9 = self.dir_imgs + '9.bmp'
        
        # xyxy ... left xy and right xy coords for use with
        # opencv, in form ((x,y),(x,y))
        self.area_xyxy = get_area_xyxy_on_screen(self.path_area)
        self.grid_xyxy = get_region_xyxy_in_area(self.path_grid, self.path_area)
        self.next_row_xyxy = get_region_xyxy_in_area(self.path_next_row, self.path_area)
        self.update_bar_xyxy = get_region_xyxy_in_area(self.path_update_bar, self.path_area)
        self.level_xyxy = get_region_xyxy_in_area(self.path_level, self.path_area)
        self.game_over_xyxy = ( self.grid_xyxy[0], ( self.grid_xyxy[1][0], ( self.grid_xyxy[1][1] - self.grid_xyxy[0][1] ) / 2 ) )
        self.number_bar_xyxy = get_region_xyxy_in_area(self.path_number_bar, self.path_area)
        self.coin_lenght = ( self.grid_xyxy[1][0] - self.grid_xyxy[0][0] ) / 14.0
        self.grid_xyxy = ( ( self.grid_xyxy[0][0], int(round(self.grid_xyxy[1][1]-15*self.coin_lenght)) ), self.grid_xyxy[1] )
        self.next_row_xyxy = ( self.next_row_xyxy[0], ( self.next_row_xyxy[1][0], int(round(self.next_row_xyxy[0][1]+self.coin_lenght))))
        self.grid_cells_xyxy = self.get_grid_cells_xyxy()
        self.narrowed_grid_cells_xyxy = self.get_narrowed_grid_cells_xyxy()
        self.next_row_cells_xyxy = self.get_next_row_cells_xyxy()
        self.narrowed_next_row_cells_xyxy = self.get_narrowed_next_row_cells_xyxy()
        self.adjusted_next_row_cells_xyxy = self.get_adjusted_next_row_cells_xyxy()

        self.colors = {0:(0,0,0), 1:(255,0,0), 2:(0,255,0), 4:(0,0,255), 6:(0,255,255), 7:(255,255,255)}

        self.money_bag_img_gray = cv2.imread(self.path_bag, 0)
        self.game_over_img_gray = cv2.imread(self.path_game_over, 0)
        
        self.numbers = self.get_numbers(self.path_0, self.path_1, self.path_2, self.path_3, self.path_4,
                                        self.path_5, self.path_6, self.path_7, self.path_8, self.path_9)
        
        self.money_bags = None
        self.grid = None
        self.next_row = None
        self.last_update_bar_color = None
        self.money_bag_collected = None
        self.money_bag_dropped = None
        self.area_img_BGR = None
        self.num_money_bags_collected = None
        self.current_money = None

        self.GAME_LENGTH = 360 # play for max 6 minutes
        self.GAME_SITUATION = 0
        self.THRESH_MATCH_GAME_OVER = 1000000
        self.THRESH_MATCH_LEVEL = 100

        #self.visualize_next_row_cells(cv2.imread(self.path_area),self.colors[7],self.adjusted_next_row_cells_xyxy)
        #self.visualize_grid_cells(cv2.imread(self.path_area),self.colors[7],self.grid_cells_xyxy)
                                  
    def play(self):
        '''Playing the game in a cycle.

        If GAME_SITUATION flag is 0, than all values are loaded anew from
        the screen, that is usually at the begining or when something wrong
        happens. If GAME_SITUATION flag is 1 then the game grid is updated
        internally and the playing is faster.
        '''
        t_start = time.time()
        while time.time() - t_start < self.GAME_LENGTH: # playing for max 6 minutes
            
            if  self.GAME_SITUATION == 0:
                
                self.money_bags = None
                self.grid = None
                self.next_row = None
                self.last_update_bar_color = None
                self.money_bag_collected = False
                self.money_bag_dropped = False
                self.area_img_BGR = None
                                
                self.area_img_BGR = screen_shot(self.area_xyxy[0],self.area_xyxy[1])
                self.current_money = self.get_current_money(self.area_img_BGR)
                self.grid = self.get_grid(self.area_img_BGR)
                self.level_img = get_region(self.area_img_BGR,self.level_xyxy[0],self.level_xyxy[1])
                self.last_update_bar_color = self.get_update_bar_color(self.area_img_BGR)
                if self.last_update_bar_color == 4:
                    self.next_row = self.get_next_row(self.area_img_BGR)
                
                self.GAME_SITUATION = 1
                
            elif self.GAME_SITUATION == 1:
                
                last_click_successful = self.click_and_update_grid()
                if not last_click_successful:
                    # something is wrong so lets wait and reload the screen
                    time.sleep(2)
                    self.area_img_BGR = screen_shot(self.area_xyxy[0],self.area_xyxy[1])
                    # test if its game over
                    display_img(self.area_img_BGR)
                    if self.is_game_over(self.area_img_BGR):
                        print 'Game Over'
                        break
                    else:
                        if self.is_level_up(self.area_img_BGR):
                            print 'Level Up!'
                            self.GAME_SITUATION = 0
                        else:
                            print 'Error: Nothing to click -> reloading the game attributes.'
                            self.GAME_SITUATION = 0
                else:
                    
                    if self.is_game_over(self.area_img_BGR):
                        print 'Game Over'
                        break
                    
                    if self.last_update_bar_color == 4 and not self.money_bag_collected:
                        time.sleep(0.1)
                        self.grid = self.add_next_row(self.grid,self.next_row)
                    # wait for the game on screen to settle
                    time.sleep(0.1)
                    
                    self.area_img_BGR = screen_shot(self.area_xyxy[0],self.area_xyxy[1])
                    self.last_update_bar_color = self.get_update_bar_color(self.area_img_BGR)

                    if self.last_update_bar_color == 4:
                        self.area_img_BGR = screen_shot(self.area_xyxy[0],self.area_xyxy[1])  
                        self.next_row = self.get_next_row(self.area_img_BGR)
                        if np.count_nonzero(self.next_row) < 14:
                            time.sleep(0.8)
                            self.area_img_BGR = screen_shot(self.area_xyxy[0],self.area_xyxy[1])

                    self.money_bags = self.get_money_bags_on_fly(self.area_img_BGR,self.grid)

                    if self.is_level_up(self.area_img_BGR):
                        print 'Level Up!'
                        time.sleep(1.5)
                        self.GAME_SITUATION = 0                       
                        
                    current_money = self.get_current_money(self.area_img_BGR)
                    if self.current_money > current_money:
                        print 'Error: Clicked the wrong -> reloading the game attributes.'
                        time.sleep(1)
                        self.GAME_SITUATION = 0
                    self.current_money = current_money
                    
    def is_level_up(self, area_img_BGR):
        '''Checks if it is a new level (level up)
        '''
        level_img = get_region(area_img_BGR, self.level_xyxy[0], self.level_xyxy[1])
        level_absdiff = np.sum(cv2.sumElems(cv2.absdiff(level_img, self.level_img)))
        if level_absdiff > self.THRESH_MATCH_LEVEL:
            return True
        else:
            return False
            
    def is_game_over(self, area_img_BGR):
        area_img_GREY = cv2.cvtColor(area_img_BGR,cv2.COLOR_BGR2GRAY)
        match_value = get_template_match(area_img_GREY, self.game_over_img_gray)[0]
        if match_value < self.THRESH_MATCH_GAME_OVER:
            return True
        else:
            return False


    def get_numbers(self,path_0,path_1,path_2,path_3,path_4,
                    path_5,path_6,path_7,path_8,path_9):
        i0 = cv2.imread(path_0,1)
        i1 = cv2.imread(path_1,1)
        i2 = cv2.imread(path_2,1)
        i3 = cv2.imread(path_3,1)
        i4 = cv2.imread(path_4,1)
        i5 = cv2.imread(path_5,1)
        i6 = cv2.imread(path_6,1)
        i7 = cv2.imread(path_7,1)
        i8 = cv2.imread(path_8,1)
        i9 = cv2.imread(path_9,1)
        i_numbers = [i0,i1,i2,i3,i4,i5,i6,i7,i8,i9]
        i_numbers = [self.get_thresh_yellow(img) for img in i_numbers]
        shape_max = max([s for img in i_numbers for s in img.shape[0:2] ])
        template = np.zeros((shape_max,shape_max),dtype=np.uint8)
        for idx,img in enumerate(i_numbers):
            h,w = img.shape[0:2]
            b_h = (shape_max - h)/2
            b_w = (shape_max - w)/2
            template[b_h:b_h+h,b_w:b_w+w] = img
            i_numbers[idx] = template.copy()
            template[:,:] = 0
        return i_numbers

    def get_thresh_yellow(self,img):
        tval,t_img = cv2.threshold(img,220,255,cv2.THRESH_BINARY)
        y = cv2.bitwise_and(t_img[:,:,1],t_img[:,:,2])
        y = y[:,~np.all(y==0,axis=0)]
        y = y[~np.all(y==0,axis=1)]
        return y
        

    def get_current_money(self, area_img_BGR):
        img_money_bar_BGR = get_region(area_img_BGR,self.number_bar_xyxy[0],self.number_bar_xyxy[1])
        tval,t_img = cv2.threshold(img_money_bar_BGR,220,255,cv2.THRESH_BINARY)
        y = cv2.bitwise_and(t_img[:,:,1],t_img[:,:,2])
        columns_zero = list(~np.all(y==0,axis=0))

        beginings = [idx for idx,item in enumerate(columns_zero) if idx!=len(columns_zero)-1 and (not item and columns_zero[idx+1]) ]
        ends = [idx+1 for idx,item in enumerate(columns_zero) if idx!=len(columns_zero)-1 and (item and not columns_zero[idx+1]) ]
        boundaries = [(left,right) for left,right in zip(beginings,ends)]
        boundaries = boundaries[1:]
        numbers = [y[:,left:right] for left,right in boundaries]
        numbers = [y[:,~np.all(y==0,axis=0)] for y in numbers]
        numbers = [y[~np.all(y==0,axis=1)] for y in numbers]
        numbers = [self.get_what_number(y) for y in numbers]
        numbers = [number*10**(len(numbers)-1-idx) for idx,number in enumerate(numbers)]
        number = sum(numbers)
        return number
        
        
    def get_what_number(self,img):
        shape_max = self.numbers[0].shape[0]*3/2
        padded_img = np.zeros((shape_max,shape_max),dtype=np.uint8)
        h,w = img.shape[0:2]
        b_h = (shape_max - h)/2
        b_w = (shape_max - w)/2
        padded_img[b_h:b_h+h,b_w:b_w+w] = img
        numbers = [cv2.matchTemplate(padded_img,img_number, cv2.TM_SQDIFF) for img_number in self.numbers]
        numbers = [cv2.minMaxLoc(number)[0] for number in numbers]
        number = numbers.index(min(numbers))
        return number
        

    def add_next_row(self, grid, next_row):
        grid = np.vstack((grid,next_row))
        grid = np.delete(grid,0,axis=0)
        return grid

    def get_visualized_grid(self):
        grid_img_BGR = cv2.imread(self.path_grid,1)
        grid_img_BGR[:] = self.colors[0]
        grid = np.reshape(self.grid,(15*14))
        for idx, cell in enumerate(self.grid_cells):
            color = self.colors[grid[idx]]
            grid_img_BGR[cell[0][1]:cell[1][1],cell[0][0]:cell[1][0]] = color
        return grid_img_BGR
        
    def visualize_regions_in_area(self, area_img_BGR):
        cv2.rectangle(area_img_BGR, self.grid_xyxy[0],self.grid_xyxy[1],self.colors[4])
        cv2.rectangle(area_img_BGR, self.next_row_xyxy[0],self.next_row_xyxy[1],self.colors[4])
        cv2.rectangle(area_img_BGR, self.update_bar_xyxy[0],self.update_bar_xyxy[1],self.colors[7])
        cv2.rectangle(area_img_BGR, self.level_xyxy[0],self.level_xyxy[1],self.colors[4])
        cv2.imshow('d',area_img_BGR)
        cv2.waitKey(0)

    def get_best_tuple(self, tuple_positions):
        tuples_values = []
        num_nonzero_per_column = [np.count_nonzero(self.grid[:,jj]) for jj in xrange(14)]
        max_column_height = np.max(num_nonzero_per_column)
        print max_column_height
        POWER_VAL = 2
        for tuple_idx_level0, positions in enumerate(tuple_positions):
            grid_level0 = np.copy(self.grid)
            
            bag_collected_level0 = self.update_grid(grid_level0,
                                                    positions)
            value_level0 = np.sum(np.power(np.sum((grid_level0 > 0),
                                           axis=0),POWER_VAL))
            tuples_values.append([bag_collected_level0,
                                  value_level0,
                                  0,
                                  max(bag_collected_level0,
                                      0),
                                  value_level0,
                                  0,
                                  max(bag_collected_level0,
                                      0,
                                      0),
                                  value_level0,
                                  tuple_idx_level0])
            
            if (self.last_update_bar_color == 4 and not bag_collected_level0):
                grid_level0 = self.add_next_row(grid_level0,
                                                self.next_row)
                
            tuple_positions_level1 = self.get_tuples_positions(grid_level0)
                
            if len(tuple_positions_level1) > 0:
                for positions_level1 in tuple_positions_level1:
                    grid_level1 = np.copy(grid_level0)
                    bag_collected_level1 = self.update_grid(grid_level1,positions_level1)
                    value_level1 = np.sum(np.power(np.sum((grid_level1 > 0),axis=0),POWER_VAL))
                    tuples_values.append([bag_collected_level0,
                                          value_level0,
                                          bag_collected_level1,
                                          max(bag_collected_level0,
                                              bag_collected_level1),
                                          value_level1,
                                          0,
                                          max(bag_collected_level0,
                                              bag_collected_level1,
                                              0),
                                          value_level1,
                                          tuple_idx_level0])
                    tuple_positions_level2 = self.get_tuples_positions(grid_level1)
                    if len(tuple_positions_level2) > 0:
                        for positions_level2 in tuple_positions_level2:
                            grid_level2 = np.copy(grid_level1)
                            bag_collected_level2 = self.update_grid(grid_level2,positions_level2)
                            value_level2 = np.sum(np.power(np.sum((grid_level2 > 0),axis=0),POWER_VAL))
                            tuples_values.append([bag_collected_level0,
                                                  value_level0,
                                                  bag_collected_level1,
                                                  max(bag_collected_level0,
                                                      bag_collected_level1),
                                                  value_level1,
                                                  bag_collected_level2,
                                                  max(bag_collected_level0,
                                                      bag_collected_level1,
                                                      bag_collected_level2),
                                                  value_level2,
                                                  tuple_idx_level0])
        if max_column_height < 10:
            tuples_values = sorted(tuples_values, key=lambda values:(-values[6],
                                                                     values[7],
                                                                     values[4],
                                                                     values[1]))
        elif 10 <= max_column_height < 12:
            tuples_values = sorted(tuples_values, key=lambda values:(-values[3],
                                                                     -values[6],
                                                                     values[7],
                                                                     values[4],
                                                                     values[1]))
        else:
            tuples_values = sorted(tuples_values, key=lambda values:(-values[0],
                                                                     -values[3],
                                                                     -values[6],
                                                                     values[7],
                                                                     values[4],
                                                                     values[1]))
        #print tuples_values[0]
        return tuple_positions[tuples_values[0][8]]        

    def test_grid(self):
        time.sleep(1)
        shot_area = screen_shot(self.area_xyxy[0],self.area_xyxy[1])
        grid_new = self.get_grid(shot_area)
        print self.grid
        print
        print grid_new
        if np.sum(self.grid-grid_new) != -8 and  np.sum(self.grid-grid_new) !=0:
            return False
        else:
            return True

    def click_and_update_grid(self):
        tuples_positions = self.get_tuples_positions(self.grid)
        if len(tuples_positions) > 0:
            # num_nonzero_per_column = [np.count_nonzero(self.grid[:,jj]) for jj in xrange(14)]
            # for bag_ii,bag_jj in self.money_bags:
            #     num_nonzero_per_column[bag_jj] += 2
            # preference_list = [kk**3 for kk in num_nonzero_per_column]
            # smoothed_pref_list = [(2*ii+jj+kk)//4 for ii,jj,kk in zip(preference_list[1:-1],preference_list[2:],preference_list[:-2])]
            # preference_list = [(2*preference_list[0]+1*preference_list[1])//3] \
            #                   + smoothed_pref_list \
            #                   + [(2*preference_list[-1]+1*preference_list[-2])//3]
            # preference_sums = []
            # best_positions = 0
            # for positions in tuples_positions:
            #     preference_sum = sum([preference_list[jj] + 14 - ii + self.get_money_bag_bonus(ii,jj) for ii,jj in positions])
            #     preference_sums.append(preference_sum)
            # t0 = time.time()
            # #print self.grid
            # print tuples_positions

            #print preference_sums
            # print 'money bags', self.money_bags
            # t1 = time.time()
            # print 'print', t1-t0
            #best_tuple_positions = tuples_positions[preference_sums.index(max(preference_sums))]
            #t0 = time.time()
            #grid = np.copy(self.grid)
            best_tuple_positions = self.get_best_tuple(tuples_positions)
            # if not self.test_grid():
            #     print 'error when getting tuples'
            #print grid - self.grid
            #print best_tuple_positions
            #print time.time() - t0
            best_opt_ii = best_tuple_positions[0][0]
            best_opt_jj = best_tuple_positions[0][1]
            best_opt_x = int(round(self.area_xyxy[0][0] + self.grid_xyxy[0][0] +
                                   best_opt_jj * self.coin_lenght + self.coin_lenght/2))
            best_opt_y = int(round(self.area_xyxy[0][1] + self.grid_xyxy[0][1] +
                                   best_opt_ii * self.coin_lenght + self.coin_lenght/2))
            mouse_click([best_opt_x, best_opt_y])
            self.money_bag_collected = 0
            self.money_bag_collected = self.update_grid(self.grid, best_tuple_positions)
            # if not self.test_grid():
            #     print 'error when upgrade of the grid'   
                
            #print self.money_bag_collected
            return True
        else:
            return False

                
    def get_money_bag_bonus(self, ii, jj):
        bonus = 0
        for bag_ii,bag_jj in self.money_bags:
            if bag_jj == jj and bag_ii == ii-1:
                bonus = 2000
                print 'BONUS 200 at', ii, jj
        return bonus
        
    def update_grid(self, grid, positions):
        num_bags_collected = 0
        positions.sort(key=lambda value: value[0])
        for yy,xx in positions:
            num_bags_collected += self.shift_down(yy,xx,grid)
            #print bag_collected
        num_left_zeros = 7 - np.count_nonzero(grid[14,0:7])
        num_right_zeros = 7 - np.count_nonzero(grid[14,7:14])
        new_column = np.zeros((15,1), dtype=np.int)
        grid_local = grid[:,grid[14]!=0]
        for ii in xrange(num_left_zeros):
            grid_local = np.hstack((new_column,grid_local))
        for ii in xrange(num_right_zeros):
            grid_local = np.hstack((grid_local,new_column))
        grid[:] = grid_local[:]
        return num_bags_collected
           
    def shift_down(self, yy, xx, grid):
        bag_collected = 0
        if yy > 0 and grid[yy-1,xx] == 8:
            grid[yy-1,xx] = 0
            bag_collected = 1
            #print bag_collected
        while yy > 0:
            grid[yy,xx] = grid[yy-1,xx]
            yy -= 1
        grid[0,xx] = 0
        return bag_collected

    def get_tuples_positions(self, grid):
        tuples_positions = []
        for color in [1,2,4,6]:     # blue, green, red, yellow (yellow = red+green = 2+4 = 6)
            tuples_positions.extend(self.get_tuples_positions_for_color(color,grid))
        return tuples_positions

    def get_tuples_positions_for_color(self, color, grid):
        grid_color = (grid == color)
        tuples_positions_for_color = []
        for xx in xrange(14):
            for yy in xrange(15):
                if grid_color[yy,xx]:
                    grid_color[yy,xx] = False
                    positions = [(yy,xx)]
                    heap = self.get_positions_around(yy,xx)
                    while len(heap) > 0:
                        pos = heap.pop()
                        new_pos = self.check_position(pos,grid_color)
                        if new_pos[0]:
                            positions.append(pos)
                            heap.extend(new_pos[1])
                            grid_color[pos[0],pos[1]] = False
                    if len(positions) > 2:
                        tuples_positions_for_color.append(positions)
        return tuples_positions_for_color

    def check_position( self, position, grid):
        yy = position[0]
        xx = position[1]
        if yy>=0 and xx>=0 and yy<15 and xx<14 and grid[yy,xx]:
            return [True,self.get_positions_around(yy,xx)]
        else:
            return [False]

    def get_positions_around( self, yy, xx ):
        return [ (yy-1,xx), (yy+1,xx), (yy,xx-1), (yy,xx+1) ]

    def get_money_bags_on_fly(self, area_img_BGR, grid):
        #self.money_bag_dropped = False
        money_bags = []
        grid_img_BGR = get_region(area_img_BGR, self.grid_xyxy[0], self.grid_xyxy[1])
        grid_local = grid*np.logical_and(grid<8,grid>0)
        first_zero_postions_from_bottom = [14-np.count_nonzero(grid_local[:,jj]) for jj in xrange(14)]
        for jj,ii in enumerate(first_zero_postions_from_bottom):
                cell_img_BGR = get_region(grid_img_BGR, tuple(self.grid_cells_xyxy[0,jj,0,:]),
                                          tuple(self.grid_cells_xyxy[ii,jj,1,:]))
                cell_img_gray = cv2.cvtColor(cell_img_BGR, cv2.COLOR_BGR2GRAY)
                
                if get_template_match(cell_img_gray,self.money_bag_img_gray)[0] < 500000:
                    money_bags.append((ii,jj))
                    #self.money_bag_dropped = True
                    grid_local[ii,jj] = 8
        grid[:] = grid_local[:]
        return money_bags

    def get_money_bags_restart(self, area_img_BGR, grid):
        #self.money_bag_dropped = False
        money_bags = []
        grid_img_BGR = get_region(area_img_BGR, self.grid_xyxy[0], self.grid_xyxy[1])
        for ii in xrange(15):
            for jj in xrange(14):
                cell_img_BGR = get_region(grid_img_BGR, tuple(self.grid_cells_xyxy[ii,jj,0,:]),
                                          tuple(self.grid_cells_xyxy[ii,jj,1,:]))
                cell_img_gray = cv2.cvtColor(cell_img_BGR, cv2.COLOR_BGR2GRAY)
                
                if get_template_match(cell_img_gray,self.money_bag_img_gray)[0] < 500000:
                    money_bags.append((ii,jj))
                    #self.money_bag_dropped = True
                    grid[ii,jj] = 8
            print 
        return money_bags 


    def get_cell_BGR_average(self, cell_img_BGR):
        return np.rint(np.average(cell_img_BGR,axis=(0,1))).astype(int)


    def get_update_bar_color( self, area_img_BGR):
        update_bar_img_BGR = get_region(area_img_BGR,self.update_bar_xyxy[0],self.update_bar_xyxy[1])
        update_bar = np.rint(np.average(update_bar_img_BGR,axis=(0,1))).astype(int)
        update_bar_color =  1*(update_bar[0]>180)+2*(update_bar[1]>180)+4*(update_bar[2]>180)
        return update_bar_color
    
    def get_next_row(self, area_img_BGR):
        next_row_img_BGR = get_region(area_img_BGR,self.next_row_xyxy[0],self.next_row_xyxy[1])
        next_row = np.zeros((1,14,3), dtype=np.int)
        for jj in xrange(next_row.shape[1]):
            next_row[0,jj,:] = np.rint(np.average(get_region(next_row_img_BGR,
                                                             tuple(self.narrowed_next_row_cells_xyxy[0,jj,0,:]),
                                                             tuple(self.narrowed_next_row_cells_xyxy[0,jj,1,:]))                                                                                      ,axis=(0,1))).astype(int)
        next_row = 1*(next_row[0,:,0]>180)+2*(next_row[0,:,1]>180)+4*(next_row[0,:,2]>180)
        if np.count_nonzero(next_row) < 14:
            next_row = np.zeros((1,14,3), dtype=np.int)
            for jj in xrange(next_row.shape[1]):               
                next_row[0,jj,:] = np.rint(np.average(get_region(next_row_img_BGR,
                                                                 tuple(self.adjusted_next_row_cells_xyxy[0,jj,0,:]),
                                                                 tuple(self.adjusted_next_row_cells_xyxy[0,jj,1,:]))
                                                      ,axis=(0,1))).astype(int)
            next_row = 1*(next_row[0,:,0]>180)+2*(next_row[0,:,1]>180)+4*(next_row[0,:,2]>180)
        if np.count_nonzero(next_row) < 14:
            print 'Error reading next row!!!'
        return next_row

    def get_grid(self, area_img_BGR):
        grid_img_BGR = get_region(area_img_BGR,self.grid_xyxy[0],self.grid_xyxy[1])
        grid = np.zeros((15,14,3), dtype=np.int)
        bags = []
        for ii in xrange(grid.shape[0]):
            for jj in xrange(grid.shape[1]):
                grid_cell_BGR_wide = get_region(grid_img_BGR,tuple(self.grid_cells_xyxy[ii,jj,0,:]),
                                              tuple(self.grid_cells_xyxy[ii,jj,1,:]))
                grid_cell_BGR_narrow = get_region(grid_img_BGR,tuple(self.narrowed_grid_cells_xyxy[ii,jj,0,:]),
                                              tuple(self.narrowed_grid_cells_xyxy[ii,jj,1,:]))
                grid_cell_GRAY_wide = cv2.cvtColor(grid_cell_BGR_wide, cv2.COLOR_BGR2GRAY)
                
                if get_template_match(grid_cell_GRAY_wide,self.money_bag_img_gray)[0] < 500000:
                    bags.append((ii,jj))
                grid[ii,jj,:] = np.rint(np.average(grid_cell_BGR_narrow,axis=(0,1))).astype(int)
        grid = 1*(grid[:,:,0]>180)+2*(grid[:,:,1]>180)+4*(grid[:,:,2]>180)
        for bag_ii,bag_jj in bags:
            grid[bag_ii,bag_jj] = 8
        return grid
    
        
    def get_next_row_cells_xyxy(self):
        next_row_cells_xyxy = np.zeros((1,14,2,2), dtype=np.int)
        next_row_xx_width = self.next_row_xyxy[1][0] - self.next_row_xyxy[0][0]
        next_row_yy_height = self.next_row_xyxy[1][1] - self.next_row_xyxy[0][1]
        next_row_xx_coords = [min(int(round(xx*self.coin_lenght)),next_row_xx_width) for xx in xrange(0,15)]
        next_row_yy_coords = [min(int(round(yy*self.coin_lenght)),next_row_yy_height) for yy in xrange(0,2)]
        for jj in xrange(next_row_cells_xyxy.shape[1]):
            next_row_cells_xyxy[0,jj,:,:] = np.array([[next_row_xx_coords[jj],
                                                        next_row_yy_coords[0]],
                                                      [next_row_xx_coords[jj+1],
                                                        next_row_yy_coords[1]]])
        return next_row_cells_xyxy
    
    def get_narrowed_next_row_cells_xyxy(self):
        narrowed_next_row_cells_xyxy = np.copy(self.next_row_cells_xyxy)
        # making it more narrow
        quater = int(round(self.coin_lenght/4))
        narrowed_next_row_cells_xyxy[:,:,0,:] += quater
        narrowed_next_row_cells_xyxy[:,:,1,:] -= quater
        # adjustment for those at sides
        narrowed_next_row_cells_xyxy[:,0,0,0] += quater
        narrowed_next_row_cells_xyxy[:,13,1,0] -= quater
        return narrowed_next_row_cells_xyxy

    def get_adjusted_next_row_cells_xyxy(self):
        adjusted_next_row_cells_xyxy = np.copy(self.next_row_cells_xyxy)
        # making it more narrow
        quater = int(round(self.coin_lenght/4))
        adjusted_next_row_cells_xyxy[:,:,0,:] += quater
        adjusted_next_row_cells_xyxy[:,:,0,1] += 2*quater
        adjusted_next_row_cells_xyxy[:,:,1,0] -= quater
        # adjustment for those at sides
        adjusted_next_row_cells_xyxy[:,0,0,0] += quater
        adjusted_next_row_cells_xyxy[:,13,1,0] -= int(round(1.5*quater))
        return adjusted_next_row_cells_xyxy

    def visualize_next_row_cells(self, area_img_BGR, color, next_row_cells_xyxy):
        next_row_img_BGR = get_region(area_img_BGR, self.next_row_xyxy[0], self.next_row_xyxy[1])
        for jj in xrange(next_row_cells_xyxy.shape[1]):
            left_corner = tuple(next_row_cells_xyxy[0,jj,0,:])
            right_corner =  tuple(next_row_cells_xyxy[0,jj,1,:])
            cv2.rectangle(next_row_img_BGR, left_corner, right_corner, color)
        cv2.imshow('next row cells',next_row_img_BGR)
        cv2.waitKey(0)       

    def get_grid_cells_xyxy(self):
        grid_cells_xyxy = np.zeros((15,14,2,2), dtype=np.int)
        grid_xx_width = self.grid_xyxy[1][0] - self.grid_xyxy[0][0]
        grid_yy_height = self.grid_xyxy[1][1] - self.grid_xyxy[0][1]
        grid_xx_coords = [min(int(round(jj*self.coin_lenght)),grid_xx_width) for jj in xrange(0,15)]
        grid_yy_coords = [min(int(round(ii*self.coin_lenght)),grid_yy_height) for ii in xrange(0,16)]
        for ii in xrange(grid_cells_xyxy.shape[0]):
            for jj in xrange(grid_cells_xyxy.shape[1]):
                grid_cells_xyxy[ii,jj,:,:] = np.array([[grid_xx_coords[jj],
                                                        grid_yy_coords[ii]],
                                                       [grid_xx_coords[jj+1],
                                                        grid_yy_coords[ii+1]]])
        return grid_cells_xyxy

    def get_narrowed_grid_cells_xyxy(self):
        narrowed_grid_cells_xyxy = np.zeros((15,14,2,2), dtype=np.int)        
        quater = int(round(self.coin_lenght/4))
        narrowed_grid_cells_xyxy[:,:,0,:] = self.grid_cells_xyxy[:,:,0,:] + quater
        narrowed_grid_cells_xyxy[:,:,1,:] = self.grid_cells_xyxy[:,:,1,:] - quater
        return narrowed_grid_cells_xyxy

    def visualize_grid_cells(self, area_img_BGR, color, grid_cells_xyxy):
        grid_img_BGR = get_region(area_img_BGR, self.grid_xyxy[0], self.grid_xyxy[1])
        for ii in xrange(grid_cells_xyxy.shape[0]):
            for jj in xrange(grid_cells_xyxy.shape[1]):       
                left_corner = tuple(grid_cells_xyxy[ii,jj,0,:])
                right_corner =  tuple(grid_cells_xyxy[ii,jj,1,:])
                cv2.rectangle(grid_img_BGR, left_corner, right_corner, color)
        cv2.imshow('grid cells',grid_img_BGR)
        cv2.waitKey(0)
    

def get_region(img, left_corner, right_corner):
    return img[left_corner[1]:right_corner[1], left_corner[0]:right_corner[0]]


def get_region_xyxy_in_area(region_path, path_area):
    area = cv2.imread(path_area, 0)
    region = cv2.imread(region_path, 0)
    min_loc = get_template_match(area, region)[1]
    left_corner = min_loc[0], min_loc[1]
    right_corner = min_loc[0] + region.shape[1], min_loc[1] + region.shape[0]
    return left_corner, right_corner


def get_area_xyxy_on_screen(path_area):
    
    ''' Returns position of the left_corner and the right_corner of a template in an image/screen. '''
    screen_BGR = screen_shot()
    screen_gray = cv2.cvtColor(screen_BGR, cv2.COLOR_BGR2GRAY)
    area = cv2.imread(path_area, 0)
    min_loc = get_template_match(screen_gray, area)[1]
    left_corner = min_loc[0], min_loc[1]
    right_corner = min_loc[0] + area.shape[1], min_loc[1] + area.shape[0]
    return left_corner, right_corner

def mouse_click(position):
    pyautogui.moveTo(position[0],position[1])
    pyautogui.click()

def get_template_match(img_gray, template):
    result = cv2.matchTemplate(img_gray, template, cv2.TM_SQDIFF )
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    value, xy = min_val, min_loc
    return value, xy

def screen_shot(left_corner=None, right_corner=None):
    if (left_corner is not None) and (right_corner is not None):
        region=(left_corner[0],left_corner[1],right_corner[0]-left_corner[0],right_corner[1]-left_corner[1])
        pil_image = pyautogui.screenshot(region=region)
    else:
        pil_image = pyautogui.screenshot()
    opencv_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
    return opencv_image

def display_img(img, window_name='img'):
    cv2.namedWindow(window_name,cv2.WINDOW_NORMAL)
    cv2.imshow(window_name,img)
    cv2.waitKey(0)

if __name__ == '__main__':
    main()
