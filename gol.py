# Python code to implement Conway's Game Of Life 
import argparse 
import numpy as np 
import matplotlib.pyplot as plt  
import matplotlib.animation as animation 
  
# setting up the values for the grid 
ON = 255
OFF = 0
RECOVER = 200 
DEAD = 100 
vals = [ON, OFF] 
FRAMES = 200
LIFETIME = float(FRAMES)
GSIZE = 7 
RateOfSpread = 3/8.0
SPEED = 5 

daysInfected =  np.zeros((GSIZE, GSIZE))

potential = np.random.choice([True, False], GSIZE*GSIZE, p=[0.97,
    0.03]).reshape(GSIZE, GSIZE) 

immune = np.random.choice([True, False], GSIZE*GSIZE, p=[0.05,
    0.95]).reshape(GSIZE, GSIZE) 

Writer = animation.writers['ffmpeg']
writer = Writer(fps=SPEED, metadata=dict(artist='Me'), bitrate=9600)

def randomGrid(N): 
  
    """returns a grid of NxN random values"""
    #return np.random.choice(vals, N*N, p=[0.001, 0.999]).reshape(N, N) 
    
    # Or, create patient zero somewhere in the array
#    arr[int(N/2)][int(N/2)] = ON 
    arr = np.zeros(shape=(N, N))
    arr[1][1] = ON 
    return arr


def infect(p, current):
    infection = np.random.random()
    if infection > (1-p) and current not in [RECOVER, DEAD]:
        return ON 
    return OFF

def recover(p, current):
    recover = np.random.random()
    if recover > (1-p) and current not in [OFF, RECOVER, DEAD,]:
        return RECOVER 
    return current 

def die(p, current):
    die = np.random.random()
    if die > (1-p) and current == ON:
        return DEAD  
    return current 

def spread(p, current, idx ):
    val = current
    i,j = idx

    if immune[i,j]:
        return OFF
    if current == OFF:
        val = infect(p, current)
        return val
    return val

def update(frameNum, img, grid, N): 
  
    # copy grid since we require 8 neighbors  
    # for calculation and we go line by line  
    newGrid = grid.copy()

    if frameNum < 1:
        return
    
    for i in range(N): 
        for j in range(N): 
  
            # Randomly infect neighbours
            if grid[i,j] == ON:
                daysInfected[i,j] += 1

            if grid[i, j] == ON and daysInfected[i,j] > 20 and potential[i,j]: 
                newGrid[i, j] = recover(0.8, grid[i, j])

            # Only die if infected for a long time and no potential to recover
            if grid[i, j] == ON and daysInfected[i,j] > 20 and not potential[i, j]: 
                newGrid[i, j] = die(.03, grid[i, j])

            if grid[i, j] == ON: 
                
                # Prevent overflow
                if j - 1 < 0 or i - 1 < 0:
                    continue

                newGrid[i, (j-1)%N] = spread(RateOfSpread, 
                        newGrid[i, (j-1)%N], [i, (j-1)%N])
                newGrid[i, (j+1)%N] = spread(RateOfSpread, 
                        newGrid[i, (j+1)%N], [i, (j+1)%N])
                newGrid[(i-1)%N, j] = spread(RateOfSpread, 
                        newGrid[(i-1)%N, j], [(i-1)%N, j])
                newGrid[(i+1)%N, j] = spread(RateOfSpread, 
                        newGrid[(i+1)%N, j], [(i+1)%N, j])
                newGrid[(i-1)%N, (j-1)%N] = spread(RateOfSpread, 
                        newGrid[(i-1)%N, (j-1)%N], [(i-1)%N, (j-1)%N])
                newGrid[(i-1)%N, (j+1)%N] = spread(RateOfSpread, 
                        newGrid[(i-1)%N, (j+1)%N], [(i-1)%N, (j+1)%N])
                newGrid[(i+1)%N, (j-1)%N] = spread(RateOfSpread, 
                        newGrid[(i+1)%N, (j-1)%N], [(i+1)%N, (j-1)%N])
                newGrid[(i+1)%N, (j+1)%N] = spread(RateOfSpread, 
                        newGrid[(i+1)%N, (j+1)%N], [(i+1)%N, (j+1)%N])
  
    # update data 
    img.set_data(newGrid) 
    grid[:] = newGrid[:] 
    return img, 
  
# main() function 
def main(): 
  
    # Command line args are in sys.argv[1], sys.argv[2] .. 
    # sys.argv[0] is the script name itself and can be ignored 
    # parse arguments 
    parser = argparse.ArgumentParser(description="Runs Conway's Game of Life simulation.") 
  
    # add arguments 
    parser.add_argument('--grid-size', dest='N', required=False) 
    parser.add_argument('--mov-file', dest='movfile', required=False) 
    parser.add_argument('--interval', dest='interval', required=False) 
    args = parser.parse_args() 

    # set grid size 
    
    N = GSIZE
    if args.N and int(args.N) > 8: 
        N = int(args.N) 
          
    # set animation update interval 
    updateInterval = 1050
    if args.interval: 
        updateInterval = int(args.interval) 
  
    # declare grid 
    grid = np.array([]) 
  
    # populate grid with random on/off - 
    # more off than on 
    grid = randomGrid(N) 
  
    # set up animation 
    fig, ax = plt.subplots() 
    img = ax.imshow(grid, interpolation='nearest') 
    # set output file 
    ani = animation.FuncAnimation(fig, update, fargs=(img, grid, N, ), 
                                  frames = FRAMES, 
                                  interval=updateInterval, 
                                  save_count=1) 
    
    # # of frames?  
    if args.movfile: 
        ani.save(args.movfile, writer=writer) 
  
    plt.show() 
  
# call main 
if __name__ == '__main__': 
    main() 
