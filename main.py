#This is a terminal
import curses
import os
import atexit

Y_MARGIN = 2
X_MARGIN = 4

# get file to be created/read
filename = input("file: ")

#initialize curses
stdscr = curses.initscr()

def exit_on_error():
	stdscr.getch()
	curses.endwin()

# register endwin() on exit to prevent terminal errors
atexit.register(exit_on_error)

# will display line numbers
def draw_line_number(lines, ymargin):
	start = ymargin  # start at y=2

	for i in range(1, lines):
		stdscr.move(start, 0)
		stdscr.addstr(str(i))
		start += 1

def draw_window():
	# size = (length, hieght)
	size = os.get_terminal_size()
	# length of bar will be: length of terminal - length of the filename.
	barSize = size[0] - len(filename)
	stdscr.move(0, 0)

	# draw titlebar
	for i in range(0, int(barSize / 2)):
		stdscr.addstr("—")
	stdscr.addstr(filename)
	for i in range(0, int(barSize / 2)):
		stdscr.addstr("—")

	stdscr.refresh()

def open_file(file):
	# if file cant be read (doesnt exist), create it
	try:
		filer = open(file, 'r')
		filee = filer.read()
		filer.close()
	except:
		return ""
	return str(filee)

# return a direction and prepare for check_char_
def parse_direc(input):
	if(input == 2): # left (CTRL+b)
		return 'l'
	elif(input == 6): # right (CTRL+f)
		return 'r'
	elif(input == 16): # up (CTRL+p)
		return 'u'
	elif(input == 14): # down (CTRL+n)
		return 'd'

def org_content(content):
	cont_r: str = []
	cont_t = ""

	for i in content:
		if(i == '\n'):
			cont_r.append(cont_t)
			cont_t = ""
		else:
			cont_t += i
	cont_r.append(cont_t)
	return cont_r

# content here should be an array of strings
def print_content(content):
	y = Y_MARGIN
	for i in content:
		for k in i:
			stdscr.addstr(k)
		y+=1
		stdscr.move(y,X_MARGIN)
	stdscr.refresh()
	return y-Y_MARGIN

# content should be the array of string created by org_content()
def do_revert(content): 
	str_content = ""
	for i in content:
		str_content+='\n'
		for k in i:
			str_content+=k
	if str_content[0] == "\n":
		str_content = str_content[1:]
	return str_content
#def update_cursor(current_char): # r,l,u,p

def main():
	# curses related
	curses.noecho()
	curses.raw()

	# var
	currentY = Y_MARGIN
	ypos, xpos = 0,0
	line_c = 0
	currentChar = 0

	# draw window & line numbers
	draw_window()
	draw_line_number(currentY+1, Y_MARGIN)

	# example debug
	stdscr.move(ypos+Y_MARGIN,xpos+X_MARGIN)

	# started blank to prevent errors regarding types
	chars = open_file(filename)
	charw = org_content(chars)
	
	currentY = print_content(charw)
	input = stdscr.getch()  # initial keypress

	# escape to quit
	while input != 27:
		nl = 0
		y, x = stdscr.getyx()
		#stdscr.box() uncomment this line to draw box
		draw_window()
		draw_line_number(currentY+1, Y_MARGIN)
		stdscr.move(Y_MARGIN,X_MARGIN)

		# manage special keys and controls
		if input in [2,6,14,16]:
			control = parse_direc(input)
			if control in ['l','r']:
				if control == 'l' and currentChar != 0:
					currentChar-=1
				elif control == 'r' and currentChar < len(charw[line_c]):
					currentChar+=1
			elif control == 'u':
				if line_c != 0:
					line_c-=1
			elif control == 'd':
				if line_c < len(charw)-1:
					line_c+=1
		else:
			if input == 127: # backspace
				if currentChar == 0 and line_c != 0:
					line_c-=1
					currentChar = len(charw[line_c])
					charw[line_c] = charw[line_c] + charw[line_c+1]
					charw.pop(line_c+1)
				else: # regular input gets inserted into the buffer
					if currentChar - 1 >= 0:
						currentChar -= 1
					charw[line_c] = charw[line_c][0:currentChar:] + charw[line_c][currentChar + 1::]
			elif input == 9:  # Tab = 4 spaces to reduce bugs
				charw[line_c] = charw[line_c][:currentChar] + "    " + charw[line_c][currentChar:]
				currentChar += 4
			elif input == 10:
				charw.insert(line_c+1, "")
				line_c+=1
				# move remaining characters of line down to the next line
				charw[line_c] = charw[line_c-1][currentChar:]
				charw[line_c-1] = charw[line_c-1][:currentChar]
				currentChar = 0
			else:
				charw[line_c] = charw[line_c][:currentChar] + chr(input) + charw[line_c][currentChar:]
				currentChar += 1

		# print contents
		currentY = print_content(charw)

		# stops cursor from being in the wrong place
		if currentChar > len(charw[line_c]):
			currentChar = len(charw[line_c])

		# keep at the end of the loop so it gets checked for 27 immediately
		stdscr.move(line_c+Y_MARGIN,currentChar+X_MARGIN)
		input = stdscr.getch()
		stdscr.clear()

	# write to file
	file = open(filename, 'w')
	filew = do_revert(charw)
	file.write(filew)
	file.close()

	atexit.unregister(exit_on_error)
	curses.endwin() # Depricated

main()
