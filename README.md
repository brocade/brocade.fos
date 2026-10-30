# Brocade FOS collection

The `brocade.fos` collection provides Ansible modules and example playbooks
for automating configuration and fact gathering on Brocade Fabric OS (FOS)
Fibre Channel switches.

## Requirements

- Python 3.12, as declared by `python_requires` in
  [tests/config.yml](https://github.com/brocade/brocade.fos/blob/main/tests/config.yml).
  No external Python packages are required.
- FOS versions tested with each release are listed in the
  [release history](https://github.com/brocade/brocade.fos/blob/main/versioning.md).
- Network access from the controller to the switch REST API, REST enabled on
  the switch, and credentials with permission to perform the requested operation.

## Installation

Install the collection on the controller or in the execution environment
where your playbooks run. The `ansible-galaxy` command is supplied by
`ansible-core`.

Use fully qualified names such as `brocade.fos.brocade_facts` in playbooks.
A collection installation does not require `ANSIBLE_LIBRARY` or a custom
`module_utils` path.

### Automation Hub

To install a certified release from Red Hat Ansible Automation Hub, use an
account with an active subscription and obtain an API token from the Hub.
Add the following server configuration to `ansible.cfg`:

```ini
[galaxy]
server_list = rh_hosted_ah

[galaxy_server.rh_hosted_ah]
url = https://console.redhat.com/api/automation-hub/content/published/
auth_url = https://sso.redhat.com/auth/realms/redhat-external/protocol/openid-connect/token
```

Set your token in the environment and install the collection:

```bash
export ANSIBLE_GALAXY_SERVER_RH_HOSTED_AH_TOKEN='<automation-hub-api-token>'
ansible-galaxy collection install brocade.fos --server rh_hosted_ah
```

### Ansible Galaxy

To install a release published on Ansible Galaxy, even when `ansible.cfg`
lists other servers:

```bash
ansible-galaxy collection install brocade.fos --server https://galaxy.ansible.com/
```

### Git

Install Git, then install the collection directly from the repository:

```bash
ansible-galaxy collection install git+https://github.com/brocade/brocade.fos.git,main
```

Replace `main` with a tag or commit to select a specific source revision.

### Installing a specific version

Append the version to the collection name, adding the `--server` option for
your source:

```bash
ansible-galaxy collection install brocade.fos:==<version>
```

### Requirements file

List the collection in a `requirements.yml` file, optionally pinning a version:

```yaml
collections:
  - name: brocade.fos
    version: "==<version>"
```

```bash
ansible-galaxy collection install -r requirements.yml
```

The example playbooks use
[collections/requirements.yml](https://github.com/brocade/brocade.fos/blob/main/collections/requirements.yml).

### Upgrading

To upgrade to the latest available release:

```bash
ansible-galaxy collection install brocade.fos --upgrade
```

## Running playbooks

Every module takes a `credential` dictionary with the switch login:

```yaml
credential:
  fos_ip_addr: "198.51.100.1"
  fos_user_name: "user_name"
  fos_password: "user_password"
  https: "true"
```

`https` is a quoted string:

| Value     | Description                                                             |
| --------- | ----------------------------------------------------------------------- |
| `"true"`  | HTTPS with certificate validation                                       |
| `"self"`  | HTTPS without certificate validation, allowing self-signed certificates |
| `"false"` | Unencrypted HTTP; the password is sent in clear text                    |

To keep `credential` encrypted, see
[Using Ansible Vault](https://github.com/brocade/brocade.fos/blob/main/docs/using_vault.md).

To write your own playbooks, see the [playbook authoring guide](https://github.com/brocade/brocade.fos/blob/main/docs/playbook_authoring.md)
and the [example playbooks](https://github.com/brocade/brocade.fos/tree/main/playbooks/tasks).

## Testing

Each release is validated on switches running the FOS versions listed in the
[release history](https://github.com/brocade/brocade.fos/blob/main/versioning.md).
Known issues for each release are listed under **Known Issues** in the
[changelog](https://github.com/brocade/brocade.fos/blob/main/CHANGELOG.rst).
For the automated checks, see
[Running Checks and Tests](https://github.com/brocade/brocade.fos/blob/main/CONTRIBUTING.md#running-checks-and-tests).

## Support

Certified releases from Automation Hub are supported through Ansible Automation
Platform; use the **Create issue** button on Automation Hub. For releases from
Galaxy or GitHub, use the
[GitHub issue tracker](https://github.com/brocade/brocade.fos/issues) or contact
[Automation.BSN@broadcom.com](mailto:Automation.BSN@broadcom.com).

## Release notes

See the [changelog](https://github.com/brocade/brocade.fos/blob/main/CHANGELOG.rst)
and [release history](https://github.com/brocade/brocade.fos/blob/main/versioning.md).

## Contributing and publishing

- [CONTRIBUTING.md](https://github.com/brocade/brocade.fos/blob/main/CONTRIBUTING.md):
  development setup, checks, changelog fragments, and pull requests.
- [PUBLISHING.md](https://github.com/brocade/brocade.fos/blob/main/PUBLISHING.md):
  release, validation, and publication to Galaxy and Automation Hub.

## License

This collection is licensed under `GPL-3.0-or-later` and `BSD-2-Clause`; see
[LICENSE](https://github.com/brocade/brocade.fos/blob/main/LICENSE) and
[LICENSES/BSD-2-Clause.txt](https://github.com/brocade/brocade.fos/blob/main/LICENSES/BSD-2-Clause.txt).
