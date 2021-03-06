# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp.osv import orm
from openerp.tools.translate import _
from openerp.osv import osv, fields
from openerp.exceptions import except_orm

import requests, json
import sys, os
from bs4 import BeautifulSoup
from rnc_wolftrak import Rnc

#Json Configuration file name 
main_base = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE_NAME = "config.json"      
CONFIG_FILE = os.path.join(main_base, CONFIG_FILE_NAME)

def load_config(json_file):
	"""
	Loading configuration from json file
	"""  
	with open(json_file, 'r') as file:    
		config_data = json.load(file)            
	return config_data
  
def get_rnc_record(cedula_rnc, config_data = None):
	"""
	Create and return a Rnc record by parsing the website from configuration
	"""  
	#Loading common parameters  
	if not config_data:
		config_data = load_config(CONFIG_FILE)  
	req_headers = config_data['request_headers'] 
	req_cookies = config_data.get('request_cookies')     
	req_params = config_data['request_parameters']    
	uri = ''.join([config_data['url'], config_data['web_resource']])  
  
	#Setting the default parameter
	req_params['txtRncCed'] = cedula_rnc
	#Making the request 
	result = requests.get(uri, params = req_params, headers=req_headers)  
	if result.status_code == requests.codes.ok:
		#Http request was successful, parsing...
		soup = BeautifulSoup(result.content)             
		data_rows  = soup.find('tr', attrs={'class': 'GridItemStyle'})
		# if not data_rows:
		# 	raise Exception(config_data['not_found_string'])
		# else:
		#comentado debido a que se utilizará try para pasar los except
		try:
			tds = data_rows.findChildren('td')   
			rnc_vals = [str(td.text.strip()) for td in tds]
			rnc = Rnc(rnc_vals)    
			# return rnc
			return rnc_vals
		except :
			pass

class wolftrak_new2(osv.Model):
	_name = "res.partner"
	_inherit = "res.partner"

	_columns = {
		'ci'		   : fields.char('Documento de Identificacion', help='Documento de Identificacion'),
		'estado'	   : fields.char(string='Estado'),
		'regimen_pago' : fields.char(string='Regimen de Pago')
	}

	@api.onchange('ci')
	def user_validation(self):
		# Realiza la comparacion del dato que se insertara con los registrados en la base de datos
		db_ci = self.search([('ci', '=', self.ci)])
		if db_ci and self.ci:
			# limpia los campo si el documento de identidad esta registrado
			self.ci = ''
			self.name = ''
			self.estado = ''
		# pasado el rroceso de busqueda de rnc por try para evitar la generacion de ventanas de error
		try:
			rnc_record = get_rnc_record(self.ci)
			self.name = rnc_record[1]
			self.estado = rnc_record[5]
			self.regimen_pago = rnc_record[4]
		except :
			pass
	
		# raise orm.except_orm(_("Warning"),_(""" Este documento ya esta registrado """),)


	 
