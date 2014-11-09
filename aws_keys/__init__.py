"""
Usage:
  aws-keys add
  aws-keys rm <NAME>
  aws-keys sync [NAME]
  aws-keys env [NAME]

Options:
  -h --help     Show this screen.

"""
from docopt import docopt
from getpass import getpass 
import dateutil.parser
import keyring
import time
import datetime
import dateutil.parser

SESSION_DURATION = 60 * 60

class Credentials(object):
    def __init__(self, name='', access_key_id='', secret_access_key='',
                 mfa_serial='', is_default=False, temporary_credentials=None):
        self.name = name
        self.access_key_id = access_key_id
        self.secret_access_key = secret_access_key
        self.mfa_serial = mfa_serial
        self.is_default = is_default
        self.temporary_credentials = temporary_credentials


class TemporaryCredentials(object):
    def __init__(self,  temporary_access_key='', temporary_secret_key='',
                 session_token='', expiration=''):
        self.temporary_access_key = temporary_access_key
        self.temporary_secret_key = temporary_secret_key
        self.session_token = session_token
        self.expiration = expiration

    def time_until_expiration(self):
        return (
            time.mktime(dateutil.parser.parse(self.expiration).timetuple()) -
            time.mktime(datetime.datetime.utcnow().timetuple())
        )

    def __str__(self):
        return "%s %s %s %s" % (
            self.temporary_access_key,
            self.temporary_secret_key,
            self.session_token,
            self.expiration,
        )


def main():
    arguments = docopt(__doc__)
    if arguments['add']:
        add()
    elif arguments['rm']:
        rm(arguments['<NAME>'])
    elif arguments['env']:
        env(arguments['NAME'])
    elif arguments['sync']:
        sync(arguments['NAME'])

def add():
    name = raw_input("Name for the AWS credentials (e.g. 'bob'): ").strip()
    access_key_id = raw_input("Access Key ID: ").strip()
    secret_access_key = raw_input("Secret Access Key: ").strip()
    enable_mfa = raw_input("Use MFA on this account? (yes/no): ").strip().lower()
    if enable_mfa.startswith('y'):
        mfa_serial = raw_input("Your MFA device serial (arn:aws:..) ID: ").strip()
    make_default = raw_input("Make this account the default for aws-keys? (yes/no): ").strip().lower()

    if make_default.startswith('y'):
        make_default = True
    else:
        make_default = False

    keyring.set_password('aws-keyring-access-key-id', name, access_key_id)
    keyring.set_password('aws-keyring-secret-access-key', name, secret_access_key)
    if enable_mfa.startswith('y'):
        keyring.set_password('aws-keyring-mfa', name, mfa_serial)
    if make_default:
        keyring.set_password('aws-keyring-default', name, '1')

    print "Credentials added for account name '%s'." % name

def rm(name):
    credentials = get_credentials(name)

    keyring.delete_password('aws-keyring-access-key-id', name)
    keyring.delete_password('aws-keyring-secret-access-key', name)

    if credentials.mfa_serial:
        keyring.delete_password('aws-keyring-mfa', name)

    is_default = keyring.get_password('aws-keyring-default', name)
    if is_default == '1':
        keyring.delete_password('aws-keyring-default', name)

    print "Credentials for account name '%s' deleted." % name

def env(name=None):
    credentials = get_credentials(name)

    if (credentials.temporary_credentials and
        credentials.temporary_credentials.time_until_expiration() > 0):
        # Unfortunately, we can't just call sync() here and get new credentials
        # if they're expired, because env() is designed to be added directly into
        # the shell environment and so we can't prompt for interactive input for
        # the MFA token. Instead, we tell people to first call sync() and then
        # use env().
        environment_exports = """
export AWS_ACCESS_KEY_ID={access_key_id}
export AWS_ACCESS_KEY={access_key_id}
export AWS_SECRET_ACCESS_KEY={secret_access_key}
export AWS_SECRET_KEY={secret_access_key}
export AWS_SESSION_TOKEN={session_token}
""".strip().format(
            access_key_id=credentials.temporary_credentials.temporary_access_key,
            secret_access_key=credentials.temporary_credentials.temporary_secret_key,
            session_token=credentials.temporary_credentials.session_token,
        )
    else:
        environment_exports = """
export AWS_ACCESS_KEY_ID={access_key_id}
export AWS_ACCESS_KEY={access_key_id}
export AWS_SECRET_ACCESS_KEY={secret_access_key}
export AWS_SECRET_KEY={secret_access_key}
""".strip().format(
            access_key_id=credentials.access_key_id,
            secret_access_key=credentials.secret_access_key,
        )

    print environment_exports

def sync(name=None):
    credentials = get_credentials(name)
    if not credentials.mfa_serial:
        # Nothing to do here.
        return

    # Have temporary credentials and they aren't expired yet, so no need to
    # get new ones.
    if (credentials.temporary_credentials and
        credentials.temporary_credentials.time_until_expiration() > 0):
        return 

    import boto
    from boto.sts import STSConnection

    mfa_TOTP = getpass("Enter the MFA code: ")

    sts_connection = STSConnection(
        aws_access_key_id=credentials.access_key_id,
        aws_secret_access_key=credentials.secret_access_key
    )

    temporary_credentials = sts_connection.get_session_token(
        duration=SESSION_DURATION,
        mfa_serial_number=credentials.mfa_serial,
        mfa_token=mfa_TOTP,
    )

    details = TemporaryCredentials(
        temporary_access_key=temporary_credentials.access_key,
        temporary_secret_key=temporary_credentials.secret_key,
        session_token=temporary_credentials.session_token,
        expiration=temporary_credentials.expiration
    )

    keyring.set_password('aws-keyring-temporary-credentials', name, str(details))

def get_credentials(name=None):
    if not name:
        name = get_default_name()

    access_key_id = keyring.get_password('aws-keyring-access-key-id', name)
    secret_access_key = keyring.get_password('aws-keyring-secret-access-key', name)
    mfa_serial = keyring.get_password('aws-keyring-mfa', name)
    is_default = keyring.get_password('aws-keyring-default', name)
    is_default = True if is_default == '1' else False
    temporary_credentials = keyring.get_password('aws-keyring-temporary-credentials', name)
    if temporary_credentials:
        access_key, secret_key, session_token, expiration = temporary_credentials.split()
        temporary_credentials = TemporaryCredentials(
            temporary_access_key=access_key,
            temporary_secret_key=secret_key,
            session_token=session_token,
            expiration=expiration
        )
   
    credentials = Credentials(
        name=name,
        access_key_id=access_key_id,
        secret_access_key=secret_access_key,
        mfa_serial=mfa_serial,
        is_default=is_default,
        temporary_credentials=temporary_credentials
    )
    return credentials
