# Password Vault

Simple personal password vault that works.

## Installation


Created and tested on Python 3.14. To initialize the app and create a new vault:

```shell
cd Password-Vault
pip install -r requirements.txt
python the-vault.py -init
```


This will create a new configuration file `config.json` in the current directory. 
The application will ask you to create a new password. This password will mpt be used to encrypt vault data. It is used to decrypt the **strong master key** that the app will generate and store in the config file.
The next step is to edit the config file to specify the vault location.

```json
{
  "path": "/path/to/vault/files",
  "secret": "Z0FBQU...docz0="
}
```

Backup your `config.json` file. The `secret` field contains the encrypted master key for the vault. Do not share this file with anyone. 

## Add a new account

To add a new account to the vault:

```shell
cd Password-Vault
python the-vault.py -add {account_name} {username} {password} [uri]
```
The application will ask you to enter the password for the vault. Then the application will create a new JSON file in the vault directory. It encrypts only the password. All other data is stored as a plain text.

## Read the account

To read the account information from the vault:

```shell
cd Password-Vault
python the-vault.py -read {account_name}
```

The application will ask you to enter the password for the vault. Then it will search for the JSON file in the vault directory.
You use the same session to retrieve multiple accounts.

## Version History

Version 1.01 - The initial release.
Version 1.02 - Clears password from the screen.
