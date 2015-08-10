import FuelSDK


class FuelSFMC:
    '''
    Sales Force Marketing Cloud API
    '''

    def __init__(self):
        try:
            self.et_client = FuelSDK.ET_Client(debug=False)
        except Exception as e:
            print('Unable to get ET_Client: {}'.format(e))
            self.et_client = None

    def data_extension(self, action, props=None, search_filter=None):
        '''
        Retrieve, Create, Update or Delete a data extension

        props is a list of Fields to return.
        search_filter is a dict

        https://code.exacttarget.com/apis-sdks/fuel-sdks/data-extensions/data-extension-retrieve.html
        '''
        de = FuelSDK.ET_DataExtension()
        de.auth_stub = self.et_client

        if props:
            de.props = props

        if search_filter:
            de.search_filter = search_filter

        if action == 'get':
            response = de.get()  # Retrieve
        elif action == 'post':
            response = de.post()  # Create
        elif action == 'patch':
            response = de.patch()  # Update
        elif action == 'delete':
            response = de.delete()

        return response

    def triggered_send(self, action, props=None, search_filter=None):
        ts = FuelSDK.ET_TriggeredSend()
        ts.auth_stub = self.et_client

        if props:
            ts.props = props

        if search_filter:
            ts.search_filter = search_filter

        if action == 'get':
            response = ts.get()
        elif action == 'post':
            response = ts.post()
        elif action == 'patch':
            response = ts.patch()
        elif action == 'delete':
            response = ts.delete()
        elif action == 'send':
            response = ts.send()

        return response
