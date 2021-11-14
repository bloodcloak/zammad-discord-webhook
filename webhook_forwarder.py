import hmac
import logging
from os import environ
from sys import stderr, exit
from flask import Flask, abort, request, jsonify, Response
from discord import Webhook, AsyncWebhookAdapter, Embed, Color
from re import findall
import aiohttp

logging.basicConfig(stream=stderr, level=logging.INFO)

# Get SHA secret
webhook_secret = environ.get('WEBHOOK_SECRET')
if webhook_secret is None:
    logging.error("Must Define WEBHOOK_SECRET")
    exit(1)

# Get webhook objects
reportsURL = environ.get('REPORTS_WEBHOOK')
contactsURL = environ.get('CONTACTS_WEBHOOK')

if reportsURL is None:
    logging.error("Must Define REPORTS_WEBHOOK")
    exit(1)

if contactsURL is None:
    logging.error("Must Define CONTACTS_WEBHOOK")
    exit(1)

subdivideRegex = r"[\s\S]{1,1024}"
baseTicketURL = 'https://contact.bsmg.dev/#ticket/zoom/'

application = Flask(__name__)

@application.route('/', methods=['GET'])
def index():
    msg = {"msg": "Service is running"}
    return jsonify(msg)

def verifyHeaders(header_signature):
    if header_signature is not None:
        # Construct an hmac, abort if it doesn't match
        try:
            sha_name, signature = header_signature.split('=')
        except:
            logging.info("X-Hub-Signature format is incorrect (%s), aborting", header_signature)
            abort(400)
        data = request.get_data()
        try:
            mac = hmac.new(webhook_secret.encode('utf8'), msg=data, digestmod=sha_name)
        except:
            logging.info("Unsupported X-Hub-Signature type (%s), aborting", header_signature)
            abort(400)
        if not hmac.compare_digest(str(mac.hexdigest()), str(signature)):
            logging.info("Signature did not match (%s and %s), aborting", str(mac.hexdigest()), str(signature))
            abort(403)
    else:
        logging.info("X-Hub-Signature was missing, aborting")
        abort(403)

@application.route('/reports', methods=['POST'])
async def userreports():
    # validate inbound webhook
    header_signature = request.headers.get('X-Hub-Signature')
    verifyHeaders(header_signature)

    rDict = request.json
    async with aiohttp.ClientSession() as session:
        reportsHook = Webhook(reportsURL, adapter = AsyncWebhookAdapter(session))

        ticketURL = baseTicketURL + rDict['ticket']['id']
        embed = Embed(title='New User Report',url=ticketURL, color=Color.orange)

        embed.add_field(name='Reporter', value=rDict['ticket']['customer']['firstname'], inline=False)

        alt_contact = rDict['ticket']['aalternative_contact']
        if alt_contact:
            embed.add_field(name='Alternative Contact', value=alt_contact, inline=False)

        reported_user = rDict['ticket']['reported_ausername']
        if reported_user:
            embed.add_field(name='Reported User Username', value=reported_user, inline=False)

        reported_userid = rDict['ticket']['reported_buseruid']
        if reported_userid:
            embed.add_field(name='Reported User ID', value=reported_userid, inline=False)
        
        reported_proof = rDict['ticket']['reported_zproof']
        if reported_proof:
            embed.add_field(name='Proof', value=reported_proof, inline=False)

        try:
            parts = findall(subdivideRegex, rDict['article']['body'])
            for part in parts:
                embed.add_field(name='Message', value=part, inline=False)
        except:
            embed.add_field(name='Message', value=rDict['article']['body'], inline=False)

        await reportsHook.send(embed=embed)
    return Response(200)

@application.route('/community', methods=['POST'])
async def community():
    # validate inbound webhook
    header_signature = request.headers.get('X-Hub-Signature')
    verifyHeaders(header_signature)

    rDict = request.json
    async with aiohttp.ClientSession() as session:
        contactsHook = Webhook(contactsURL, adapter = AsyncWebhookAdapter(session))

        ticketURL = baseTicketURL + rDict['ticket']['id']
        embed = Embed(title='Hub Application',url=ticketURL, color=Color.purple)

        embed.add_field(name='User', value=rDict['ticket']['customer']['firstname'], inline=False)
        embed.add_field(name='User ID', value=rDict['ticket']['customer']['login'], inline=False)

        alt_contact = rDict['ticket']['aalternative_contact']
        if alt_contact:
            embed.add_field(name='Alternative Contact', value=alt_contact, inline=False)

        aaactivecontacttype = rDict['ticket']['aaactivecontacttype']
        if aaactivecontacttype:
            embed.add_field(name='App Type', value=aaactivecontacttype, inline=False)

        community_aname = rDict['ticket']['community_aname']
        if community_aname:
            embed.add_field(name='Community Name', value=community_aname, inline=False)

        community_bdescription = rDict['ticket']['community_bdescription']
        if community_bdescription:
            embed.add_field(name='Community Description', value=community_bdescription, inline=False)
        
        community_cjoinlink = rDict['ticket']['community_cjoinlink']
        if community_cjoinlink:
            embed.add_field(name='Join Link', value=community_cjoinlink, inline=False)

        community_dotherlinks = rDict['ticket']['community_dotherlinks']
        if community_dotherlinks:
            embed.add_field(name='Other Link', value=community_dotherlinks, inline=False)

        community_ecolor = rDict['ticket']['community_ecolor']
        if community_ecolor:
            embed.add_field(name='Embed Color', value=community_ecolor, inline=False)

        community_ficon = rDict['ticket']['community_ficon']
        if community_ficon:
            embed.add_field(name='Icon', value=community_ficon, inline=False)

        try:
            parts = findall(subdivideRegex, rDict['article']['body'])
            for part in parts:
                embed.add_field(name='Message', value=part, inline=False)
        except:
            embed.add_field(name='Message', value=rDict['article']['body'], inline=False)

        await contactsHook.send(embed=embed)
    return Response(200)

@application.route('/general', methods=['POST'])
async def general():
    # validate inbound webhook
    header_signature = request.headers.get('X-Hub-Signature')
    verifyHeaders(header_signature)

    rDict = request.json
    async with aiohttp.ClientSession() as session:
        contactsHook = Webhook(contactsURL, adapter = AsyncWebhookAdapter(session))

        ticketURL = baseTicketURL + rDict['ticket']['id']
        embed = Embed(title='Contact Response',url=ticketURL, color=Color.blue)

        embed.add_field(name='User', value=rDict['ticket']['customer']['firstname'], inline=False)
        embed.add_field(name='User ID', value=rDict['ticket']['customer']['login'], inline=False)

        alt_contact = rDict['ticket']['aalternative_contact']
        if alt_contact:
            embed.add_field(name='Alternative Contact', value=alt_contact, inline=False)

        aaactivecontacttype = rDict['ticket']['aaactivecontacttype']
        if aaactivecontacttype:
            embed.add_field(name='What is this about?', value=aaactivecontacttype, inline=False)

        try:
            parts = findall(subdivideRegex, rDict['article']['body'])
            for part in parts:
                embed.add_field(name='Message', value=part, inline=False)
        except:
            embed.add_field(name='Message', value=rDict['article']['body'], inline=False)

        await contactsHook.send(embed=embed)
    return Response(200)

# Run the application if we're run as a script
if __name__ == '__main__':
    logging.info("All systems operational, beginning application loop")
    application.run(debug=False, host='0.0.0.0', port=8000)