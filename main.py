import asyncio
import aiosqlite3
import aiosmtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

MAIL_PARAMS = {'TLS': True, 'host': 'smtp.gmail.com', 'password': 'password', 'user': 'user', 'port': 587}


async def read_contacts_from_db(loop):
    async with aiosqlite3.connect('contacts.db', loop=loop) as conn:
        async with conn.cursor() as cur:
            await cur.execute("SELECT * FROM contacts;")
            contacts_list = await cur.fetchall()
            return contacts_list


async def send_mail(address, name, **params):
    mail_params = params.get("mail_params", MAIL_PARAMS)
    msg = MIMEMultipart()
    msg.preamble = f'{name}, примите благодарность!'
    msg['Subject'] = f'{name}, примите благодарность!'
    msg['From'] = mail_params.get('user')
    msg['To'] = address
    body = f'Уважаемый, {name}!\nСпасибо, что пользуетесь нашим сервисом объявлений.'
    msg.attach(MIMEText(body, 'plain'))

    host = mail_params.get('host', 'localhost')
    isSSL = mail_params.get('SSL', False)
    isTLS = mail_params.get('TLS', False)
    port = mail_params.get('port', 465 if isSSL else 25)
    smtp = aiosmtplib.SMTP(hostname=host, port=port, use_tls=isSSL)
    await smtp.connect()
    if isTLS:
        await smtp.starttls()
    if 'user' in mail_params:
        await smtp.login(mail_params['user'], mail_params['password'])
    await smtp.send_message(msg)
    await smtp.quit()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    list_cont = loop.run_until_complete(read_contacts_from_db(loop))
    co_list = []
    for mail in list_cont:
        co1 = send_mail(to=mail[3], name=f'{mail[1]} {mail[2]}')
        co_list.append(co1)
    loop.run_until_complete(asyncio.gather(*co_list))
    loop.close()
