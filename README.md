# periscope-public-engagement-tool
Demo: [https://kind.io.tudelft.nl/periscope/](https://kind.io.tudelft.nl/periscope/)

This repository hosts code of a tool to engage citizens in participatory decision-making, developed by the Knowledge and Intelligence Design (KInD) research group in the Department of Sustainable Design Engineering, Faculty of Industrial Design Engineering, [Technische Universiteit Delft](https://www.tudelft.nl/en/).

### Acknowledgement
This project is supported by the European Commission under the [Horizon 2020](https://ec.europa.eu/programmes/horizon2020/) framework, within project [PERISCOPE](https://periscopeproject.eu/) (Pan-European Response to the Impacts of COVID-19 and future Pandemics and Epidemics). This project is a derivative of the [COCTEAU](https://github.com/DataSciencePolimi/COCTEAU) tool contributed by [Politecnico di Milano](https://www.polimi.it/) and [CEPS](https://www.ceps.eu/). Many features in this project are inspired by the COCTEAU tool and re-designed to fit the Netherlands context.

### Resources
For development, please check this [video labeling tool](https://github.com/CMU-CREATE-Lab/video-labeling-tool) for implementation examples. This project's code structure is inspired by the video labeling tool. Here is a [cheatsheet of commonly used operations](https://github.com/yenchiah/public-resources/blob/main/coding-cheatsheet.md). Please read the [coding standards](#coding-standards) section carefully before contributing to this project.

### Table of Content
- [Coding standards](#coding-standards)
- [Install PostgreSQL (administrator only)](#install-postgresql)
- [Setup back-end (administrator only)](#setup-back-end)
- [Setup Unsplash (administrator only)](#setup-unsplash)
- [Setup Google Analytics (administrator only)](#setup-ga)
- [Setup development environment](#setup-dev-env)
- [Setup initial data](#setup-init-data)
- [Manipulate database](#manipulate-database)
- [Update and test code infrastructure](#code-infrastructure)
- [Deploy back-end using uwsgi (administrator only)](#deploy-back-end-using-uwsgi)
- [Setup back-end and front-end on apache (administrator only)](#setup-apache)
- [Setup SSL certificates for https (administrator only)](#setup-https)
- [API calls](#api-calls)

# <a name="coding-standards"></a>Coding standards
When contributing code for this repository, please follow the guidelines below:
### Git workflow
- Follow the [Git Feature Branch Workflow](https://www.atlassian.com/git/tutorials/comparing-workflows/feature-branch-workflow). The master branch preserves the development history with no broken code. When working on a system feature, create a separate feature branch.
- Always create a pull request before merging the feature branch into the main branch. Doing so helps keep track of the project history and manage git issues.
- NEVER perform git rebasing on public branches, which means that you should not run "git rebase [FEATURE-BRANCH]" while you are on a public branch (e.g., the main branch). Doing so will badly confuse other developers since rebasing rewrites the git history, and other people's works may be based on the public branch. Check [this tutorial](https://www.atlassian.com/git/tutorials/merging-vs-rebasing#the-golden-rule-of-rebasing) for details.
- NEVER push credentials to the repository, for example, database passwords or private keys for signing digital signatures.
- Request a code review when you are not sure if the feature branch can be safely merged into the main branch.
### Python package installation
- Make sure you are in the correct conda environment before installing packages. Otherwise, the packages will be installed to the server's general python environment, which can be problematic.
- Make sure the packages are in the [install_packages.sh](/back-end/install_packages.sh) script with version numbers, which makes it easy for others to install packages.
- Use the pip command first. Only use the conda command to install packages when the pip command does not work.
### Coding style
- Use the functional programming style (check [this Python document](https://docs.python.org/3/howto/functional.html) for the concept). It means that each function is self-contained and does NOT depend on a state that may change outside the function (e.g., global variables). Avoid using the object-oriented programming style unless necessary. In this way, we can accelerate the development progress while maintaining code reusability.
- Minimize the usage of global variables, unless necessary, such as system configuration variables. In this way, each function can be independent, which is good for debugging code and assigning coding tasks to a specific collaborator.
- Use a consistent coding style.
  - For Python, follow the [PEP 8 style guide](https://www.python.org/dev/peps/pep-0008/), for example, putting two blank lines between functions, using the lower_snake_case naming convention for variable and function names. Please use double quote (not single quote) for strings.
  - For JavaScript, follow the [Idiomatic JavaScript style guide](https://github.com/rwaldron/idiomatic.js), for example, using lowerCamelCase naming convention for variable and function names. Please use double quote (not single quote) for strings.
- Document functions and script files using docstrings.
  - For Python, follow the [numpydoc style guide](https://numpydoc.readthedocs.io/en/latest/format.html). Here is an [example](https://numpydoc.readthedocs.io/en/latest/example.html#example). More detailed numpydoc style can be found on [LSST's docstrings guide](https://developer.lsst.io/python/numpydoc.html).
  - For JavaScript, follow the [JSDoc style guide](https://jsdoc.app/index.html)
- For naming files, never use white spaces.
  - For Python script files (and shell script files), use the lower_snake_case naming convention. Avoid using uppercase.
  - For JavaScript files, use the lower_snake_case naming convention. Avoid using uppercases.
- Always comment your code, which helps others read the code and reduce our pain in the future when debugging or adding new features.

# <a name="install-postgresql"></a>Install PostgreSQL (administrator only)
WARNING: this section is only for system administrators, not developers.

Install and start postgresql database (we will use version 13). This assumes that Ubuntu 18.04 LTS or Ubuntu 20.04 LTS is installed.
```sh
# For Ubuntu

# Get the signing key and import it
wget https://www.postgresql.org/media/keys/ACCC4CF8.asc
sudo apt-key add ACCC4CF8.asc

# Add the repository
echo "deb http://apt.postgresql.org/pub/repos/apt/ `lsb_release -cs`-pgdg main" | sudo tee /etc/apt/sources.list.d/pgdg.list

# Fetch the metadata from the new repo
sudo apt-get update

# Install PostgreSQL 13
sudo apt-get install -y postgresql-13

# Start the service
sudo systemctl start postgresql

# Check postgresql status
sudo systemctl status postgresql

# Check postgresql log
sudo tail -100 /var/log/postgresql/postgresql-13-main.log
```
For Mac OS, I recommend installing postgresql by using [Homebrew](https://brew.sh/).
```sh
# For Mac OS

# Install PostgreSQL 13
brew install postgresql@13

# Start the service
brew services start postgresql@13

# Add to path
echo 'export PATH="/usr/local/opt/postgresql@13/bin:$PATH"' >> ~/.zshrc
```
Enter the postgres shell.
```sh
# For Ubuntu
sudo -u postgres psql postgres

# For Mac OS
psql postgres
```
In the psql shell, create a project user, create a database for the user with a password, and check if the user and database exist. Replace the [SECRET_PROJECT_PASSWORD] with the project user password. IMPORTANT: do not forget the semicolon and the end of the commands.
```sh
# Set the password encryption method
SET password_encryption = 'scram-sha-256';
# Give the project user with a password
CREATE USER public_engagement_tool PASSWORD '[SECRET_PROJECT_PASSWORD]';

# Create databases for the project user
# For the staging server
CREATE DATABASE public_engagement_tool_staging OWNER public_engagement_tool;
# For the production server
CREATE DATABASE public_engagement_tool_production OWNER public_engagement_tool;
# For the test cases
CREATE DATABASE public_engagement_tool_testing OWNER public_engagement_tool;

# Check the list of user roles
SELECT rolname FROM pg_authid;

# Check the list of encrypted user passwords
SELECT rolpassword FROM pg_authid;

# Check if the user role exists
\du

# Check if the database exists
\l

# Exist the shell
\q
```
Edit the "pg_hba.conf" file to set the authentication methods to the ones that require encrypted passwords. This step is used to increase the security of the database on the Ubuntu server. You can skip this step if you are using Mac OS for development.
```sh
# For Ubuntu
sudo vim /etc/postgresql/13/main/pg_hba.conf
# Scroll to the end and relace all "peer" with "scram-sha-256", except those for the local connections
# Below are examples
local   all             postgres                                peer
local   all             all                                     peer
host    all             all             127.0.0.1/32            scram-sha-256
host    all             all             ::1/128                 scram-sha-256
local   replication     all                                     peer
host    replication     all             127.0.0.1/32            scram-sha-256
host    replication     all             ::1/128                 scram-sha-256

# For Mac OS
vim /usr/local/var/postgresql@13/pg_hba.conf
# Scroll to the end and relace all "trust" with "scram-sha-256", except those for the local connections
# Below are examples
local   all             all                                     trust
host    all             all             127.0.0.1/32            scram-sha-256
host    all             all             ::1/128                 scram-sha-256
local   replication     all                                     trust
host    replication     all             127.0.0.1/32            scram-sha-256
host    replication     all             ::1/128                 scram-sha-256
```
If you want to delete a user or a database, enter the postgres shell and use the following:
```sh
# Delete the staging server database
DROP DATABASE public_engagement_tool_staging;

# Delete the project user
DROP USER public_engagement_tool;
```

# <a name="setup-back-end"></a>Setup back-end (administrator only)
WARNING: this section is only for system administrators, not developers.

Install conda for all users. This assumes that Ubuntu is installed. A detailed documentation is [here](https://conda.io/projects/conda/en/latest/user-guide/install/index.html). First visit [here](https://conda.io/miniconda.html) to obtain the downloading path. The following script install conda for all users:
```sh
# For Ubuntu
cd ~
wget https://repo.anaconda.com/miniconda/Miniconda3-py38_4.9.2-Linux-x86_64.sh
sudo sh Miniconda3-py38_4.9.2-Linux-x86_64.sh -b -p /opt/miniconda3
echo '' | sudo tee -a /etc/bash.bashrc
echo '# For miniconda3' | sudo tee -a /etc/bash.bashrc
echo 'export PATH="/opt/miniconda3/bin:$PATH"' | sudo tee -a /etc/bash.bashrc
echo '. /opt/miniconda3/etc/profile.d/conda.sh' | sudo tee -a /etc/bash.bashrc
source /etc/bash.bashrc
```
For Mac OS, I recommend installing conda by using [Homebrew](https://brew.sh/).
```sh
# For Mac OS
brew install --cask miniconda
echo 'export PATH="/usr/local/Caskroom/miniconda/base/bin:$PATH"' >> ~/.zshrc
echo '. /usr/local/Caskroom/miniconda/base/etc/profile.d/conda.sh' >> ~/.zshrc
source ~/.bash_profile
```
Clone this repository
```sh
git clone https://github.com/TUD-KInD/COCTEAU-TUD.git periscope-public-engagement-tool
```
Set the permission of the folder (for Ubuntu server setup only, not Mac OS).
```sh
# Add a development group for the project
sudo addgroup periscope-dev

# Add yourself and collaborators to the group
sudo usermod -a -G periscope-dev $USER
sudo usermod -a -G periscope-dev [user_name]

# Check the groups of a user
groups [user_name]

# Check the group list
cat /etc/group

# Set permissions
sudo chown -R root periscope-public-engagement-tool/
sudo chmod -R 775 periscope-public-engagement-tool/
sudo chgrp -R periscope-dev periscope-public-engagement-tool/

# Ignore permission changes in this repository
cd periscope-public-engagement-tool/
git config core.fileMode false
```
Create three text files to store the database urls in the "back-end/secret/" directory for the staging, production, and testing environments. For the url format, refer to [the flask-sqlalchemy documentation](http://flask-sqlalchemy.pocoo.org/2.3/config/#connection-uri-format). Replace [DATABASE_PASSWORD] with the database password. IMPORTANT: never push the database urls to the repository.
```sh
mkdir periscope-public-engagement-tool/back-end/secret/
cd periscope-public-engagement-tool/back-end/secret/
echo "postgresql://public_engagement_tool:[DATABASE_PASSWORD]@localhost/public_engagement_tool_staging" > db_url_staging
echo "postgresql://public_engagement_tool:[DATABASE_PASSWORD]@localhost/public_engagement_tool_production" > db_url_production
echo "postgresql://public_engagement_tool:[DATABASE_PASSWORD]@localhost/public_engagement_tool_testing" > db_url_testing
```
Create two text files to store the Google Sign-In API client ID in the "back-end/secret/" directory for the staging and production environments. For detailed documentation about how to obtain the client ID, refer to the [Google Sign-In API documentation](https://developers.google.com/identity/sign-in/web/sign-in). In the Google Cloud Console, remember to go to "APIs & Services" -> "Credentials" and add the desired domain names to the "Authorized JavaScript origins" in the OAuth client. This makes it possible to call the Google Sign-In API from these desired domains. You can use the [login_test.html](front-end/login_test.html) front-end page to test if the API works. Below are the commands for creating the text files:
```sh
cd periscope-public-engagement-tool/back-end/secret/
echo "[GOOGLE_SIGNIN_API_CLIENT_ID_STAGING]" > google_signin_client_id_staging
echo "[GOOGLE_SIGNIN_API_CLIENT_ID_PRODUCTION]" > google_signin_client_id_production
```
Also notice that you need to change the gid in the getGoogleSignInClientId() function in the [account.js](front-end/js/account.js).
```JavaScript
/**
 * Get the client ID for the Google Sign-In API.
 * @private
 * @returns {string} - the client ID for the Google Sign-In API.
 */
function getGoogleSignInClientId() {
  var urlHostName = window.location.hostname;
  var gid;
  if (urlHostName.indexOf("[REPLACE_TO_YOUR_CUSTOM_STAGING_URL]") !== -1) {
    // staging back-end
    gid = "[REPLACE_TO_YOUR_STAGING_GID]";
  } else if (urlHostName.indexOf("staging") !== -1) {
    // staging back-end
    gid = "[REPLACE_TO_YOUR_STAGING_GID]"";
  } else if (urlHostName.indexOf("periscope.io.tudelft.nl") !== -1) {
    // production back-end
    gid = "[REPLACE_TO_YOUR_PRODUCTION_GID]";
  } else if (urlHostName.indexOf("localhost") !== -1) {
    // developement back-end
    gid = "[REPLACE_TO_YOUR_DEVELOPEMENT_GID]";
  }
  return gid;
}
```
Create a private key for the server to encode the JSON Web Tokens for user login:
```sh
cd periscope-public-engagement-tool/back-end/www/
python gen_key.py ../secret/private_key confirm
```

# <a name="setup-unsplash"></a>Setup Unsplash (administrator only)
We use Unsplash API to serve the photos. First, register a developer account on the [Unsplash API website](https://unsplash.com/developers). After doing so, [create two Unsplash applications](https://unsplash.com/oauth/applications) and obtain their access keys (one for staging, and another one for production). Then, create two text files with names "unsplash_access_key_staging" and "unsplash_access_key_production" to store the access keys in the "back-end/secret/" directory.
```sh
cd periscope-public-engagement-tool/back-end/secret/
echo "[YOUR_UNSPLASH_STAGING_APP_ACCESS_KEY]" > unsplash_access_key_staging
echo "[YOUR_UNSPLASH_PRODUCTION_APP_ACCESS_KEY]" > unsplash_access_key_production
```
Notice that you will need to later [upgrade the application](https://help.unsplash.com/en/articles/2511245-unsplash-api-guidelines) (no cost) to the actural "production" version so that you can make more requests using the Unsplash API. The Unsplash API documentation is [here](https://unsplash.com/documentation).

# <a name="setup-ga"></a>Setup Google Analytics (administrator only)
IMPORTANT: do not use the gid in the getGoogleAnalyticsId() function in the [tracker.js](front-end/js/tracker.js).

This web-based application uses the [Google Analytics tracker API](https://developers.google.com/analytics/devguides/collection/gtagjs). First, follow [the steps](https://support.google.com/analytics/answer/9304153?hl=en) to set up a Google Analytics property and a data stream. After that, [get the Measurement ID](https://support.google.com/analytics/answer/9539598) and paste it into the "getGoogleAnalyticsId()" function in the tracker script [tracker.js](front-end/js/tracker.js). Then the tracker script will load Google's global site tag (gtag.js), set custom dimensions, and send the initial page view to the Google Analytics property. You can use the "sendEvent()" function in the tracker script to send events to the property. Note that it is better to have different data steams for development, staging, and production environments, where you can put different Measurement IDs in the "getGoogleAnalyticsId()" function in the tracker script.

# <a name="setup-dev-env"></a>Setup development environment
Create conda environment and install packages. It is important to install pip first inside the newly created conda environment.
```sh
conda create -n ppet
conda activate ppet
conda install python=3.8
conda install pip
which pip # make sure this is the pip inside the ppet environment
sh periscope-public-engagement-tool/back-end/install_packages.sh
```
If the environment already exists and you want to remove it before installing packages, use the following:
```sh
conda deactivate
conda env remove -n ppet
```
Run the following to upgrade the database to the latest migration.
```sh
cd periscope-public-engagement-tool/back-end/www/

# Upgrade the database to the latest migration
sh db.sh upgrade
```
If this is the first time that you set up the database, run the following to initialize the database migration. IMPORTANT: do NOT perform this step if the database migration folder exists on the repository. 
```sh
# Generate the migration directory
# IMPORTANT: do not perform this step if the database migration folder exists 
sh db.sh init

# Generate the migration script
# IMPORTANT: do not perform this step if the database migration folder exists 
sh db.sh migrate "initial migration"
```
Run server in the conda environment for development purpose.
```sh
sh development.sh
```
You can test the application using [http://localhost:5000/](http://localhost:5000/) or the following curl command.
```sh
curl localhost:5000
```
When the back-end code repository on the staging/production server is updated, run the following to restart the deployed service.
```sh
# Restart the uwsgi service
sudo systemctl restart ppet

# If error happend, check the uwsgi log
tail -100 periscope-public-engagement-tool/back-end/log/uwsgi.log

# Restart the apache service
sudo systemctl restart apache2
```

# <a name="setup-init-data"></a>Setup initial data
Before releasing the website, you need to provide the initial data. First, you need to go to the [index.html](/front-end/index.html) page to sign in using your Google account. Then, the account sign-in dialog will display your user ID. After that, use the [set_client_type.py](/back-end/www/set_client_type.py) script to give yourself the admin permission:
```sh
python set_client_type.py [user_id] [client_type]

# For example, giving the user with ID 1 the admin permission
python set_client_type.py 1 0
```
After giving yourself the admin permission, go to the [admin.html](/front-end/admin.html) to manipulate data (e.g., creating scenarios and questions). We have made this step easier by providing the "Delete all data" and "Set initial data" buttons at the end of the admin page. Just click on the checkbox before the "Set initial data" button to enable it, and then you can click on the button to give initial data to the website for testing. To delete the testing data, use the "Delete all data" button.

# <a name="manipulate-database"></a>Manipulate database
We use [flask-migrate](https://flask-migrate.readthedocs.io/en/latest/) to manage database migrations. The script "db.sh" enhances the workflow by adding the FLASK_APP environment. If you edit the database model and want to perform database migration, run the following:
```sh
cd periscope-public-engagement-tool/back-end/www/

# Generate the migration script
sh db.sh migrate "[YOUR_MIGRATION_COMMIT_MESSAGE]"
```
Then, a new migration script will be generated under the "back-end/www/migrations/versions" folder. Make sure that you open the file and check if the code make sense. After that, run the following to upgrade the database to the latest migration:
```sh
# Upgrade the database to the latest migration
sh db.sh upgrade
```
If you want to downgrade the database to a previous state, run the following.
```sh
# Downgrade the database to the previous migration
sh db.sh downgrade
```

# <a name="code-infrastructure"></a>Update and test code infrastructure
For the back-end, the test cases are stored in the "back-end/www/tests" folder and written using [Flask-Testing](https://pythonhosted.org/Flask-Testing/). Remember to write test cases for the model operations in the "back-end/www/models/model_operations" folder. Below shows how to run test cases:
```sh
cd periscope-public-engagement-tool/back-end/www/tests
# Run all tests
python run_all_tests.py
# Run one test
python answer_tests.py
```
Remember that every time the back-end script is pulled from the repository, you need to restart the service:
```sh
sudo systemctl restart ppet
```

# <a name="deploy-back-end-using-uwsgi"></a>Deploy back-end using uwsgi (administrator only)
WARNING: this section is only for system administrators, not developers.

Install [uwsgi](https://uwsgi-docs.readthedocs.io/en/latest/) using conda.
```sh
conda activate ppet
conda install -c conda-forge uwsgi=2.0.19
```
Create a folder for server logging.
```sh
mkdir periscope-public-engagement-tool/back-end/log/
```
Run the uwsgi server and check if it works.
```sh
cd periscope-public-engagement-tool/back-end/www/
sh deploy.sh
```
Check if the uwsgi server works.
```sh
curl localhost:8080
```
The server log is stored in the "back-end/log/uwsgi.log" file. Refer to the "back-end/www/uwsgi.ini" file for details. The documentation is on the [uwsgi website](https://uwsgi-docs.readthedocs.io/en/latest/Configuration.html). A custom log is stored in the "back-end/log/app.log" file.
```sh
# Keep printing the log files when updated
tail -f ../log/uwsgi.log
tail -f ../log/app.log
```
Create a service on Ubuntu, so that the uwsgi server will start automatically after rebooting the system. Replace [PATH] with the path to the cloned repository. Replace [USERNAME] with your user name on Ubuntu.
```sh
sudo vim /etc/systemd/system/ppet.service
# Add the following line to this file
[Unit]
Description=uWSGI instance to serve ppet
After=network.target

[Service]
User=[USERNAME]
Group=www-data
WorkingDirectory=/[PATH]/periscope-public-engagement-tool/back-end/www
Environment="PATH=/home/[USERNAME]/.conda/envs/ppet/bin"
ExecStart=/home/[USERNAME]/.conda/envs/ppet/bin/uwsgi --ini uwsgi.ini

[Install]
WantedBy=multi-user.target
```
Register the uwsgi server as a service on Ubuntu.
```sh
sudo systemctl enable ppet
sudo systemctl start ppet

# Check the status of the service
sudo systemctl status ppet

# Restart the service
sudo systemctl restart ppet

# Stop and disable the service
sudo systemctl stop ppet
sudo systemctl disable ppet
```
Check if the service work.
```sh
curl localhost:8080
```

# <a name="setup-apache"></a>Setup back-end and front-end on apache (administrator only)
WARNING: this section is only for system administrators, not developers.

Install apache2 and enable mods.
```sh
sudo apt-get install apache2
sudo apt-get install apache2-dev

sudo a2enmod headers
sudo a2enmod rewrite
sudo a2enmod ssl
sudo a2enmod proxy
sudo a2enmod proxy_http
sudo a2enmod proxy_balancer
sudo a2enmod lbmethod_byrequests
```
### For the production server
For the production server, obtain domains from providers such as [Google Domains](https://domains.google/) or [Namecheap](https://www.namecheap.com/) for both the back-end and the front-end. Point these domain names to the domain of the Ubuntu machine. In the Google Cloud Console, remember to go to "APIs & Services" -> "Credentials" and add the domain names to the "Authorized JavaScript origins" in the OAuth client. This makes it possible to call the Google Sign-In API from these domains.

For the production server back-end, create an apache virtual host as a reverse proxy for the uwsgi server. Replace [BACK_END_DOMAIN] and [FRONT_END_DOMAIN] with your domain name for the back-end and the front-end respectively.
```sh
sudo vim /etc/apache2/sites-available/[BACK_END_DOMAIN].conf
# Add the following lines to this file
<VirtualHost *:80>
  ServerName [BACK_END_DOMAIN]
  Header always set Access-Control-Allow-Origin "http://[FRONT_END_DOMAIN]"
  Header set Access-Control-Allow-Methods "POST, GET, PUT, DELETE, PATCH, OPTIONS"
  Header set Access-Control-Allow-Headers "Content-Type"
  # The following line forces the browser to break the cache
  Header set Cache-Control "max-age=5, public, must-revalidate"
  ProxyPreserveHost On
  ProxyRequests Off
  ProxyVia Off
  ProxyPass / http://127.0.0.1:8080/
  ProxyPassReverse / http://127.0.0.1:8080/
  ErrorLog ${APACHE_LOG_DIR}/[BACK_END_DOMAIN].error.log
  CustomLog ${APACHE_LOG_DIR}/[BACK_END_DOMAIN].access.log combined
</VirtualHost>
```
Create a symlink of the virtual host and restart apache.
```sh
cd /etc/apache2/sites-enabled/
sudo ln -s ../sites-available/[BACK_END_DOMAIN].conf
sudo systemctl restart apache2
```
For the production server front-end, create an apache virtual host. Replace [FRONT_END_DOMAIN] with your domain name for the front-end. Replace [PATH] with the path to the cloned repository.
```sh
sudo vim /etc/apache2/sites-available/[FRONT_END_DOMAIN].conf
# Add the following lines to this file
<VirtualHost *:80>
  ServerName [FRONT_END_DOMAIN]
  DocumentRoot /[PATH]/periscope-public-engagement-tool/front-end
  # The following line enables cors
  Header always set Access-Control-Allow-Origin "*"
  # The following line forces the browser to break the cache
  Header set Cache-Control "max-age=5, public, must-revalidate"
  <Directory "/[PATH]/periscope-public-engagement-tool/front-end">
    Options FollowSymLinks
    AllowOverride None
    Require all granted
  </Directory>
  ErrorLog ${APACHE_LOG_DIR}/[FRONT_END_DOMAIN].error.log
  CustomLog ${APACHE_LOG_DIR}/[FRONT_END_DOMAIN].access.log combined
</VirtualHost>
```
Create a symlink of the virtual host and restart apache.
```sh
cd /etc/apache2/sites-enabled/
sudo ln -s ../sites-available/[FRONT_END_DOMAIN].conf
sudo systemctl restart apache2
```
### For the staging server
For the staging server, use the following if you only want to access the server from an IP address using different paths (e.g., http://192.168.1.72/api/ for the back-end and http://192.168.1.72/web/ for the front-end).
```sh
sudo vim /etc/apache2/sites-available/ppet.conf
# Add the following lines to this file
<VirtualHost *:80>
  ServerAdmin webmaster@localhost
  Alias /web /var/www/periscope-public-engagement-tool/front-end
  Header set Access-Control-Allow-Headers "Content-Type"
  # The following line forces the browser to break the cache
  Header set Cache-Control "max-age=5, public, must-revalidate"
  ProxyPreserveHost On
  ProxyRequests Off
  ProxyVia Off
  ProxyPass /api http://127.0.0.1:8080/
  ProxyPassReverse / http://127.0.0.1:8080/
  ErrorLog ${APACHE_LOG_DIR}/ppet.error.log
  CustomLog ${APACHE_LOG_DIR}/ppet.access.log combined
</VirtualHost>
```
If you want to protect the front-end using user names and passwords, run the following to create users:
```sh
# The first time to create an user/password pair
sudo htpasswd -c /etc/apache2/.htpasswd [USERNAME]

# Add more user/password pairs
sudo htpasswd /etc/apache2/.htpasswd [ANOTHER_USER]
```
Then, use the following configuration.
```sh
sudo vim /etc/apache2/sites-available/ppet.conf
# Add the following lines to this file
<VirtualHost *:80>
  ServerAdmin webmaster@localhost
  Alias /web /var/www/periscope-public-engagement-tool/front-end
  <Directory "/var/www/periscope-public-engagement-tool/front-end">
    AuthType Basic
    AuthName "Restricted Content"
    AuthUserFile /etc/apache2/.htpasswd
    Require valid-user
  </Directory>
  Header set Access-Control-Allow-Headers "Content-Type"
  # The following line forces the browser to break the cache
  Header set Cache-Control "max-age=5, public, must-revalidate"
  ProxyPreserveHost On
  ProxyRequests Off
  ProxyVia Off
  ProxyPass /api http://127.0.0.1:8080/
  ProxyPassReverse / http://127.0.0.1:8080/
  ErrorLog ${APACHE_LOG_DIR}/ppet.error.log
  CustomLog ${APACHE_LOG_DIR}/ppet.access.log combined
</VirtualHost>
```
For testing the application with Google Sign-In API, you need to add "http://[STAGING_SITE_IP].sslip.io" to the authorized JavaScript origins for the OAuth client (the Google Login API), for example "http://192.168.1.72.sslip.io". To access the staging front-end and back-end, you can use "http://192.168.1.72.sslip.io/web/" and "http://192.168.1.72.sslip.io/api/". The "sslip.io" URL is a DNS server that maps "http://192.168.1.72.sslip.io" to the "192.168.1.72" IP address. You can check if it works using the following command:
```sh
nslookup http://[STAGING_SITE_IP].sslip.io
```

# <a name="setup-https"></a>Setup SSL certificates for https (administrator only)
Go to https://certbot.eff.org/ and follow the instructions to install Certbot on the Ubuntu server. Then run the following to enable Apache2 mods.
```sh
sudo a2enmod headers
sudo a2enmod rewrite
sudo a2enmod ssl
```
Run the Certbot.
```sh
sudo certbot --apache certonly
```
Copy the directories that point to the SSL certificate and the SSL certificate key in the terminal provided by the certbot. For example:
```sh
/etc/letsencrypt/live/[...]/fullchain.pem
/etc/letsencrypt/live/[...]/privkey.pem
```
### For the production server
Edit apache configuration file for the production back-end. Note the "https" before the FRONT_END_DOMAIN, not http.
```sh
sudo vim /etc/apache2/sites-available/[BACK_END_DOMAIN].conf
# Add the following lines to this file
<VirtualHost *:443>
  ServerName [BACK_END_DOMAIN]
  # Enable https ssl support
  SSLEngine On
  # The following line enables cors
  Header always set Access-Control-Allow-Origin "https://[FRONT_END_DOMAIN]"
  Header set Access-Control-Allow-Methods "POST, GET, PUT, DELETE, PATCH, OPTIONS"
  Header set Access-Control-Allow-Headers "Content-Type"
  # The following line forces the browser to break the cache
  Header set Cache-Control "max-age=5, public, must-revalidate"
  # Reverse proxy to the uwsgi server
  ProxyPreserveHost On
  ProxyRequests Off
  ProxyVia Off
  ProxyPass / http://127.0.0.1:8080/
  ProxyPassReverse / http://127.0.0.1:8080/
  # APACHE_LOG_DIR is /var/log/apache2/
  ErrorLog ${APACHE_LOG_DIR}/[BACK_END_DOMAIN].error.log
  CustomLog ${APACHE_LOG_DIR}/[BACK_END_DOMAIN].access.log combined
  # Add ssl
  SSLCertificateFile /etc/letsencrypt/live/[...]/fullchain.pem
  SSLCertificateKeyFile /etc/letsencrypt/live/[...]/privkey.pem
  Include /etc/letsencrypt/options-ssl-apache.conf
</VirtualHost>

<VirtualHost *:80>
  ServerName [BACK_END_DOMAIN]
  # Enable the url rewriting
  RewriteEngine on
  # Redirect http to https
  RewriteRule ^ https://%{SERVER_NAME}%{REQUEST_URI} [END,NE,R=permanent] 
</VirtualHost>
```
Edit apache configuration file for the production front-end.
```sh
sudo vim /etc/apache2/sites-available/[FRONT_END_DOMAIN].conf
# Add the following lines to this file
<VirtualHost *:443>
  ServerName [FRONT_END_DOMAIN]
  DocumentRoot /[PATH]/periscope-public-engagement-tool/front-end
  # Enable https ssl support
  SSLEngine On
  # The following line enables cors
  Header always set Access-Control-Allow-Origin "*"
  # The following line forces the browser to break the cache
  Header set Cache-Control "max-age=5, public, must-revalidate"
  <Directory "/[PATH]/periscope-public-engagement-tool/front-end">
    Options FollowSymLinks
    AllowOverride None
    Require all granted
  </Directory>
  # APACHE_LOG_DIR is /var/log/apache2/
  ErrorLog ${APACHE_LOG_DIR}/[FRONT_END_DOMAIN].error.log
  CustomLog ${APACHE_LOG_DIR}/[FRONT_END_DOMAIN].access.log combined
  # Add ssl
  SSLCertificateFile /etc/letsencrypt/live/[...]/fullchain.pem
  SSLCertificateKeyFile /etc/letsencrypt/live/[...]/privkey.pem
  Include /etc/letsencrypt/options-ssl-apache.conf
</VirtualHost>

<VirtualHost *:80>
  ServerName [FRONT_END_DOMAIN]
  # Enable the url rewriting
  RewriteEngine on
  # Redirect http to https
  RewriteRule ^ https://%{SERVER_NAME}%{REQUEST_URI} [END,NE,R=permanent] 
</VirtualHost>
```
### For the staging server
For the staging server, edit apache configuration file that contains both the front-end and back-end.
```sh
sudo vim /etc/apache2/sites-available/ppet.conf
# Add the following lines to this file
<VirtualHost *:443>
  ServerAdmin webmaster@localhost
  Alias /web /var/www/periscope-public-engagement-tool/front-end
  <Directory "/var/www/periscope-public-engagement-tool/front-end">
      AuthType Basic
      AuthName "Restricted Content"
      AuthUserFile /etc/apache2/.htpasswd
      Require valid-user
  </Directory>
  # Enable https ssl support
  SSLEngine On
  Header set Access-Control-Allow-Headers "Content-Type"
  # The following line forces the browser to break the cache
  Header set Cache-Control "max-age=5, public, must-revalidate"
  ProxyPreserveHost On
  ProxyRequests Off
  ProxyVia Off
  ProxyPass /api http://127.0.0.1:8080/
  ProxyPassReverse / http://127.0.0.1:8080/
  ErrorLog ${APACHE_LOG_DIR}/ppet.error.log
  CustomLog ${APACHE_LOG_DIR}/ppet.access.log combined
  # Add ssl
  SSLCertificateFile /etc/letsencrypt/live/[...]/fullchain.pem
  SSLCertificateKeyFile /etc/letsencrypt/live/[...]/privkey.pem
  Include /etc/letsencrypt/options-ssl-apache.conf
</VirtualHost>

<VirtualHost *:80>
  # Enable the url rewriting
  RewriteEngine on
  # Redirect http to https
  RewriteRule ^ https://%{SERVER_NAME}%{REQUEST_URI} [END,NE,R=permanent]
</VirtualHost>
```
### Restart apache and set the crontab
Restart the apache server for both production and staging servers.
```sh
sudo /etc/init.d/apache2 restart
```
Set a cron job to renew the SSL certificate automatically.
```sh
sudo bash
crontab -e
```
Add the following to the crontab.
```sh
# Renew our SSL certificate
0 0 1 * * /opt/certbot-auto renew --no-self-upgrade >>/var/log/certbot.log
```
Then type "exit" in the terminal to exit the bash mode. Remember to go to the Google API console and update the http domains to https domains (both back-end and front-end) in the authorized JavaScript origins for the OAuth client (the Google Login API). All http urls in the front-end code (e.g., API urls, video urls) also need to be replaced with the https version.

# <a name="api-calls"></a>API calls
The following code examples assusme that the root url is http://localhost:5000.
### Log in to the system
The server will return a user token in the form of JWT (JSON Web Token).
- Path:
  - **/login/**
- Available methods:
  - POST
- Required fields (either google_id_token or client_id):
  - "google_id_token": obtained when logging in using the [Google Sign-In API](https://developers.google.com/identity/sign-in/web/sign-in)
  - "client_id": the client ID returned by the Google Analytics tracker or created by the front-end client
- Returned fields:
  - "user_token": user token for the front-end client
```JavaScript
// jQuery examples
$.ajax({
  url: "http://localhost:5000/login/",
  type: "POST",
  data: JSON.stringify({google_id_token: gapi.auth2.getAuthInstance().currentUser.get().getAuthResponse().id_token}),
  contentType: "application/json",
  dataType: "json",
  success: function (data) {console.log(data)},
  error: function (xhr) {console.error(xhr)}
});

$.ajax({
  url: "http://localhost:5000/login/",
  type: "POST",
  data: JSON.stringify({client_id: "uid_for_testing"}),
  contentType: "application/json",
  dataType: "json",
  success: function (data) {console.log(data)},
  error: function (xhr) {console.error(xhr)}
});
```
