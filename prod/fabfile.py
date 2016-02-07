# fabfile.py

import os

from fabric.api import *
from fabric.contrib.files import sed

"""
Fabric Script which does the following things:
    # Uploading the SSH keys pair (public/private) on to the remote servers.
    # Creating non-root-users and specific groups for them.
    # Preventing SSH-ing into the remote server as a root-user.
"""

# Initialising Base Dir Path
abs_dir_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Declaring all the env's Globals

# Root User
env.user = 'root'

# List of remote IP's
# env.hosts = ['<remote-server-ip>']

# Password for the remote server
# env.password = '<remote-server-password>'

# Full name of the user
env.full_name_user = 'Saurabh Sharma'

# User group
env.user_group = 'deployers'

# User for the above group
env.user_name = 'deployer'

# SSH Keys Path
env.ssh_keys_dir = os.path.join(abs_dir_path, 'ssh_keys')
print env.ssh_keys_dir


def start_provision():
    """
    Starts off server provisioning
    """
    # creating new Dir for a new remote server
    env.ssh_keys_name = os.path.join(
        env.ssh_keys_dir, env.host_string + "_prod_key")
    print env.ssh_keys_name
    local('ssh-keygen -t rsa -b 2048 -f {}'.format(env.ssh_keys_name))
    local(
        'cp {} {}/authorized_keys'.format(env.ssh_keys_name + ".pub", env.ssh_keys_dir))
    # Preventing Root SSH-ing into the remote server
    sed('/etc/ssh/sshd_config', '^UsePAM yes', 'UsePAM no')
    sed('/etc/ssh/sshd_config', '^PermitRootLogin yes', 'PermitRootLogin no')
    sed('/etc/ssh/sshd_config', '^#PasswordAuthentication yes',
        'PasswordAuthentication no')

    install_ansible_dependency()
    create_deployers_group()
    ceate_deployer_user()
    upload_keys()
    run('service sshd reload')
    upgrade_server()


def upgrade_server():
    """
    Upgrade the server as a root user
    """
    run('dnf upgrade -y')
    # optional command(had to use for my Fedora 23 Server)
    run('dnf install -y python')
    run('reboot')


def install_ansible_dependency():
    """
    Install the python-dnf module for making Ansible
    communicate with the Fedora's Package Manager
    """
    run('dnf install -y python-dnf')


def create_deployers_group():
    """
    Creates a group for all the developers on the project
    """
    run('groupadd {}'.format(env.user_group))
    run('mv /etc/sudoers /etc/sudoers-backup')
    run('(cat /etc/sudoers-backup; echo "%' +
        env.user_group + ' ALL=(ALL) ALL") > /etc/sudoers')
    run('chmod 440 /etc/sudoers')


def ceate_deployer_user():
    """
    Creates a user for Deployers group
    """
    run('adduser -c "{}" -m -g {} {}'.format(env.full_name_user,
                                             env.user_group, env.user_name))
    run('passwd {}'.format(env.user_name))
    run('usermod -a -G {} {}'.format(env.user_group, env.user_name))
    run('mkdir /home/{}/.ssh'.format(env.user_name))
    run('chown -R {} /home/{}/.ssh'.format(env.user_name, env.user_name))
    run('chgrp -R {} /home/{}/.ssh'.format(env.user_group, env.user_name))


def upload_keys():
    """
    Uploads the ssh public/private keys on to the remote server via scp.
    """
    scp_command = "scp {} {}/authorized_keys {}@{}:~/.ssh".format(
        env.ssh_keys_name + '.pub',
        env.ssh_keys_dir,
        env.user_name,
        env.host_string
    )
    local(scp_command)
