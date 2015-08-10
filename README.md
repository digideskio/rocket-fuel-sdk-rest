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




# FuelSDK

For the FuelSDK examples create a `~/.fuelsdk/config.python` file containing 
the following. Replace clientid and clientsecret with your own.
```
[Web Services]
appsignature: none
clientid: XXXXXXXXXXXXXXXXXXXXXXXX
clientsecret: XXXXXXXXXXXXXXXXXXXXXXXX
defaultwsdl: https://webservice.exacttarget.com/etframework.wsdl
authenticationurl: https://auth.exacttargetapis.com/v1/requestToken?legacy=1
wsdl_file_local_loc: /tmp/ExactTargetWSDL.s6.xml
```


## FuelSDK Example
```	
from rocket_fuel_sdk import FuelSFMC
    sfmc = FuelSFMC()

    props = [
        'Name',
        'CustomerKey',
        ]

    reponse = sfmc.data_extension(action='get', props=props)
    results = response.resulsts
```
