import os
import requests

# NOIP URL
NOIP_UPDATE_URL = "https://dynupdate.no-ip.com/nic/update?hostname={hostname}&myip={ip}"

def update_ip(ip_file_path, current_ip, logger):
    
   
    # Get enviroment variables
    HOSTNAMES = os.getenv("NOIP_HOSTNAMES", None) 
    if HOSTNAMES is None:
        error_e =  "Enviroment variable \"NOIP_HOSTNAMES\" not set"
        logger.error(error_e)
        raise ValueError(error_e)
    HOSTNAMES=HOSTNAMES.split(',')

    USERNAME = os.getenv("NOIP_USERNAME", None) 
    if USERNAME is None:
        error_e = "Enviroment variable \"NOIP_USERNAME\" not set"
        logger.error(error_e)
        raise ValueError(error_e)

    PASSWORD = os.getenv("NOIP_PASSWORD", None) 
    if PASSWORD is None:
        error_e = "Enviroment variable \"NOIP_PASSWORD\" not set"
        logger.error(error_e)
        raise ValueError(error_e)
	
  
    # Read last IP uploaded
    try:
        f = open(ip_file_path,"r")
        no_ip_act = f.read()
        f.close()
    except Exception as e:
        logger.warning(f"Cannot open current IP file ({str(e)}). Update forced.")
        no_ip_act = None

    # Check if we need to update
    all_fail = True
    if current_ip != no_ip_act:

        logger.info('... Updating www.noip.com account ...')
        logger.info('... OLD IP: {ip}'.format(ip=no_ip_act))
        logger.info('... NEW IP: {ip}'.format(ip=current_ip))

        # For each of the selected domains
        for hostname in HOSTNAMES:

            # Update current public ip
            _url_called_ = NOIP_UPDATE_URL.format(hostname=hostname, ip=current_ip)
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
            logger.error(f"Failed to update IP. Last domain: {hostname}, Status Code: {r.status_code}, Response: {r.content}")
            return False

        # Update tracking file to the new IP
        f = open(ip_file_path,"w")
        f.write(current_ip)
        f.close()

    else:
        logger.info('IP has not changed.')
    
    
    return True

