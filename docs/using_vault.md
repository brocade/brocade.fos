# Using Ansible Vault

Every `brocade.fos` module takes a `credential` dictionary containing the
switch login. Keep it out of plain-text inventories and playbooks by storing
it in an [Ansible Vault](https://docs.ansible.com/ansible/latest/vault_guide/index.html)
encrypted file.

## Create a secrets file

`ansible-vault create` prompts for a new vault password, then opens your
editor:

```bash
ansible-vault create secrets.yml
```

Add the credential dictionary:

```yaml
credential:
  fos_ip_addr: "198.51.100.1"
  fos_user_name: "user_name"
  fos_password: "user_password"
  https: "true"
```

| Key             | Description                                               |
| --------------- | --------------------------------------------------------- |
| `fos_ip_addr`   | Switch IP address                                         |
| `fos_user_name` | Login username                                            |
| `fos_password`  | Login password                                            |
| `https`         | Connection mode, quoted: `"true"`, `"self"`, or `"false"` |

`"true"` uses HTTPS with certificate validation, `"self"` uses HTTPS without
certificate validation (self-signed certificates), and `"false"` uses
unencrypted HTTP. With `"false"`, the switch password is sent in clear text.

## Run with `-e @secrets.yml`

Playbooks pass the variable through to each task:

```yaml
- name: Gather switch facts
  hosts: fos_switches
  gather_facts: false

  tasks:
    - name: Gather facts
      brocade.fos.brocade_facts:
        credential: "{{ credential }}"
        vfid: -1
        gather_subset:
          - brocade_chassis_chassis
```

Load the secrets file as extra variables and enter the vault password when
prompted:

```bash
ansible-playbook <playbook>.yml -e @secrets.yml --ask-vault-pass
```

Extra variables take precedence over inventory and play variables, so
`credential` from `secrets.yml` replaces any value set elsewhere. Every
targeted host receives the same credential; use `--limit <hostname>` to run
against one switch, or use per-host files as described below.

Other secrets work the same way. For example,
[playbooks/tasks/firmwaredownload.yml](https://github.com/brocade/brocade.fos/blob/main/playbooks/tasks/firmwaredownload.yml)
defines the remote server login in its `firmwaredownload` play variable.
Define the complete `firmwaredownload` dictionary in `secrets.yml` to replace
it, including the password.

## Inventory integration

The sample
[playbooks/tasks/inventory](https://github.com/brocade/brocade.fos/blob/main/playbooks/tasks/inventory)
stores `credential` on each host. When using a secrets file, remove the
`credential` key from those hosts and supply it at runtime with
`-e @secrets.yml`.

For different credentials per switch, create an encrypted host variables file
next to the inventory instead. Ansible loads it automatically:

```bash
ansible-vault create playbooks/tasks/host_vars/switch1.yml
ansible-playbook <playbook>.yml --ask-vault-pass
```

## Unattended runs

For runs with no one at the prompt, such as cron jobs or pipelines, read the
vault password from a file instead. Keep the file outside the repository and
readable only by the user that runs the playbook:

```bash
ansible-playbook <playbook>.yml -e @secrets.yml --vault-password-file ~/.vault_pass

# Or set it once in the environment.
export ANSIBLE_VAULT_PASSWORD_FILE=~/.vault_pass
ansible-playbook <playbook>.yml -e @secrets.yml
```

To encrypt only the password in an otherwise plain-text variables file, use
`ansible-vault encrypt_string`, then paste the output, indented, under
`credential:` in place of the plain `fos_password` line:

```bash
ansible-vault encrypt_string 'user_password' --name fos_password
```

### Automation controller

In Ansible Automation Platform, add a Vault credential containing the vault
password to the job template; the controller decrypts vaulted content at
runtime. Job templates cannot pass `-e @secrets.yml`, so keep the encrypted
`credential` in the project instead, as encrypted `host_vars` or `group_vars`
files, or load it with `vars_files` in the playbook.
