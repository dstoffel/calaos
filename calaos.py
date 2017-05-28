# -*- coding: utf-8 -*-
from automation import *
import calaos_config as cfg 
class calaos(automation):
	def __init__(self):
                super(calaos, self).__init__()
                for rule in cfg.rules:
                        self.register_rule(rule)

	def callback(self, data, m, rdata):
		print data
		if type(data['where_out']) == type([]):
			refs = data['where_out']
		else:
			refs = [data['where_out']]

		vals = {}
		for ref in refs:
			if 'input_' in ref:
				vals[ref] = 'true'
			else:
				try:
					state = m.group('value')
					state = 'set %s' %state
				except IndexError:
					state = cfg.state[data['action']]
				vals[ref] = state

		self.log('executing : %s ' % vals)
		return self.set_state(vals)

	#https://calaos.fr/wiki/fr/protocole_json
	def do_calaos(self, query):
		data = {'cn_user' : cfg.user, 'cn_pass' : cfg.pw}
		data.update(query)
		self.debug('Sending to calaos : %s' % data)
		r = requests.post(cfg.url, json=data,verify=0)
		return r.json()

	def get_state(self,ref):
		self.debug('getting state for %s ' % (ref))
		if str(type(ref)) == type([]):
			r  = self.do_calaos({'action': 'get_state', 'outputs' : ref, 'inputs' : [ref]})
			return r['ouputs']
		else:
			r  = self.do_calaos({'action': 'get_state', 'outputs' : [ref], 'inputs' : [ref]})
			current_state = r['outputs'][ref]
			self.debug('current state for %s is %s ' % (ref, current_state))
			return r['outputs'][ref]

	def set_state(self,vals):
		queries = []
		i = 0
		for ref in vals:
			if 'input' in ref:
				t = 'input'
				i = 1
			else:
				t = 'output'
			state = vals[ref]
			query = {'action' : 'set_state', 'id' : ref, 'value' : state, 'type': t}
			queries.append(query)

		self.debug("calaos rules : %s" % queries)
		if cfg.sym:
			self.debug('set_state %s  SIMULATE, DONE' %  vals)
			return "c'est fait"

		if i:
			e = 0
			for q in queries:
				r = self.do_calaos(q)
				if r['success'] != 'true':
					e=1
			if e:
				return "une erreur est intervenue"
			else:
				return "c'est fait"
		else:
			diff = 0
			for q in queries:
				if q['value'] != self.get_state(q['id']):
					diff = 1
			if diff:
				e = 0
				for q in queries:
					r = self.do_calaos(q)
					if r['success'] != 'true':
						e=1
				if e:
					return "une erreur est intervenue"
				else:
					return "c'est fait"

			else:
				return "c'est déjà fait"
		
