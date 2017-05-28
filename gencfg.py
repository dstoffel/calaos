from xml.dom import minidom
exclude_rooms=['automatisme','chauffage','alarme']
xmldoc = minidom.parse('io.xml')
rooms = xmldoc.getElementsByTagName('calaos:room')
out=''


data = {}

def c(s):
	o = s.lower()
	o = o.replace('-', ' ')
	o = o.replace('[dim]', '')
	o = o.replace('[', '')
	o = o.replace(']','')
	o = o.replace('(', '')
	o = o.replace(')','')
	return o.lower().strip()
		

for room in rooms:
	roomname = c(room.attributes['name'].value)
	if roomname in exclude_rooms:
	#	prin 'escaping %s' % name
		continue
	#print "----------- %s -----------" % name	
	outputs = room.getElementsByTagName('calaos:output')
	inputs = room.getElementsByTagName('calaos:input')
	for output in outputs:
		i = output.attributes['id'].value
		t = output.attributes['type'].value
		n = c(output.attributes['name'].value)
		if not n in data:
			data[n] = {'inputs': [], 'outputs': []}
			data[n] = {}
		if not roomname in data[n]:
			data[n][roomname] = {'outputs': []}

		data[n][roomname]['outputs'].append((c(i), t))

value_e = ',execonwait=True, context=False, childs=[c_val]'
out = "rules = [\n\tRule(id='action', pattern='(allume|eteins)', out='quoi?', childs=["
for what in data:
	c=[]
        for room in data[what]:
                for output in data[what][room]['outputs']:
			t = output[1]
			if t == 'WODigital':
				r = "\n\t\t\tRule(id='where', pattern='%s', out='%s')," % (room, output[0])
			elif t == 'WODali':
				r = "\n\t\t\tRule(id='where', pattern='%s', out='%s'%s)," % (room, output[0], value_e) 
			else:
				continue
			c.append(r)
	if len(c) != 0:
		out += "\n\t\tRule(id='what', pattern='%s', out='laquel?', childs=[" % what
		out += ''.join(c)
		out += "\n\t\t]),"
out += "\n\t]),\n\tRule(id='action', pattern='(ouvre|ferme|arrete)', out='quoi?', childs=["
for what in data:
	c=[]
        for room in data[what]:
                for output in data[what][room]['outputs']:
			t = output[1]
			if t == 'WOVoletSmart':
				r = "\n\t\t\tRule(id='where', pattern='%s', out='%s'%s)," % (room, output[0], value_e) 
			else:
				continue
			c.append(r)
	if len(c) != 0:
		out += "\n\t\tRule(id='what', pattern='%s', out='laquel?', childs=[" % what
		out += ''.join(c)
		out += "\n\t\t]),"
out += "\n\t])"
out += "\n]"
print out
