# -*- coding: utf-8 -*-
# 1 : imports of python lib
import logging
import threading

# 2 :  imports of odoo
import odoo
from odoo.tools.config import config
from odoo import SUPERUSER_ID

# 3 :  imports of odoo modules

# 4 :  imports from custom modules
from skpy import Skype, SkypeEventLoop, SkypeNewMessageEvent, SkypeAuthException


_logger = logging.getLogger(__name__)


class OdooSkype(SkypeEventLoop):
    """ Skype Instance to process skype events """

    @staticmethod
    def get_db_name():
        """
        Get db name from config.
        :return str: db name
        """
        return config.get('db_name')

    @staticmethod
    def get_admin_object(env):
        """
        Get admin.
        :param env: environment instance
        :return class 'res.partner': res.partner object - admin
        """
        admin = env['res.users'].search([
            ('name', 'ilike', 'Administrator')
        ]).partner_id
        return admin

    def send_messageto_admin(self, env):
        admin_skype_login = self.get_admin_object(env).skype
        ch = sk.chats["8:{}".format(admin_skype_login)]
        ch.sendMsg("Hello.")

    def onEvent(self, event):
        """
        Method to react to incoming messages and events.
        :param class 'skpy.event.SkypeNewMessageEvent' event: event instance
        :return: None
        """

        if isinstance(event, SkypeNewMessageEvent):

            _logger.info(
                'Incoming Skype event "{}" happened at {}.'.format(event.type, event.time)
            )

            db_name = self.get_db_name()

            if not db_name:
                _logger.warning('Odoo DB name not found!')
                return None

            registry = odoo.registry(db_name)

            with registry.cursor() as cr:
                context = {}
                with odoo.api.Environment.manage():
                    env = odoo.api.Environment(cr, SUPERUSER_ID, context)

                    admin = self.get_admin_object(env)

                    message = env['mail.message'].create({
                        'model': 'mail.channel',
                        'res_id': env['mail.channel'].search([
                            ('channel_type', '=', 'chat')]
                        ).id,
                        'message_type': 'notification',
                        'body': event.msg.content,
                        'partner_ids': [(6, 0, [admin.id])],
                        'subject': 'Incoming skype event: "{}" from "{}".'.format(
                            event.msg.type, event.msg.userId
                        ),
                        'subtype_id': env['mail.message.subtype'].search([
                            ('name', '=', 'Discussions')]
                        ).id
                    })

                    try:
                        cr.commit()
                        _logger.info('Message for Skype event is created: id={}, model="{}".'.format(
                            message.id,
                            message._name,
                        ))
                    except Exception:
                        cr.rollback()
                        raise


def start_thread(target):
    """
    Initialize and start thread with target
    :param target: target fot threading
    :return: None
    """
    if target:
        thread = threading.Thread(target=target)
        thread.start()

# trying to connecting the Skype and start Skype loop in thread
try:
    # get skype login and password from odoo.conf
    sk_login = config.get('sk_login')
    sk_password = config.get('sk_password')
    # get Skype connection
    sk = OdooSkype(user=sk_login, pwd=sk_password, autoAck=True)
    # start skype loop in threading
    start_thread(sk.loop)
    _logger.info('Thread is initialed. Waiting for Skype event ....')
except SkypeAuthException:
    _logger.exception('An exception thrown when authentication cannot be completed.')
    sk = Skype(connect=False)
    # try to set tokenfile(path)
    sk.conn.setTokenFile(config.get('tokenfile'))
    tokenfile = sk.conn.tokenFile
    if tokenfile:
        # attempt to re-establish a connection using previously acquired tokens
        sk.conn.readToken()
    else:
        # method with one that connects via the Microsoft account flow using the
        # given credentials.  Avoids storing the account password in an accessible way.
        sk.conn.setUserPwd(sk_login, sk_password)
        # applies the previously given username and password
        sk.conn.getSkypeToken()

    sk = OdooSkype(user=sk_login, pwd=sk_password, tokenFile=sk.conn.tokenFile)
    start_thread(sk.loop)
    _logger.info('Thread is initialed. Waiting for Skype event ....')
except Exception as err:
    _logger.exception(err)


