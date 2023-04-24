import dns.resolver
import sys

record_types = ['A', 'AAAA', 'NS', 'CNAME', 'MX', 'PTR', 'SOA', 'TXT']
domain = sys.argv[1]
for records in record_types:
    try:
        answer = dns.resolver.resolve(domain, records)
        print(f'\n{records} Records')
        print('-'*30)

        for server in answer:
            print(server.to_text()+'\n')
    except dns.resolver.NoAnswer:
        # print('No Records Found')
        pass
    except dns.resolver.NXDOMAIN:
        print(f'{domain} does not exists')
        quit()
    except KeyboardInterrupt:
        quit()