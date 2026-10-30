# Playbook Authoring

The `brocade.fos` collection manages Brocade Fabric OS (FOS) through its REST API.
This guide covers credentials, module selection, task examples, and reference tables.

- [Before you start](#before-you-start)
- [Using Ansible Vault](#using-ansible-vault)
- [Choose a module](#choose-a-module)
- [Manage zoning](#manage-zoning)
- [Configure generic objects](#configure-generic-objects)
- [Reference](#reference)

## Before you start

Install the collection and enable REST access on the switch, as described in the
[README](https://github.com/brocade/brocade.fos/blob/main/README.md).
Run tasks on the controller with `connection: local` in the play or
`ansible_connection: local` in the inventory. Set `gather_facts: false` to skip
Ansible's host fact gathering; use the collection's facts modules for switch data.

Use fully qualified module names, such as `brocade.fos.brocade_zoning_alias`.
Every module takes a `credential` dictionary. The examples below use the shared
`credential` variable configured in the next section.

Use `vfid: -1` for Access Gateway mode or switches without virtual fabrics
enabled. You can also use `-1` for the default logical switch when it is
the REST user's home fabric. To target another logical switch, set `vfid`
to its fabric ID.

## Using Ansible Vault

Store switch credentials in an
[Ansible Vault](https://docs.ansible.com/ansible/latest/vault_guide/index.html)
encrypted file to keep passwords out of plain-text inventories and playbooks.

### Create a secrets file

Create an encrypted variables file. The command prompts for a vault password,
then opens your editor:

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

| Key             | Description                                             |
| --------------- | ------------------------------------------------------- |
| `fos_ip_addr`   | Switch IP address                                       |
| `fos_user_name` | Switch login username                                   |
| `fos_password`  | Switch login password                                   |
| `https`         | Connection mode, supplied as a quoted string; see below |

| `https` value | Connection mode                                                         |
| ------------- | ----------------------------------------------------------------------- |
| `"true"`      | HTTPS with certificate validation                                       |
| `"self"`      | HTTPS without certificate validation, allowing self-signed certificates |
| `"false"`     | Unencrypted HTTP; the switch password is sent in clear text             |

### Run a playbook

Pass the shared variable to each task. For example, save this playbook as
`facts.yml`:

```yaml
- name: Gather switch facts
  hosts: fos_switches
  connection: local
  gather_facts: false

  tasks:
    - name: Gather chassis facts
      brocade.fos.brocade_facts:
        credential: "{{ credential }}"
        vfid: -1
        gather_subset:
          - brocade_chassis_chassis
```

From the repository root, load the sample inventory and encrypted file:

```bash
ansible-playbook -i playbooks/tasks/inventory facts.yml -e @secrets.yml --ask-vault-pass
```

Extra variables override inventory and play variables. Every targeted host
receives the same `credential`, including the switch IP address. Use
`--limit switch1` for one switch, or use per-host variables as described below.

Other secrets work the same way. For example,
[firmwaredownload.yml](https://github.com/brocade/brocade.fos/blob/main/playbooks/tasks/firmwaredownload.yml)
defines a remote server login in `firmwaredownload`. Put the complete dictionary,
including its password, in `secrets.yml` to override that play variable.

### Inventory integration

The sample
[inventory](https://github.com/brocade/brocade.fos/blob/main/playbooks/tasks/inventory)
defines `credential` on each host. Remove those plain-text credentials when
supplying the variable from an encrypted file; retain `ansible_connection: local`.

For different credentials per switch, create an encrypted host variables file
next to the inventory. Put that host's complete `credential` dictionary in it.
Ansible loads the file automatically, so omit `-e @secrets.yml`:

```bash
mkdir -p playbooks/tasks/host_vars
ansible-vault create playbooks/tasks/host_vars/switch1.yml
ansible-playbook -i playbooks/tasks/inventory facts.yml --ask-vault-pass
```

Create one file per inventory hostname. Use encrypted `group_vars` when several
hosts share variables.

### Encrypt an individual value

To encrypt only the password in an otherwise plain-text variables file:

```bash
ansible-vault encrypt_string --prompt --name fos_password
```

Enter the vault password and the value to encrypt when prompted. Paste the
result, indented, under `credential:` in place of its plain `fos_password` line.

### Unattended runs

For cron jobs or pipelines, read the vault password from a file. Keep it outside
the repository and readable only by the user running the playbook:

```bash
ansible-playbook -i playbooks/tasks/inventory facts.yml -e @secrets.yml --vault-password-file ~/.vault_pass

# Or set the password file once in the environment.
export ANSIBLE_VAULT_PASSWORD_FILE=~/.vault_pass
ansible-playbook -i playbooks/tasks/inventory facts.yml -e @secrets.yml
```

### Automation Controller

Keep encrypted `host_vars` or `group_vars` in the project, or load an encrypted
file with `vars_files` in the playbook. Attach an
[Ansible Vault credential](https://docs.redhat.com/en/documentation/red_hat_ansible_automation_platform/2.6/secure-ref_controller_credential_vault)
to the job template so the controller can decrypt the file at runtime. For
scheduled jobs, supply the vault password in that credential instead of selecting
**Prompt on launch**.

## Choose a module

Use a dedicated module when one covers the task. Use generic object modules for
other REST configuration objects supported by the switch and the module inputs.

| Task                                                       | Modules                                                                                                 |
| ---------------------------------------------------------- | ------------------------------------------------------------------------------------------------------- |
| Check collection/FOS compatibility                         | `brocade_module_compatibility`                                                                          |
| Manage aliases, zones, or zoning configurations            | `brocade_zoning_alias`, `brocade_zoning_zone`, `brocade_zoning_cfg`                                     |
| Copy zoning objects                                        | `brocade_zoning_copy`                                                                                   |
| Disable the active zoning configuration                    | `brocade_zoning_cfg_disable`                                                                            |
| Configure default zoning access                            | `brocade_zoning_default_zone`                                                                           |
| Configure a specific switch feature                        | Dedicated configuration module from the [catalogue](#module-catalogue)                                  |
| Configure a supported writable YANG container              | `brocade_singleton_obj`                                                                                 |
| Configure a supported writable YANG list                   | `brocade_list_obj`                                                                                      |
| Read switch data                                           | `brocade_facts`, `brocade_singleton_obj_facts`, `brocade_list_obj_facts`, or a specialized facts module |
| Run firmware, file transfer, or other operations           | Dedicated operation module or `brocade_scalar_operation`                                                |
| Reconcile IP storage (IPS) entries and wait for completion | `brocade_operation`                                                                                     |
| Submit explicit IPS actions; poll for completion           | `brocade_list_operation`                                                                                |
| Monitor operation status                                   | `brocade_operation_show_status`                                                                         |

Prefix each name with `brocade.fos.` in a playbook. The following examples are
**tasks** to place under a play's `tasks:` key.

## Manage zoning

### Create or update entries

Use `brocade_zoning_alias`, `brocade_zoning_zone`, and `brocade_zoning_cfg` for
aliases, zones, and configurations (CFGs), respectively. Each takes a list of
entries with `name` and `members`. Zones can also take `principal_members`
for peer zoning.

This task creates two aliases, or updates their members if they already exist:

```yaml
- name: Configure aliases
  brocade.fos.brocade_zoning_alias:
    credential: "{{ credential }}"
    vfid: -1
    aliases:
      - name: alias_host_1
        members:
          - aa:bb:cc:dd:ee:ff:11:1a
          - aa:bb:cc:dd:ee:ff:11:1b
      - name: alias_target_1
        members:
          - aa:bb:cc:dd:ee:ff:11:1c
```

### Update members

Object lists and member lists have different behavior:

| Input                                                              | Result                                                                                  |
| ------------------------------------------------------------------ | --------------------------------------------------------------------------------------- |
| An alias, zone, or CFG is omitted from the task                    | The existing object remains unchanged                                                   |
| `members` or `principal_members`, with neither member mode enabled | The supplied list is the desired membership of that object; omitted members are removed |
| `members_add_only: true`                                           | Add supplied members and preserve existing members                                      |
| `members_remove_only: true`                                        | Remove the supplied members                                                             |

Use one member mode per task. See the examples for
[default replacement](https://github.com/brocade/brocade.fos/blob/main/playbooks/tasks/zoning_zone_add.yml),
[adding members](https://github.com/brocade/brocade.fos/blob/main/playbooks/tasks/zoning_zone_members_add_only.yml),
and [removing members](https://github.com/brocade/brocade.fos/blob/main/playbooks/tasks/zoning_zone_members_remove_only.yml).

### Delete entries

Use `aliases_to_delete`, `zones_to_delete`, or `cfgs_to_delete` to delete whole
objects. Keep creation/update lists and deletion lists in separate tasks.

```yaml
- name: Delete aliases
  brocade.fos.brocade_zoning_alias:
    credential: "{{ credential }}"
    vfid: -1
    aliases_to_delete:
      - name: alias_host_1
      - name: alias_target_1
```

See [zoning_zone_delete.yml](https://github.com/brocade/brocade.fos/blob/main/playbooks/tasks/zoning_zone_delete.yml)
for zone and CFG deletion examples.

### Copy objects

Use `brocade_zoning_copy` with `object_name` and `new_name` to copy an alias,
zone, or CFG. Later runs reconcile the destination with changes to the source.
See [zoning_copy.yml](https://github.com/brocade/brocade.fos/blob/main/playbooks/tasks/zoning_copy.yml).

### Save or activate a configuration

After changing zoning entries, the modules re-enable the current CFG if one is
active, or save the defined configuration if none is active. Failed updates
attempt to abort the zoning transaction.

Set `active_cfg` on `brocade_zoning_cfg` to enable a specific configuration:

```yaml
- name: Configure and activate a zoning configuration
  brocade.fos.brocade_zoning_cfg:
    credential: "{{ credential }}"
    vfid: -1
    cfgs:
      - name: cfg_1
        members:
          - zone_1
          - zone_2
    active_cfg: cfg_1
```

## Configure generic objects

### Map YANG names to task inputs

For `brocade_singleton_obj` and `brocade_list_obj`, set `module_name` to the
YANG module and `obj_name` or `list_name` to the object. These selector values
accept hyphens or underscores. Use underscores in attribute keys:
`chassis-user-friendly-name` becomes `chassis_user_friendly_name`.

Check the module's documented inputs and the YANG model for your FOS version
for writable leaves, required keys, and valid values. The
[Brocade YANG repository](https://github.com/brocade/yang) contains models by
FOS version. Follow each Ansible module's documented input types and examples
when its inputs differ from the REST representation.

IPS modules `brocade_operation` and `brocade_list_operation` use the selected
list's original attribute names, such as `vrfID` and `dhcpEnabled`. Their
`module_name` values are case-sensitive; follow their module documentation.

### Configure a singleton

A singleton is a YANG container with one instance in its REST scope. Supply its
leaves in `attributes`. This task changes the chassis name only if needed:

```yaml
- name: Set the chassis name
  brocade.fos.brocade_singleton_obj:
    credential: "{{ credential }}"
    vfid: -1
    module_name: brocade_chassis
    obj_name: chassis
    attributes:
      chassis_user_friendly_name: XYZ
```

### Configure a list

A YANG list contains multiple entries identified by key leaves. Supply those
keys and the attributes to configure in `entries`.

| `all_entries`      | Behavior                                                                              |
| ------------------ | ------------------------------------------------------------------------------------- |
| `false`            | Add or update supplied entries; preserve entries omitted from the task                |
| `true`, or omitted | Treat `entries` as the complete desired list; delete existing entries omitted from it |

Set `all_entries: false` when managing only part of a list. This task configures
two SNMPv3 accounts while preserving other accounts:

```yaml
- name: Configure SNMPv3 accounts
  brocade.fos.brocade_list_obj:
    credential: "{{ credential }}"
    vfid: -1
    module_name: brocade_snmp
    list_name: v3_account
    all_entries: false
    entries:
      - index: 1
        user_name: snmp_monitor_1
        user_group: read-only
      - index: 2
        user_name: snmp_monitor_2
        user_group: read-only
```

SNMPv3 uses `user_name`; `community_name` belongs to SNMPv1 accounts. See
[snmp.yml](https://github.com/brocade/brocade.fos/blob/main/playbooks/tasks/snmp.yml)
for authentication and privacy settings. Use `delete_entries` in a separate
task to delete selected list entries explicitly.

## Reference

### Module catalogue

The following tables list the collection's modules. Prefix each name with
`brocade.fos.` when invoking it. For full options and examples, run
`ansible-doc brocade.fos.<module_name>`. Available switch features depend on
the FOS version and hardware; see the
[release history](https://github.com/brocade/brocade.fos/blob/main/versioning.md).

#### Switch, fabric, and Access Gateway

| Module                                                            | Purpose                       |
| ----------------------------------------------------------------- | ----------------------------- |
| `brocade_access_gateway_n_port_map`                               | Configure AG N-Port mappings  |
| `brocade_access_gateway_n_port_settings`                          | Configure AG N-Port settings  |
| `brocade_access_gateway_policy`                                   | Configure AG policies         |
| `brocade_access_gateway_port_group`                               | Configure AG port groups      |
| `brocade_chassis`                                                 | Configure chassis attributes  |
| `brocade_fibrechannel_configuration_fabric`                       | Configure fabric attributes   |
| `brocade_fibrechannel_configuration_port_configuration`           | Configure port behavior       |
| `brocade_fibrechannel_logical_switch_fibrechannel_logical_switch` | Configure logical switches    |
| `brocade_fibrechannel_switch`                                     | Configure switch attributes   |
| `brocade_interface_fibrechannel`                                  | Configure Fibre Channel ports |

#### Facts and compatibility

| Module                               | Purpose                                                                     |
| ------------------------------------ | --------------------------------------------------------------------------- |
| `brocade_fabric_switch_facts_by_pid` | Find the fabric switch for a device PID                                     |
| `brocade_facts`                      | Gather facts for selected REST areas                                        |
| `brocade_ips_facts`                  | Gather IP storage facts                                                     |
| `brocade_module_compatibility`       | Check switch FOS against the installed collection release's tested versions |
| `brocade_zoning_alias_facts_by_wwn`  | Find zoning information by WWN                                              |

#### Generic objects

| Module                        | Purpose                            |
| ----------------------------- | ---------------------------------- |
| `brocade_list_obj`            | Configure entries in a REST list   |
| `brocade_list_obj_facts`      | Gather facts from a REST list      |
| `brocade_singleton_obj`       | Configure a REST singleton         |
| `brocade_singleton_obj_facts` | Gather facts from a REST singleton |

#### Logging, MAPS, and time

| Module                          | Purpose                  |
| ------------------------------- | ------------------------ |
| `brocade_logging_audit`         | Configure audit logging  |
| `brocade_logging_syslog_server` | Configure syslog servers |
| `brocade_maps_maps_config`      | Configure MAPS settings  |
| `brocade_maps_maps_policy`      | Configure MAPS policies  |
| `brocade_maps_rule`             | Configure MAPS rules     |
| `brocade_time_clock_server`     | Configure clock servers  |
| `brocade_time_time_zone`        | Configure the time zone  |

#### Operations

| Module                               | Purpose                                                                       |
| ------------------------------------ | ----------------------------------------------------------------------------- |
| `brocade_list_operation`             | Submit IPS entries with explicit actions; poll status separately              |
| `brocade_operation`                  | Reconcile IPS entries and wait for each operation to complete                 |
| `brocade_operation_firmwaredownload` | Initiate a firmware download                                                  |
| `brocade_operation_license`          | Perform license operations                                                    |
| `brocade_operation_show_status`      | Retrieve operation status                                                     |
| `brocade_operation_supportsave`      | Initiate SupportSave collection                                               |
| `brocade_scalar_operation`           | Run an operation with dictionary input, such as configuration upload/download |

#### Security

| Module                                            | Purpose                                         |
| ------------------------------------------------- | ----------------------------------------------- |
| `brocade_security_ipfilter_policy`                | Configure IP filter policies                    |
| `brocade_security_ipfilter_rule`                  | Configure IP filter rules                       |
| `brocade_security_ldap_role_map`                  | Configure LDAP role mappings                    |
| `brocade_security_password`                       | Change a switch account password                |
| `brocade_security_sec_crypto_cfg_template_action` | Import or export crypto configuration templates |
| `brocade_security_security_certificate_action`    | Import or export certificates and CSRs          |
| `brocade_security_security_certificate_generate`  | Generate certificates or CSRs                   |
| `brocade_security_sshutil_public_key`             | Delete SSH public keys                          |
| `brocade_security_sshutil_public_key_action`      | Import or export SSH public keys                |
| `brocade_security_user_config`                    | Configure login accounts                        |

#### SNMP

| Module                    | Purpose                          |
| ------------------------- | -------------------------------- |
| `brocade_snmp_system`     | Configure SNMP system settings   |
| `brocade_snmp_v1_account` | Configure SNMPv1 accounts        |
| `brocade_snmp_v1_trap`    | Configure SNMPv1 trap recipients |
| `brocade_snmp_v3_account` | Configure SNMPv3 accounts        |
| `brocade_snmp_v3_trap`    | Configure SNMPv3 trap recipients |

#### Zoning

| Module                        | Purpose                                    |
| ----------------------------- | ------------------------------------------ |
| `brocade_zoning_alias`        | Configure aliases                          |
| `brocade_zoning_cfg`          | Configure or enable a zoning configuration |
| `brocade_zoning_cfg_disable`  | Disable the active zoning configuration    |
| `brocade_zoning_copy`         | Copy an alias, zone, or configuration      |
| `brocade_zoning_default_zone` | Configure default zoning access            |
| `brocade_zoning_zone`         | Configure zones, including peer zones      |

### Example singleton object mappings

Use these `module_name` / `obj_name` pairs with `brocade_singleton_obj`.
The example links show the corresponding feature, often through its dedicated
module. Check feature support for your FOS version.

| `module_name`                        | `obj_name`           | Example playbook                                                                                                        |
| ------------------------------------ | -------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| `brocade_chassis`                    | `chassis`            | [switch_initial_config.yml](https://github.com/brocade/brocade.fos/blob/main/playbooks/tasks/switch_initial_config.yml) |
| `brocade_fibrechannel_configuration` | `fabric`             | [switch_initial_config.yml](https://github.com/brocade/brocade.fos/blob/main/playbooks/tasks/switch_initial_config.yml) |
| `brocade_fibrechannel_configuration` | `port_configuration` | [switch_initial_config.yml](https://github.com/brocade/brocade.fos/blob/main/playbooks/tasks/switch_initial_config.yml) |
| `brocade_logging`                    | `audit`              | [switch_initial_config.yml](https://github.com/brocade/brocade.fos/blob/main/playbooks/tasks/switch_initial_config.yml) |
| `brocade_maps`                       | `maps_config`        | [relay_server.yml](https://github.com/brocade/brocade.fos/blob/main/playbooks/tasks/relay_server.yml)                   |
| `brocade_security`                   | `password`           | [password.yml](https://github.com/brocade/brocade.fos/blob/main/playbooks/tasks/password.yml)                           |
| `brocade_snmp`                       | `system`             | [snmp.yml](https://github.com/brocade/brocade.fos/blob/main/playbooks/tasks/snmp.yml)                                   |
| `brocade_time`                       | `clock_server`       | [switch_initial_config.yml](https://github.com/brocade/brocade.fos/blob/main/playbooks/tasks/switch_initial_config.yml) |
| `brocade_time`                       | `time_zone`          | [switch_initial_config.yml](https://github.com/brocade/brocade.fos/blob/main/playbooks/tasks/switch_initial_config.yml) |

### Example list object mappings

Use configuration rows with `brocade_list_obj` and facts rows with
`brocade_list_obj_facts`. Include the object's key leaves in each configuration
entry. As above, example playbooks may use the corresponding dedicated module.

| `module_name`                 | `list_name`                | Usage         | Example playbook                                                                                                        |
| ----------------------------- | -------------------------- | ------------- | ----------------------------------------------------------------------------------------------------------------------- |
| `brocade_fibrechannel_switch` | `fibrechannel_switch`      | Configuration | [switch_initial_config.yml](https://github.com/brocade/brocade.fos/blob/main/playbooks/tasks/switch_initial_config.yml) |
| `brocade_interface`           | `fibrechannel`             | Configuration | [portname.yml](https://github.com/brocade/brocade.fos/blob/main/playbooks/tasks/portname.yml)                           |
| `brocade_logging`             | `syslog_server`            | Configuration | [switch_initial_config.yml](https://github.com/brocade/brocade.fos/blob/main/playbooks/tasks/switch_initial_config.yml) |
| `brocade_name_server`         | `fibrechannel_name_server` | Facts         | [find_ns_by_pwwn.yml](https://github.com/brocade/brocade.fos/blob/main/playbooks/tasks/find_ns_by_pwwn.yml)             |
| `brocade_snmp`                | `v3_account`               | Configuration | [snmp.yml](https://github.com/brocade/brocade.fos/blob/main/playbooks/tasks/snmp.yml)                                   |
| `brocade_snmp`                | `v3_trap`                  | Configuration | [snmp.yml](https://github.com/brocade/brocade.fos/blob/main/playbooks/tasks/snmp.yml)                                   |
| `brocade_security`            | `user_config`              | Configuration | [switch_initial_config.yml](https://github.com/brocade/brocade.fos/blob/main/playbooks/tasks/switch_initial_config.yml) |
| `brocade_security`            | `ipfilter_rule`            | Configuration | [switch_initial_config.yml](https://github.com/brocade/brocade.fos/blob/main/playbooks/tasks/switch_initial_config.yml) |
