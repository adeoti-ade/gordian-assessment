import json
from bs4 import BeautifulSoup

class SeatMapParser:
    """
    This class parces a seatmap xml file and return it as a json object
    """
    def _fetch_bs_object(self, filename=None):
        """
        This private method gets a xml file name, and return the file as a beautifulsoup object
        
        @Params:
            filename: the name of the file to be read in and converted to beautifulsoup object
        
        @Return:
            soup: a beautiful soup object that will be further used to parse the xml file
        """
        with open(filename, 'r') as f:
            xml_data = f.read()
        soup = BeautifulSoup(xml_data, "xml")
        return soup
    
    def _fetch_seat_definitions(self, soup):
        """
        This private method retrived the seat definitions and return as a dictionary with 
        seat id as key and seat definition as value.
        
        @Params:
            soup: beautiful soup object of the xml file to be parsed
        
        @Return:
            seat_definition_obj: dictionary with seat id as key and seat definition as value
        """
        seat_definitions = soup.find_all("SeatDefinition")
        seat_definition_obj = {}
        for definition in seat_definitions:                
            seat_definition_obj[definition.get("SeatDefinitionID")] = definition.find("Text").text
   
        
        return seat_definition_obj

    def _process_seat_map2(self, filename):
        """
        This is a private method that processes the seat map file and return it as an array of different objects including
        `Seat`, `Column`, `OfferItemRefs`, `Availability`.
        
        @Params: 
            filename: the name of the file to be read in and parsed
        
        @Return:
            list_of_seatmaps: array of objects including `Seat`, `Column`, `OfferItemRefs`, `Availability`
        """
        soup = self._fetch_bs_object(filename)
        seatmaps = soup.find_all("SeatMap")
        seat_definition_obj = self._fetch_seat_definitions(soup)
        seatmap_dict = {}
        list_of_seatmaps = []
        for seatmap in seatmaps:
            seatmap_dict["SegmentRef"] = seatmap.find("SegmentRef").text
            rows = seatmap.find_all("Row")
            items = []
            for row in rows:
                dict_object = {
                "Seat": {}
                }
                dict_object["Number"] = row.find("Number").text
                seats = row.find_all("Seat")
                for seat in seats:
                    dict_object["Seat"]["Column"] = seat.find("Column").text
                    dict_object["Seat"]["OfferItemRefs"] = seat.find("OfferItemRefs").text if seat.find("OfferItemRefs") else None
                    dict_object["Seat"]["Availability"] = [seat_definition_obj[obj.text] for obj in seat.find_all("SeatDefinitionRef")]
                items.append(dict_object)
            seatmap_dict["Row"] = items
            list_of_seatmaps.append(seatmap_dict)

        return list_of_seatmaps

    def _process_cabin_classes(self, filename):
        """
        This is a private method that processes the seat map file and return it as an array of different objects including
        `BlockedInd`, `BulkheadInd`, `ColumnNumber`, `PlaneSection`, etc.
        
        @Params: 
            filename: the name of the file to be read in and parsed
        
        @Return:
            list_of_cabin_classes: array of objects including `BlockedInd`, `BulkheadInd`, `ColumnNumber`, `PlaneSection`, etc.
        """
        soup = self._fetch_bs_object(filename)
        cabin_classes = soup.find_all("CabinClass")
        cabin_list = []
        for cabin_class in cabin_classes:
            cabin_obj = {}
            cabin_obj["Layout"] = cabin_class.get("Layout")
            cabin_obj["UpperDeckInd"] = cabin_class.get("UpperDeckInd")
            row_info = cabin_class.find_all("ns:RowInfo")
            list_of_objs = []
            parent_obj = {}
            for row in row_info:
                parent_obj["CabinType"] = row.get("CabinType")
                seat_info = row.find_all("ns:SeatInfo")
                list_of_seats = []
                for seat in seat_info:
                    json_object = {}
                    json_object["BlockedInd"] = seat.get("BlockedInd")
                    json_object["BulkheadInd"] = seat.get("BulkheadInd")
                    json_object["ColumnNumber"] = seat.get("ColumnNumber")
                    json_object["PlaneSection"] = seat.get("PlaneSection")
                    json_object["AvailableInd"] = seat.find("ns:Summary")["AvailableInd"]
                    json_object["SeatNumber"] = seat.find("ns:Summary")["SeatNumber"]
                    json_object["Amount"] = seat.find("ns:Service").find("ns:Fee")["Amount"] \
                                            if seat.find("ns:Service") else None
                    json_object["Currency"] = seat.find("ns:Service").find("ns:Fee")["CurrencyCode"] \
                                            if seat.find("ns:Service") else None
                    list_of_seats.append(json_object)
                parent_obj["seat"] = list_of_seats
                list_of_objs.append(parent_obj)
                cabin_obj["Row"] = list_of_objs
            cabin_list.append(cabin_obj)

        return cabin_list
    
    def get_parsed_data(self):
        data = {
            "seat_maps": self._process_seat_map2("seatmap2.xml"),
            "cabin_classes": self._process_cabin_classes("seatmap1.xml")
        }
        # Serializing json 
        json_object = json.dumps(data, indent = 4)
        
        # Writing to sample.json
        with open("seat_map_parsed.json", "w") as outfile:
            outfile.write(json_object)

if __name__ == '__main__':
    seat_map_parser = SeatMapParser()
    data = seat_map_parser.get_parsed_data()
