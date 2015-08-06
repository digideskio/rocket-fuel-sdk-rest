# rocket-fuel-sdk
Supports py2 & py3.
Wrapper around ET/SalesForce's fuel-sdk

# Example
	
    from rocket_fuel_sdk import RestSFMC
    sfmc = RestSFMC(client_id='ID',
                client_secret='SECRET')
    is_valid = sfmc.validate_email('dude@abides.com')

    customers = [
        {
            'email': 'dude@abides.com',
            'first_name': 'dude',
            'age': 49,
        },
        {
            'email': 'joeyjojo@shabadoo.com',
            'first_name': 'joey',
            'age': 94,
        },
    ]
    de_key = 'XYZ'
    pk_fields = ['email', 'first_name']
    result = sfmc.upsert_data_extension_rows(data_extension_key=de_key,
                                             pk_fields=pk_fields,
                                             rows=customers)
