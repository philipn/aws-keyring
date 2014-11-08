"""
Usage:
  aws-keys add
  aws-keys rm <NAME>
  aws-keys env [NAME]

Options:
  -h --help     Show this screen.

"""
from docopt import docopt
import keyring

class Credentials(object):
    def __init__(self, name='', access_key_id='', secret_access_key='',
                 enable_mfa=False, is_default=False):
        self.name = name
        self.access_key_id = access_key_id
        self.secret_access_key = secret_access_key
        self.enable_mfa = enable_mfa
        self.is_default = is_default


def main():
    arguments = docopt(__doc__)
    if arguments['add']:
        add()
    elif arguments['rm']:
        rm(arguments['<NAME>'])
    elif arguments['env']:
        env(arguments['NAME'])

def add():
    name = raw_input("Name for the AWS credentials (e.g. 'bob'): ").strip()
    access_key_id = raw_input("Access Key ID: ").strip()
    secret_access_key = raw_input("Secret Access Key: ").strip()
    enable_mfa = raw_input("Use MFA on this account? (yes/no): ").strip().lower()
    make_default = raw_input("Make this account the default for aws-keys? (yes/no): ").strip().lower()

    if enable_mfa.startswith('y'):
        enable_mfa = True
    else:
        enable_mfa = False

    if make_default.startswith('y'):
        make_default = True
    else:
        make_default = False

    keyring.set_password('aws-keyring-access-key-id', name, access_key_id)
    keyring.set_password('aws-keyring-secret-access-key', name, secret_access_key)
    keyring.set_password('aws-keyring-use-mfa', name, '1' if enable_mfa else '0')
    if make_default:
        keyring.set_password('aws-keyring-default', name, '1')

    print "Credentials added for account name '%s'." % name

def rm(name):
    keyring.delete_password('aws-keyring-access-key-id', name)
    keyring.delete_password('aws-keyring-secret-access-key', name)
    keyring.delete_password('aws-keyring-use-mfa', name)

    is_default = keyring.get_password('aws-keyring-default', name)
    if is_default == '1':
        keyring.delete_password('aws-keyring-default', name)

    print "Credentials for account name '%s' deleted." % name

def env(name=None):
    credentials = get_credentials(name)

    environment_exports = """
export AWS_ACCESS_KEY_ID="{access_key_id}"
export AWS_ACCESS_KEY="{access_key_id}"
export AWS_SECRET_ACCESS_KEY="{secret_access_key}"
export AWS_SECRET_KEY="{secret_access_key}"
""".strip().format(
        access_key_id=credentials.access_key_id,
        secret_access_key=credentials.secret_access_key,
    )

    print environment_exports

def get_credentials(name=None):
    if not name:
        name = get_default_name()

    access_key_id = keyring.get_password('aws-keyring-access-key-id', name)
    secret_access_key = keyring.get_password('aws-keyring-secret-access-key', name)
    enable_mfa = keyring.get_password('aws-keyring-use-mfa', name)
    enable_mfa = True if enable_mfa == '1' else False
    is_default = keyring.get_password('aws-keyring-default', name)
    is_default = True if is_default == '1' else False
   
    credentials = Credentials(
        name=name,
        access_key_id=access_key_id,
        secret_access_key=secret_access_key,
        enable_mfa=enable_mfa,
        is_default=is_default
    )
    return credentials
