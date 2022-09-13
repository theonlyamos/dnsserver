import json

zones = {}
zones['$origin'] = "howcode.org."
zones["$ttl"] = 3600
zones['soa'] = {}
zones['soa']['mname'] = 'ns1.howcode.org.'
zones['soa']['rname'] = 'admin.howcode.org.'
zones['soa']['serial'] = "{time}"
zones['soa']['refresh'] = 3600
zones['soa']['retry'] = 600
zones['soa']['expire'] = 604800
zones['soa']['minimum'] = 86400
ns = zones['ns'] = []
ns.append({'host': 'ns1.howcode.org.'})
ns.append({'host': 'ns2.howcode.org.'})
a = zones['a'] = []
a.append({'name': '@', 'ttl': 400, 'value': '255.255.255.255'})
a.append({'name': '@', 'ttl': 400, 'value': '127.0.0.1'})
a.append({'name': '@', 'ttl': 400, 'value': '127.0.0.1'})

with open('zones/howcode.org.zone', 'wt') as file:
    json.dump(zones, file, indent=4)
