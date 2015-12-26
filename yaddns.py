import requests
import click

PDD_BASE = 'https://pddimp.yandex.ru/'


@click.command()
@click.option('--domain', help='Base domain name')
@click.option('--subdomain', help='Subdomain name', default='ddns')
@click.option('--token', help='PddToken auth token (get one here: https://pddimp.yandex.ru/api2/admin/get_token)')
def main(domain, subdomain, token):
    ip_address = requests.get('https://api.ipify.org').text
    print('Your public facing IP address is', ip_address)

    def pdd_call(method, url, params):
        return method(PDD_BASE + url, params, headers={'PddToken': token}).json()

    def pdd_get(url, params):
        return pdd_call(requests.get, url, params)

    def pdd_post(url, params):
        return pdd_call(requests.post, url, params)

    for record in pdd_get('/api2/admin/dns/list', {'domain': domain})['records']:
        if record['type'] == 'A' and record['subdomain'] == subdomain:
            print('Found existing record, updating...')
            print('Existing record ID:', record['record_id'])
            pdd_post('/api2/admin/dns/edit', {
                'record_id': record['record_id'],
                'domain': domain,
                'type': 'A',
                'content': ip_address,
                'subdomain': subdomain
            })
            break
    else:
        print("Didn't find a record, creating...")
        pdd_post('/api2/admin/dns/add', {
            'domain': domain,
            'type': 'A',
            'content': ip_address,
            'subdomain': subdomain
        })
    print('Done!')


if __name__ == "__main__":
    main()
