
import requests
import time


#A Class for using the Dweet.io servers for data communication between devices
class Dweet(object):

    #dweet root domain and endpoints
    BASE_URL = "http://dweet.io/"

    #creates a name for the thing dweeting.
    #for anonymous or first time use.
    #assigns a random dweet name to the thing.
    DWEET = "{0}{1}".format(BASE_URL , "dweet?")

    #dweet by thing name.
    DWEET_BY_NAME = "{0}{1}".format(BASE_URL, "dweet/for/{name}?")

    #get latest dweets by name.
    LATEST_DWEET = "{0}{1}".format(BASE_URL, "get/latest/dweet/for/{name}")

    #get all dweets by name.
    ALL_DWEETS = "{0}{1}".format(BASE_URL, "get/dweets/for/{name}")


    def dweet(self, data):
        """
        Make a dweet without a thing name.
        Assigns a random thing name which is returned
        in the response body.
        Returns a dict type.

        Parameter name is a string type.
        Parameter data is a dict type.
        Usage:

        data = {"foo": "bar"}

        is turned into:
        /dweet?foo=bar
        """
        try:
            return requests.get(self.DWEET, params=data).json()
        except (requests.exceptions.ConnectionError, e):
            raise e


    def dweet_by_name(self, name, data):
        """
        Make a dweet with a named thing.
        Returns a dict type.

        Parameter name is a string type.
        Parameter data is a dict type.

        Usage:

        data = {"foo": "bar"}

        is turned into:
        /{name}?foo=bar

        """
        try:
            return requests.get(self.DWEET_BY_NAME.format(name=name),
                            params=data).json()
        except (requests.exceptions.ConnectionError, e):
            raise e



    def latest_dweet(self, name):
        """
        Get the latest dweet by thing name.
        Only returns one dweet as response.
        Returns dict type.
        Parameter name is a string type.
        """
        try:
            return requests.get(self.LATEST_DWEET.format(name=name)).json()
        except (requests.exceptions.ConnectionError, e):
            raise e



    def all_dweets(self, name):
        """
        Get dweets in last 24 hours by thing name.
        Dweet limit currently is 500 dweets.
        Returns dict type.
        Parameter name is a string type.
        """
        try:
            return requests.get(self.ALL_DWEETS.format(name=name)).json()
        except (requests.exceptions.ConnectionError, e):
            raise e




if __name__ == "__main__":

    dweet = Dweet()

    #dweet an dweet without a thing name. Returns a a thing name in the response
#    print (dweet.dweet({"hello": "25"}))

    #dweet with a thing name
    for i in range(100):
        print (dweet.dweet_by_name(name="201700302-001", data={"hello": str(i)}))
        time.sleep(2)


    #get the latest dweet by thing name. Only returns one dweet.
#    print (dweet.latest_dweet(name="201700302-001"))

    #get all the dweets by dweet name.
#    print (dweet.all_dweets(name="201700302-001"))