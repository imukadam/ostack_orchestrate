#!/usr/local/bin/python2.7

import applogger
import os
import sys

import config

from os.path import basename
import time

# Set encoding type to UTF8
reload(sys)
sys.setdefaultencoding('UTF8')

if applogger.chkLogger() > 0:
    logger = applogger.getLogger()
else:
    logger = applogger.setLogger()
logger.debug(msg='Running %s' % os.path.basename(__file__))

def list_zones(session, domain=None):
	'''
	Lists DNS zones available on a tenant
	'''
	if domain is None:
		return session.zones.list()
	else:
		# Check domain is correct format
		if not domain.endswith('.'):
			domain += "."
		domain_filter = filter(lambda name: name['name'] == domain, list_zones(session))
		if len(domain_filter) == 0:
			logger.error('Could not find zone %s' % domain)
			return None

		return domain_filter[0]


def list_records(session, zone_id, domain=None):
	'''
	Lists DNS records that are available to a tenant or tenant's domain
	'''
	if domain is None:
		records = session.recordsets.list(zone_id)
		if len(records) == 0:
			logger.error('Could not find any records in zone %s' % zone_id)
			return None
		
		return records
	else:
		# Check domain is correct format
		if not domain.endswith('.'):
			domain += "."
		
		domain_filter = [] 
		for record in list_records(session, zone_id):
			if record['name'] == domain:
				domain_filter.append(record)

		if len(domain_filter) == 0:
			logger.error('Could not any records for domain %s' % domain)
			return None

		return domain_filter


def create_record(session, zone_id, name, record_type, records, description=None, ttl=None):
	'''
	Adds new DNS record
	'''
	logger.info('Creating DNS record %s in zone %s' % (name, zone_id))
	# Set time to live if it is not already set
	if ttl is None:
		ttl = 120

	my_record = session.recordsets.create(zone=zone_id, name=name, type_=record_type, records=records, description=description, ttl=ttl)
	return my_record


def delete_record(session, zone_id, record_id):
	'''
	Deletes a DNS record
	'''
	logger.warn('Deleting record %s from zone %s' % (record_id, zone_id))
	session.recordsets.delete(zone=zone_id, recordset=record_id)

