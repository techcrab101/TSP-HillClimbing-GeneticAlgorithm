import math
import random
from Tkinter import*

def getCoordinates(file):
    '''takes the x y values in a txt file and returns the coordinates'''
    f = open(file, 'r')
    coordinates = []
    for line in iter(f):
        x,y = line.strip().split(',')
        coordinates.append((float(x), float(y)))
    return coordinates

def getDistances(coordinates):
    '''takes in a tuple f x,y coords and outputs a dictionary of the distances
    between any two cities in the list.'''
    distances = {}
    for i, (x, y) in enumerate(coordinates):
        for j, (x1, y1) in enumerate(coordinates):
            distances[i, j] = math.sqrt((x-x1)*(x-x1)+(y-y1)*(y-y1))
    return distances

def getPathDistance(coordinates, path, distances):
    '''takes in the coordinates of the cities and the path in which the salemen will
    follow and outputs the distance of the entire route. The path is a series of
    integers coresponding to the'''
    totalDistance = 0
    for i in range(len(path)-1):
        totalDistance += distances[path[i],path[i+1]]
    totalDistance += distances[path[-1], path[0]]
    return totalDistance

def drawCities(coordinates):
    '''draws the cities as dots in cartesian coordinates on the canvas'''
    for i, (x, y) in enumerate(coordinates):
        canvas.create_oval(x-5, y-5, x+5, y+5, width=0, fill='red')
        canvas.create_text(x,y,anchor=NW, text=str(i)+" ( "+str(x)+", "+str(y)+")")

def drawLines(coordinates, path, distances):
    '''draws the paths between the cities'''
    if (len(path)>2):
        for i in range(len(path)-1):
            canvas.create_line(coordinates[path[i]][0],coordinates[path[i]][1], coordinates[path[i+1]][0], coordinates[path[i+1]][1], width=1, fill='black')
            #canvas.create_text((coordinates[path[i]][0] + coordinates[path[i+1]][0])/2,(coordinates[path[i]][1] + coordinates[path[i+1]][1])/2, text = "distance: " + str(distances[(path[i],path[i+1])]))

        canvas.create_line(coordinates[path[-1]][0],coordinates[path[-1]][1], coordinates[path[0]][0], coordinates[path[0]][1], width=1, fill='black')
        #canvas.create_text((coordinates[path[-1]][0] + coordinates[path[0]][0])/2,(coordinates[path[-1]][1] + coordinates[path[0]][1])/2, text = "distance: " + str(distances[(path[0], path[-1])]))
    else:
        canvas.create_line(coordinates[path[0]][0],coordinates[path[0]][1], coordinates[path[1]][0], coordinates[path[1]][1], width=1, fill='black')
        #canvas.create_text((coordinates[path[0]][0] + coordinates[path[1]][0])/2,(coordinates[path[0]][1] + coordinates[path[1]][1])/2, text = "distance: " + str(distances[(path[0],path[1])]))

def generateRandomPath(coordinates):
    '''Takes in the coordinates and randomly generates a path.'''
    path = []
    for i in range(len(coordinates)):
        path.append(i)
    random.shuffle(path)
    return path

def createRandomPairs(size,shuffle=random.shuffle):
    x=range(size)
    y=range(size)
    shuffle(x)
    shuffle(y)
    for i in x:
        for j in y:
            yield (i,j)

def pathCombinations(path):
    for i,j in createRandomPairs(len(path)):
        if i < j:
            copy=path[:]
            copy[i],copy[j]=path[j],path[i]
            yield copy

def hillClimb (initial,  maxSteps):

    best = initial
    bestScore = getPathDistance(coordinates, best, distances)
    steps=1
    while steps < maxSteps:
        moveMade = False
        for next in pathCombinations(best):
            if steps >= maxSteps:
                break
            nextScore = getPathDistance(coordinates, next, distances)
            steps+=1
            if nextScore < bestScore:
                best = next
                bestScore = nextScore
                moveMade = True
                break

        if not moveMade:
            break

    return (steps, best, bestScore)

def individual():
    '''Creates an individual for the genetic Algorithm, The individual is just a path possiblity.'''
    return generateRandomPath(coordinates)

def getPopulation(count):
    '''Creates a list of individuals in a population'''
    return [individual() for x in range(count)]

def averageFitness(population):
    result = 0
    for x in range(len(population)):
        result += getPathDistance(coordinates,population[x],distances)
    return result / len(population)

def mutate(population):
    mutationProbability = 0.1
    for i in range(len(population)):
        if mutationProbability > random.random():
            city1 = random.randint(0,len(population[i])-1)
            city2 = random.randint(0,len(population[i])-1)
            temp = population[i][city1]
            population[i][city1] = population[i][city2]
            population[i][city2] = temp

def crossOver(parent1, parent2):
    '''Breeding is done by selecting a random range of parent1, and placing it into the empty child route (in the same place).
        Gaps are then filled in, without duplicates, in the order they appear in parent2. '''

    firstRange = random.randint(1, len(coordinates)-1)
    child = individual()
    for i in range(len(child)):
        child[i] = "#"

    for i in range(firstRange):
        child[i] = parent1[i]

    for i in range(len(parent2)):
        if not parent2[i] in child:
            for j in range(len(child)):
                if child[j] == "#":
                    child[j] = parent2[i]
                    break
    return child


def geneticAlgorithm(pop, maxSteps):
    print "GA start"
    population = pop
    popSize = len(population)
    steps = 1
    while steps < maxSteps:
        grade = averageFitness(population)
        print "population size: ", popSize," steps: ", steps, " end: ", maxSteps
        # kill off the ones with the least fitness (kill off the parents that are below average)
        i = 0
        while i < len(population):
            d = getPathDistance(coordinates, population[i], distances)
            if d > grade:
                population.remove(population[i])
            i+= 1
        # mutate existing
        mutate(population)
        # cross over parents to create children
        while len(population) < popSize:

            child = crossOver(population[random.randint(0,len(population)-1)],population[random.randint(0,len(population)-1)] )
            # append the children to the parent list
            population.append(child)
        steps += 1
    return (steps, grade, population[random.randint(0,len(population)-1)])


coordinates = getCoordinates('C:\Users\Terry\Documents\TravelingSalesmen\py\coordinates.txt')
path = generateRandomPath(coordinates)
distances = getDistances(coordinates)
pathDistances = getPathDistance(coordinates, path, distances)

evaluationLimitHC = 5000
evaluationLimitGA = 5000
pop = getPopulation(5)

root = Tk()
root.wm_title("TravelingSalesmenProblem")
root.config(background="#333333")

leftFrame = Frame(root, width=200, height=600)
leftFrame.grid(row=1, column=0, padx=10, pady=2)

leftUFrame = Frame(root, width=200, height=600)
leftUFrame.grid(row=0, column=0, padx=10, pady=2)

Label(leftUFrame, text="Coordinates:").grid(row=0, column=0, padx=10, pady=2)
x = 0
y = 0
for i in range(len(coordinates)):
    if x % 5 == 0:
        y += 1
        x = 0
    coordLabel = Label(leftUFrame, text=str(i) + " " + str(coordinates[i]))
    coordLabel.grid(row=y+1, column=x, padx=10, pady=2)
    x += 1

Label(leftFrame, text="Path:").grid(row=0, column=0, padx=10, pady=2)
pathLabel = Label(leftFrame, text=path)
pathLabel.grid(row=1, column=0, padx=10, pady=2)

Label(leftFrame, text="totalDistance:").grid(row=2, column=0, padx=10, pady=2)
tdLabel = Label(leftFrame, text=pathDistances)
tdLabel.grid(row=3, column=0, padx=10, pady=2)

Label(leftFrame, text="Iterations:").grid(row=4, column=0, padx=10, pady=2)
evaluationsLabel = Label(leftFrame, text=0)
evaluationsLabel.grid(row=5, column=0, padx=10, pady=2)

rightFrame = Frame(root, width=500, height=500)
rightFrame.grid(row=0, column=1, rowspan=2, padx=10, pady=2)

btnFrame = Frame(rightFrame, width=200, height=200)
btnFrame.grid(row=1, column=0, padx=10, pady=2)

canvas = Canvas(rightFrame, width=500, height=500, bg='white')
canvas.grid(row=0, column=0, padx=10, pady=2)

def randBtnPress ():
    path = generateRandomPath(coordinates)
    updateCanvas(path)

def hillBtnPress ():
    x = hillClimb(path, evaluationLimitHC)
    xpath = x[1]
    xEvaluations = x[0]
    evaluationsLabel = Label(leftFrame, text=xEvaluations)
    evaluationsLabel.grid(row=5, column=0, padx=10, pady=2)
    updateCanvas(xpath)

def gABtnPress ():
    gA = geneticAlgorithm(pop, evaluationLimitGA)
    gpath = gA[2]
    gEvaluations = gA[0]
    evaluationsLabel = Label(leftFrame, text=gEvaluations)
    evaluationsLabel.grid(row=5, column=0, padx=10, pady=2)
    pathLabel = Label(leftFrame, text=gpath)
    pathLabel.grid(row=1, column=0, padx=10, pady=2)
    updateCanvas(gpath)

def updateCanvas(xpath):
    canvas.delete("all")
    pathDistances = getPathDistance(coordinates, xpath, distances)
    drawCities(coordinates)
    drawLines(coordinates,xpath, distances)
    pathLabel = Label(leftFrame, text=xpath)
    pathLabel.grid(row=1, column=0, padx=10, pady=2)
    tdLabel = Label(leftFrame, text=pathDistances)
    tdLabel.grid(row=3, column=0, padx=10, pady=2)

hCBtn = Button(btnFrame, text="Hill Climbing Algorithm", command=hillBtnPress)
hCBtn.grid(row=0, column=1, padx=10, pady=2)

gABtn = Button(btnFrame, text="Genetic Algorithm", command=gABtnPress)
gABtn.grid(row=0, column=2, padx=10, pady=2)

rBtn = Button(btnFrame, text="random path", command=randBtnPress)
rBtn.grid(row=0, column=0, padx=10, pady=2)

HillClimbEntryFrame = Frame(btnFrame, width=200, height=600)
HillClimbEntryFrame.grid(row=1, column=1, padx=10, pady=2)

gAEntryFrame = Frame(btnFrame, width=200, height=600)
gAEntryFrame.grid(row=1, column=2, padx=10, pady=2)

Label(HillClimbEntryFrame, text="Evaluation Limit:").grid(row=0, column=0, padx=3, pady=2)
hillVarEvalLimitLabel = Label(HillClimbEntryFrame, text=evaluationLimitHC)
hillVarEvalLimitLabel.grid(row=0, column=1, padx=1, pady=2)

Label(gAEntryFrame, text="Evaluations:").grid(row=0, column=0, padx=3, pady=2)
gAVarEvalLimitLabel = Label(gAEntryFrame, text=evaluationLimitGA)
gAVarEvalLimitLabel.grid(row=0, column=1, padx=1, pady=2)

Label(gAEntryFrame, text="Population").grid(row=1, column=0, padx=3, pady=2)
gAPopLabel = Label(gAEntryFrame, text=len(pop))
gAPopLabel.grid(row=1, column=1, padx=1, pady=2)

HillEvalLimit = Entry(HillClimbEntryFrame)
HillEvalLimit.grid(row=0, column=2, padx=3, pady=2)

gAEvalLimit = Entry(gAEntryFrame)
gAEvalLimit.grid(row=0, column=2, padx=3, pady=2)

gAPop = Entry(gAEntryFrame)
gAPop.grid(row=1, column=2, padx=3, pady=2)

def EvalLimitEntry ():
    global evaluationLimitHC
    s = HillEvalLimit.get()
    try:
        evaluationLimitHC = int(s)
        hillVarEvalLimitLabel = Label(HillClimbEntryFrame, text=evaluationLimitHC)
        hillVarEvalLimitLabel.grid(row=0, column=1, padx=1, pady=2)
    except:
        print 'enter an int'

def EvalEntry ():
    global evaluationLimitGA
    s = gAEvalLimit.get()
    try:
        evaluationLimitGA = int(s)
        gAVarEvalLimitLabel = Label(gAEntryFrame, text=evaluationLimitGA)
        gAVarEvalLimitLabel.grid(row=0, column=1, padx=1, pady=2)
    except:
        print 'enter an int'

def popEntry ():
    global pop
    s = gAPop.get()
    try:
        pop = getPopulation(int(s))
        gAPopLabel = Label(gAEntryFrame, text=len(pop))
        gAPopLabel.grid(row=1, column=1, padx=1, pady=2)
    except:
        print 'enter an int'

EvalLimitBtn = Button(HillClimbEntryFrame, text="Enter", command=EvalLimitEntry)
EvalLimitBtn.grid(row=0, column=3, padx=10, pady=2)

gALimitBtn = Button(gAEntryFrame, text="Enter", command=EvalEntry)
gALimitBtn.grid(row=0, column=3, padx=10, pady=2)

gAPopBtn = Button(gAEntryFrame, text="Enter", command=popEntry)
gAPopBtn.grid(row=1, column=3, padx=10, pady=2)


drawCities(coordinates)
drawLines(coordinates, path, distances)

root.mainloop()
