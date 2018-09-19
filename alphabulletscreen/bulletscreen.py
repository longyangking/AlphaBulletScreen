import numpy as np 
import copy
import time

class Point:
    def __init__(self, position, velocity, bounds, r0=0.2):
        self.position = position
        self.velocity = velocity
        self.bounds = bounds
        self.r0 = r0

    def update_position(self, diff_position):
        self.position = self.position + diff_position

    def update(self, dt):
        self.position += self.velocity*dt
        return not self.is_dead()

    def get_position(self):
        return np.copy(self.position)

    def get_velocity(self):
        return self.velocity

    def is_dead(self):
        x_min, x_max, y_min, y_max = self.bounds
        x, y = self.position
        if (x < x_min) or (x > x_max) or (y < y_min) or (y > y_max):
            return True
        return False

    def touch(self, target_point):
        x, y = target_point.get_position()
        x0, y0 = self.position
        if (x-x0)**2 + (y-y0)**2 < self.r0**2:
            return True
        return False

class PointCrowd:
    def __init__(self, n_points, target_point, bounds, velocity_max):
        self.points = list()

        self.n_points = n_points
        self.target_point = target_point
        self.bounds = bounds
        self.velocity_max = velocity_max

        target_position = target_point.get_position()

        # bounds: [x_min, x_max, y_min, y_max]
        x_min, x_max, y_min, y_max = bounds
        latent_positions = np.zeros((4*n_points,2))
        latent_positions[:n_points,0] = x_min
        latent_positions[:n_points,1] = np.random.random(n_points)*(y_max - y_min) + y_min
        latent_positions[n_points:2*n_points,0] = x_max
        latent_positions[n_points:2*n_points,1] = np.random.random(n_points)*(y_max - y_min) + y_min
        latent_positions[2*n_points:3*n_points,0] = np.random.random(n_points)*(x_max - x_min) + x_min
        latent_positions[2*n_points:3*n_points,1] = y_min
        latent_positions[3*n_points:,0] = np.random.random(n_points)*(x_max - x_min) + x_min
        latent_positions[3*n_points:,1] = y_max

        list_latent_positions = range(4*n_points)
        for i in range(n_points):
            index = np.random.choice(list_latent_positions)
            position = latent_positions[index]
            direction = target_position - position
            direction = direction/np.sqrt(direction.dot(direction))
            velocity = velocity_max*np.random.random()*direction
            point = Point(position=position, velocity=velocity, bounds=bounds)
            self.points.append(point)

    def update(self, dt):
        n_lives = 0
        n_points = len(self.points)
        for i in range(n_points):
            if self.points[i].update(dt):
                n_lives += 1
        return n_lives

    def get_positions(self):
        n_points = len(self.points)
        positions = np.zeros((n_points, 2))
        for i in range(n_points):
            positions[i] = self.points[i].get_position()
        return positions

    def touch(self, target_point):
        n_points = len(self.points)
        for i in range(n_points):
            flag = self.points[i].touch(target_point)
            if flag:
                return True
        return False

class GameEngine:
    def __init__(self, n_points, bounds, velocity_max, dt, 
        target_position, target_speed, n_grid,
        n_crowds=3, timestep_intervals=10,
        verbose=False
        ):

        self.n_points = n_points
        self.bounds = bounds
        self.velocity_max = velocity_max

        self.dt = dt
        self.target_position = target_position
        self.target_speed = target_speed

        self.target_point = Point(
            position=self.target_position,
            velocity=[0,0],
            bounds=None
        )

        self.pointcrowds = list()
        self.n_crowds = n_crowds
        self.timestep_intervals = timestep_intervals
        self.last_emit_timestep = 0

        self.n_grid = n_grid
        self.score = 0
        self.verbose = verbose

    def get_area(self):
        n_grid = self.n_grid
        area = np.zeros((n_grid, n_grid))
        x_min, x_max, y_min, y_max = self.bounds

        n_crowds = len(self.pointcrowds)
        for i in range(n_crowds):
            positions = self.pointcrowds[i].get_positions()
            for k in range(len(positions)):
                x, y = positions[k]
                m, n = int((x-x_min)/(x_max-x_min)*(n_grid-1)), int((y-y_min)/(y_max-y_min)*(n_grid-1)) 
                if (m>=0) and (m<n_grid) and (n>=0) and (n<n_grid):
                    area[m, n] = -1

        x, y = self.target_point.get_position()
        m, n = int((x-x_min)/(x_max-x_min)*(n_grid-1)), int((y-y_min)/(y_max-y_min)*(n_grid-1)) 
        area[m, n] = 1

        return area

    def init(self):
        self.last_emit_timestep = 0
        self.emit_points()

    def emit_points(self):
        pointcrowd = PointCrowd(
            n_points=self.n_points, 
            target_point=self.target_point, 
            bounds=self.bounds, 
            velocity_max=self.velocity_max
        )
        self.pointcrowds.append(pointcrowd)

        if self.verbose:
            print("Emitting new point crowd and current number of crowd is [{0}]".format(len(self.pointcrowds))) 

    def play(self, control_code=[1,0,0,0,0]):
        # Control Code:
        #   [1, 0, 0, 0, 0]: stay
        #   [0, 1, 0, 0, 0]: left
        #   [0, 0, 1, 0, 0]: right
        #   [0, 0, 0, 1, 0]: up
        #   [0, 0, 0, 0, 1]: down
        s_stay, s_left, s_right, s_up, s_down = control_code
        if s_stay:
            direction = np.array([0,0])
        if s_left:
            direction = np.array([1,0])
        if s_right:
            direction = np.array([-1,0])
        if s_up:
            direction = np.array([0,1])
        if s_down:
            direction = np.array([0,-1])

        diff_position = self.target_speed*self.dt*direction
        self.target_point.update_position(diff_position)
        flag = self.update()

        return flag

    def update(self):
        n_crowds = len(self.pointcrowds)
        lives = np.zeros(n_crowds)
        flag = False
        # Update point cowrds and Check collision
        for i in range(n_crowds):
            lives[i] = self.pointcrowds[i].update(self.dt)
            if (self.pointcrowds[i].touch(self.target_point)):
                flag = True

        # Remove points crowd
        pointcrowds = list()
        for i in range(n_crowds):
            if lives[i] >= 1:
                pointcrowds.append(self.pointcrowds[i])
        self.pointcrowds = pointcrowds

        # Emit points
        if (len(self.pointcrowds) < self.n_crowds) and (self.last_emit_timestep >= self.timestep_intervals):
            
            self.emit_points()
            self.last_emit_timestep = 0
        self.last_emit_timestep += 1

        if not flag:
            self.score += 1

        # if self.verbose:
        #     count = np.sum(lives)
        #     print("The number of living pointcrowd is [{0}]".format(count))

        return flag

    def get_score(self):
        return self.score

class BulletScreen:
    '''
    Bullet Screen Game for Human
    '''
    def __init__(self, state_shape, ai=None, verbose=False):
        n_points=10
        bounds = [-5, 5, -5, 5] # bounds: [x_min, x_max, y_min, y_max]
        velocity_max = 2.0
        dt = 0.1
        target_position = np.array([0,0]) 
        target_speed = 2.0
        n_crowds=3
        timestep_intervals=10

        self.state_shape = state_shape
        self.n_grid = state_shape[0]
        self.ai = ai

        self.verbose = verbose
        self.dt = dt

        self.gameengine = GameEngine(
            n_points=n_points, 
            bounds=bounds, 
            velocity_max=velocity_max, 
            dt=dt, 
            target_position=target_position, 
            target_speed=target_speed,
            n_crowds=n_crowds, 
            n_grid=self.n_grid,
            timestep_intervals=timestep_intervals,
            verbose=self.verbose
        )

    def pressaction(self, code):
        # Control Code:
        #   [1, 0, 0, 0, 0]: stay
        #   [0, 1, 0, 0, 0]: left
        #   [0, 0, 1, 0, 0]: right
        #   [0, 0, 0, 1, 0]: up
        #   [0, 0, 0, 0, 1]: down
        control_code = np.zeros(5)
        control_code[code] = 1
        self.gameengine.play(control_code=control_code)

    def start(self):
        from ui import UI

        self.gameengine.init()

        #n_grid = self.n_grid
        sizeunit = 20
        area = self.gameengine.get_area()
        ui = UI(pressaction=self.pressaction, area=area, sizeunit=sizeunit)

        #ui.setDaemon(True)
        ui.start()

        # for i in range(20):
        #     self.gameengine.update()
        # ui.setarea(area=self.gameengine.get_area(n_grid))

        if self.verbose:
            count = 0
        
        while not self.gameengine.update():
            if self.verbose:
                count += 1

            time.sleep(self.dt)
            ui.setarea(area=self.gameengine.get_area())
        
        ui.gameend(self.gameengine.get_score())

        if self.verbose:
            print("Game end with steps [{0}] and score [{1}].".format(count, self.gameengine.get_score()))

    def start_ai(self):
        pass

        # TODO Play game by AI