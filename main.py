from shade import *
from json import dumps

simple_logging(debug=True)
conn = openstack_cloud(cloud='maas')

print("Images:")
images = conn.list_images()
for image in images:
    print(dumps(image,indent = 4, sort_keys=True))

print("Flavor:")
flavors =  conn.list_flavors()
for flavor in flavors:
    print(dumps(flavor,indent = 4, sort_keys=True))


image_id = '78ecb1ba-b44c-4277-833c-6268ae2045c1'
image = conn.get_image(image_id)
#print(dumps(image,indent = 4, sort_keys=True))


flavor_id = '0cb1f143-8b9a-4367-8ab3-9be101ceb305'
flavor = conn.get_flavor(flavor_id)
#print(dumps(flavor,indent = 4, sort_keys=True))

print('Checking for existing SSH keypair...')
keypair_name = 'maaskey'
pub_key_file = '/home/cloud/.ssh/id_rsa.pub'

if conn.search_keypairs(keypair_name):
    print('Keypair already exists. Skipping import.')
else:
    print('Adding keypair...')
    conn.create_keypair(keypair_name, open(pub_key_file, 'r').read().strip())

for keypair in conn.list_keypairs():
    print(keypair)

print('Checking for existing security groups...')
sec_group_name = 'paulo-sec'
if conn.search_security_groups(sec_group_name):
    print('Security group already exists. Skipping creation.')
else:
    print('Creating security group.')
    conn.create_security_group(sec_group_name, 'network access for all-in-one application.')
    conn.create_security_group_rule(sec_group_name, 80, 80, 'TCP')
    conn.create_security_group_rule(sec_group_name, 22, 22, 'TCP')

conn.search_security_groups(sec_group_name)

ex_userdata = '''#!/usr/bin/env bash
curl -L -s https://git.openstack.org/cgit/openstack/faafo/plain/contrib/install.sh | bash -s -- \
-i faafo -i messaging -r api -r worker -r demo
'''

instance_name = 'Paulo-Proto2'
testing_instance = conn.create_server(wait=True, auto_ip=False,
    name=instance_name,
    image=image_id,
    flavor=flavor_id,
    key_name=keypair_name,
    security_groups=['paulo-sec'],
    userdata=ex_userdata)

print(instance_name)

f_ip = conn.available_floating_ip(network="7196d7d8-426a-4d1b-9be4-4355acf59172")

print('The Fractals app will be deployed to http://%s' % f_ip['floating_ip_address'] )
