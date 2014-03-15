#!/usr/bin/python
import sys
import time
from collections import defaultdict

def main (argv):

	#print lines
	a = createfsm('a')
	#a.closureFsm()
	b = createfsm('b')
	a.concatFsm(b)
	b.closureFsm()
	b.concatFsm(a)
	output = open("out.dot", 'w')
	print >> output, b.dotGenerator()
	output.close()
	#print nfa.nodes[0].tlist.items()

def inProc (argv):
	global out	
	if len(argv) < 2 : 
		lines = sys.stdin.readlines()	
		out = "out.dot"
	else:
	
		arg1 = argv[1]
		file = None
		try:
			file = open(arg1)
		except IOError as e:
			print "Unable to open file"
		lines = file.readlines()
		out = file.name.split('.')[0]
		out += ".dot"
	return lines

def createfsm(char) :
	nfa = fsm('NFA', 3)
	anode = node(0)
	bnode = node(1)
	cnode = node(2)
	anode.tlist['EPSILON'].append(1)
	bnode.tlist[char].append(2)
	nfa.symbols.append('EPSILON')
	nfa.symbols.append(char)
	nfa.addNode(anode)
	nfa.addNode(bnode)
	nfa.addNode(cnode)
	return nfa
	
class fsm:
	def __init__ (self, title, stateCount):
		self.title = title
		self.totalstates = stateCount
		self.finalstate = stateCount-1
		self.nodes = []
		self.symbols = []

	def returnNode(self, state):
		for node in self.nodes:
			if state is node.state:
				return node
		return None

	def addNode(self, anode):
		if self.returnNode(anode.state) is None:
			#print 'not in the fsm'
			self.nodes.append(anode)
	
	def getNextStates(self, state, char):
		char.strip()
		statesList = []
		for node in self.nodes:
			if state is node.state:
				#node.visited = True
				for v in node.tlist[char]:
					statesList.append(v)
				epsList = list(node.tlist['EPSILON'])
				#print '1.', epsList
				while len(epsList) > 0:
					#time.sleep(5)
					el = int(epsList[0])
					anode = self.returnNode(el)
					#print '2.', anode.state
					if anode.visited is False:
						anode.visited = True
						for v in anode.tlist[char]:
							#print 'alu', v
							if v not in statesList:
								statesList.append(v)
					epsList = epsList[1:]
					temp = []
					for it in epsList:
						bnode = self.returnNode(int(it))
						if bnode.visited is False:
							temp.append(it)
					#print "temp " , temp, 
					epsList = list(temp)
					#print epsList, len(epsList)
					for ll in anode.tlist['EPSILON']:
						cnode = self.returnNode(int(ll))
						if cnode.visited is False:
							if cnode.state not in epsList:
								epsList.insert(0,cnode.state)
					#print "new " ,epsList
				
		#print char, statesList
		self.clearNodes()
		return statesList	

	def addTNode(self, char) :
		# adds a new node with char transition to the fsm
		final = self.finalstate
		prevFNode = self.returnNode(final)
		fNode = node(final+1) #add char transition state
		
		prevFNode.tlist[char].append(final+1) # add transition from the previous final to the new node
		if char not in self.symbols:
			self.symbols.append(char)
		#1 more state added and this is the final state
		self.totalstates = self.totalstates+1
		self.finalstate = final+1
		
	def concatFsm(self, fsm1) :
		#add fsm1 to the tail of this fsm
		#check if fsm1's state 0 has just 1 or more transitions
		final = self.finalstate
		#combine self.finalstate and fsm1.startingstate
		anode = self.returnNode(final)
		bnode = fsm1.returnNode(0)
		#count branches of nodes from bnode
		count = 0
		for c in bnode.tlist.keys():
			for i in bnode.tlist[c]:
				count += 1
		start = 1
		newtotal = self.totalstates + fsm1.totalstates -1
		newfinal = newtotal-1
		#if count is 1 it is safe to remove this node and the next one
		if count == 1 :
			bnode = fsm1.returnNode(1)
			start = 2
			newtotal = newtotal - 1
			newfinal = newtotal - 1
		
		index = start - 1	
		for c in bnode.tlist.keys():
			if c not in self.symbols:
				self.symbols.append(c)
			for i in bnode.tlist[c]:
				anode.tlist[c].append(final+i-index)
		#now copies the the rest of nodes from fsm1 to self
		self.copyNodes(fsm1, start)
		#change finalstate and totalstates
		self.totalstates = newtotal
		self.finalstate = newfinal
		
	def copyNodes(self, fsm1, start) :
		#start copying from state 1 
		final = self.finalstate
		index = start - 1
		#add the nodes to self
		for i in range(start, fsm1.totalstates):
			self.addNode(node(final+i-index))
			
		for i in range(start, fsm1.totalstates) :
			anode = fsm1.returnNode(i)
			bnode = self.returnNode(final+i-index)
			for c in anode.tlist.keys() :
				if c not in self.symbols:
					self.symbols.append(c)
				for j in anode.tlist[c]:
					bnode.tlist[c].append(final+j-index)
		
					
			
	def unionFsm(self, fsm1) :
		#add fsm2 to a new branch to state 0 of self
		anode = self.returnNode(0)
		bnode = fsm1.returnNode(0)
		final = self.finalstate
		
		for c in bnode.tlist.keys():
                        for i in bnode.tlist[c]:
                                anode.tlist[c].append(final+i)
		#now copies the rest of nodes from fsm1 to self
		self.copyNodes(fsm1,1)
		#now add a final state to join these two fsms
		newfinal = self.totalstates + fsm1.totalstates - 1
		self.addNode(node(newfinal))
		#point previous finals from self and fsm1 to the new final
		self.returnNode(final).tlist['EPSILON'].append(newfinal)
		self.returnNode(newfinal-1).tlist['EPSILON'].append(newfinal)
		
		#fix a problem when fsm1 is a closure
		lastnode = fsm1.returnNode(fsm1.finalstate)
		if 0 in lastnode.tlist['EPSILON']:
			anode = self.returnNode(newfinal-1)
			anode.tlist['EPSILON'].remove(final)
			anode.tlist['EPSILON'].append(0)
			
		#update totalstates and final state
		self.totalstates = newfinal + 1
		self.finalstate = newfinal
		
	def closureFsm(self) :
		#make a closure to this fsm
		final = self.finalstate
		#add a final node to the fsm
		newfinal = node(final+1)
		newfinal.tlist['EPSILON'].append(0)
		self.addNode(newfinal)
		#now point the previous final to the new final
		self.returnNode(final).tlist['EPSILON'].append(final+1)
		#also point state 0 to new final
		self.returnNode(0).tlist['EPSILON'].append(final+1)
		#update totalstates and finalstate for the fsm
		self.totalstates = final + 2
		self.finalstate = final + 1
	
	def read(self, transitions, count):
		
		for i in range(0, count):
			line = transitions[i].strip()
			#print (line)
			line = line[1:-1] #removing the outer parenthesis
			tokens = line.split(',')
			state = int(tokens[0])
			anode = self.returnNode(state)
			newnode = False
			if anode is None:
				anode = node(state)
				newnode = True
				self.addNode(anode)

			symbol = tokens[1]
			if symbol not in self.symbols:
				self.symbols.append(symbol)
			#print (symbol)
			for token in tokens[2:]:
				state = int(token.strip(')('))
				#print (token)
				self.addNode(node(state)) #adds node to nfa if not already present
				anode.tlist[symbol].append(state)
			if newnode:
				self.addNode(anode)
			#print self.nodes[0].tlist.items()
		
	def dotGenerator(self):
		lines = "digraph fsm {\nrankdir=\"LR\"\n"
		lines += "start [shape=\"plaintext\", label=\"start\"]\n"
		max = len(self.nodes)
		for i in range (0, max-1):
			lines += "{} [shape=\"circle\",label=\"S{}\"]\n".format(i+1, i)
		lines += "{} [shape=\"doublecircle\",label=\"S{}\"]\n".format(max, max-1)
		lines += "start->1\n"
		
		for i in range (0, len(self.nodes)):
			anode = self.nodes[i]
			state = anode.state
			for char in anode.tlist:
				#print char, 
				for endstate in anode.tlist[char]:
					#print endstate,
					lines += "{}->{} [label=\"{}\"]\n".format(state+1, endstate+1, char)
		lines += "}"
		return lines
	
	def clearNodes(self):
		for node in self.nodes:
			node.visited = False
			
	def simulate(self, input):
		input = input.strip()
		#print input
		if len(input) is 0:
			return False 
		next = []
		first = input[0]
		if first not in self.symbols:
			return False
		next = self.getNextStates(0,input[0])
		#print "next ", next
		input = input[1:] #remove the first character
		for c in input:
			#print "next ", next
			if c not in self.symbols:
				return False
			#print next
			temp = []
			for item in next:
				nextTemp = self.getNextStates(item,c)
				for it in nextTemp:
					if it not in temp:
						temp.append(it)
			next = temp
		#print next
		self.clearNodes() #removes visited mark
		if self.finalstate in next:
			return True
		else: 
			return False

class node:
	def __init__ (self, state):
		self.state = int(state)
		self.visited = False
		self.tlist = defaultdict(list)

if __name__ == '__main__':
	sys.exit(main(sys.argv))
#else :
	#print "Can't run main. I am imported"
