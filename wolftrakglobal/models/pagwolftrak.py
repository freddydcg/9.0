from openerp import models, fields, api
from openerp.osv import orm
from openerp.tools.translate import _

from bs4 import BeautifulSoup
from lxml import etree
from io import StringIO, BytesIO
import requests
import lxml
import time

class pag_wolftrak(models.Model):
	_name = 'pag.wolftrak.search'
	_description = "Paginas Amarillas Buscador"

	busc 	 = fields.Char(string='Busqueda')
	fh_busc  = fields.Date(string='Fecha de Busqueda', default=time.strftime('%Y-%m-%d'))
	pag_line = fields.One2many('pag.wolftrak.line', 'empresa', 'tlf')

	# @api.onchange('busc')
	# @api.depends('busc')
	@api.one
	def searching(self):
		keyword = self.busc
		if type(keyword) != bool:
			keyword = keyword.replace(' ','-')
			k = 1
			emplist = []
			tlflist = []
			while k <= 5:
				j = str(k)
				link = 'http://www.paginasamarillas.com.do/Searchpg.aspx?nombre='+keyword+'&ciudad=Santo+Domingo&showQuantity=100&order=Relevancia&currentPage='+j+'&classCode=&subClassCode=&keyword=&other=&latitude=&longitude=&filter=true'
				print link
				page = requests.get(link)
				content = page.content
				soup = BeautifulSoup(content, 'lxml')
				s_body = soup.body
				s_body_span = s_body.find_all('span')
				data = [] 
				for span in s_body_span:
					if span.parent.name == 'a' and span.attrs and span.attrs != {'class': ['search-cat']} and span.attrs != {'itemprop': 'streetAddress'} and span.attrs != {'itemprop': 'addressLocality'} and span.string != ', ':
						data.append(span.string)
				meta=[]
				for n in range(len(data)):
					if n%2 == 0:
						meta.append(data[n:n+2])
				for n in meta:
					emplist.append(n[0])
					tlflist.append(n[1])
					line_result = self.pag_line.create({'empresa': n[0], 'tlf': n[1]})
					self.busc = line_result
				k+=1
			
			# funciona...
			# mayorlist = []
			# for n in emplist:
			# 	result={}
			# 	result.update({'srch_id':n})
			# 	mayorlist.append(result)
			# self.pag_line = mayorlist
			# i = 0
			# for m in self.pag_line:
			# 	m.empresa = emplist[i]
			# 	m.tlf = tlflist[i]
			# 	i += 1
			# emplist = []
			# tlflist = []

		else:
			self.empresa = ''
			self.tlf = ''

class pag_line(models.Model):
	_name = 'pag.wolftrak.line'

	empresa = fields.Char(string="Empresa")
	tlf 	= fields.Char(string="Telefono")
	search_id = fields.Many2one('pag.wolftrak.search')
	estatus = fields.Boolean(string="Completado", default=False)

	@api.one
	def to_lead(self):
		return {
		'name' : ('crm.lead'),
		'view_type' : 'form',
		'view_mode' : 'form',
		'res_model' : 'crm.lead',
		'view_id' : False,
		'type' : 'ir.actions.act_window',
		'target' : 'new'
		}