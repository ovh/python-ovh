# -*- encoding: utf-8 -*-

import datetime
from tabulate import tabulate
import ovh

# Services type desired to mine. To speed up the script, delete service type you don't use!
service_types 	= [ 
	'allDom',
	'cdn/dedicated',
	'cdn/website',
	'cdn/webstorage',
	'cloud/project',
	'cluster/hadoop',
	'dedicated/housing',
	'dedicated/nas',
	'dedicated/nasha',
	'dedicated/server',
	'dedicatedCloud',
	'domain/zone',
	'email/domain',
	'email/exchange',
	'freefax',
	'hosting/privateDatabase',
	'hosting/web',
	'hosting/windows',
	'hpcspot',
	'license/cloudLinux',
	'license/cpanel',
	'license/directadmin',
	'license/office',
	'license/plesk',
	'license/sqlserver',
	'license/virtuozzo',
	'license/windows',
	'license/worklight',
	'overTheBox',
	'pack/xdsl',
	'partner',
	'router',
	'sms',
	'telephony',
	'telephony/spare',
	'veeamCloudConnect',
	'vps',
	'xdsl',
	'xdsl/spare',
]
# Delay before expiration in days
delay = 60

# Create a client using ovh.conf
client = ovh.Client()

# Compute now + delay
delay_date = datetime.datetime.now() + datetime.timedelta(days=delay)

services_will_expired = []

# Checking all OVH product (service type)
for service_type in service_types:
	service_list = client.get('/%s' % service_type )

	# If we found you have this one or more of this product, we get these informations
	for service in service_list:
		service_infos = client.get('/%s/%s/serviceInfos' % (service_type, service) )
		service_expiration_date = datetime.datetime.strptime(service_infos['expiration'], '%Y-%m-%d')

		# If the expiration date is before (now + delay) date, we add it into our listing
		if service_expiration_date < delay_date:
			services_will_expired.append( [ service_type, service, service_infos['status'], service_infos['expiration'] ] )
			
# At the end, we show service expirated or that will expirated (in a table with tabulate)
print tabulate(services_will_expired, headers=['Type', 'ID', 'status', 'expiration date'])
