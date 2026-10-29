# Brocade FOS collection

The `brocade.fos` collection provides Ansible modules and example playbooks
for storage administrators to manage Brocade Fibre Channel switches through
the Fabric OS (FOS) REST API. It supports gathering facts and managing FOS
switches.

## Requirements

- See the [compatibility matrix](https://github.com/brocade/brocade.fos/blob/main/versioning.md)
  for tested Python, ansible-core, and FOS versions.
- The minimum Ansible version is declared in
  [meta/runtime.yml](https://github.com/brocade/brocade.fos/blob/main/meta/runtime.yml).
- Network access from the controller to the switch REST API, REST enabled on
  the switch, and credentials with permission to perform the requested operation.

## Installation

Install the collection on the controller or in the execution environment
where your playbooks run. The `ansible-galaxy` command is supplied by
`ansible-core`.

The collection requirements for the example playbooks are listed in
[collections/requirements.yml](https://github.com/brocade/brocade.fos/blob/main/collections/requirements.yml).

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

To install a release published on Ansible Galaxy:

```bash
ansible-galaxy collection install brocade.fos --server https://galaxy.ansible.com/
```

### Git

Install Git, then install the collection directly from the repository:

```bash
ansible-galaxy collection install git+https://github.com/brocade/brocade.fos.git,main
```

Replace `main` with a tag or commit to select a specific source revision.

### Development dependencies

For development dependencies, testing, and documentation tools, follow the
[Development Setup guide](https://github.com/brocade/brocade.fos/blob/main/CONTRIBUTING.md#development-setup).

## Connection to FOS

Playbooks connect to FOS through its REST API.

## How to create playbooks

Use the dedicated zoning modules when creating zoning playbooks. These
modules handle operational details that would otherwise require explicit
configuration with generic templates. Most other FOS REST objects can be
managed using the generic modules brocade_singleton_obj and brocade_list_obj.

### Zoning

Use the brocade_zoning_alias, brocade_zoning_zone, and brocade_zoning_cfg
modules to update aliases, zones, and CFGs, respectively, in the FOS
zoning database.

When adding Alias, Zone or CFG, each module takes a list of entries.
Each entry contains a name and a list of members. brocade_zoning_zone
module can take principal_members in addition to members if you are
interested in creating peer zones. During addition, entries are
considered additive to the existing FOS Zoning database. In other words,
if a playbook contains Aliases AAA and BBB and FOS Zoning database
contained BBB and CCC before the execution of the playbook, the result
of the playbook will contain Aliases AAA, BBB, and CCC. CCC is not
removed even though it is not mentioned in the playbook.

The following example creates the alias alias_host_1 with two members
and the alias alias_target_1 with one member.

```yaml
- name: Create aliases
  brocade_zoning_alias:
    credential:
      fos_ip_addr: 198.51.100.1
      fos_user_name: user_name
      fos_password: user_password
      https: "false"
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

Alias, Zone, or CFG entry is deleted only if aliases_to_delete,
zones_to_delete or cfgs_to_delete variable is provided with a list of
Aliases, Zones or CFGs to delete.

The following example deletes the aliases alias_host_1 and alias_target_1.

```yaml
- name: Delete aliases
  brocade_zoning_alias:
    credential:
      fos_ip_addr: 198.51.100.1
      fos_user_name: user_name
      fos_password: user_password
      https: "false"
    vfid: -1
    aliases_to_delete:
      - name: alias_host_1
      - name: alias_target_1
```

Please refer to playbooks/tasks/zoning_zone_delete.yml for additional reference.

Alias, Zone, or CFG entry addition and deletion are mutually exclusive.

Members of existing alias, zone, or CFG entries are updated during a play
if a difference exists between a playbook and the existing FOS Zoning
database. By default, the members and principal_members parameters each specify the
complete desired list rather than an additive list. The resulting FOS zoning database
will therefore contain only the members defined in the playbook. For example, if a
playbook defines an Alias with members AAA and BBB and the Alias in FOS
Zoning database contained BBB and CCC before the execution of the
playbook, the result of the playbook will be an Alias with AAA and BBB.
AAA was added and CCC was deleted.

However, if optional members_add_only variable is set to True for the
task, the result of the previous playbook will be AAA, BBB, and CCC,
where AAA is added and CCC remains.

Conversely, set the optional members_remove_only variable to True to
remove specific alias, zone, or CFG members.

Please refer to playbooks/tasks/zoning_zone_add.yml for default behavior
reference, playbooks/tasks/zoning_zone_members_add_only.yml for members_add_only
reference and playbooks/tasks/zoning_zone_members_remove_only.yml for
members_remove_only reference.

To copy an existing alias, zone, or CFG to a new
object, use the brocade_zoning_copy module. If any changes are detected
in the Zoning object - for example, new member is added to a Zone -
being copied from, the difference is newly applied to the destination
object - i.e. the added member is added to the destination Zone if
already created.

During execution, each module will update the defined configuration and
either save or enable CFG depending on whether a CFG is already active on
FOS. If any error is encountered, the changes are aborted and the FOS
Zoning database will revert back to pre-task state.

An optional active_cfg variable is only applicable to brocade_zoning_cfg
module. The variable is used to specify a CFG to be enabled.

### YANG module/object specific Ansible modules

The following is a list of additional Ansible modules beyond zoning. These
modules typically take a dictionary or a list of dictionaries. The
dictionary contains attributes matching YANG REST leaf definitions.
Use underscores in dictionary attribute names in place of the hyphens
used in YANG REST leaf names. For example, my-leaf-name in a YANG model
becomes my_leaf_name in an Ansible playbook.

| Ansible module name | Description |
|---|---|
| brocade_chassis.py | update chassis attributes |
| brocade_facts.py | retrieve facts for specified areas |
| brocade_fibrechannel_configuration_fabric.py | update fabric configuration |
| brocade_fibrechannel_configuration_port_configuration.py | update port configuration |
| brocade_fibrechannel_switch.py | update switch configuration |
| brocade_interface_fibrechannel.py | update FC port configuration |
| brocade_logging_audit.py | update audit configuration |
| brocade_logging_syslog_server.py | update syslog server configuration |
| brocade_maps_maps_config.py | update MAPS configuration |
| brocade_operation_show_status.py | show status on operations initiated |
| brocade_operation_supportsave.py | initiate supportsave operation |
| brocade_security_ipfilter_policy.py | update ip filter policy |
| brocade_security_ipfilter_rule.py | update ip filter rule |
| brocade_security_password.py | update password. Passwords are given in clear text |
| brocade_security_security_certificate_action.py | import/export CSR/certificate |
| brocade_security_security_certificate_generate.py | generate CSR/certificate |
| brocade_security_user_config.py | update login accounts |
| brocade_snmp_system.py | update snmp system attributes |
| brocade_snmp_v3_account.py | update snmp v3 account |
| brocade_snmp_v3_trap.py | update snmp v3 trap |
| brocade_time_clock_server.py | update clock server configuration |
| brocade_time_time_zone.py | update time zone |

### How to add attribute input to modules

As documented above, attribute names passed to modules match YANG REST
attribute names, with hyphens replaced by underscores to follow Ansible conventions.
Most attribute values also match their YANG REST definitions. Details
can be found in [Brocade YANG models](https://github.com/brocade/yang).

However, in some instances, attribute values are modified to
maintain consistency and improve playbook readability.

| Ansible module name | Attribute name | Value description |
|---|---|---|
| brocade_access_gateway_policy.py | auto_policy_enabled | boolean |
| brocade_access_gateway_policy.py | port_group_policy_enabled | boolean |
| brocade_fibrechannel_switch.py | enabled_state | boolean |
| brocade_interface_fibrechannel.py | compression_configured | boolean |
| brocade_interface_fibrechannel.py | credit_recovery_enabled | boolean |
| brocade_interface_fibrechannel.py | csctl_mode_enabled | boolean |
| brocade_interface_fibrechannel.py | d_port_enable | boolean |
| brocade_interface_fibrechannel.py | e_port_disable | boolean |
| brocade_interface_fibrechannel.py | enabled_state | boolean |
| brocade_interface_fibrechannel.py | encryption_enabled | boolean |
| brocade_interface_fibrechannel.py | ex_port_enabled | boolean |
| brocade_interface_fibrechannel.py | fault_delay_enabled | boolean |
| brocade_interface_fibrechannel.py | fec_enabled | boolean |
| brocade_interface_fibrechannel.py | g_port_locked | boolean |
| brocade_interface_fibrechannel.py | isl_ready_mode_enabled | boolean |
| brocade_interface_fibrechannel.py | long_distance | Disabled/L0/L1/L2/LE/L0.5/LD/LS |
| brocade_interface_fibrechannel.py | los_tov_mode_enabled | Disabled/Fixed/FixedAuto |
| brocade_interface_fibrechannel.py | max_speed | 32Gig/16Gig/10Gig/8Gig/4Gig/2Gig/1Gig/Auto |
| brocade_interface_fibrechannel.py | mirror_port_enabled | boolean |
| brocade_interface_fibrechannel.py | n_port_enabled | boolean |
| brocade_interface_fibrechannel.py | non_dfe_enabled | boolean |
| brocade_interface_fibrechannel.py | npiv_enabled | boolean |
| brocade_interface_fibrechannel.py | npiv_flogi_logout_enabled | boolean |
| brocade_interface_fibrechannel.py | persistent_disable | boolean |
| brocade_interface_fibrechannel.py | port_autodisable_enabled | boolean |
| brocade_interface_fibrechannel.py | qos_enabled | boolean |
| brocade_interface_fibrechannel.py | rscn_suppression_enabled | boolean |
| brocade_interface_fibrechannel.py | sim_port_enabled | boolean |
| brocade_interface_fibrechannel.py | speed | 32Gig/16Gig/10Gig/8Gig/4Gig/2Gig/1Gig/Auto |
| brocade_interface_fibrechannel.py | target_driven_zoning_enable | boolean |
| brocade_interface_fibrechannel.py | trunk_port_enabled | boolean |
| brocade_interface_fibrechannel.py | vc_link_init | boolean |
| brocade_interface_fibrechannel.py | via_tts_fec_enabled | boolean |
| brocade_security_password.py | new_password | clear text |
| brocade_security_password.py | old_password | clear text |
| brocade_security_security_certificate_action.py | remote_user_password | clear text |
| brocade_security_sshutil_public_key_action.py | remote_user_password | clear text |
| brocade_security_sec_crypto_cfg_template_action.py | remote_user_password | clear text |
| brocade_security_user_config.py | password | clear text |
| brocade_snmp_v3_account.py | authentication_password | clear text |

### Template based Ansible modules

Dedicated Ansible modules are used to handle REST YANG objects that need specific
handling; else template based Ansible modules are used.

#### Singleton object

A singleton object is a FOS REST object with only one instance on a
FOS switch. These objects are defined as YANG containers. Use the
brocade_singleton_obj module and the YANG definition to create
playbooks that update them.

All FOS REST YANG models are published at github.com/brocade/yang.

For example, brocade-chassis module contains an object named chassis.
And chassis object contains a string type leaf named
chassis-user-friendly-name, among other attributes.

```
module brocade-chassis {
    container brocade-chassis {
        container chassis {
            leaf chassis-user-friendly-name {
            }
        }
    }
}
```

To create a playbook that sets chassis-user-friendly-name to XYZ:

1. use brocade_singleton_obj module
2. provide the module_name to match the YANG REST FOS module name -
   brocade-chassis or brocade_chassis. "-" and "_" are interchangeable as
   module_name.
3. provide the obj_name to match the YANG REST FOS object name -
   chassis. As with module_name, "-" and "_" are interchangeable as
   obj_name.
4. provide leaf entry within attributes. Only one -
   chassis-user-friendly-name - is being referenced for the moment.
   Since Ansible variable should not contain "-", they are replaced by "_".

```yaml
- name: chassis configuration
  brocade_singleton_obj:
    credential:
      fos_ip_addr: 198.51.100.1
      fos_user_name: user_name
      fos_password: user_password
      https: "false"
    vfid: -1
    module_name: "brocade_chassis"
    obj_name: "chassis"
    attributes:
      chassis_user_friendly_name: XYZ
```

Running this playbook sets chassis-user-friendly-name to XYZ if its value
differs, or reports no change if it is already set to XYZ.

Although the module should apply to all objects in general, the
following table lists the modules and objects that have been verified
using the playbooks in the tasks directory.

| module name | object name |
|---|---|
| brocade_chassis | chassis |
| brocade_fibrechannel_configuration | fabric |
| brocade_fibrechannel_configuration | port_configuration |
| brocade_logging | audit |
| brocade-maps | maps-config |
| brocade-security | password |
| brocade-snmp | system |
| brocade_time | clock_server |
| brocade_time | time_zone |

#### List object

A list object refers to a FOS REST object that can contain multiple
entries on a FOS switch. These objects are defined as YANG lists. Use
the brocade_list_obj module and the YANG definition to create playbooks
that create, update, or delete entries.

All FOS REST YANG models are published at github.com/brocade/yang.

For example, brocade-snmp module contains an object named v3-account.
And v3-account object contains a key named index and a string type leaf
named community-name, among other attributes.

```
module brocade-snmp {
    container brocade-snmp {
        list v3-account {
            key "index";
            leaf index {
            }
            leaf community-name {
            }
        }
    }
}
```

To create a playbook to set community-name to XYZ for an entry with
index of 1, and ZYX for index of 2:

1. use brocade_list_obj module
2. provide the module_name to match the YANG REST FOS module name -
   brocade-snmp or brocade_snmp. "-" and "_" are interchangeable as
   module_name.
3. provide the list_name to match the YANG REST FOS object name -
   v3-account or v3_account. As with module_name, "-" and "_" are
   interchangeable as list_name.
4. provide an array within entries. Only key and community_string are
   being referenced for the moment. Since Ansible variable should not
   contain "-", they are replaced by "_".
5. if the array contains all the entries, all_entries variable can be
   left out or set to True. If so, entries in playbook but not in FOS
   are added, entries in both playbook and FOS are updated if different,
   and entries not in playbook but in FOS are deleted. If the array
   contains only a subset of the entries, only additions and updates are
   performed.

```yaml
- name: snmp configuration
  brocade_list_obj:
    credential:
      fos_ip_addr: 198.51.100.1
      fos_user_name: user_name
      fos_password: user_password
      https: "false"
    vfid: -1
    module_name: "brocade_snmp"
    obj_name: "v3_account"
    all_entries: False
    entries:
      - index: 1
        community_name: XYZ
      - index: 2
        community_name: ZYX
```

Running this playbook sets the community name for two entries.
Other entries already present on the switch remain unchanged.

Although the module should apply to all objects in general, the
following table lists the modules and objects that have been verified
using the playbooks in the tasks directory.

| module name | list name |
|---|---|
| brocade_fibrechannel_switch | fibrechannel_switch |
| brocade-interface | fibrechannel |
| brocade_logging | syslog_server |
| brocade-name-server | fibrechannel-name-server |
| brocade-snmp | v3-account |
| brocade-snmp | v3-trap |
| brocade_security | user_config |
| brocade-security | ipfilter-rule |

## Running Playbooks with Ansible Vault

Ansible Vault allows you to encrypt sensitive data such as credentials,
passwords, and API keys. This section explains how to run playbooks with
encrypted variables using `ansible-playbook` CLI.

### Creating Encrypted Variables File

Step 1: Create an encrypted secrets file using `ansible-vault create`:

```
ansible-vault create secrets.yml
```

This command will:

1. **Prompt for a new vault password** - Enter a strong password and remember it
2. **Confirm the password** - Re-enter the same password
3. **Open your default editor** (vi/vim/nano) to add content

Step 2: Add your credentials to the file.

Add the sensitive variables that you want to protect:

```yaml
# secrets.yml - Store sensitive credentials here

# FOS switch credentials
credential:
  fos_ip_addr: "198.51.100.1"
  fos_user_name: "user_name"
  fos_password: "user_password"
  https: "true"

# Additional sensitive variables (as needed by your playbooks)
fwdl_remote_server_password: "fwdl_remote_server_password"
```

Step 3: Save and exit. The file is now encrypted with your vault password.

#### Integrating with the inventory file

Instead of storing credentials directly on a host in
[playbooks/tasks/inventory](https://github.com/brocade/brocade.fos/blob/main/playbooks/tasks/inventory), omit the
`credential` key for that host there and supply it at runtime 
via `-e @secrets.yml` instead. 

### Running Playbooks with Vault

Any playbook can use vault-encrypted variables. The following variables are commonly
used across playbooks and can be stored in your encrypted secrets file:

**Required variables (used by all playbooks):**

- `credential` - Dictionary containing switch login credentials
  - `fos_ip_addr` - Switch IP address
  - `fos_user_name` - Login username
  - `fos_password` - Login password
  - `https` - HTTPS mode, quoted string: `"true"`, `"false"`, or `"self"`

**Optional variables (add as needed by specific playbooks):**

```
# fwdl_remote_server_password  - Remote server password (e.g., firmware download, backup)
# snmp_community       - SNMP community string
# syslog_password      - Syslog server credentials
# ldap_bind_password   - LDAP authentication password
# radius_secret        - RADIUS shared secret
```

**Running playbook with vault password prompt:**

```
ansible-playbook <your_playbook>.yml -e @secrets.yml --ask-vault-pass
```

## Documentation

Documentation can be generated by following the instructions in
[docs/documentation.rst](https://github.com/brocade/brocade.fos/blob/main/docs/documentation.rst).

## Testing and compatibility

Certification CI runs collection build/import checks, production lint, and
full sanity tests through Red Hat's Partner Certification Checker. These
checks do not exercise a live switch. The 3.0.0 lab qualification matrix covers
FOS 10.0.1 and 9.2.2d; live validation results are recorded separately. See the
[ordered validation checklist](https://github.com/brocade/brocade.fos/blob/main/PUBLISHING.md#certification-validation-checklist).

Example playbooks cover zoning, fact gathering, and configuration operations.
Select and review examples for your switch, permissions, and FOS version.

## Support

This collection is maintained by the Brocade Automation Team at Broadcom.
For certified releases obtained through Automation Hub, Red Hat customers
can open an Ansible Automation Platform support case using the **Create issue**
link on Automation Hub.

For source and community issues, use the
[GitHub issue tracker](https://github.com/brocade/brocade.fos/issues).
The maintainer contact is [Automation.BSN@broadcom.com](mailto:Automation.BSN@broadcom.com).

## Release notes

See the [changelog](https://github.com/brocade/brocade.fos/blob/main/CHANGELOG.rst)
and [version history](https://github.com/brocade/brocade.fos/blob/main/versioning.md).

## License

The collection metadata declares `GPL-3.0-or-later` and `BSD-2-Clause`.
The license texts and existing file-specific notices are retained in this release.

- [GNU GPL version 3](https://github.com/brocade/brocade.fos/blob/main/LICENSE)
- [BSD 2-Clause](https://github.com/brocade/brocade.fos/blob/main/LICENSES/BSD-2-Clause.txt)
