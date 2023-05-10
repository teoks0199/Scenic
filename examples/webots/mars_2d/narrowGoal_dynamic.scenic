
# Dynamic version of the narrowGoal scenario.

model model

ego = new Rover at 0 @ -2, with controller 'sojourner'

goal = new Goal at Range(-2, 2) @ Range(2, 2.5)

terminate when (distance to goal) <= 0.2

monitor terminateOnT():
    keyboard = simulation().supervisor.getKeyboard()
    keyboard.enable(20)
    print('Select the 3D window and press T to terminate the scenario and generate a new one.')
    time = 0
    while True:
    	if time%50 == 0:
	        print(f"Ego Current Position: {ego.position}")
	        print(f"Ego Current Elevation: {ego.elevation}")
        time+=1
        wait
        if keyboard.getKey() == ord('T'):
            terminate

require monitor terminateOnT()

# Bottleneck made of two pipes with a rock in between

gap = 1.2 * ego.width
halfGap = gap / 2

bottleneck = new OrientedPoint offset by Range(-1.5, 1.5) @ Range(0.5, 1.5), facing Range(-30, 30) deg

require abs((angle to goal) - (angle to bottleneck)) <= 10 deg

new BigRock at bottleneck

leftEdge = new OrientedPoint left of bottleneck by halfGap,
    facing Range(60, 120) deg relative to bottleneck.heading
rightEdge = new OrientedPoint right of bottleneck by halfGap,
    facing Range(-120, -60) deg relative to bottleneck.heading

new Pipe ahead of leftEdge, with length Range(1, 2)
new Pipe ahead of rightEdge, with length Range(1, 2)

# Other junk because why not?

new Pipe
new BigRock beyond bottleneck by Range(-0.5, 0.5) @ Range(0.5, 1)
new BigRock beyond bottleneck by Range(-0.5, 0.5) @ Range(0.5, 1)
new Rock
new Rock
new Rock with elevation 4