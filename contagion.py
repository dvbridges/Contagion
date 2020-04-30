import argparse 
import numpy as np 
from matplotlib import colors
import matplotlib.pyplot as plt  
import matplotlib.animation as animation 
  
# setting up the values for the grid 
ON = 50
OFF = 0
RECOVER = 100 
DEAD = 150 
vals = [ON, OFF] 
FRAMES = 200
LIFETIME = float(FRAMES)
GSIZE = 100 
RateOfSpread = 3/8.0
MOVIE_SPEED = 5 

# create a very simple color palette
red = np.array([48, 255, 252, 127]) / 256.
green = np.array([41, 140, 250, 127]) / 256.
blue = np.array([40, 0, 104, 127]) / 256.
cols = np.array([red, green, blue]).T

bounds = np.arange(0,150,4)
cm = colors.ListedColormap(cols)
norm = colors.BoundaryNorm(bounds, cm.N)

daysInfected =  np.zeros(
        (GSIZE, GSIZE))
potential = np.random.choice(
        [True, False], 
        GSIZE*GSIZE, 
        p=[0.97, 0.03]).reshape(GSIZE, GSIZE) 
immune = np.random.choice(
        [True, False], 
        GSIZE*GSIZE, 
        p=[0.01, 0.99]).reshape(GSIZE, GSIZE) 

Writer = animation.writers['ffmpeg']
writer = Writer(fps=MOVIE_SPEED, metadata=dict(artist='Me'), bitrate=9600)

def randomGrid(N): 
  
    """returns a grid of NxN random values"""
    #return np.random.choice(vals, N*N, p=[0.001, 0.999]).reshape(N, N) 
    
    # Or, create patient zero somewhere in the array
    arr = np.zeros(shape=(N, N))
    arr[1][1] = ON 
    return arr


def infect(p, current):
    infection = np.random.random()
    if infection > (1-p) and current == OFF:
        return ON 
    return OFF

def recover(p, current):
    recover = np.random.random()
    if recover > (1-p) and current == ON:
        return RECOVER 
    return current 

def die(p, current):
    die = np.random.random()
    if die > (1-p) and current == ON:
        return DEAD  
    return current 

def spread(p, current, idx):
    i,j = idx

    if immune[i,j]:
        return OFF
    if current == OFF:
        return infect(p, current)
    return current 

def update(frameNum, img, grid, N): 
  
    # copy grid since we require 8 neighbors  
    newGrid = grid.copy()

    if frameNum < 1:
        return
    
    for i in range(N): 
        for j in range(N): 
            
            # Count days infected
            if grid[i,j] == ON:
                daysInfected[i,j] += 1
            
            # Check if possible to recover
            if grid[i, j] == ON and daysInfected[i,j] > 40 and potential[i,j]: 
                newGrid[i, j] = recover(0.8, grid[i, j])

            # Die if infected for a long time and no potential to recover
            if grid[i, j] == ON and daysInfected[i,j] > 40 and not potential[i, j]: 
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
    # parse arguments 
    parser = argparse.ArgumentParser(description="Runs Conway's Game of Life simulation.") 
  
    # add arguments 
    parser.add_argument('--mov-file', dest='movfile', required=False) 
    parser.add_argument('--interval', dest='interval', required=False) 
    args = parser.parse_args() 

    # set animation update interval 
    updateInterval = 100
    if args.interval: 
        updateInterval = int(args.interval) 
  
    # declare grid 
    grid = np.array([]) 
  
    # populate grid 
    grid = randomGrid(GSIZE) 
  
    # set up animation 
    fig, ax = plt.subplots() 
    img = ax.imshow(grid, interpolation='nearest', cmap=cm, norm=norm) 
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    ax.set_xticks([])
    ax.set_yticks([])
    # set output file 
    ani = animation.FuncAnimation(fig, update, fargs=(img, grid, GSIZE, ), 
                                  frames = FRAMES, 
                                  interval=updateInterval, 
                                  save_count=1) 
    
    # Save movie?  
    if args.movfile: 
        ani.save(args.movfile, writer=writer) 
    else: 
        plt.show() 
  
# call main 
if __name__ == '__main__': 
    main() 
