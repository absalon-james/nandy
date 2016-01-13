# nandy

## Dependencies
* python-novaclient==2.35.0
* python-keystoneclient=2.0.0
* sqlalchemy==1.0.11
* MySQL-python

## Installation
```shell
git clone https://github.com/absalon-james/nandy.git
cd nandy
python setup.py install

# Create the mysql database
mysql
create database nandy;
exit
```

## Configuration
The default location for the nandy yaml configuration is /etc/nandy/nandy.yaml. This can be changed with the command line argument '--config-file'.

```yaml
# Usually something like http://some-ip:5000/v2.0
auth_url: http://your_auth_url

# Openstack username
username: some_username

# Openstack password
password: some_password

# Openstack tenant uuid
project_id: some_tenant_id


# Time in seconds between observing active stats.
polling_interval: 30

# MySQL Database configuration
db:
  username: database_username
  password: database_password
  host: 127.0.0.1
  port: 3306
  dbname: nandy
```

## Optional
Copy the service/nandy script to /etc/init.d/nandy and use as a service.

## Usage
### One time report
Generate a one time report and write to stdout:
```shell
nandy report
```

The the date interval for a report defaults to from today until tomorrow.
The start and end dates can be specified via command line:
```shell
nandy report --start 2015-01-01 --end 2015-12-31
```

In addition, the report can be limited to a single tenant by providing
the tenant uuid via command line:
```shell
nandy report --tenant-id 11111111111111111111111111111111
```

### Agent for time series data
Nandy can be used to track active vcpus, active memory in MB, and active
local storage in GB. Active stats are saved to MySQL at each polling interval.
The data is timeseries and can be used to generate graphs with some external
program.

```shell
nandy agent
```
