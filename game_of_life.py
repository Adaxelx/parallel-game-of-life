from tkinter import Tk, Canvas, Frame, BOTH
import numpy as np
from mpi4py import MPI
import sys
import math

from tkinter import *
import time

speed = 20
width = 600

board = np.array([[0,0,0,0,0,0,0, 0, 0, 0,0,0,0,0,0,0,0,0,0,0,0],
                  [0,0,0,0,0,0,0, 0, 0, 0,0,0,0,0,0,0,0,0,0,0,0],
                  [0,0,0,0,0,0,0, 0, 0, 0,0,0,0,0,0,0,0,0,0,0,0],
                  [0,0,0,0,0,0,0, 0, 0, 0,0,0,0,0,0,0,0,0,0,0,0],
                  [0,0,0,0,0,0,0, 0, 0, 0,0,0,0,0,0,0,0,0,0,0,0],
                  [0,0,0,0,0,0,0, 0, 0, 0,0,0,0,0,0,0,0,0,0,0,0],
                  [0,0,0,0,0,0,0, 1,1, 1,0,0,0,0,0,0,0,0,0,0,0],
                  [0,0,0,0,0,0,0, 1, 0, 1,0,0,0,0,0,0,0,0,0,0,0],
                  [0,0,0,0,0,0,0, 1, 1, 1,0,0,0,0,0,0,0,0,0,0,0],
                  [0,0,0,0,0,0,0, 1, 1, 1,0,0,0,0,0,0,0,0,0,0,0],
                  [0,0,0,0,0,0,0, 1, 1, 1,0,0,0,0,0,0,0,0,0,0,0],
                  [0,0,0,0,0,0,0, 1, 1, 1,0,0,0,0,0,0,0,0,0,0,0],
                  [0,0,0,0,0,0,0, 1, 0, 1,0,0,0,0,0,0,0,0,0,0,0],
                  [0,0,0,0,0,0,0, 1, 1, 1,0,0,0,0,0,0,0,0,0,0,0],
                  [0,0,0,0,0,0,0, 0, 0, 0,0,0,0,0,0,0,0,0,0,0,0],
                  [0,0,0,0,0,0,0, 0, 0, 0,0,0,0,0,0,0,0,0,0,0,0],
                  [0,0,0,0,0,0,0, 0, 0, 0,0,0,0,0,0,0,0,0,0,0,0],
                  [0,0,0,0,0,0,0, 0, 0, 0,0,0,0,0,0,0,0,0,0,0,0],
                  [0,0,0,0,0,0,0, 0, 0, 0,0,0,0,0,0,0,0,0,0,0,0],
                  [0,0,0,0,0,0,0, 0, 0, 0,0,0,0,0,0,0,0,0,0,0,0],
                  [0,0,0,0,0,0,0, 0, 0, 0,0,0,0,0,0,0,0,0,0,0,0],
                  ])

startArray = board
initArray = startArray
comm = MPI.COMM_WORLD
rank = comm.Get_rank()

def generatePartition(number, parts):
    res = [0] * parts
    qu = math.floor(number / parts)
    rm = number % parts
    for i in range(0, parts):
        res[i] = qu
        if(i < rm):
            res[i] += 1

    return res


def calculateNextState(surface, prevCell):
    sum = 0 - prevCell
    rows, cols = surface.shape
    for i in range(0, rows):
        for j in range(0, cols):
            sum += surface[i][j]
    newCell = prevCell
    if(sum == 3 and prevCell == 0):
        newCell = 1
    if(prevCell == 1):
        if(sum==2 or sum ==3):
            newCell = 1
        else:
            newCell = 0
    return newCell

def main():
    comm = MPI.COMM_WORLD
    id = comm.Get_rank()  # number of the process running the code
    numProcesses = comm.Get_size()  # total number of processes running
    myHostName = MPI.Get_processor_name()
    
    
    if rank == 0:
        root = Tk()
        siatka_y, siatka_x= initArray.shape
        rows, columns = initArray.shape
        
        window_size_x = width
        window_size_y = math.ceil(window_size_x*(rows/columns) + 20)

        size = math.ceil(window_size_x/columns)-1

        root.title('Game of life')
        root.geometry("" + str(window_size_x) + "x" + str(window_size_y + 20))
        j = Canvas(root, width=columns*size, height=rows*size)
        j.pack( 
            side='bottom'
        )

        for iy, ix in np.ndindex(initArray.shape):
            x = ix * size
            y = iy * size
            points = [x,y, x+size,y, x+size, y+size, x, y+size]
            j.create_polygon(points, outline='#CBE6FF', fill='#FFFFFF')


        global program_start, auto_iteration
        program_start= False
        auto_iteration = False

        def start_stop_iteration(button):
            print("test")
            global auto_iteration, program_start
            if(program_start == True):
                if(auto_iteration == False):
                    auto_iteration = True
                    button.config(text='Stop')
                else:
                    auto_iteration = False
                    button.config(text='Start')


        def restart():
            global initArray
            initArray = startArray


        button_auto = Button(
            root,
            text='Start'
        )

        button_auto.pack( 
            ipadx=5,
            ipady=10,
            expand=True,
            fill='both',
            side='left'
        )

        button_auto.config(
            command=lambda: start_stop_iteration(button_auto)
        )

        button_restart = Button(
            root,
            text='Restart'
        )

        button_restart.config(
            command=lambda: restart()
        )

        iter = 0

        partition = generatePartition(rows, numProcesses-1)

        while True:
            if(auto_iteration == True):
                for iy, ix in np.ndindex(initArray.shape):
                    x = ix * size
                    y = iy * size
                    points = [x,y, x+size,y, x+size, y+size, x, y+size]
                    if(initArray[iy, ix]):
                        j.create_polygon(points, outline='#CBE6FF', fill='#000000')
                    else:
                        j.create_polygon(points, outline='#CBE6FF', fill='#FFFFFF')
                prevIt = 0
                for i in range(1, numProcesses):
                    calculatedIndex = i-1
                    rowStart = prevIt
                    if(i!=1):
                        rowStart=rowStart-2
                    rowEnd = partition[calculatedIndex]+1 if i==1 else prevIt + partition[calculatedIndex]
                    if(i==numProcesses-1):
                        rowEnd=rowEnd-1
                    prevIt = rowEnd
                    comm.send((initArray[rowStart:rowEnd,
                            0:columns], iter), dest=i, tag=11)
                    print('Root send to', i, 'Iteration:', iter)


                iter += 1
                prevIt = 0
                for i in range(1, numProcesses):
                    req = comm.recv(source=i, tag=11)
                    data = req
                    rows, columns = data.shape
                    dataRowsStart = 0
                    dataRowsEnd = rows
                    if(i!=1):
                        dataRowsStart=1
                    if(i!=numProcesses-1):
                        dataRowsEnd=rows-1
                    initArray[prevIt:prevIt+partition[i-1],
                            0:columns] = data[dataRowsStart:dataRowsEnd, 0:columns]
                    prevIt=prevIt+partition[i-1]


            root.update_idletasks()
            root.update()
            time.sleep(0.1)
            program_start = True
    else:
        iter = 0
        while True:
            req = comm.recv(source=0, tag=11)
            if(iter == req[1]):
                iter += 1
                data = req[0]
                
                rows, columns = data.shape    
                finalData = np.copy(data)
                rows, columns = finalData.shape

                for i in range(0,rows):
                    for j in range(0,columns):
                        if rank != 1 and i==0 or rank!=numProcesses-1 and i==rows-1:
                            continue
                        prevCell = data[i,j]
                        rowStart,rowEnd = getNeighbours(i,rows)
                        columnStart,columnEnd = getNeighbours(j,columns)
                        finalData[i][j] = calculateNextState(data[rowStart:rowEnd,columnStart:columnEnd],data[i,j])
                print(i,'send to root. Iteration:', iter)
                comm.send(finalData, dest=0, tag=11)
        


def getNeighbours(index,border):
    return [index-1 if index!=0 else 0,index+2 if index!=border else border]


if __name__ == '__main__':
    main()


