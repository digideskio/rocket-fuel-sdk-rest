# rocket-fuel-sdk
Wrapper around ET/SalesForce's fuel-sdk

# Example
	
    from rocket_fuel_sdk import SFMC
    sfmc = SFMC(client_id='ID',
                client_secret='SECRET')
    is_valid = sfmc.validate_email('dude@abides.com')
