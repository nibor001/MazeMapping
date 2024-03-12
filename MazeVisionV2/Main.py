import socket
import matplotlib.pyplot as plt
import numpy as np
import time
import threading


PORT = 4498
MY_ADDR = "192.168.172.121" #ip computer
buff_size = 1024
instruction_list = []
def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((MY_ADDR, PORT))
    server_socket.listen(1)
    print(f"Server listening on {MY_ADDR}:{PORT}")
    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Accepted connection from {client_address}")

        data = client_socket.recv(buff_size).decode('utf-8')

        if data != "Connection between esp32 closed":
            print(f"Received message: {data}")
            instruction, digits = data.split(',')
            digit_list = list(digits)
            instruction_list.append([instruction] + digit_list)
            print(instruction_list)
            client_socket.close()
        else:
            print(f"Received message: {data}")
            instruction_list.append([data])
            client_socket.close()
            break

def decide_walls(facing,direction,front,left,right,back):
    if facing == "forward":
        if direction[1] == "1":
            front = True
        if direction[2] == "1":
            left = True
        if direction[3] == "1":
            right = True
        if direction[4] == "1":
            back = True
    elif facing == "right":
        if direction[1] == "1":
            right = True
        if direction[2] == "1":
            front = True
        if direction[3] == "1":
            back = True
        if direction[4] == "1":
            left = True
    elif facing == "left":
        if direction[1] == "1":
            left = True
        if direction[2] == "1":
            back = True
        if direction[3] == "1":
            front = True
        if direction[4] == "1":
            right = True
    elif facing == "back":
        if direction[1] == "1":
            front = True
        if direction[2] == "1":
            left = True
        if direction[3] == "1":
            right = True
        if direction[4] == "1":
            back = True
    return front,left,right,back
def mazeGrid(current_x, current_y, colored_grid, facing):
    if instruction_list:
        direction = instruction_list.pop()
    else:
        direction = ["k","k","k","k","k"]
    changed = False
    while direction[0] != "Connection between esp32 closed":
        #for direction in instruction_list:
        if direction[0] == "found":
            colored_grid.color_coordinate(current_x, current_y, 'green', front, left, right, back)
            colored_grid.draw_grid()
            break
        front=left=right=back = False
        if facing == "forward":
            if direction[1] == "1":
                front = True
            if direction[2] == "1":
                left = True
            if direction[3] == "1":
                right = True
            if direction[4] == "1":
                back = True
            if direction[0] == "forward":
                current_y += 1
                changed = True
            elif direction[0] == "left":
                current_x -= 1
                facing = "left"
                changed = True
            elif direction[0] == "right":
                current_x += 1
                facing = "right"
                changed = True
            elif direction[0] == "back":
                current_y -= 1
                facing = "back"
                changed = True
        elif facing == "right":
            if direction[1] == "1":
                right = True
            if direction[2] == "1":
                front = True
            if direction[3] == "1":
                back = True
            if direction[4] == "1":
                left = True
            if direction[0] == "forward":
                current_x += 1
                changed = True
            elif direction[0] == "left":
                current_y += 1
                changed = True
                facing = "forward"
            elif direction[0] == "right":
                current_y -= 1
                facing = "back"
                changed = True
            elif direction[0] == "back":
                current_x -= 1
                facing = "left"
                changed = True
        elif facing == "left":
            if direction[1] == "1":
                right = True
            if direction[2] == "1":
                front = True
            if direction[3] == "1":
                back = True
            if direction[4] == "1":
                left = True
            if direction[0] == "forward":
                current_x -= 1
                changed = True
            elif direction[0] == "left":
                current_y -= 1
                facing = "back"
                changed = True
            elif direction[0] == "right":
                current_y += 1
                facing = "forward"
                changed = True
            elif direction[0] == "back":
                current_x += 1
                facing = "right"
                changed = True
        elif facing == "back":
            if direction[1] == "1":
                front = True
            if direction[2] == "1":
                left = True
            if direction[3] == "1":
                right = True
            if direction[4] == "1":
                back = True
            if direction[0] == "forward":
                current_y -= 1
                changed = True
            elif direction[0] == "left":
                current_x += 1
                facing = "right"
                changed = True
            elif direction[0] == "right":
                current_x -= 1
                facing = "left"
                changed = True
            elif direction[0] == "back":
                current_y += 1
                facing = "forward"
                changed = True
        #print(current_x)
        #print(current_y)
        if changed:
            front=left=right=back = False
            front,left,right,back = decide_walls(facing,direction,front,left,right,back)
            colored_grid.color_coordinate(current_x, current_y, 'blue',front,left,right,back)
            colored_grid.draw_grid()
            changed = False
        if instruction_list:
            direction = instruction_list.pop()
        else:
            direction = ["k","k","k","k","k"]
class ColoredGrid:
    def __init__(self, rows, cols, coord_size=1):
        self.rows = rows
        self.cols = cols
        self.coord_size = coord_size
        self.colored_coords = []

    def draw_grid(self):
        fig, ax = plt.subplots()
        for coord in self.colored_coords:
            x, y, color,front,left,right,back = coord
            if left:
                ax.axvline(x, ymin=y/self.rows, ymax=(y+self.coord_size)/self.rows, color='black', linewidth=1)
            if right:
                ax.axvline(x+self.coord_size, ymin=y/self.rows, ymax=(y+self.coord_size)/self.rows, color='black', linewidth=1)
            if back:
                ax.axhline(y, xmin=x/self.cols, xmax=(x+self.coord_size)/self.cols, color='black', linewidth=1)
            if front:
                ax.axhline(y+self.coord_size, xmin=x/self.cols, xmax=(x+self.coord_size)/self.cols, color='black', linewidth=1)

        # Set axis limits
        ax.set_xlim(0, self.cols)
        ax.set_ylim(0, self.rows)

        # Remove ticks
        ax.set_xticks([])
        ax.set_yticks([])

        # Draw colored coordinates
        for coord in self.colored_coords:
            x, y, color,front,back,left,right = coord
            ax.add_patch(plt.Rectangle((x+0.1, y+0.1), self.coord_size-0.2, self.coord_size-0.2, fill=True, color=color))

        plt.grid(False)
        plt.show()

    def color_coordinate(self, x, y, color,front,left,right,back):
        self.colored_coords.append((x, y, color,front,left,right,back))


if __name__ == "__main__":
    current_x = 0
    current_y = 0
    #rows = input("Enter total rows: ")
    #columns = input("Enter total columns: ")
    #current_x = int(input("Enter start x: "))
    #current_y = int(input("Enter start y: "))
    # rows = 8
    # columns = 8
    # colored_grid = ColoredGrid(int(rows), int(columns))
    # colored_grid.color_coordinate(current_x, current_y, 'red',front=True,left=True,right=False,back=True)
    # current_x = 1
    # current_y = 0
    # colored_grid.color_coordinate(current_x, current_y, 'blue',front=False,left=False,right=True,back=True)
    # current_x = 1
    # current_y = 1
    # colored_grid.color_coordinate(current_x, current_y, 'blue',front=True,left=True,right=False,back=False)
    # current_x = 2
    # current_y = 1
    # colored_grid.color_coordinate(current_x, current_y, 'green',front=True,left=False,right=True,back=True)
    # colored_grid.draw_grid()
    current_x = 0
    current_y = 0
    rows = input("Enter total rows: ")
    columns = input("Enter total columns: ")
    current_x = int(input("Enter start x: "))
    current_y = int(input("Enter start y: "))
    facing = input("Enter facing direction: ")
    front = input("Enter True if wall in front: ")
    if front == "True":
        front = True
    else:
        front = False
    left = input("Enter True if wall left: ")
    if left == "True":
        left = True
    else:
        left = False
    right = input("Enter True if wall right: ")
    if right == "True":
        right = True
    else:
        right = False
    back = input("Enter True if wall back: ")
    if back == "True":
        back = True
    else:
        back = False
    colored_grid = ColoredGrid(int(rows), int(columns))
    colored_grid.color_coordinate(current_x, current_y, 'red',front,left,right,back)
    colored_grid.draw_grid()
    threadServer = threading.Thread(target=start_server, args=())
    threadMaze = threading.Thread(target=mazeGrid, args=(current_x, current_y, colored_grid, facing))
    #start_server()
    #print(str(instruction_list))
    #mazeGrid(current_x, current_y, colored_grid, facing)
    threadServer.start()
    threadMaze.start()
    threadServer.join()
    threadMaze.join()