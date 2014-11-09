# aws-keyring

`aws-keyring` is a simple utility to make handling your AWS credentials a little more secure and easy.  Instead of hard-coding your credentials into dotfiles, `aws-keyring` will instead store them in your system keychain / keyring.

`aws-keyring` also makes dealing with AWS MFA much easier when using the AWS CLI or other AWS API tools.

## Installation

To install:

    pip install aws-keyring

## Usage

First, add your credentials to `aws-keys`:

    aws-keys add

This will prompt you for your AWS Access Key ID, AWS Secret Acces Key, and ask you some other questions.

You can then get the environment settings for this account by running:

    aws-keys sync
    aws-keys env

To initialize these in your current shell, simply run:

    aws-keys sync
    $(aws-keys env)

for the default account.  For a specific account, run:

    aws-keys sync <name>
    $(aws-keys env <name>)

If you're using MFA, then you will be prompted for an MFA token, and `aws-keys` will connect to AWS and obtain a security token.  When your security token has expired, `aws-keys` will re-prompt you for these details.

You'll probably want to integrate `aws-keys` directly into your shell.  For instance, if you add the following to your .bash_profile or .bashrc, it will make the usual `aws` command work right:

    alias aws='$(aws-keys env) && aws'

and if you're using MFA:

    alias aws='aws-keys sync && $(aws-keys env) && aws'
