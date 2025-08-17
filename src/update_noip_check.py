import requests
import os
import logging

# Set logger
LOGFILE = "/output/log.txt"

# Last uploaded IP location of file
IP_FILE = "/output/NP_IP_ACT"

# Get enviroment variables
HOSTNAMES = os.getenv("NOIP_HOSTNAMES", None) 
if HOSTNAMES is None:
	raise ValueError("Enviroment variable \"NOIP_HOSTNAMES\" not set")
HOSTNAMES=HOSTNAMES.split(',')

USERNAME = os.getenv("NOIP_USERNAME", None) 
if USERNAME is None:
	raise ValueError("Enviroment variable \"NOIP_USERNAME\" not set")

PASSWORD = os.getenv("NOIP_PASSWORD", None) 
if PASSWORD is None:
	raise ValueError("Enviroment variable \"NOIP_PASSWORD\" not set")

LOG_LEVEL = os.getenv("NOIP_LOGLEVEL", None) 
if LOG_LEVEL is None:
	raise ValueError("Enviroment variable \"NOIP_LOGLEVEL\" not set")
if LOG_LEVEL == "INFO":
	log_level = logging.INFO
elif LOG_LEVEL == "DEBUG":
	log_level = logging.DEBUG
elif LOG_LEVEL == "ERROR":
	log_level = logging.ERROR
elif LOG_LEVEL == "WARN":
	log_level = logging.WARN
else:
	raise ValueError("Enviroment variable \"NOIP_LOGLEVEL\" value not supported, choose among: DEBUG, INFO, WARN, ERROR")

# Setup Logger
logging.basicConfig(
                    format="%(asctime)s [%(levelname)-5.5s] [%(name)s]  %(message)s",
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=log_level,
					handlers=[
							logging.FileHandler(LOGFILE),
							logging.StreamHandler()
						]
					)

# NOIP URL
NOIP_UPDATE_URL = "https://dynupdate.no-ip.com/nic/update?hostname={hostname}&myip={ip}"

def main():

	# Initialize loger
	logger = logging.getLogger('MAIN')
	logger.info("Starting new run.")

	# Read last IP uploaded
	try:
		f = open(IP_FILE,"r")
		no_ip_act = f.read()
		f.close()
	except Exception as e:
		logger.warning(f"Cannot open current IP file ({str(e)}). Update forced.\n")
		no_ip_act = None

	# Get my current IP
	response = requests.get("https://api.ipify.org?format=json")
	# Check if the request was successful (status code 200)
	if response.status_code == 200:
		# Convert the JSON response to a Python dictionary
		data = response.json()
		# Extract the IP address from the "ip" key in the dictionary
		_new_ = data["ip"]
	else:
		# Cannot get IP bail
		logger.error("Failed to get public ip.")
		exit(1)

	# Check if we need to update
	all_fail = True
	if _new_ != no_ip_act:

		logger.info('... Updating www.noip.com account ...')
		logger.info('... OLD IP: {ip}\n'.format(ip=no_ip_act))
		logger.info('... NEW IP: {ip}\n'.format(ip=_new_))

		# For each of the selected domains
		for hostname in HOSTNAMES:

			# Update current public ip
			_url_called_ = NOIP_UPDATE_URL.format(hostname=hostname, ip=_new_)
			r = requests.get(_url_called_, auth=(USERNAME, PASSWORD))
			
			# if 200 this means the page was reached
			# r.content should be the response from noip.com
			logger.debug(f"Domain: {hostname}, Status Code: {r.status_code}, Response: {r.content}")

			if r.status_code == 200:
				success = 'yes'
				all_fail = False
			else:
				success = 'no'
			logger.info(f'... Domain: {hostname}, Succeed: {success} ...')

		if all_fail:
			logger.error("Failed to update IP. Last domain: {hostname}, Status Code: {r.status_code}, Response: {r.content}")
			exit(1)

		# Update tracking file to the new IP
		f = open(IP_FILE,"w")
		f.write(_new_)
		f.close()

	else:
		logger.info('IP has not changed.')

	exit(0)

if __name__ == "__main__":
    main()




