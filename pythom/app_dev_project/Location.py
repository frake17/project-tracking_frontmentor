class Location:
    count_id = 0
    def __init__(self, neighbourhood, address, availability):
        Location.count_id += 1
        self.__location_id = Location.count_id
        self.__neighbourhood = neighbourhood
        self.__address = address
        self.__availability = availability

    def get_location_id(self):
        return self.__location_id
    def get_neighbourhood(self):
        return self.__neighbourhood
    def get_address(self):
        return self.__address
    def get_availability(self):
        return self.__availability

    def set_location_id(self, location_id):
        self.__location_id = location_id
    def set_neighbourhood(self, neighbourhood):
        self.__neighbourhood = neighbourhood
    def set_address(self, address):
        self.__address = address
    def set_availability(self, availability):
        self.__availability = availability