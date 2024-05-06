'''
To run this file:
    scenic examples/driving/car.scenic --2d --model scenic.simulators.carla.model --simulate
'''

param map = localPath('../../assets/maps/CARLA/Town01.xodr')

model scenic.domains.driving.model

ego = new Car