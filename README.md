# Linux Web Server Project

# Project Overview
This project uses the base OS installation of a Linux Server using Ubuntu and prepare it to host a web application.
Also, provision the AWS Lightsail instance using OS only option then configure the AWS services like Route53 domain and host configuration to use "somphouang.com".
The process steps involves installing and configuring the Apache Web Server, WSGI to launch the python flask web application, configuring a progresql database server, and deploying an ItemCatalog web application onto it.
 
# STEP 1: Get started on AWS Lightsail
* 1. Create an account with Amazon Web Services cloud [aws.amazon.com](https://aws.amazon.com)
* Click on the top right button "sign In to the Console" log into console and enter the login.

* 2. Under Compute services click on "Lightsail"
* 3. Create Instance to create new Instance 
* 4. Selet a platform "Linux/Unix" and choose blueprint OS Only, select Ubuntu 16.04 LTS
* 5. Choose instance plan of $3.50 USD per month.
* 6. Can change instance name or leave the default.
* 7. When Instance is created and running, go to the Networking tab and choose "Create static IP" 
and attached it to the new Lightsail instance.
* 8. Go back into Instances tab, click on the "..." on the top right and choose "Manage"
* 9. Click on "Connect using SSH" and follow the STEP 2 below.

* 10. Optional and used in this project:

## In AWS Console, Route53 
* 1. Register domain "somphouang.com"
* 2. In Hosted Zone, select "somphouang.com"
* 3. Create Record Set with Type "A - IPv4 address" and enter Value "18.233.103.5"
 
# STEP 2: Configuring the AWS Lightsail Instance
* 1. When connected using the AWS Console web interface, from "Connect using SSH"
* a.  Add the "grader" user
```
$ adduser grader
```
* In this project, enter the password: <sent to grader in the comment>
* b.  Give the sudo privilege to grader user
```
$ usermod -aG sudo grader
```
* It is also possible to do this by configuring the sudoer
```
$ sudo nano /etc/sudoers.d/grader
```

Enter below into the file /etc/sudoers.d/grader
```
grader ALL=(ALL) NOPASSWD:ALL

```
Then press Ctrl+O to flush to file and then Ctrl+x to exit.

* c. Configuring the UTC Timezone
```
$ sudo dpkg-reconfigure tzdata
```
This will result in something like below
```
Current default time zone: 'Etc/UTC'
Local time is now:      Sat Jan 26 02:01:32 UTC 2019.
Universal Time is now:  Sat Jan 26 02:01:32 UTC 2019.
```

* d. Change the SSH port from 22 to 2200
Edit the file in /etc/ssh/sshd_config
```
$ sudo nano /etc/ssh/sshd_config
```

Change in the file from "Port 22" to "Port 2200"
```
# What ports, IPs and protocols we listen for
Port 2200
```

At this point, the new user grader exist and has sudo, however, we need to add the SSH key for remote login
* On the PC, say using git bash or any other OS platform use the ssh-keygen
``` 
$ ssh-key -t rsa -b 4096 -C admin@somphouang.com
```
This will create the file if using all defaults path and filename into "folder/.ssh/"
1. File id_rsa --> Used for the key to log into the Remote Linux Server
2. File id_rsa.pub --> copy this content inside the file to the Linux Server using 
```
$ sudo nano /home/grader/.ssh/authorized_keys
```
* Make sure that on the AWS Lightsail Home web interface click on the Instance and go to Network tab, add the new rule for custom TCP 2200, when tested below successfully, can go remove the rule for SSH at 22.
* In the PC using git bash, try to log into the remote Linux Server by ssh
```
$ ssh -p 2200 grader@somphouang.com -i id_rsa
```
This should be successful otherwise, try restarting the SSH service on the Linux Server using command
```
$ sudo service ssh restart
```

* e.  Install Progresql and other requirements
```
$ sudo apt-get update
$ sudo apt-get install postgresql postgresql-contrib libpq-dev
$ sudo apt-get install python-pip
$ sudo apt-get install libapache2-mod-wsgi
$ sudo pip install psycopg2 Flask-SQLAlchemy Flask-Migrate
$ sudo pip install google_auth_oauthlib
```

* Add Postgresql user "catalogitem" and created password "udacity"
* Creating user
``` 
$ sudo -u postgres createuser catalogitem
```
Creating Database catalogitem
```
$ sudo -u postgres createdb catalogitem
```
Giving the "catalogitem" user a password
```
$ sudo -u postgres psql
psql=# alter user catalogitem with encrypted password 'udacity';
Granting privileges on database
psql=# grant all privileges on database catalogitem to catalogitem;

```

* f.  Install the Apache for Web Server
```
$ sudo apt-get update
$ sudo apt-get install apache2
```
This will create the /var/www/ folder with default webpage

* g.  Configure the Apache site
Create a folder in "/var/www/flask-prod/" and file webtool.wsgi
```
$ sudo nano /var/www/flask-prod/webtool.wsgi

#!/usr/bin/python
import sys
sys.path.append('/var/www/flask-prod/ItemCatalog/')
from app import app as application

application.secret_key = '<ENTER SECRET KEY HERE>'
application.config['SQLALCHEMY_DATABASE_URI'] = (
        'postgresql://'
        'catalogitem:udacity@localhost/catalogitem')

```

Create a folder as see "/var/www/somphouang.com/logs/" for the logs to go into when configuring the virtualhost later 

Navigate to the folder /var/www/flask-prod and get the repository project for ItemCatalog
```
$ cd /var/www/flask-prod
$ sudo git clone https://github.com/soundmos/ItemCatalog.git
```
This will create the folder "ItemCatalog" for the web application.  

Open the file app.py and modified the followings:
```
$ sudo nano /var/www/flask-prod/ItemCatalog/app.py



```


Edit the /etc/hosts with the domain name somphouang.com
```
$ sudo nano /etc/hosts

127.0.0.1 somphouang.com

# The following lines are desirable for IPv6 capable hosts
::1 ip6-localhost ip6-loopback
fe00::0 ip6-localnet
ff00::0 ip6-mcastprefix
ff02::1 ip6-allnodes
ff02::2 ip6-allrouters
ff02::3 ip6-allhosts

``` 

Configure the site to enable
```
$ sudo nano /etc/apache2/sites-enabled/somphouang.com.conf


<virtualhost *:80>
    ServerName www.somphouang.com
    ServerAdmin admin@somphouang.com
    ServerAlias somphouang.com
    ErrorLog /var/www/somphouang.com/logs/error.log
    CustomLog /var/www/somphouang.com/logs/access.log combined

    WSGIScriptAlias / /var/www/flask-prod/webtool.wsgi

    <directory /var/www/flask-prod/ItemCatalog>
        Order allow,deny
        Allow from all
    </directory>
RewriteEngine on
RewriteCond %{SERVER_NAME} =somphouang.com [OR]
RewriteCond %{SERVER_NAME} =www.somphouang.com
RewriteRule ^ https://%{SERVER_NAME}%{REQUEST_URI} [END,NE,R=permanent]
</virtualhost>

```

After completing the above steps enabe the mod-wsgi configuration and restart the apache service
```
$ sudo a2enconf mod-wsgi
$ sudo service apache2 restart
```

Configure the site to use SSL for Secure Transport when using with Google OAuth2 API, it required HTTPS.
Using the free SSL Certificate from Let's Encrypt
```
$ sudo git clone https://github.com/letsencrypt/letsencrypt /opt/letsencrypt
```
Navigate to the new /opt/letsencrypt directory
```
$ cd /opt/letsencrypt
$ sudo -H ./letsencrypt-auto certonly --standalone -d somphouang.com
$ sudo add-apt-repository ppa:certbot/certbot
$ sudo apt-get install python-certbot-apache

Enter Y, choose option 2: Renew & replace the cert, choose option 2: Redirect - Make all requests redirect to secure HTTPS..
```

When done, it will also created a new file in /etc/apache2/sites-enabled/somphouang.com-le-ssl.conf with the following:
```
<IfModule mod_ssl.c>
<virtualhost *:443>
    ServerName www.somphouang.com
    ServerAdmin admin@somphouang.com
    ServerAlias somphouang.com
    ErrorLog /var/www/somphouang.com/logs/error.log
    CustomLog /var/www/somphouang.com/logs/access.log combined

    WSGIScriptAlias / /var/www/flask-prod/webtool.wsgi

    <directory /var/www/flask-prod/ItemCatalog>
        Order allow,deny
        Allow from all
    </directory>
SSLCertificateFile /etc/letsencrypt/live/somphouang.com/fullchain.pem
SSLCertificateKeyFile /etc/letsencrypt/live/somphouang.com/privkey.pem
Include /etc/letsencrypt/options-ssl-apache.conf
</virtualhost>
</IfModule>

```

# STEP 3: Update the Google API Client Key Instruction

### Google API Client Key Instruction
1. Sign in at `https://console.developers.google.com/apis/`
2. Create a new Web application
3. Go to Credential under `APIs & Services`
4. Add the following to the field `Authorized JavaScript origins`
```
http://somphouang.com
https://somphouang.com
```
5. Add the following the field `Authorized redirect URIs`
```
http://somphouang.com/login
http://somphouang.com/catalog
http://somphouang.com/oauth2callback
https://somphouang.com/login
https://somphouang.com/catalog
https://somphouang.com/oauth2callback

```


# STEP 4: Please visit [http://somphouang.com](http://somphouang.com) to test run this web application for Item Catalog!

Thank you to Udacity Nanodegree Course trainers for Fullstack Web Developer and teaching me to learn to be able to develop exciting projects like this one. 
