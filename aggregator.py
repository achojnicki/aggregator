import requests, re
import dns
import dns.resolver
import ipaddress
import json

TLD_REGEX=r"(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.){1,4}(?:[a-zA-Z]{2,63}|xn--[a-zA-Z0-9]{1,59})"

CLOUDFLARE_IPv4_URL="https://www.cloudflare.com/ips-v4"
CLOUDFLARE_IPv6_URL="https://www.cloudflare.com/ips-v6"
AWS_URL="https://ip-ranges.amazonaws.com/ip-ranges.json"

FILE_FORMAT="""\
#IPv4

##aws
{ipv4_aws}

##all_others
{ipv4}

#IPv6

##aws
{ipv6_aws}

##all_others
{ipv6}
"""

HOSTS_URLS=[
	"https://raw.githubusercontent.com/0n1cOn3/The-Paragon-Blacklist/main/hosts.txt",
	"https://raw.githubusercontent.com/0n1cOn3/The-Intellexa-Blocklist/main/hosts.txt",
	"https://raw.githubusercontent.com/0n1cOn3/The-Candiru-Blocklist/main/hosts.txt",
	"https://raw.githubusercontent.com/0n1cOn3/The-NSO-Blacklist/main/hosts.txt"
]

C2_URLS=[
	"https://raw.githubusercontent.com/0n1cOn3/The-Paragon-Blacklist/main/C2-hosts.txt",
	"https://raw.githubusercontent.com/0n1cOn3/The-Intellexa-Blocklist/main/C2-hosts.txt",
	"https://raw.githubusercontent.com/0n1cOn3/The-Candiru-Blocklist/main/C2-hosts.txt",
	"https://raw.githubusercontent.com/0n1cOn3/The-NSO-Blacklist/main/C2-hosts.txt"
]


SUCCESS_IPv4=0
SUCCESS_IPv6=0
NXDOMAIN_IPv4=0
NXDOMAIN_IPv6=0
EXCPT=0
SUCCESS_IPv4_AWS=0
SUCCESS_IPv6_AWS=0

ipv4_addr=[]
aws_ipv4_addr=[]
ipv6_addr=[]
aws_ipv6_addr=[]
subnets_cloudflare=[]
subnets_aws=[]
subnets_cloudfront=[]

domains=[]
results=[]

print('Downloading cloudflare ipv4 address range')
r=requests.get(CLOUDFLARE_IPv4_URL)
d=r.text
d=d.split('\n')

subnets_cloudflare=subnets_cloudflare+d


print('Downloading cloudflare ipv6 address range')
r=requests.get(CLOUDFLARE_IPv6_URL)
d=r.text
d=d.split('\n')

subnets_cloudflare=subnets_cloudflare+d

print('Downloading aws ip address range')
r=requests.get('https://ip-ranges.amazonaws.com/ip-ranges.json')
d=r.json()

for prefix in d['prefixes']:
	if prefix['service'] != 'CLOUDFRONT' and prefix['service'] !='GLOBALACCELERATOR':
		subnets_aws.append(prefix['ip_prefix'])
	else:
		subnets_cloudfront.append(prefix['ip_prefix'])

for prefix in d['ipv6_prefixes']:
	if prefix['service'] != 'CLOUDFRONT' and prefix['service'] !='GLOBALACCELERATOR':
		subnets_aws.append(prefix['ipv6_prefix'])
	else:
		subnets_cloudfront.append(prefix['ipv6_prefix'])

def clean_up(data):
	ready=""
	data=data.split('\n')
	for l in data:
		if len(l)>0 and l[0]!="#":
			ready+=l+"\n"
	return ready
	

def join(data):
	r=""
	for x in data:
		r+=x+"\n"
	return r

def in_any(ip_str, cidrs):
    ip = ipaddress.ip_address(ip_str)
    for c in cidrs:
        net = ipaddress.ip_network(c, strict=False)
        if ip.version == net.version and ip in net:
            return True
    return False

def print_stats():
	print(f"success_ipv4: {SUCCESS_IPv4}, SUCCESS_IPv6: {SUCCESS_IPv6}")
	print(f"success_ipv4_aws: {SUCCESS_IPv4_AWS}, SUCCESS_IPv6_AWS: {SUCCESS_IPv6_AWS}")

	print(f"NXDOMAIN_IPv4: {NXDOMAIN_IPv4}, NXDOMAIN_IPv6: {NXDOMAIN_IPv6}")
	print(f"EXCPT: {EXCPT}")




for url in HOSTS_URLS+C2_URLS:
	r=requests.get(url)
	results.append(clean_up(r.text))



for result in results:
	r=re.findall(TLD_REGEX, result)
	domains=domains+r





for domain in domains:
	#ipv4
	try:
		res=dns.resolver.resolve(domain,'a')
		for d in res:
			addr=d.to_text()
			if addr not in ipv4_addr and not in_any(addr, subnets_cloudflare) and not in_any(addr,subnets_aws) and not in_any(addr, subnets_cloudfront):
				ipv4_addr.append(addr)
				SUCCESS_IPv4+=1

			elif addr not in aws_ipv4_addr and not in_any(addr, subnets_cloudflare) and not in_any(addr,subnets_cloudfront) and in_any(addr,subnets_aws):
				aws_ipv4_addr.append(addr)
				SUCCESS_IPv4_AWS+=1


	except dns.resolver.NXDOMAIN:
		NXDOMAIN_IPv4+=1

	except:
		EXCPT+=1

	#ipv6
	try:
		res=dns.resolver.resolve(domain,'aaaa')
		for d in res:
			addr=d.to_text()
			if addr not in ipv6_addr and not in_any(addr, subnets_cloudflare) and not in_any(addr,subnets_aws) and not in_any(addr, subnets_cloudfront):
				ipv6_addr.append(addr)
				SUCCESS_IPv6+=1

			elif addr not in aws_ipv6_addr and not in_any(addr, subnets_cloudflare) and not in_any(addr,subnets_cloudfront) and in_any(addr,subnets_aws):
				aws_ipv6_addr.append(addr)
				SUCCESS_IPv6_AWS+=1


	except dns.resolver.NXDOMAIN:
		NXDOMAIN_IPv6+=1

	except:
		EXCPT+=1

	if domains.index(domain)%10==0:
		print_stats()




with open('out.txt', 'w') as file:
	file.write(
		FILE_FORMAT.format(
			ipv4=join(ipv4_addr), 
			ipv4_aws=join(aws_ipv4_addr),
			ipv6=join(ipv6_addr),
			ipv6_aws=join(aws_ipv6_addr),
			
			)

		)
