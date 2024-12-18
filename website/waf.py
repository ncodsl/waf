from .request import Request, DBController
from .classifier import ThreatClassifier
import urllib
from flask import request, jsonify
import requests
from twilio.rest import Client
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

db = DBController()
threat_clf = ThreatClassifier()
req = Request()


class WAF(object):
    def __init__(self):
        pass
    
    def test():
        print('*' * 100)
        haders = dict(request.headers)
        host = urllib.parse.unquote(request.headers.get('Host'))
        path_request = urllib.parse.unquote(request.full_path)
        method = request.method
        body = []
        for i in list(request.form.values()):
            body.append(urllib.parse.unquote(i))

        ip = request.headers.get('Cf-Connecting-Ip')  # source ip
        src_port = request.environ.get('REMOTE_PORT')

        # Get geolocation data first with proper error handling
        try:
            geo_response = requests.get(
                f'https://api.ip2location.io/?key=020EAE9E5E1881E1EBB56A074AC7CB4F&ip={ip}',
                headers={'Accept': 'application/json'}
            )
            geo_location = geo_response.json() if geo_response.status_code == 200 else {}
        except Exception as e:
            print(f"Geolocation Error: {str(e)}")
            geo_location = {}

        req.origin = ip
        req.host = host
        req.request = path_request
        req.method = method
        req.headers = haders
        req.threat_type = 'None'
        req.body = body

        threat_clf.classify_request(req)
        print(req.threats)
        db.save(req)

        if list(req.threats.keys())[0] == 'valid':
            threat_state_valid = 1
            req.geo_location = {}
        else:
            threat_state_unvalid = 1
            geo_location['threat_state_unvalid'] = threat_state_unvalid
            geo_location['payload'] = req.body
            geo_location['threat_type'] = req.threats
            req.geo_location = geo_location

        if list(req.threats.keys())[0] != 'valid':
            try:
                account_sid = os.getenv('TWILIO_ACCOUNT_SID')
                auth_token = os.getenv('TWILIO_AUTH_TOKEN')
                from_whatsapp = os.getenv('TWILIO_PHONE_NUMBER')
                to_whatsapp = os.getenv('YOUR_PHONE_NUMBER')
                
                print(f"From WhatsApp: whatsapp:{from_whatsapp}")
                print(f"To WhatsApp: whatsapp:{to_whatsapp}")
                
                client = Client(account_sid, auth_token)

                message = client.messages.create(
                    from_=f'whatsapp:{from_whatsapp}',
                    body=f"🚨 WAF Alert!\nThreat detected from IP: {ip}\nThreat Type: {list(req.threats.keys())[0]}\nMore details: https://waf.grafana.net",
                    to=f'whatsapp:{to_whatsapp}'
                )
                print(f"WhatsApp message sent! SID: {message.sid}")
            except Exception as e:
                print(f"Twilio WhatsApp Error: {str(e)}")
                print(f"From: {from_whatsapp}")
                print(f"To: {to_whatsapp}")
                print(f"Auth SID: {account_sid[:5]}...")
                pass

        print(req.headers)
        print('*' * 100)
        print(request.environ['REMOTE_ADDR'])
        print('*' * 100)
        print(jsonify({'ip': request.remote_addr}), 200)
        print('*' * 100)
        print('host is ', request.headers.get('Host'))
        print('*' * 100)
        print('url is ', request.full_path)
        print('*' * 100)
        print('Method is', request.method)
        print('*' * 100)
        print('form  is', body)
        print('*' * 100)
        print('port  is', request.environ.get('REMOTE_PORT'))
        print(list(req.threats.keys())[0])
        print('*' * 100)
        print('port is', src_port)
        print('*' * 100)
        print('ip is', ip)
        return req.threats
     
       