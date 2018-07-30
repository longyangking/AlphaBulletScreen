import numpy as np 
import copy

class Point:
    def __init__(self, position, velocity, bounds, r0=0.1):
        self.position = position
        self.velocity = velocity
        self.bounds = bounds

    def update_position(self, diff_position):
        self.position += diff_position

    def update(self, dt):
        self.position += self.velocity*dt
        return self.is_dead()

    def get_position(self):
        return self.position

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
        if (x-x0)**2 + (y-y0)**2 < r0**2:
            return True
        return False

class PointCrowd:
    def __init__(self, n_points, target_point, bounds, velocity_max):
        self.points = list()
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

        for i in range(n_points):
            position = np.random.choice(latent_positions)
            direction = target_position - position
            direction = direction/np.sqrt(direction.dot(direction))
            velocity = velocity_max*np.random.random()*direction
            point = Point(position=position, velocity=velocity, bounds=bounds)
            self.points.append(point)

    def update(self, dt):
        n_lives = 0
        for i in range(n_points):
            if self.points[i].update(dt):
                n_lives += 1
        return n_lives

    def get_positions(self):
        positions = np.zeros((n_points, 2))
        for i in range(n_points):
            positions[i] = self.points[i].get_position()
        return positions

    def touch(self, target_point):
        for i in range(n_points):
            flag = self.points[i].touch(target_point)
            if flag:
                return True
        return False

class GameEngine:
    def __init__(self, n_points, bounds, velocity_max, dt, 
        target_position, target_speed,
        n_crowds=3, timestep_intervals=10,
        is_selfplay=False, is_computer=False
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

    def clone(self):
        pass

    def get_state(self):
        pass 

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

        # Emit points
        if (len(self.pointcrowds) < self.n_crowds) and (last_emit_timestep >= self.timestep_intervals):
            self.emit_points()
        last_emit_timestep += 1

        # Remove points crowd
        pointcrowds = list()
        for i in range(n_crowds):
            if lives[i] >= 1:
                pointcrowds.append(self.pointcrowds[i])
        self.pointcrowds = pointcrowds

        return flag

class BulletScreen:
    '''
    Bullet Screen Game for Human
    '''
    def __init__(self):
        n_points=10
        bounds = [0, 10, 0, 10] # bounds: [x_min, x_max, y_min, y_max]
        velocity_max = 0.5 
        dt = 0.1 
        target_position = np.array([0,0]) 
        target_speed = 0.1
        n_crowds=3
        timestep_intervals=10

        self.gameengine = GameEngine(
            n_points=n_points, 
            bounds=bounds, 
            velocity_max=velocity_max, 
            dt=dt, 
            target_position=target_position, 
            target_speed=target_speed,
            n_crowds=n_crowds, 
            timestep_intervals=timestep_intervals
        )

    def start(self):
        from ui import UI

        self.gameengine.init()

        sizeunit = 30
        area = self.gameengine.getarea()
        ui = UI(pressaction=self.player.setdirection, area=area, sizeunit=sizeunit)
        ui.start()
        
        while self.gameengine.update():
            ui.setarea(area=self.gameengine.getarea())

        ui.gameend(self.gameengine.getscore())

if __name__=='__main__':
    # Just for debugging
    bulletscreen = BulletScreen()
    bulletscreen.start()