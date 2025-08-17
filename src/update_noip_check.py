import requests
import os
import logging
import noip
import cloudlflare

# Set logger
LOGFILE = "/output/log.txt"

# Get update flags
NOIP_CHECK = os.getenv("NOIP_CHECK", None) 
CLOUDFLARE_CHECK = os.getenv("CLOUDFLARE_CHECK", None) 

LOG_LEVEL = os.getenv("NOIP_LOGLEVEL", None) 
if LOG_LEVEL is None:
	log_level = logging.INFO
	print("Enviroment variable \"NOIP_LOGLEVEL\" not set, defaulting to INFO")
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


def get_current_ip(logger):
	# Get my current IP
    response = requests.get("https://api.ipify.org?format=json")
    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Convert the JSON response to a Python dictionary
        data = response.json()
        # Extract the IP address from the "ip" key in the dictionary
        return data["ip"]
    else:
        # Cannot get IP bail
        logger.error("Failed to get public ip.")
        return None
	
def main():

	# Initialize loger
	logger = logging.getLogger('MAIN')
	logger.info("Starting new run.")

	if NOIP_CHECK is None and CLOUDFLARE_CHECK is None:
		logger.error("No check tipe selected, please set NOIP_CHECK or CLOUDFLARE_CHECK.")
		exit(1)

	# Get current IP
	current_ip = get_current_ip(logger)
	if current_ip is None:
		exit(1)

	# Check No-IP
	if NOIP_CHECK:
		logger_noip = logging.getLogger('NO-IP')
		noip.update_ip("/output/IP_ACT_NOIP", current_ip, logger_noip)

	# Check Cloudflare
	if CLOUDFLARE_CHECK:
		logger_cloudlflare = logging.getLogger('CLOUDFLARE')
		cloudlflare.update_ip("/output/IP_ACT_CLOUDFLARE", current_ip, logger_cloudlflare)
		
	exit(0)

if __name__ == "__main__":
    main()




