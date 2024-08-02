import pandas as pd 
import numpy as np 

class CourtCoordinates:
    '''
    Stores court dimensions and calculates the (x,y,z) coordinates of the outside perimeter, 
    three point line, backboard, hoop, and free throw line.
    The default dimensions of a men's NCAA court.
    '''
    def __init__(self):
        self.court_length = 94                 # the court is 94 feet long
        self.court_width = 50                  # the court is 50 feet wide
        self.hoop_loc_x = 25                   # the hoop is at the center of the court length-wise
        self.hoop_loc_y = 4.25                 # the center of the hoop is 63 inches from the baseline
        self.hoop_loc_z = 10                   # the hoop is 10 feet off the ground
        self.hoop_radius = .75
        self.three_arc_distance = 23.75       # the NCAA men's three-point arc is 22ft and 1.75in from the hoop center
        self.three_straight_distance = 22      # the NCAA men's three-point straight section is 21ft 8in from the hoop center
        self.three_straight_length = 8.89      # the NCAA men's three-point straight section length is 8ft and 10.75in
        self.backboard_width = 6               # backboard is 6ft wide
        self.backboard_height = 4              # backboard is 4ft tall
        self.backboard_baseline_offset = 3     # backboard is 3ft from the baseline
        self.backboard_floor_offset = 9        # backboard is 9ft from the floor
        self.free_throw_line_distance = 15     # distance from the free throw line to the backboard

    @staticmethod
    def calculate_quadratic_values(a, b, c):
        '''
        Given values a, b, and c,
        the function returns the output of the quadratic formula
        '''
        x1 = (-b + (b ** 2 - 4 * a * c) ** 0.5) / (2 * a)
        x2 = (-b - (b ** 2 - 4 * a * c) ** 0.5) / (2 * a)

        return x1, x2

    def __get_court_perimeter_coordinates(self):
        '''
        Returns coordinates of full court perimeter lines. A court that is 50 feet wide and 94 feet long
        In shot chart data, each foot is represented by 10 units.
        '''
        width = self.court_width
        length = self.court_length
        court_perimeter_bounds = [
            [0, 0, 0], 
            [width, 0, 0], 
            [width, length, 0], 
            [0, length, 0], 
            [0, 0, 0]
        ]

        court_df = pd.DataFrame(court_perimeter_bounds, columns=['x','y','z'])
        court_df['line_group'] = 'outside_perimeter'
        court_df['color'] = 'court'
        
        return court_df
    
    def __get_half_court_coordinates(self):
        '''
        Returns coordinates for the half court line.
        '''
        width = self.court_width 
        half_length = self.court_length / 2
        circle_radius = 6
        circle_radius2 = 2
        circle_center = [width / 2, half_length, 0]
        circle_points = []
        circle_points2 = []
        num_points = 400  # Number of points to approximate the circle
        for i in range(num_points):
            angle = 2 * np.pi * i / num_points
            x = circle_center[0] + circle_radius * np.cos(angle)
            y = circle_center[1] + circle_radius * np.sin(angle)
            circle_points.append([x, y, circle_center[2]])
        for i in range(num_points):
            angle = 2 * np.pi * i / num_points
            x = circle_center[0] + circle_radius2 * np.cos(angle)
            y = circle_center[1] + circle_radius2 * np.sin(angle)
            circle_points2.append([x, y, circle_center[2]])

  # Example radius of the free throw circle, adjust as needed

        half_court_bounds = [[0, half_length, 0], [width, half_length, 0]]

        half_df = pd.DataFrame(half_court_bounds, columns=['x','y','z'])
        circle_df = pd.DataFrame(circle_points, columns=['x', 'y', 'z'])
        circle_df['line_group'] = f'free_throw_circle'
        circle_df['color'] = 'court'

        circle_df2 = pd.DataFrame(circle_points2, columns=['x', 'y', 'z'])
        circle_df2['line_group'] = f'free_throw_circle'
        circle_df2['color'] = 'court'

        half_df['line_group'] = 'half_court'
        half_df['color'] = 'court'

        return pd.concat([half_df, circle_df,circle_df2])

    def __get_backboard_coordinates(self, loc):
        '''
        Returns coordinates of the backboard on both ends of the court
        A backboard is 6 feet wide, 4 feet tall 
        '''

        backboard_start = (self.court_width/2)  -  (self.backboard_width/2)
        backboard_end = (self.court_width/2) + (self.backboard_width/2)
        height = self.backboard_height
        floor_offset = self.backboard_floor_offset
        if loc == 'far':
            offset = self.backboard_baseline_offset
        if loc == 'near':
            offset = self.court_length - self.backboard_baseline_offset

        backboard_bounds = [
            [backboard_start, offset, floor_offset], 
            [backboard_start, offset, floor_offset + height], 
            [backboard_end, offset, floor_offset + height], 
            [backboard_end, offset, floor_offset], 
            [backboard_start, offset, floor_offset]
        ]

        backboard_df = pd.DataFrame(backboard_bounds, columns=['x','y','z'])
        backboard_df['line_group'] = f'{loc}_backboard'
        backboard_df['color'] = 'court'

        return  backboard_df
    
    def __get_three_point_coordinates(self, loc):
        '''
        Returns coordinates of the three point line on both ends of the court
        Given that the ncaa men's three point line is 22ft and 1.5in from the center of the hoop
        '''
        
        # init values
        hoop_loc_x, hoop_loc_y = self.hoop_loc_x, self.hoop_loc_y
        strt_dst_start = (self.court_width/2) - self.three_straight_distance
        strt_dst_end = (self.court_width/2) + self.three_straight_distance
        strt_len = self.three_straight_length
        arc_dst = self.three_arc_distance

        start_straight = [
            [strt_dst_start,0,0],
            [strt_dst_start,strt_len,0]
        ]
        end_straight = [
            [strt_dst_end,strt_len,0], 
            [strt_dst_end,0,0]
        ]
        line_coordinates = []

        if loc == 'near': 
            crt_len = self.court_length
            hoop_loc_y = crt_len - hoop_loc_y
            start_straight = [[strt_dst_start,crt_len,0],[strt_dst_start,crt_len-strt_len,0]]
            end_straight = [[strt_dst_end,crt_len-strt_len,0], [strt_dst_end,crt_len,0]]

        # drawing the three point line
        line_coordinates.extend(start_straight)
        
        a = 1
        b = -2 * hoop_loc_y
        d = arc_dst 
        for x_coord in np.linspace(int(strt_dst_start), int(strt_dst_end), 100):
            c = hoop_loc_y ** 2 + (x_coord - 25) ** 2 - (d) ** 2

            y1, y2 = self.calculate_quadratic_values(a, b, c)
            if loc == 'far':
                y_coord = y1
            if loc == 'near':
                y_coord = y2
        
            line_coordinates.append([x_coord, y_coord, 0])

        line_coordinates.extend(end_straight)

        far_three_df = pd.DataFrame(line_coordinates, columns=['x', 'y', 'z'])
        far_three_df['line_group'] = f'{loc}_three'
        far_three_df['color'] = 'court'

        return far_three_df

    def __get_hoop_coordinates(self, loc):
        '''
        Returns the hoop coordinates of the far/near hoop
        '''
        hoop_coordinates_top_half = []
        hoop_coordinates_bottom_half = []

        hoop_loc_x, hoop_loc_y, hoop_loc_z = (self.hoop_loc_x, self.hoop_loc_y, self.hoop_loc_z)

        if loc == 'near': 
            hoop_loc_y = self.court_length - hoop_loc_y

        hoop_radius = self.hoop_radius
        hoop_min_x, hoop_max_x = (hoop_loc_x - hoop_radius, hoop_loc_x + hoop_radius)
        hoop_step = 0.1

        a = 1
        b = -2 * hoop_loc_y
        for hoop_coord_x in np.arange(hoop_min_x, hoop_max_x + hoop_step/2, hoop_step):
            c = hoop_loc_y ** 2 + (hoop_loc_x - round(hoop_coord_x,2)) ** 2 - hoop_radius ** 2
            hoop_coord_y1, hoop_coord_y2 = self.calculate_quadratic_values(a, b, c)

            hoop_coordinates_top_half.append([hoop_coord_x, hoop_coord_y1, hoop_loc_z])
            hoop_coordinates_bottom_half.append([hoop_coord_x, hoop_coord_y2, hoop_loc_z])

        hoop_coordinates_df = pd.DataFrame(hoop_coordinates_top_half + hoop_coordinates_bottom_half[::-1], columns=['x','y','z'])
        hoop_coordinates_df['line_group'] = f'{loc}_hoop'
        hoop_coordinates_df['color'] = 'hoop'
        
        return hoop_coordinates_df




    @staticmethod
    def calculate_quadratic_values(a, b, c):
        '''
        Given values a, b, and c,
        the function returns the output of the quadratic formula
        '''
        x1 = (-b + (b ** 2 - 4 * a * c) ** 0.5) / (2 * a)
        x2 = (-b - (b ** 2 - 4 * a * c) ** 0.5) / (2 * a)

        return x1, x2

    def __get_free_throw_line_and_circle_coordinates(self, loc):
        '''
        Returns coordinates of the free throw line, circle at the center of the free throw line,
        and lines extending from the free throw line to the baseline. 
        Also adds two parallel lines, each 2 feet away from the existing lines,
        and a semicircle with a 4 ft radius starting at 3 ft or 91 ft from the baseline.
        The free throw line is 15 feet from the backboard and spans from sideline to sideline.
        The circle is centered on the free throw line and cuts the line in half.
        '''
        distance = 18
        width = self.court_width
        length = self.court_length
        circle_radius = 6  # Radius of the free throw circle
        semicircle_radius = 4  # Radius of the semicircle
        offset = 2  # Offset distance for the additional lines
        semicircle_start_distance_near = 3  # Starting distance from baseline for 'near'
        semicircle_start_distance_far = 91  # Starting distance from baseline for 'far'
        semicircle_start = semicircle_start_distance_near
        semicircle_start2 = semicircle_start_distance_far
        # Coordinates for the free throw line and the circle
        if loc == 'far':
            line_start = [17, length - distance, 0]
            line_end = [width - 17, length - distance, 0]
            circle_center = [width / 2, length - distance, 0]
            baseline_y = length  # Baseline is at the end of the court
            left_offset = -offset
            right_offset = offset
        else:
            line_start = [17, distance, 0]
            line_end = [width - 17, distance, 0]
            circle_center = [width / 2, distance, 0]
            baseline_y = 0  # Baseline is at the start of the court
            left_offset = -offset
            right_offset = offset

        # Generate circle coordinates
        circle_points = []
        num_points = 400  # Number of points to approximate the circle
        for i in range(num_points):
            angle = 2 * np.pi * i / num_points
            x = circle_center[0] + circle_radius * np.cos(angle)
            y = circle_center[1] + circle_radius * np.sin(angle)
            circle_points.append([x, y, circle_center[2]])
        

        # Generate semicircle coordinates
        semicircle_points = []
        num_points = 100  # Number of points to approximate the semicircle
        for i in range(num_points + 1):
            angle = np.pi * i / num_points
            x = circle_center[0] + 4 * np.cos(angle)
            y = semicircle_start + 5 * np.sin(angle)
            semicircle_points.append([x, y, circle_center[2]])
        semicircle_points2 = []
        for i in range(num_points + 1):
            angle = np.pi * i / num_points
            x = circle_center[0] + 4 * np.cos(angle)
            y = semicircle_start2 - 5 * np.sin(angle)
            semicircle_points2.append([x, y, circle_center[2]])

        # Coordinates for the straight lines extending to the baseline
        left_line_start = [19, length - distance, 0] if loc == 'far' else [19, distance, 0]
        left_line_end = [19, baseline_y, 0]
        right_line_start = [width - 19, length - distance, 0] if loc == 'far' else [width - 19, distance, 0]
        right_line_end = [width - 19, baseline_y, 0]

        # Additional lines
        left_offset_line_start = [19 + left_offset, length - distance, 0] if loc == 'far' else [19 + left_offset, distance, 0]
        left_offset_line_end = [19 + left_offset, baseline_y, 0]
        right_offset_line_start = [width - 19 + right_offset, length - distance, 0] if loc == 'far' else [width - 19 + right_offset, distance, 0]
        right_offset_line_end = [width - 19 + right_offset, baseline_y, 0]

        # Combine coordinates into DataFrames
        free_throw_line_bounds = [line_start, line_end]
        free_throw_line_df = pd.DataFrame(free_throw_line_bounds, columns=['x', 'y', 'z'])
        free_throw_line_df['line_group'] = f'{loc}_free_throw_line'
        free_throw_line_df['color'] = 'court'

        circle_df = pd.DataFrame(circle_points, columns=['x', 'y', 'z'])
        circle_df['line_group'] = f'{loc}_free_throw_circle'
        circle_df['color'] = 'court'

        semicircle_df = pd.DataFrame(semicircle_points, columns=['x', 'y', 'z'])
        semicircle_df['line_group'] = f'free_throw_semicircle'
        semicircle_df['color'] = 'court'

        semicircle_df2 = pd.DataFrame(semicircle_points2, columns=['x', 'y', 'z'])
        semicircle_df2['line_group'] = f'free_throw_semicircle2'
        semicircle_df2['color'] = 'court'

        left_line_df = pd.DataFrame([left_line_start, left_line_end], columns=['x', 'y', 'z'])
        left_line_df['line_group'] = f'{loc}_free_throw_left_line'
        left_line_df['color'] = 'court'

        right_line_df = pd.DataFrame([right_line_start, right_line_end], columns=['x', 'y', 'z'])
        right_line_df['line_group'] = f'{loc}_free_throw_right_line'
        right_line_df['color'] = 'court'

        # Additional offset lines
        left_offset_line_df = pd.DataFrame([left_offset_line_start, left_offset_line_end], columns=['x', 'y', 'z'])
        left_offset_line_df['line_group'] = f'{loc}_free_throw_left_offset_line'
        left_offset_line_df['color'] = 'court'

        right_offset_line_df = pd.DataFrame([right_offset_line_start, right_offset_line_end], columns=['x', 'y', 'z'])
        right_offset_line_df['line_group'] = f'{loc}_free_throw_right_offset_line'
        right_offset_line_df['color'] = 'court'

        # Return combined DataFrame
        return pd.concat([
            free_throw_line_df, 
            circle_df, 
            semicircle_df2,
            semicircle_df, 
            left_line_df, 
            right_line_df, 
            left_offset_line_df, 
            right_offset_line_df
        ])



    

    def get_court_lines(self):
        '''
        Returns a concatenated DataFrame of all the court coordinates including the new free throw line.
        '''
        court_df = self.__get_court_perimeter_coordinates()
        half_df = self.__get_half_court_coordinates()
        backboard_home = self.__get_backboard_coordinates('near')
        backboard_away = self.__get_backboard_coordinates('far')
        hoop_away = self.__get_hoop_coordinates('near')
        hoop_home = self.__get_hoop_coordinates('far')
        three_home = self.__get_three_point_coordinates('near')
        three_away = self.__get_three_point_coordinates('far')
        free_throw_line = self.__get_free_throw_line_and_circle_coordinates('near')
        free_throw_line2 = self.__get_free_throw_line_and_circle_coordinates('far')  # Get free throw line coordinates

        court_lines_df = pd.concat([court_df, half_df, backboard_home, backboard_away, hoop_away, hoop_home, three_home, three_away, free_throw_line,free_throw_line2])

        return court_lines_df
