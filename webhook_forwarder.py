import hmac
import logging
from os import environ
from sys import stderr, exit
from flask import Flask, abort, request, jsonify, Response
from discord import Webhook, AsyncWebhookAdapter, Embed, Colour
from re import findall
import aiohttp
from bs4 import BeautifulSoup

logging.basicConfig(stream=stderr, level=logging.INFO)

# Get SHA secret
webhook_secret = environ.get('WEBHOOK_SECRET')
if webhook_secret is None:
    logging.error("Must Define WEBHOOK_SECRET")
    exit(1)

# Get webhook objects
reportsURL = environ.get('REPORTS_WEBHOOK')
contactsURL = environ.get('CONTACTS_WEBHOOK')
wikiURL = environ.get('WIKI_WEBHOOK')

modelsURL = environ.get('MODELS_WEBHOOK')
roleAppsURL = environ.get('ROLEAPPS_WEBHOOK')

if reportsURL is None:
    logging.error("Must Define REPORTS_WEBHOOK: ", reportsURL)
    exit(1)

if contactsURL is None:
    logging.error("Must Define CONTACTS_WEBHOOK: ", contactsURL)
    exit(1)

if wikiURL is None:
    logging.error("Must Define WIKI_WEBHOOK:", wikiURL)
    exit(1)

if modelsURL is None:
    logging.error("Must Define MODELS_WEBHOOK:", modelsURL)
    exit(1)

if roleAppsURL is None:
    logging.error("Must Define ROLEAPPS_WEBHOOK:", roleAppsURL)
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
        reportsHook = Webhook.from_url(reportsURL, adapter = AsyncWebhookAdapter(session))

        embedTitle = 'New User Report | Ticket #' + str(rDict['ticket']['id'])
        ticketURL = baseTicketURL + str(rDict['ticket']['id'])
        embed = Embed(title=embedTitle,url=ticketURL)

        embed.add_field(name='Ticket Title', value=rDict['ticket']['title'], inline=False)
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

        system_attachments = rDict['article']['attachments']
        if system_attachments:
            embed.add_field(name="Additional Files", value="Yes - See Ticket", inline=False)

        articlebody = BeautifulSoup(rDict['article']['body'])
        try:
            parts = findall(subdivideRegex, articlebody.get_text())
            for part in parts:
                embed.add_field(name='Message', value=part, inline=False)
        except:
            embed.add_field(name='Message', value=articlebody.get_text(), inline=False)

        await reportsHook.send(embed=embed)
    resp = jsonify(success=True)
    return resp

@application.route('/community', methods=['POST'])
async def community():
    # validate inbound webhook
    header_signature = request.headers.get('X-Hub-Signature')
    verifyHeaders(header_signature)

    rDict = request.json
    async with aiohttp.ClientSession() as session:
        contactsHook = Webhook.from_url(contactsURL, adapter = AsyncWebhookAdapter(session))

        embedTitle = 'Hub Application | Ticket #' + str(rDict['ticket']['id'])
        ticketURL = baseTicketURL + str(rDict['ticket']['id'])
        embed = Embed(title=embedTitle,url=ticketURL)

        embed.add_field(name='User', value=rDict['ticket']['customer']['firstname'], inline=False)
        embed.add_field(name='User ID', value=rDict['ticket']['customer']['login'], inline=False)
        embed.add_field(name='Ticket Title', value=rDict['ticket']['title'], inline=False)

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

        system_attachments = rDict['article']['attachments']
        if system_attachments:
            embed.add_field(name="Additional Files", value="Yes - See Ticket", inline=False)

        articlebody = BeautifulSoup(rDict['article']['body'])
        try:
            parts = findall(subdivideRegex, articlebody.get_text())
            for part in parts:
                embed.add_field(name='Message', value=part, inline=False)
        except:
            embed.add_field(name='Message', value=articlebody.get_text(), inline=False)

        await contactsHook.send(embed=embed)
    resp = jsonify(success=True)
    return resp

@application.route('/general', methods=['POST'])
async def general():
    # validate inbound webhook
    header_signature = request.headers.get('X-Hub-Signature')
    verifyHeaders(header_signature)

    rDict = request.json
    async with aiohttp.ClientSession() as session:
        contactsHook = Webhook.from_url(contactsURL, adapter = AsyncWebhookAdapter(session))

        embedTitle = 'Contact Response | Ticket #' + str(rDict['ticket']['id'])
        ticketURL = baseTicketURL + str(rDict['ticket']['id'])
        embed = Embed(title=embedTitle,url=ticketURL)

        embed.add_field(name='User', value=rDict['ticket']['customer']['firstname'], inline=False)
        embed.add_field(name='User ID', value=rDict['ticket']['customer']['login'], inline=False)
        embed.add_field(name='Ticket Title', value=rDict['ticket']['title'], inline=False)
        
        alt_contact = rDict['ticket']['aalternative_contact']
        if alt_contact:
            embed.add_field(name='Alternative Contact', value=alt_contact, inline=False)

        aaactivecontacttype = rDict['ticket']['aaactivecontacttype']
        if aaactivecontacttype:
            embed.add_field(name='What is this about?', value=aaactivecontacttype, inline=False)

        system_attachments = rDict['article']['attachments']
        if system_attachments:
            embed.add_field(name="Additional Files", value="Yes - See Ticket", inline=False)

        articlebody = BeautifulSoup(rDict['article']['body'])
        try:
            parts = findall(subdivideRegex, articlebody.get_text())
            for part in parts:
                embed.add_field(name='Message', value=part, inline=False)
        except:
            embed.add_field(name='Message', value=articlebody.get_text(), inline=False)

        await contactsHook.send(embed=embed)
    resp = jsonify(success=True)
    return resp

@application.route('/wiki', methods=['POST'])
async def wiki():
    # validate inbound webhook
    header_signature = request.headers.get('X-Hub-Signature')
    verifyHeaders(header_signature)

    rDict = request.json
    async with aiohttp.ClientSession() as session:
        wikiHook = Webhook.from_url(wikiURL, adapter = AsyncWebhookAdapter(session))

        embedTitle = 'Wiki Contact Response | Ticket #' + str(rDict['ticket']['id'])
        ticketURL = baseTicketURL + str(rDict['ticket']['id'])
        embed = Embed(title=embedTitle,url=ticketURL)

        embed.add_field(name='User', value=rDict['ticket']['customer']['firstname'], inline=False)
        embed.add_field(name='User ID', value=rDict['ticket']['customer']['login'], inline=False)
        embed.add_field(name='Ticket Title', value=rDict['ticket']['title'], inline=False)
        
        alt_contact = rDict['ticket']['aalternative_contact']
        if alt_contact:
            embed.add_field(name='Alternative Contact', value=alt_contact, inline=False)

        aaactivecontacttype = rDict['ticket']['aaactivecontacttype']
        if aaactivecontacttype:
            embed.add_field(name='What is this about?', value=aaactivecontacttype, inline=False)

        system_attachments = rDict['article']['attachments']
        if system_attachments:
            embed.add_field(name="Additional Files", value="Yes - See Ticket", inline=False)

        articlebody = BeautifulSoup(rDict['article']['body'])
        try:
            parts = findall(subdivideRegex, articlebody.get_text())
            for part in parts:
                embed.add_field(name='Message', value=part, inline=False)
        except:
            embed.add_field(name='Message', value=articlebody.get_text(), inline=False)

        await wikiHook.send(embed=embed)
    resp = jsonify(success=True)
    return resp

@application.route('/models', methods=['POST'])
async def models():
    # validate inbound webhook
    header_signature = request.headers.get('X-Hub-Signature')
    verifyHeaders(header_signature)

    rDict = request.json
    async with aiohttp.ClientSession() as session:
        postHook = Webhook.from_url(modelsURL, adapter = AsyncWebhookAdapter(session))

        embedTitle = '3D Artist Application | Ticket #' + str(rDict['ticket']['id'])
        ticketURL = baseTicketURL + str(rDict['ticket']['id'])
        embed = Embed(title=embedTitle,url=ticketURL)

        embed.add_field(name='User', value=rDict['ticket']['customer']['firstname'], inline=False)
        embed.add_field(name='User ID', value=rDict['ticket']['customer']['login'], inline=False)
        embed.add_field(name='Ticket Title', value=rDict['ticket']['title'], inline=False)
        
        alt_contact = rDict['ticket']['aalternative_contact']
        if alt_contact:
            embed.add_field(name='Alternative Contact', value=alt_contact, inline=False)

        modelsaber_username = rDict['ticket']['modelsaber_username']
        if modelsaber_username:
            embed.add_field(name='Modelsaber Username', value=modelsaber_username, inline=False)

        for linkNumber in range(1,6):
            current_link = 'submission_link' + str(linkNumber)
            fieldValue = rDict['ticket'][current_link]
            if fieldValue:
                fieldName = 'Link ' + str(linkNumber)
                embed.add_field(name=fieldName, value=fieldValue, inline=False)

        system_attachments = rDict['article']['attachments']
        if system_attachments:
            embed.add_field(name="Additional Files", value="Yes - See Ticket", inline=False)

        articlebody = BeautifulSoup(rDict['article']['body'])
        try:
            parts = findall(subdivideRegex, articlebody.get_text())
            for part in parts:
                embed.add_field(name='Message', value=part, inline=False)
        except:
            embed.add_field(name='Message', value=articlebody.get_text(), inline=False)

        await postHook.send(embed=embed)
    resp = jsonify(success=True)
    return resp

@application.route('/modapps', methods=['POST'])
async def modapps():
    # validate inbound webhook
    header_signature = request.headers.get('X-Hub-Signature')
    verifyHeaders(header_signature)

    rDict = request.json
    embedTitle = 'Moderator Role App | Ticket #' + str(rDict['ticket']['id'])
    ticketURL = baseTicketURL + str(rDict['ticket']['id'])
    embed = Embed(title=embedTitle,url=ticketURL)

    return roleapphelper(rDict, embed)

@application.route('/staffapps', methods=['POST'])
async def staffapps():
    # validate inbound webhook
    header_signature = request.headers.get('X-Hub-Signature')
    verifyHeaders(header_signature)

    rDict = request.json
    embedTitle = 'Staff Role App | Ticket #' + str(rDict['ticket']['id'])
    ticketURL = baseTicketURL + str(rDict['ticket']['id'])
    embed = Embed(title=embedTitle,url=ticketURL)

    return roleapphelper(rDict, embed)
    
async def roleapphelper(rDict, embed):
    async with aiohttp.ClientSession() as session:
        postHook = Webhook.from_url(roleAppsURL, adapter = AsyncWebhookAdapter(session))

        embed.add_field(name='User', value=rDict['ticket']['customer']['firstname'], inline=False)
        embed.add_field(name='User ID', value=rDict['ticket']['customer']['login'], inline=False)
        embed.add_field(name='Ticket Title', value=rDict['ticket']['title'], inline=False)
        
        alt_contact = rDict['ticket']['aalternative_contact']
        if alt_contact:
            embed.add_field(name='Alternative Contact', value=alt_contact, inline=False)

        dateofbirth = rDict['ticket']['dateofbirth']
        if dateofbirth:
            embed.add_field(name='Date of Birth', value=dateofbirth, inline=False)

        location = rDict['ticket']['location']
        if location:
            embed.add_field(name='What country (and state) and timezone are you based in?', value=location, inline=False)

        twofa = rDict['ticket']['2fa_affirm']
        if twofa:
            embed.add_field(name='Do you have Two-Factor Authentication Enabled?', value=twofa, inline=False)

        system_attachments = rDict['article']['attachments']
        if system_attachments:
            embed.add_field(name="Additional Files", value="Yes - See Ticket", inline=False)

        articlebody = BeautifulSoup(rDict['article']['body'])
        try:
            parts = findall(subdivideRegex, articlebody.get_text())
            for part in parts:
                embed.add_field(name='Message', value=part, inline=False)
        except:
            embed.add_field(name='Message', value=articlebody.get_text(), inline=False)

        await postHook.send(embed=embed)
    resp = jsonify(success=True)
    return resp

# Run the application if we're run as a script
if __name__ == '__main__':
    logging.info("All systems operational, beginning application loop")
    application.run(debug=False, host='0.0.0.0', port=8000)