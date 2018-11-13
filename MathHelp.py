import globalCommands as gc
import globalPluginHandler
import texcheck
import keyboardHandler
import winInputHook
import tones
import win32api
import time
import ui
import speech
import api
import louis
import braille
import config
import textInfos

#additional class
class alpha_array:
	def __init__(self, m, n):
		self.row = n+1
		self.col = m+1
		self.table = [["" for x in range(self.row)] for y in range(self.col)]
		self.cur_row = 1
		self.cur_col = 1
		self.buffer = []
		self.pass_idx = []
		self.read_pos = False
		self.latex_sub = True

	def toggle_read_pos(self):
		self.read_pos = not self.read_pos
		if self.read_pos:
			return True
		else:
			return False

	def set_matrix_style(self):
		self.begin_head = "\\begin{matrix} \r\n"
		self.end_head = "\\end{matrix} \n"
		self.col_dil = "&"
		self.row_dil = "\\\\\r\n"
		self.row_begin = ""
		self.row_end = ""
		self.vector_sign = 0
		self.row_extra = " "
		self.column_head = 1
		self.pass_zero = False
		self.mode = "matrix"

	def set_equation_style(self):
		self.begin_head = ""
		self.end_head = ""
		self.col_dil = " "
		self.row_dil = "\r\n"
		self.row_begin = "$"
		self.row_end = "$"
		self.vector_sign = 0
		self.row_extra = " "
		self.column_head = 1
		self.pass_zero = True
		self.mode = "equation"

	def set_vector_style(self):
		self.begin_head = "$"
		self.end_head = "$"
		self.col_dil = ","
		self.row_dil = ""
		self.row_begin = "("
		self.row_end = ")"
		self.vector_sign = True
		self.row_extra = " "
		self.column_head = False
		self.pass_zero = False
		self.mode = "vector"


	def is_pass(self, row=-1):
		if row >= 0:
			check = row
		else:
			check = self.cur_row
		if check in self.pass_idx:
			return True
		else:
			return False

	def print_array(self, type=0, line=-1):
		obj2 = api.getFocusObject()
		if obj2.windowClassName == u"_WwG":
			api.copyToClip(unicode(self.prepare_array(type, line)))
			return None
		try:
			old = api.getClipData()
		except TypeError:
			old = ""
		api.copyToClip(unicode(self.prepare_array(type, line)))
		time.sleep(0.01)
		win32api.SendMessage(obj2.windowHandle, 0x302, 0, 0)
		api.copyToClip(old)

	def prepare_array(self, type=0, line=-1):
		if type == 0:
			self.set_matrix_style()
		elif type == 1:
			self.set_equation_style()
		elif type == 2:
			self.set_vector_style()
		if line >= 0:
			if self.mode == "equation":
				self.row_begin = ""
				self.row_end = ""
			start_row = self.cur_row
			self.pass_zero = False
			if self.cur_row < self.row:
				end_row = self.cur_row+1
			else:
				end_row = None
			print_all = True
		else:
			start_row = self.cur_row
			end_row = None
			print_all = False
		start_col = -1
		out = self.begin_head
		for h,i in enumerate(self.table[start_row:end_row]):
			if self.is_pass(h+1):
				continue
			if start_col == -1:
				for s,t in enumerate(i[1:]):
					if t != "":
						start_col = s+1
						break
				else:
					continue
			if i[start_col] == "" or (start_col != 1 and i[start_col-1] != ""):
				break
			if self.latex_sub == True:
				sub = self.table[h+1][0]
				sub = sub.replace("\\times", "$\\times$")
				sub = sub.replace("\\divides", "$\\divides$")
				sub = sub.replace("\\s", u'\u0e41\u0e17\u0e19 ')
				sub = sub.replace("\\i", u' \u0e43\u0e19 ')
			else:
				sub = self.table[h+1][0]
			out += sub + " " + self.row_begin + " "
			for j,k in enumerate(i[start_col:]):
				if k == "=" and self.vector_sign == True:
					self.row_extra = "="
					break
				elif k == "+" and self.vector_sign == True:
					self.row_extra = "+"
					break
				elif k == "-" and self.vector_sign == True:
					self.row_extra = "-"
					break
				elif k == "*" and self.vector_sign == True:
					self.row_extra = "\\cdot"
					break
				elif k == "/" and self.vector_sign == True:
					self.row_extra = "\divides"
					break
				else:
					self.row_extra = " "
				if k == "" and not print_all:
					break
				if j != 0:
					out += self.col_dil
				if print_all and k == "":
					out = out[:-1]
					continue
				if "J" in k:
					k = k.replace("J","\\hat{j}")
				elif "I" in k:
					k = k.replace("I","\\hat{i}")
				elif "K" in k:
					k = k.replace("K","\\hat{k}")
				if self.pass_zero and (k == "+0" or k == "-0" or k == "0"):
					continue
				if self.pass_zero and (k == "+1"):
					out += "+" + self.table[0][j+1]
					continue
				if self.pass_zero and (k == "1"):
					out += self.table[0][j+1]
					continue
				elif self.pass_zero and (k == "-1"):
					out += "-" + self.table[0][j+1]
					continue
				out += k + self.table[0][j+1]
			out += self.row_end + self.row_extra + self.row_dil
		out += self.end_head
		return out

	def delete_current_cell(self):
		temp = self.table[self.cur_row][self.cur_col]
		self.table[self.cur_row][self.cur_col] = ""
		return temp

	def delete_current_row(self):
		self.table[self.cur_row] = [""]*self.row

	def delete_all(self):
		self.table = [["" for x in range(self.row)] for y in range(self.col)]

	def copy_current_column(self):
		temp = []
		for i in range(self.row):
			print(i)
			temp.append(self.table[i][self.cur_col])
		self.buffer = list(temp)


	def copy_current_row(self):
		self.buffer = list(self.table[self.cur_row])

	def paste_to_current_column(self):
		if len(self.buffer) == 0:
			return None
		for i in range(self.row):
			self.table[i][self.cur_col] = self.buffer[i]

	def paste_to_current_row(self):
		if len(self.buffer) == 0:
			return None
		self.table[self.cur_row] = list(self.buffer)

	def set_cell(self,m,n, val):
		self.table[m][n] = val
	def read_cell(self,m,n):
		return self.table[m][n]

	def read_current_cell(self):
		return self.table[self.cur_row][self.cur_col]

	def set_current_cell(self, val):
		self.table[self.cur_row][self.cur_col] = val

	def move_startrow(self):
		return self.move_to(self.cur_row, 1)

	def move_endrow(self):
		s = 0
		e = 0
		for i,j in enumerate(self.table[self.cur_row][self.cur_col:]):
			if j != "" and s == 0:
				s =i+self.cur_col
				continue
			if j == "" and s >= 0:
				e = i+self.cur_col-1
				break
		if s >= 0 and e == 0:
			e = self.col-1
		return self.move_to(self.cur_row, e)


	def move_rel_startrow(self):
		s = self.col
		e = 1
		for i in range(self.cur_col, 0,-1):
			if self.table[self.cur_row][i] != "" and s == self.col:
				s =i
				continue
			if self.table[self.cur_row][i] == "" and s < self.col:
				e = i+1
				break
		return self.move_to(self.cur_row, e)

	def move_to(self, row,col):
		self.cur_row = row
		self.cur_col = col
		return self.table[self.cur_row][self.cur_col] + " ,at %d, %d" % (self.cur_row, self.cur_col) if self.read_pos else self.table[self.cur_row][self.cur_col]

	def move_up(self):
		if self.cur_row == 0:
			return None
		self.cur_row -= 1
		if self.is_pass():
			return self.move_up()
		return self.table[self.cur_row][self.cur_col] + " ,at %d, %d" % (self.cur_row, self.cur_col) if self.read_pos else self.table[self.cur_row][self.cur_col]

	def move_down(self):
		if self.cur_row == self.row-1:
			return None
		self.cur_row += 1
		if self.is_pass():
			return self.move_down()
		return self.table[self.cur_row][self.cur_col] + " ,at %d, %d" % (self.cur_row, self.cur_col) if self.read_pos else self.table[self.cur_row][self.cur_col]

	def move_left(self):
		if self.cur_col == 0:
			return None
		self.cur_col -= 1
		if self.is_pass():
			return self.move_left()
		return self.table[self.cur_row][self.cur_col] + " ,at %d, %d" % (self.cur_row, self.cur_col) if self.read_pos else self.table[self.cur_row][self.cur_col]

	def move_right(self):
		if self.cur_col == self.col-1:
			return None
		self.cur_col += 1
		if self.is_pass():
			return self.move_right()
		return self.table[self.cur_row][self.cur_col] + " ,at %d, %d" % (self.cur_row, self.cur_col) if self.read_pos else self.table[self.cur_row][self.cur_col]

	def move_upleft(self):
		if self.cur_row == 0 or self.cur_col == 0:
			return None
		self.cur_row -= 1
		self.cur_col -= 1
		if self.is_pass():
			return self.move_upleft()
		return self.table[self.cur_row][self.cur_col] + " ,at %d, %d" % (self.cur_row, self.cur_col) if self.read_pos else self.table[self.cur_row][self.cur_col]

	def move_upright(self):
		if self.cur_row == 0 or self.cur_col == self.col-1:
			return None
		self.cur_row -= 1
		self.cur_col += 1
		if self.is_pass():
			return self.move_upright()
		return self.table[self.cur_row][self.cur_col] + " ,at %d, %d" % (self.cur_row, self.cur_col) if self.read_pos else self.table[self.cur_row][self.cur_col]

	def move_downleft(self):
		if self.cur_row == self.row-1 or self.cur_col == 0:
			return None
		self.cur_row += 1
		self.cur_col -= 1
		if self.is_pass():
			return self.move_downleft()
		return self.table[self.cur_row][self.cur_col] + " ,at %d, %d" % (self.cur_row, self.cur_col) if self.read_pos else self.table[self.cur_row][self.cur_col]

	def move_downright(self):
		if self.cur_row == self.row-1 or self.cur_col == self.col-1:
			return None
		self.cur_row += 1
		self.cur_col += 1
		if self.is_pass():
			return self.move_downright()
		return self.table[self.cur_row][self.cur_col] + " ,at %d, %d" % (self.cur_row, self.cur_col) if self.read_pos else self.table[self.cur_row][self.cur_col]

	def mark_pass(self):
		self.pass_idx.append(self.cur_row)

	def clear_pass(self):
		self.pass_idx = []

#Function
oldSpeak = speech.speak
oldBraille = braille.Region.update

#Variables
speakData=""
isBrailleFreeze = False
prior_timeout = 4

#Constants
CONST_WM_PASTE = 0x302
CONST_WM_KEYDOWN = 0x100
CONST_WM_KEYUP = 0x101
CONST_VK_LEFT = 0x25
CONST_VK_RIGHT = 0x27 #added
CONST_VK_CONTROL = 0x11
CONST_VK_MENU = 0x12

#Global function

a_array = []
alpha = alpha_array(15,15)
beta = alpha_array(15,15)
onDelete = False
pending = ""
cur_pos = 0
last_press = 0
last_key = 0

def insert_string(string,char):
	global cur_pos
	pos = cur_pos
	cur_pos += 1
	return string[:pos] + char + string[pos:]

def delete_last_char_string(string):
	global cur_pos
	cur_pos = cur_pos - 1
	return string[:cur_pos]+string[cur_pos+1:]

def character_handle(key, upper):
	global pending
	if key == 187:
		if upper:
			pending = insert_string(pending,"+")
			speech.cancelSpeech()
			speech.speakText("plus")
		else:
			pending = insert_string(pending,"=")
			speech.cancelSpeech()
			speech.speakText("=")
		return None
	if key == 189:
		if upper:
			pending = insert_string(pending,"_")
			speech.cancelSpeech()
			speech.speakText("_")
		else:
			pending = insert_string(pending,"-")
			speech.cancelSpeech()
			speech.speakText("-")
		return None
	if key == 107:
		pending = insert_string(pending,"+")
		speech.cancelSpeech()
		speech.speakText("+")
		return None
	if key == 106:
		pending = insert_string(pending,"*")
		speech.cancelSpeech()
		speech.speakText("*")
		return None
	if key == 111:
		pending = insert_string(pending,"/")
		speech.cancelSpeech()
		speech.speakText("/")
		return None
	if key == 109:
		pending = insert_string(pending,"-")
		speech.cancelSpeech()
		speech.speakText("-")
		return None
	if (key >= 48 and key <= 57) and not upper:
		pending = insert_string(pending,chr(key))
		speech.cancelSpeech()
		speech.speakText(chr(key))
		return None
	elif key == 57 and upper:
		pending = insert_string(pending,"(")
		speech.cancelSpeech()
		speech.speakText("(")
		return None
	elif key == 48 and upper:
		pending = insert_string(pending,")")
		speech.cancelSpeech()
		speech.speakText(")")
		return None
	elif key >= 96 and key <= 105:
		pending = insert_string(pending,chr(key-48))
		speech.cancelSpeech()
		speech.speakText(chr(key-48))
		return None
	if key == 32:
		pending = insert_string(pending," ")
		speech.cancelSpeech()
		speech.speakText("space")
	if key >= 219 and key <= 221:
		if upper:
			pending = insert_string(pending,chr(key-96))
			speech.cancelSpeech()
			speech.speakText(chr(key-96))
		else:
			pending = insert_string(pending,chr(key-128))
			speech.cancelSpeech()
			speech.speakText(chr(key-128))
	if (key >= 65 and key <= 90):
		if not upper:
			pending = insert_string(pending,chr(key+32))
			speech.cancelSpeech()
			speech.speakText(chr(key+32))
		else:
			pending = insert_string(pending,chr(key))
			speech.cancelSpeech()
			speech.speakText(chr(key))

def operation_handle(key, modifier=0):
	global a_array, pending, cur_pos, onDelete
	if len(pending) > 0 and key != 8:
		onDelete = False
		a_array.set_current_cell(pending)
		pending = ""
		cur_pos = 0
	if key == 8:
		onDelete = True
		if cur_pos == 0:
			return
		print(cur_pos-1)
		speech.cancelSpeech()
		speech.speakText(pending[cur_pos-1])
		pending = delete_last_char_string(pending)
	elif key == 118:
		a_array.mark_pass()
		speech.cancelSpeech()
		speech.speakText("mark pass")
	elif key == 117:
		if a_array.toggle_read_pos():
			speech.cancelSpeech()
			speech.speakText("Read position")
		else:
			speech.cancelSpeech()
			speech.speakText("don't read position")
	elif key == 119:
		a_array.clear_pass()
		speech.cancelSpeech()
		speech.speakText("clear pass")
	elif key == 120:
		a_array.copy_current_column()
		speech.cancelSpeech()
		speech.speakText("Copy current column")
	elif key == 121:
		a_array.paste_to_current_column()
		speech.cancelSpeech()
		speech.speakText("paste to current column")
	elif key == 122:
		a_array.copy_current_row()
		speech.cancelSpeech()
		speech.speakText("Copy current row")
	elif key == 19:
		if modifier == 0:
			a_array.print_array(1)
			speech.cancelSpeech()
			speech.speakText("printing equation to document")
		elif modifier == 1:
			a_array.print_array()
			speech.cancelSpeech()
			speech.speakText("printing matrix to document")
	elif key == 145:
		if modifier == 0:
			a_array.print_array(1,1)
			speech.cancelSpeech()
			speech.speakText("printing current row as equation")
		elif modifier == 1:
			a_array.print_array(0,1)
			speech.cancelSpeech()
			speech.speakText("printing current row as matrix")
		elif modifier == 2:
			a_array.print_array(2,1)
			speech.cancelSpeech()
			speech.speakText("printing current row as vector")
	elif key == 3:
		a_array.print_array(2)
		speech.cancelSpeech()
		speech.speakText("printing vector to document")
	elif key == 123:
		a_array.paste_to_current_row()
		speech.cancelSpeech()
		speech.speakText("paste to current row")
	elif key == 44:
		if modifier == 0:
			a_array.delete_current_row()
			speech.cancelSpeech()
			speech.speakText("Delete current row")
		if modifier == 1:
			a_array.delete_all()
			speech.cancelSpeech()
			speech.speakText("Delete all")
	elif key == 46:
		speech.cancelSpeech()
		speech.speakText(a_array.delete_current_cell())

def arrow_handle(key, extended):
	global a_array
	global pending, cur_pos, onDelete
	#print(pending)
	if (len(pending) > 0) or (len(pending) == 0 and onDelete == True):
		a_array.set_current_cell(pending)
		pending = ""
		cur_pos = 0
	if key == 33:
		if extended == True:
			speech.cancelSpeech()
			speech.speakText("rrelative start of row, "+a_array.move_rel_startrow())
		else:
			speech.cancelSpeech()
			speech.speakText(a_array.move_upright())
	elif key == 36:
		if extended == True:
			speech.cancelSpeech()
			speech.speakText("start of row, "+a_array.move_startrow())
		else:
			speech.cancelSpeech()
			speech.speakText(a_array.move_upleft())
	elif key == 35:
		if extended == True:
			speech.cancelSpeech()
			speech.speakText("end of row, "+a_array.move_endrow())
		else:
			speech.cancelSpeech()
			speech.speakText(a_array.move_downleft())
	elif key == 34:
		if extended == True:
			speech.cancelSpeech()
			speech.speakText("top of table, "+a_array.move_to(1,1))
		else:
			speech.cancelSpeech()
			speech.speakText(a_array.move_downright())
	elif key == 38:
		speech.cancelSpeech()
		speech.speakText(a_array.move_up())
	elif key == 40:
		speech.cancelSpeech()
		speech.speakText(a_array.move_down())
	elif key == 37:
		speech.cancelSpeech()
		speech.speakText(a_array.move_left())
	elif key == 39 or key == 9:
		speech.cancelSpeech()
		speech.speakText(a_array.move_right())
	elif key == 13:
		speech.cancelSpeech()
		speech.speakText(a_array.move_down())
	elif key == 12:
		speech.cancelSpeech()
		speech.speakSpelling(a_array.read_current_cell())
	pending = a_array.read_current_cell()
	cur_pos = len(pending)



def my_keyDownEvent(vkCode,scanCode,extended,injected):
	global last_press
	global last_key
	is_upper = False
	if (vkCode >= 33 and vkCode <= 40) or vkCode == 9 or vkCode == 13 or vkCode == 12:
		if time.time() - last_press >= 0.05:
			arrow_handle(vkCode, extended)
			last_key = vkCode
			last_press = time.time()
	elif vkCode == 187 or vkCode == 189:
		if time.time() - last_press >= 0.05:
			if last_key == 160:
				is_upper = True
			character_handle(vkCode, is_upper)
			last_key = vkCode
			last_press = time.time()
	elif (vkCode >= 48 and vkCode <= 57) or (vkCode >= 65 and vkCode <= 90) or (vkCode >= 96 and vkCode <= 111) or (vkCode >= 219 and vkCode <= 221) or vkCode == 32:
		if time.time() - last_press >= 0.05:
			if last_key == 160 and ((vkCode >= 65 and vkCode <= 90) or (vkCode >= 48 and vkCode <= 57) or (vkCode >= 219 and vkCode <= 221)):
				is_upper = True
			character_handle(vkCode, is_upper)
			last_key = vkCode
			last_press = time.time()
	elif vkCode == 3 or vkCode == 8 or vkCode == 19 or vkCode == 117 or vkCode == 118 or vkCode == 119 or vkCode == 120 or vkCode == 121 or vkCode == 122 or vkCode == 123 or vkCode == 44 or vkCode == 46 or vkCode == 145:
		if time.time() - last_press >= 0.05:
			if last_key == 160 or last_key == 161:
				operation_handle(vkCode,1)
				last_key = vkCode
				last_press = time.time()
			elif (last_key == 162 or last_key == 163) and vkCode == 145:
				operation_handle(vkCode,2)
				last_key = vkCode
				last_press = time.time()
			else:
				operation_handle(vkCode)
				last_key = vkCode
				last_press = time.time()
	else:
		last_key = vkCode
		return keyboardHandler.internal_keyDownEvent(vkCode,scanCode,extended,injected)



def my_keyUpEvent(vkCode,scanCode,extended,injected):
	return keyboardHandler.internal_keyUpEvent(vkCode,scanCode,extended,injected)

def mySpeak(text, *args, **kwargs):
	global speakData
	speakData = text
	oldSpeak(text, *args, **kwargs)

def myBraille(*args, **kwargs):
	if isBrailleFreeze:
		pass
	else:
		oldBraille(*args, **kwargs)

class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	def __init__(self, *args, **kwargs):
		globalPluginHandler.GlobalPlugin.__init__(self, *args, **kwargs)
		global oldSpeak
		global oldBraille

		oldSpeak = speech.speak
		oldBraille = braille.Region.update
		speech.speak = mySpeak
		braille.Region.update = myBraille
		templist = list(braille.TABLES)
		templist.append(	("thai-gr1.cti", _("Thai grade 1"), False))
		braille.TABLES = tuple(templist)
		louis.pass1Only = 0
		self.slot1 = ""
		self.slot2 = ""
		self.slot3 = ""
		self.slot4 = ""
		self.slot5 = ""
		self.slot6 = ""
		self.slot7 = ""
		self.slot8 = ""
		self.slotlast = ""
		self.IsHelp = False
		self.IsNav = True
		self.use_array = None

	def script_ToggleArray_1(self, gesture):
		global a_array, alpha
		if self.use_array == "A":
			self.use_array = None
			speech.cancelSpeech()
			speech.speakText("Array mode is off")
			winInputHook.setCallbacks(keyDown=keyboardHandler.internal_keyDownEvent,keyUp=keyboardHandler.internal_keyUpEvent)
		elif self.use_array == "B":
			self.use_array = "A"
			a_array = alpha
			speech.cancelSpeech()
			speech.speakText("Array mode is alpha")
		elif self.use_array == None:
			self.use_array = "A"
			a_array = alpha
			speech.cancelSpeech()
			speech.speakText("Array mode is alpha")
			winInputHook.setCallbacks(keyDown=my_keyDownEvent,keyUp=my_keyUpEvent)

	def script_ToggleArray_2(self, gesture):
		global a_array, beta
		if self.use_array == "B":
			self.use_array = None
			speech.cancelSpeech()
			speech.speakText("Array mode is off")
			winInputHook.setCallbacks(keyDown=keyboardHandler.internal_keyDownEvent,keyUp=keyboardHandler.internal_keyUpEvent)
		elif self.use_array == "A":
			self.use_array = "B"
			a_array = beta
			speech.cancelSpeech()
			speech.speakText("Array mode is beta")
		elif self.use_array == None:
			self.use_array = "B"
			a_array = beta
			speech.cancelSpeech()
			speech.speakText("Array mode is beta")
			winInputHook.setCallbacks(keyDown=my_keyDownEvent,keyUp=my_keyUpEvent)


	def script_ToggleHelp(self, gesture):
		self.IsHelp = not self.IsHelp
		if self.IsHelp:
			speech.speakText("Help mode is on")
		else:
			speech.speakText("Help mode is off")

	def script_ToggleNav(self, gesture):
		self.IsNav = not self.IsNav
		if self.IsNav:
			speech.speakText("Navigational mode is on")
		else:
			speech.speakText("Navigational mode is off")

	def script_review_markStartForCopy(self, gesture):
		com_ex = gc.GlobalCommands()
		com_ex.script_review_markStartForCopy(gesture)

	def script_review_copy(self, gesture):
		com_ex = gc.GlobalCommands()
		com_ex.script_review_copy(gesture)

	def MoveTill(self, chars, dir, sel=False):
		if not self.IsNav:
			return
		so_far = ""
		obj = api.getFocusObject()
		if dir.lower() == "left":
			dir_key = CONST_VK_LEFT
		elif dir.lower() == "right":
			dir_key = CONST_VK_RIGHT
		firsttime = 1
		time.sleep(0.1)
		while True:
			obj = api.getFocusObject()
			buf = obj.makeTextInfo(textInfos.POSITION_CARET)
			buf.expand(textInfos.UNIT_CHARACTER)
			if buf.text in chars and firsttime == 0:
				break
			else:
				so_far += buf.text
				firsttime = 0
				win32api.SendMessage(obj.windowHandle, CONST_WM_KEYDOWN, dir_key, 0)
				win32api.SendMessage(obj.windowHandle, CONST_WM_KEYUP, dir_key, 0)
		speech.speakText(so_far)

	def script_RightDelimiter(self, gesture):
		self.MoveTill("()[]$ ", "right")

	def script_LeftDelimiter(self, gesture):
		self.MoveTill("()[]$ ", "left")

	def script_RightOperator(self, gesture):
		self.MoveTill("+-=$", "right")

	def script_LeftOperator(self, gesture):
		self.MoveTill("+-=$", "left")

	def script_toggleBrailleFreeze(self, gesture):
		global isBrailleFreeze, prior_timeout
		isBrailleFreeze = not isBrailleFreeze
		if isBrailleFreeze:
			prior_timeout = config.conf["braille"]["messageTimeout"]
			config.conf["braille"]["messageTimeout"] = 0
			speech.speakText("Braille freeze")
		else:
			config.conf["braille"]["messageTimeout"] = prior_timeout
			speech.speakText("Braille unfreeze")

	def script_T_copylast(self, gesture):
		rawSpeak = u""
		if speakData:
			for i in speakData:
				if type(i) == type(u"test"):
					rawSpeak = rawSpeak + " " + i
			self.slotlast = rawSpeak
			tones.beep(1500, 120)

	def DType(self, message, sel=False, force=False, offset=0, altbf="", altaf="", say=""):
		if self.IsHelp:
			if say:
				speech.speakText(say)
			else:
				speech.speakText(message)
			return
		if api.getFocusObject().windowClassName == u"_WwG":
			self.D_word(message, sel, force, offset, altbf, altaf, say)
		else:
			self.D_norm(message, sel, force, offset, altbf, altaf, say)

	def D_word(self, message, sel=False, force=False, offset=0, altbf="", altaf="", say=""):
		obj = api.getFocusObject()
		info = obj.makeTextInfo(textInfos.POSITION_SELECTION)
		text = info.text
		text = text.strip("\r")
		text = text.strip("\n")
		if (sel == True and len(text) > 0) or force == True:
			f_sel_mode = True
			if altbf != "" and altaf != "":
				message = altbf + text + altaf
			elif altbf != "" and altaf == "":
				message = altbf + text + "}"
			elif altbf == "" and altaf != "":
				message = message + text + altaf
			else:
				message = message + text + "}"
		else:
			f_sel_mode = False
		obj.WinwordSelectionObject.TypeText(message)
		if say != "":
			speech.speakText(say)
		else:
			speech.speakText(message)
		time.sleep(0.3)
		if f_sel_mode==True and offset > 0:
			for i in range(len(message)-offset):
				obj.WinwordSelectionObject.MoveLeft()
			f_sel_mode = False

	def D_norm(self, message, sel=False, force=False, offset=0, altbf="", altaf="", say=""):
		try:
			old = api.getClipData()
		except TypeError:
			old = ""
		obj = api.getFocusObject()
		info = obj.makeTextInfo(textInfos.POSITION_SELECTION)
		text = info.text
		if (sel == True and len(text) > 0) or force == True:
			f_sel_mode = True
			if altbf != "" and altaf != "":
				message = altbf + text + altaf
			elif altbf != "" and altaf == "":
				message = altbf + text + "}"
			elif altbf == "" and altaf != "":
				message = message + text + altaf
			else:
				message = message + text + "}"
		else:
			f_sel_mode = False
		api.copyToClip(unicode(message))
		time.sleep(0.01)
		win32api.SendMessage(obj.windowHandle, 0x302, 0, 0)
		if say != "":
			speech.speakText(say)
		else:
			speech.speakText(message)
		time.sleep(0.3)
		if f_sel_mode==True and offset > 0:
			for i in range(len(message)-offset):
				win32api.SendMessage(obj.windowHandle, CONST_WM_KEYDOWN, CONST_VK_LEFT, 0)
				win32api.SendMessage(obj.windowHandle, CONST_WM_KEYUP, CONST_VK_LEFT, 0)
			f_sel_mode = False
		api.copyToClip(old)


	def script_G_alpha(self, gesture):
		self.DType("color=\"black:black\"", say="double edge")

	def script_G_beta(self, gesture):
		self.DType("""
Graph g {\r\n
rotate = 90;\r\n
node [shape=oval];\r\n
\r\n
label="Title";\r\n
}\r\n
""", say="initialize")

	def script_G_gamma(self, gesture):
		self.DType(r"\gamma")

	def script_G_delta(self, gesture):
		self.DType(r"\delta")

	def script_G_bigdelta(self, gesture):
		self.DType(r"style=dotted", say="dotted node shape")

	def script_G_epsilon(self, gesture):
		self.DType(r"len=3", say="long length")

	def script_G_zeta(self, gesture):
		self.DType(r"shape=oval", say="oval shape")

	def script_G_eta(self, gesture):
		self.DType(r"\eta")

	def script_G_theta(self, gesture):
		self.DType(r"\theta")

	def script_G_iota(self, gesture):
		self.DType(r"\iota")

	def script_G_kappa(self, gesture):
		self.DType(r"\kappa")

	def script_G_lambda(self, gesture):
		self.DType(r"\lambda")

	def script_G_mu(self, gesture):
		self.DType(r"\mu")

	def script_G_nu(self, gesture):
		self.DType(r"\nu")

	def script_G_xi(self, gesture):
		self.DType(r"shape=rectangle", say="rectangle shape")

	def script_G_omicron(self, gesture):
		self.DType(r"\omicron")

	def script_G_bigomicron(self, gesture):
		self.DType(r"\Omicron", say="Big Omicron")

	def script_G_pi(self, gesture):
		self.DType(r"\pi")

	def script_G_rho(self, gesture):
		self.DType(r"\rho")

	def script_G_sigma(self, gesture):
		self.DType(r"\sigma")

	def script_G_bigsigma(self, gesture):
		self.DType(r"peripheries=2", say="double node shape")

	def script_G_tau(self, gesture):
		self.DType(r"\tau")

	def script_T_greater(self, gesture):
		self.DType(r"\geq", sel=False, say="Greater than or equal to")

	def script_T_less(self, gesture):
		self.DType(r"\leq", sel=False, say="less than or equal to")

	def script_G_upsilon(self, gesture):
		self.DType(r"\upsilon")

	def script_G_phy(self, gesture):
		self.DType(r"\phi")

	def script_G_chi(self, gesture):
		self.DType(r"shape=diamond", say="diamond shape")

	def script_G_psi(self, gesture):
		self.DType(r"\psi")

	def script_G_omega(self, gesture):
		self.DType(r"len=1.5", say="short length")

	def script_G_bigomega(self, gesture):
		self.DType(r"label=", say="label")

	def script_T_frac(self, gesture):
		self.DType(r"\frac{", sel=True)

	def script_T_opencase(self, gesture):
		self.DType("\\begin{cases}\r\n", sel=False)

	def script_T_closecase(self, gesture):
		self.DType("\r\n\\end{cases}", sel=False)

	def script_T_openmatrix(self, gesture):
		self.DType("\\begin{matrix}\r\n")

	def script_T_closematrix(self, gesture):
		self.DType("\r\n\\end{matrix}")

	def script_T_tenexp(self, gesture):
		self.DType(r" \cdot 10^{", force=True, offset=11)

	def script_T_hat(self, gesture):
		self.DType(r"\hat{", sel=True)

	def script_T_hatr(self, gesture):
		self.DType(r"\hat{r}")

	def script_T_hati(self, gesture):
		self.DType(r"\hat{i}")

	def script_T_hatj(self, gesture):
		self.DType(r"\hat{j}")

	def script_T_hatk(self, gesture):
		self.DType(r"\hat{k}")

	def script_T_lim(self, gesture):
		self.DType(r"\lim_{", sel=True, altbf="\lim{", offset=4)

	def script_T_int(self, gesture):
		self.DType(r"\int", sel=True, altbf="\int{", offset=4)

	def script_T_oint(self, gesture):
		self.DType(r"\oint", sel=True, altbf="\oint{", offset=5)

	def script_T_vec(self, gesture):
		self.DType(r"\vec{", sel=True)

	def script_T_sum(self, gesture):
		self.DType(r"\sum_{", sel=True, altbf="\sum", offset=4)

	def script_T_cos(self, gesture):
		self.DType(r"\cos", sel=True, altbf="\cos{", offset=4)

	def script_T_sin(self, gesture):
		self.DType(r"\sin", sel=True, altbf="\sin{", offset=4)

	def script_T_tan(self, gesture):
		self.DType(r"\tan", sel=True, altbf="\tan{", offset=4)

	def script_T_csc(self, gesture):
		self.DType(r"\csc", sel=True, altbf="\csc{", offset=4)

	def script_T_sec(self, gesture):
		self.DType(r"\sec", sel=True, altbf="\sec{", offset=4)

	def script_T_cot(self, gesture):
		self.DType(r"\cot", sel=True, altbf="\cot{", offset=4)


	def script_T_arccos(self, gesture):
		self.DType(r"\arccos", sel=True, altbf="\arccos{", offset=7)

	def script_T_arcsin(self, gesture):
		self.DType(r"\arcsin", sel=True, altbf="\arcsin{", offset=7)

	def script_T_arctan(self, gesture):
		self.DType(r"\arctan", sel=True, altbf="\arctan{", offset=7)

	def script_T_arccsc(self, gesture):
		self.DType(r"\arccsc", sel=True, altbf="\arccsc{", offset=7)

	def script_T_arcsec(self, gesture):
		self.DType(r"\arcsec", sel=True, altbf="\arcsec{", offset=7)

	def script_T_arccot(self, gesture):
		self.DType(r"\arccot", sel=True, altbf="\arccot{", offset=7)

	def script_T_degree(self, gesture):
		self.DType(r"^{\circ}", sel=False)

	def script_T_bar(self, gesture):
		self.DType(r"\bar{", sel=True)

	def script_T_bracel(self, gesture):
		self.DType(r"{", sel=True)

	def script_T_bracer(self, gesture):
		obj = api.getFocusObject()
		info = obj.makeTextInfo(textInfos.POSITION_CARET)
		info.expand(textInfos.UNIT_LINE)
		time.sleep(0.1)
		text = info.text
		l = text.count('{')
		r = text.count('}')
		if l > r:
			insert = '}'*(l-r)
			self.DType(insert)
		else:
			speech.speakText("All brace matched")

	def script_T_para(self, gesture):
		self.DType(r"(", sel=True, altaf=")")

	def script_T_a(self, gesture):
		self.DType(r"{m}/{s^2}", sel=False)

	def script_T_adol(self, gesture):
		self.DType(r"${m}/{s^2}$", sel=False)

	def script_T_v(self, gesture):
		self.DType(r"{m}/{s}", sel=False)

	def script_T_vdol(self, gesture):
		self.DType(r"${m}/{s}$", sel=False)

	def script_T_w(self, gesture):
		self.DType(r"{rad}/{s}", sel=False)

	def script_T_p(self, gesture):
		self.DType(r"\frac{n{}m^2}", sel=False)

	def script_T_e(self, gesture):
		self.DType(r"\frac{n c{}m^2}", sel=False)

	def script_T_wdol(self, gesture):
		self.DType(r"${rad}/{s}$", sel=False)

	def script_T_r(self, gesture):
		self.DType(r"{kg}/{m^3}", sel=False)

	def script_T_j(self, gesture):
		self.DType(r"{j}/{kg  \cdot  ^{\circ} C}", sel=False)

	def script_T_log(self, gesture):
		self.DType(r"\log", sel=True, altbf="\log{", offset=4)
		
	def script_T_ln(self, gesture):
		self.DType(r"\ln", sel=True, altbf="\ln{")

	def script_T_infty(self, gesture):
		self.DType(r"\infty")

	def script_T_sqrt(self, gesture):
		self.DType(r"\sqrt{", sel=True)

	def script_T_root(self, gesture):
		self.DType(r"\sqrt[", sel=True, altbf="\sqrt[]{", altaf = "}", offset=6)

	def script_T_divx(self, gesture):
		self.DType(r" \times ", sel=True, altbf=r"\frac{d(", altaf=r")}{dx}")

	def script_T_divy(self, gesture):
		self.DType(r" \cdot ", sel=True, altbf=r"\frac{d(", altaf=r")}{dy}")

	def script_T_divz(self, gesture):
		self.DType(r" \cross ", sel=True, altbf=r"\frac{d(", altaf=r")}{dz}")

	def script_T_perp(self, gesture):
		self.DType(r"\perp", say="perpendicular to")

	def script_T_parallel(self, gesture):
		self.DType(r"\parallel", say="parallel to")

	def script_T_divt_time(self, gesture):
		self.DType(r"\frac{d", sel=True, say="First time derivative",altbf=r"\frac{d", altaf=r"}{dt}", force=True, offset=7)

	def script_T_ddivt_time(self, gesture):
		self.DType(r"\frac{d^2", sel=True, say="Second time derivative", altbf=r"\frac{d^2", altaf=r"}{dt^2}", force=True, offset=9)


	def script_T_partial(self, gesture):
		self.DType(r"\partial")

	def script_T_divt(self, gesture):
		self.DType(r"\dot{", say="Single dot", sel=True, altbf=r"\frac{d(", altaf=r")}{dt}")

	def script_T_ddivt(self, gesture):
		self.DType(r"\ddot{", say="Double dots", sel=True, altbf=r"\frac{d^2(", altaf=r")}{dt^2}")

	def script_T_text(self, gesture):
		self.DType(r" \text{", sel=True)

	def script_T_left(self, gesture):
		self.DType(r" \leftarrow ", sel=False)

	def script_T_right(self, gesture):
		self.DType(r" \rightarrow ", sel=False)

	def script_T_rightleft(self, gesture):
		self.DType(r" \rightleftharpoons ", sel=False)

	def script_T_leftright(self, gesture):
		self.DType(r" \leftrightarrow ", sel=False)

	def script_T_dot(self, gesture):
		self.DType(r"\dot{", sel=True, say="Single dot")

	def script_T_super(self, gesture):
		self.DType(r"^{", sel=True, altbf="^{")

	def script_T_sub(self, gesture):
		self.DType(r"_{", sel=True, altbf="_{")

	def script_T_NumPlus(self, gesture):
		self.DType(r"---\overset{+}{-}---", say="Plus range")

	def script_T_NumMinus(self, gesture):
		self.DType(r"---\overset{-}{-}---", say="Minus range")

	def script_T_NumCirc(self, gesture):
		self.DType(r"\overset{}{\circ", say="Open circle", force=True, offset=9)

	def script_T_NumUnd(self, gesture):
		self.DType(r"\overset{}{\underset{ \text{undefine}}{\circ}", say="Undefine", force=True, offset=9)

	def script_T_NumDef(self, gesture):
		self.DType(r"\overset{}{\underset{ \text{critical point}}{\bullet}", say="Critical point", force=True, offset=9)

	def script_T_NumFill(self, gesture):
		self.DType(r"\overset{}{\bullet", say="Close circle", force=True, offset=9)

	def script_T_NumConvex(self, gesture):
		self.DType(r"---\overset{+}{\underset{\text{concave up}}{-}}---", say="Concave up")

	def script_T_NumConcave(self, gesture):
		self.DType(r"---\overset{-}{\underset{\text{concave down}}{-}}---", say="Concave down")

	def script_T_NumIncreasing(self, gesture):
		self.DType(r"---\overset{+}{\underset{\text{increasing}}{-}}---", say="Increasing function")

	def script_T_NumDecreasing(self, gesture):
		self.DType(r"---\overset{-}{\underset{\text{decreasing}}{-}}---", say="Decreasing function")


	def script_T_NumUnion(self, gesture):
		self.DType(r"\cup", say="Union")

	def script_T_NumIntersect(self, gesture):
		self.DType(r"\cap", say="Intersect")

	def script_T_nabla(self, gesture):
		self.DType(r"\nabla ", sel=False, say="curl operator")

	def script_T_abs(self, gesture):
		self.DType(r"\|", sel=True, altbf=r"\|", altaf=r"\|")

	def script_T_l_brace(self, gesture):
		self.DType(r"\{", sel=True, altbf=r"\{", altaf=r"\}")

	def script_T_r_brace(self, gesture):
		self.DType(r"\}", sel=True, altbf=r"\{", altaf=r"\}")

	def script_T_approx(self, gesture):
		self.DType(r"\approx", sel=False)

	def script_T_bigbar(self, gesture):
		self.DType(r"\big|", sel=False)

	def script_T_ddot(self, gesture):
		self.DType(r"\ddot{", sel=True, say="Double dot")

	def script_T_in_n(self, gesture):
		self.DType(r"\in \mathbb{N}", sel=False, say="in natural number")

	def script_T_in_r(self, gesture):
		self.DType(r"\in \mathbb{R}", sel=False, say="in real number")

	def script_T_in_z(self, gesture):
		self.DType(r"\in \mathbb{Z}", sel=False, say="in integer")


	def script_T_copyblock(self, gesture):
		obj = api.getFocusObject()
		info = obj.makeTextInfo(textInfos.POSITION_CARET)
		buf = obj.makeTextInfo(textInfos.POSITION_CARET)
		buf.expand(textInfos.UNIT_LINE)
		lim = len(buf.text)
		#find the starting and ending point
		info.move(textInfos.UNIT_CHARACTER, 1, endPoint='end')
		for i in range(lim):
			if info.text[-1] == '}' or info.text[-1] == ')' or info.text[-1] == '$' or info.text[-1] == ']' or info.text[-1] == "\n":
				break
			info.move(textInfos.UNIT_CHARACTER, 1, endPoint='end')
		for i in range(lim):
			if info.text[0] == '{' or info.text[0] == '(' or info.text[0] == '$' or info.text[0] == ']' or info.text[0] == "\n":
				break
			info.move(textInfos.UNIT_CHARACTER, -1, endPoint='start')
		api.copyToClip(info.text)
		speech.speakText("copy " + info.text + " to the clipboard")

	def script_T_copywhole(self, gesture):
		cls_dolla = 0
		obj = api.getFocusObject()
		info = obj.makeTextInfo(textInfos.POSITION_CARET)
		buf = obj.makeTextInfo(textInfos.POSITION_CARET)
		buf.expand(textInfos.UNIT_LINE)
		lim = len(buf.text)
		#find the starting and ending point
		info.move(textInfos.UNIT_CHARACTER, 1, endPoint='end')
		for i in range(lim):
			if info.text[-1] == '}':
				break
			elif  info.text[-1] == "$":
				cls_dolla = 1
				break
			info.move(textInfos.UNIT_CHARACTER, 1, endPoint='end')
		for i in range(lim):
			if info.text[0] == '\\' or info.text[0] == '$' or info.text[0] == "\n":
				break
			info.move(textInfos.UNIT_CHARACTER, -1, endPoint='start')
		if cls_dolla == 1:
			info.text = info.text[0:-1]
			cls_dolla = 0
		api.copyToClip(info.text)
		speech.speakText("copy " + info.text + " to the clipboard")

	def script_T_copydolla(self, gesture):
		obj = api.getFocusObject()
		info = obj.makeTextInfo(textInfos.POSITION_CARET)
		buf = obj.makeTextInfo(textInfos.POSITION_CARET)
		buf.expand(textInfos.UNIT_LINE)
		lim = len(buf.text)
		#find the starting and ending point
		info.move(textInfos.UNIT_CHARACTER, 1, endPoint='end')
		for i in range(lim):
			if info.text[-1] == '$':
				break
			info.move(textInfos.UNIT_CHARACTER, 1, endPoint='end')
		for i in range(lim):
			if info.text[0] == '$':
				break
			info.move(textInfos.UNIT_CHARACTER, -1, endPoint='start')
		api.copyToClip(info.text)
		speech.speakText("copy " + info.text + " to the clipboard")

	def script_T_copyline(self, gesture):
		obj = api.getFocusObject()
		info = obj.makeTextInfo(textInfos.POSITION_CARET)
		info.expand(textInfos.UNIT_LINE)
		api.copyToClip(info.text)
		speech.speakText("copy " + info.text + " to the clipboard")

	def script_T_copypara(self, gesture):
		obj = api.getFocusObject()
		info = obj.makeTextInfo(textInfos.POSITION_CARET)
		info.expand(textInfos.UNIT_PARAGRAPH)
		api.copyToClip(info.text)
		speech.speakText("copy " + info.text + " to the clipboard")


	def script_store1(self, gesture):
		obj = api.getFocusObject()
		info = obj.makeTextInfo(textInfos.POSITION_SELECTION)
		text = info.text
		text = text.strip("\n")
		text = text.strip("\r")
		if info and len(text) > 0:
			msg = text
		else:
			msg = api.getClipData()
		self.slot1 = msg
		speech.speakText("store " + msg + " in slot 1")

	def script_store2(self, gesture):
		obj = api.getFocusObject()
		info = obj.makeTextInfo(textInfos.POSITION_SELECTION)
		text = info.text
		text = text.strip("\n")
		text = text.strip("\r")
		if info and len(text) > 0:
			msg = text
		else:
			msg = api.getClipData()
		self.slot2 = msg
		speech.speakText("store " + msg + " in slot 2")

	def script_store3(self, gesture):
		obj = api.getFocusObject()
		info = obj.makeTextInfo(textInfos.POSITION_SELECTION)
		text = info.text
		text = text.strip("\n")
		text = text.strip("\r")
		if info and len(text) > 0:
			msg = text
		else:
			msg = api.getClipData()
		self.slot3 = msg
		speech.speakText("store " + msg + " in slot 3")

	def script_store4(self, gesture):
		obj = api.getFocusObject()
		info = obj.makeTextInfo(textInfos.POSITION_SELECTION)
		text = info.text
		text = text.strip("\n")
		text = text.strip("\r")
		if info and len(text) > 0:
			msg = text
		else:
			msg = api.getClipData()
		self.slot4 = msg
		speech.speakText("store " + msg + " in slot 4")

	def script_store5(self, gesture):
		obj = api.getFocusObject()
		info = obj.makeTextInfo(textInfos.POSITION_SELECTION)
		text = info.text
		text = text.strip("\n")
		text = text.strip("\r")
		if info and len(text) > 0:
			msg = text
		else:
			msg = api.getClipData()
		self.slot5 = msg
		speech.speakText("store " + msg + " in slot 5")

	def script_store6(self, gesture):
		obj = api.getFocusObject()
		info = obj.makeTextInfo(textInfos.POSITION_SELECTION)
		text = info.text
		text = text.strip("\n")
		text = text.strip("\r")
		if info and len(text) > 0:
			msg = text
		else:
			msg = api.getClipData()
		self.slot6 = msg
		speech.speakText("store " + msg + " in slot 6")

	def script_store7(self, gesture):
		obj = api.getFocusObject()
		info = obj.makeTextInfo(textInfos.POSITION_SELECTION)
		text = info.text
		text = text.strip("\n")
		text = text.strip("\r")
		if info and len(text) > 0:
			msg = text
		else:
			msg = api.getClipData()
		self.slot7 = msg
		speech.speakText("store " + msg + " in slot 6")

	def script_store8(self, gesture):
		obj = api.getFocusObject()
		info = obj.makeTextInfo(textInfos.POSITION_SELECTION)
		text = info.text
		text = text.strip("\n")
		text = text.strip("\r")
		if info and len(text) > 0:
			msg = text
		else:
			msg = api.getClipData()
		self.slot8 = msg
		speech.speakText("store " + msg + " in slot 6")

	def script_recall1(self, gesture):
		self.DType(self.slot1, sel=False)

	def script_recall2(self, gesture):
		self.DType(self.slot2, sel=False)

	def script_recall3(self, gesture):
		self.DType(self.slot3, sel=False)

	def script_recall4(self, gesture):
		self.DType(self.slot4, sel=False)

	def script_recall5(self, gesture):
		self.DType(self.slot5, sel=False)

	def script_recall6(self, gesture):
		self.DType(self.slot6, sel=False)

	def script_recall7(self, gesture):
		self.DType(self.slot7, sel=False)

	def script_recall8(self, gesture):
		self.DType(self.slot8, sel=False)

	def script_recalllast(self, gesture):
		self.DType(self.slotlast, sel=False)

	def script_read1(self, gesture):
		speech.speakText("read as " + self.slot1)

	def script_read2(self, gesture):
		speech.speakText("read as " + self.slot2)

	def script_read3(self, gesture):
		speech.speakText("read as " + self.slot3)

	def script_read4(self, gesture):
		speech.speakText("read as " + self.slot4)

	def script_read5(self, gesture):
		speech.speakText("read as " + self.slot5)

	def script_read6(self, gesture):
		speech.speakText("read as " + self.slot6)

	def script_read7(self, gesture):
		speech.speakText("read as " + self.slot7)

	def script_read8(self, gesture):
		speech.speakText("read as " + self.slot8)

	def script_readlast(self, gesture):
		speech.speakText(self.slotlast)

	def script_T_check(self, gesture):
		obj = api.getFocusObject()
		info = obj.makeTextInfo(textInfos.POSITION_SELECTION)
		text = info.text
		if info and len(text) > 0:
			texcheck.main(text)
		else:
			info = obj.makeTextInfo(textInfos.POSITION_CARET)
			info.expand(textInfos.UNIT_PARAGRAPH)
			text = info.text
			texcheck.main(text)

	__gestures={
"kb:Control+Shift+a":"G_alpha",
"kb:Control+Shift+s":"G_bigsigma",
"kb:Control+Shift+d":"G_bigdelta",
"kb:Control+Shift+z":"G_zeta",
"kb:Control+Shift+x":"G_xi",
"kb:Control+Shift+c":"G_chi",
"kb:Control+Shift+q":"G_bigomega",
"kb:Control+Shift+w":"G_omega",
"kb:Control+Shift+e":"G_epsilon",
"kb:Control+Shift+f":"G_beta"
}

