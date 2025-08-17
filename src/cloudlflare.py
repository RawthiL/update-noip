import os
import requests
import json

def update_ip(ip_file_path, current_ip, logger):
    
   
    # Get enviroment variables
    HOSTNAMES = os.getenv("CLOUDFLARE_HOSTNAMES", None) 
    if HOSTNAMES is None:
        error_e = "Enviroment variable \"CLOUDFLARE_HOSTNAMES\" not set"
        logger.error(error_e)
        raise ValueError(error_e)
    HOSTNAMES=HOSTNAMES.split(',')

    TOKEN = os.getenv("CLOUDFLARE_TOKEN", None) 
    if TOKEN is None:
        error_e = "Enviroment variable \"CLOUDFLARE_TOKEN\" not set"
        logger.error(error_e)
        raise ValueError(error_e)

    ZONE_ID = os.getenv("CLOUDFLARE_ZONE_ID", None) 
    if ZONE_ID is None:
        error_e = "Enviroment variable \"CLOUDFLARE_ZONE_ID\" not set"
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

        logger.info('... Updating www.cloudflare.com account ...')
        logger.info('... OLD IP: {ip}'.format(ip=no_ip_act))
        logger.info('... NEW IP: {ip}'.format(ip=current_ip))

        # Get DNS records here
        query_url = f"https://api.cloudflare.com/client/v4/zones/{ZONE_ID}/dns_records"
        headers = {
            "Authorization": f"Bearer {TOKEN}"
        }
        response = requests.get(query_url, headers=headers)
        if response.status_code != 200:
            logger.error(f"Failed to get DNS records. Status Code: {response.status_code}, Response: {response.content}")
            return False
        dns_dict = json.loads(response.text)
    
        # For each of the selected domains
        for hostname in HOSTNAMES:

            # Find hostname in DNS list
            to_update = None
            update_id = None
            for dns_entry in dns_dict["result"]:
                if hostname == dns_entry["name"]:
                    update_id = dns_entry['id']
                    to_update = {
                        "name": hostname,
                        "ttl": dns_entry["ttl"],
                        "type": dns_entry["type"],
                        "comment": "Script update",
                        "content": current_ip,
                        "proxied": dns_entry["proxied"]
                    }
            if to_update is None:
                logger.error(f"Cannot find requested domain in zone list: Domain {hostname}")
                return False

            # Update
            query_url = f"https://api.cloudflare.com/client/v4/zones/{ZONE_ID}/dns_records/{update_id}"
            headers = {
                "Authorization": f"Bearer {TOKEN}"
            }
            response = requests.get(query_url, headers=headers, json=to_update)

            # Check response
            logger.debug(f"Domain: {hostname}, Status Code: {response.status_code}, Response: {response.content}")
            if response.status_code == 200:
                success = 'yes'
                all_fail = False
            else:
                success = 'no'
            logger.info(f'... Domain: {hostname}, Succeed: {success} ...')

        if all_fail:
            logger.error(f"Failed to update IP. Last domain: {hostname}, Status Code: {response.status_code}, Response: {response.content}")
            return False

        # Update tracking file to the new IP
        f = open(ip_file_path,"w")
        f.write(current_ip)
        f.close()

    else:
        logger.info('IP has not changed.')
    
    return True