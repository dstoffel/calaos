# -*- coding: utf-8 -*-
from automation import *
import calaos_config as cfg 
class calaos(automation):
	def __init__(self):
                super(calaos, self).__init__()
                for rule in cfg.rules:
                        self.register_rule(rule)

	def callback(self, data, m, rdata):
		try:
			state = m.group('value')
		except IndexError:
			state = cfg.state[data['action']]

		output = data['out']
		self.log('executing : %s ' % data)
		return self.set_state(state, output)

	#https://calaos.fr/wiki/fr/protocole_json
	def do_calaos(query):
		data = {'cn_user' : cfg.user, 'cn_pass' : cfg.pw}
		data.update(query)
		debug(data)
		r = requests.post(cfg.url, json=data,verify=0)
		return r.json()

	def get_state(self,ref):
		self.debug('getting state for %s ' % (ref))
		query = {'outputs' : ref}
		r  = self.do_calaos({'action': 'get_state', 'outputs' : [ref], 'inputs' : [ref]})
		current_state = r['outputs'][ref]
		self.debug('current state for %s is %s ' % (ref, current_state))
		return r['outputs'][ref]

	def set_state(self,state,ref):
		if cfg.sym:
			self.debug('set_state %s to %s SIMULATE, DONE' % ( ref, state))
			return "c'est fait"
		#TODO: handle correctly array
		if str(type(ref)) == "<type 'list'>":
			for r in ref:
				set_state(state,r)
			return "c'est fait"
		current_state = self.get_state(ref)
		self.log('setting state %s for %s ' % (state, ref))
		if current_state == state:
			self.debug('ref %s already in state %s' % (ref, state))
			return "c'est déjà fait"
		query = {'action' : 'set_state', 'id' : ref, 'value' : state, 'type': 'output'}
		r = self.do_calaos(query)
		if r['success'] != 'true':
			self.debug('set_state %s to %s ERROR' % ( ref, state))
			return "une erreur est intervenue"
		else:
			self.debug('set_state %s to %s done' % ( ref, state))
			return "c'est fait"

