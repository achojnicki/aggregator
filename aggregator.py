import requests, re
import dns
import dns.resolver

TLD_REGEX=r"(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.){1,4}(?:[a-zA-Z]{2,63}|xn--[a-zA-Z0-9]{1,59})"


FILE_FORMAT="""\
#IPv4

{ipv4}

#IPv6

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
EMPTY_IPv4=0
EMPTY_IPv6=0
EXCPT=0

ipv4_addr=[]
ipv6_addr=[]

domains=[]
results=[]

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

def print_stats():
	print(f"success_ipv4: {SUCCESS_IPv4}, SUCCESS_IPv6: {SUCCESS_IPv6}")
	print(f"EMPTY_IPv4: {EMPTY_IPv4}, EMPTY_IPv6: {EMPTY_IPv6}")
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
			if addr not in ipv4_addr:
				ipv4_addr.append(d.to_text())
		
		if len(res)>0:
			SUCCESS_IPv4+=1
		else:
			EMPTY_IPv4+=1

	except dns.resolver.NXDOMAIN:
		NXDOMAIN_IPv4+=1

	except:
		EXCPT+=1

	#ipv6
	try:
		res=dns.resolver.resolve(domain,'aaaa')
		for d in res:
			addr=d.to_text()
			if addr not in ipv6_addr:
				ipv6_addr.append(d.to_text())
		
		if len(res)>0:
			SUCCESS_IPv6+=1
		else:
			EMPTY_IPv6+=1

	except dns.resolver.NXDOMAIN:
		NXDOMAIN_IPv6+=1

	except:

		EXCPT+=1
	print_stats()




with open('out.txt', 'w') as file:
	file.write(
		FILE_FORMAT.format(
			ipv4=join(ipv4_addr), 
			ipv6=join(ipv6_addr)
			)
		)
