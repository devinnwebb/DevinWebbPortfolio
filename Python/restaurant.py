import requests
import json
import tkinter as tk
import tkintermapview

API_KEY = "YOUR_API_KEY"
    
class YelpRestaurantSearch:
    def __init__(self, API_KEY):
        """ Initialize a class object with the API key

        Args: 
            API_KEY(str): the Yelp API key
        """
        self.API_KEY = API_KEY
        self.root = tk.Tk()
        self.root.geometry("800x900")
        self.root.title("Yelp Restaurant Search")
        self.root.configure(bg='#FFFFFF')
        self.create_widgets()

    def create_widgets(self):
        """ Creates the GUI widgets for the applicaiton, including labels, entry boxes, buttons, drop down menus, and map
        """
        # Create the search box label and entry field
        search_label = tk.Label(self.root, text="Search for a Restaurant:")
        search_label.pack()
        self.search_entry = tk.Entry(self.root, width=30)
        self.search_entry.pack()

        # Create the search parameters labels and entry fields
        city_label = tk.Label(self.root, text="City:")
        city_label.pack()
        self.city_entry = tk.Entry(self.root, width=30)
        self.city_entry.pack()

       

        state_label = tk.Label(self.root, text="State:")
        state_label.pack()
        self.state_entry = tk.Entry(self.root, width=30)
        self.state_entry.pack()

        
        price_label = tk.Label(self.root, text="Price:")
        price_label.pack()
        self.price_entry = tk.Entry(self.root, width=30)
        self.price_entry.pack()

        food_type_label = tk.Label(self.root, text="Food Type:")
        food_type_label.pack()
        self.food_type_entry = tk.Entry(self.root, width=30)
        self.food_type_entry.pack()

        # Create the search button
        search_button = tk.Button(
            self.root, text="Search", command=self.search_restaurants)
        search_button.pack(pady=18)

        # Create the search results listbox
        self.listbox_frame = tk.Frame(self.root, bd=2, relief="groove")
        self.listbox_frame.pack(side="left", fill="both", expand=True)

        self.listbox_scrollbar = tk.Scrollbar(
            self.listbox_frame, orient="vertical")
        self.listbox_scrollbar.pack(side="right", fill="y")

        self.listbox = tk.Listbox(
            self.listbox_frame, width=50, yscrollcommand=self.listbox_scrollbar.set)
        self.listbox.pack(side="left", fill="both", expand=True)

        self.listbox_scrollbar.config(command=self.listbox.yview)

        # Create a map
        my_label = tk.LabelFrame(self.root)
        my_label.pack(pady=20)

        self.map_widget = tkintermapview.TkinterMapView(
            my_label, width=350, height=350, corner_radius=0)

        # Set address
        self.map_widget.set_zoom(10)

        # Create search button for map
        explore_addy = tk.Label(self.root, text="Enter an address to explore:")
        explore_addy.pack()

        # Create input box for address input
        self.explore_addy_input = tk.Entry(self.root, width=30)
        self.explore_addy_input.pack()

        search_addy = tk.Button(
            self.root, text="Search Address", command=self.add_marker)
        search_addy.pack()


        self.map_widget.pack()

        # Create the sorting dropdown menu
        sort_options = ["Best Match", "Rating - High to Low",
                        "Rating - Low to High", "Price - High to Low", "Price - Low to High"]
        self.sort_variable = tk.StringVar(self.root)
        self.sort_variable.set(sort_options[0])
        self.sort_menu = tk.OptionMenu(
        self.root, self.sort_variable, *sort_options)
        self.sort_menu.pack(pady=(18, 0))

        # Create the sort button
        self.sort_button = tk.Button(
            self.root, text="Sort List", command=self.sort_results)
        self.sort_button.pack(side=tk.LEFT)
    def get_search_params(self):
        """ Get the search parameters from the entry fields 

            Returns: 
            params(dict): a dictionary of the user input search parameters
        """
        search_term = self.search_entry.get()
        city = self.city_entry.get()
        state = self.state_entry.get()
        price_str = self.price_entry.get()
        food_type = self.food_type_entry.get()

        # First convert the price string to an integer value for API use
        try:
            price = self.get_price_value(price_str)
            if price is None:
                print("Invalid price entered. Please use $, $$, $$$, or $$$$.")  # Provide user feedback if price is invalid
                return {}
        except ValueError:
            print("Invalid price format")
            return {}

        # Handle food type filter
        try:
            food_type_id = self.get_food_type_filter(food_type)
            if not food_type_id:
                print("No valid food types entered")
                return {}
        except KeyError:
            print("Invalid food type")
            return {}

        # Create the search parameters dictionary
        params = {
            "term": search_term,
            "location": f"{city}, {state}",
            "price": price,
            "categories": food_type_id
        }

        # Remove any parameters that are not provided by the user
        params = {k: v for k, v in params.items() if v}
        return params


    # Create the search button
    def search_restaurants(self):
        """Scrapes the API for restaurants and obtains only the fields we need based on the provided parameters"""

        # Clear any previous results
        self.listbox.delete(0, tk.END)

        # Get the search parameters from the entry fields
        params = self.get_search_params()

        # Make the API request
        headers = {"Authorization": "Bearer " + self.API_KEY}
        response = requests.get(
            "https://api.yelp.com/v3/businesses/search", headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()

            # Loop through the results and add them to the listbox
            businesses = data.get("businesses", [])
            for business in businesses:
                name = business.get("name")
                rating = business.get("rating")
                price = business.get("price", "N/A")  # Default to "N/A" if no price is available
                address = business.get("location", {}).get("address1", "No address provided")
                list_entry = f"{name} - Rating: {rating}, Price: {price}, Address: {address}"
                self.listbox.insert(tk.END, list_entry)

        else:
            print("Failed to fetch data:", response.status_code, response.text)


    def add_marker(self):
        """ Adds a marker to the map widget based on the address entered"""

        address = self.explore_addy_input.get()
        city = self.city_entry.get()
        state = self.state_entry.get()
        country = "United States"
        full_address = f'{address}, {city}, {state}, {country}'

        self.map_widget.set_address(full_address, marker=True)

    # Create the sort button

    def sort_results(self):
        """Sort the recommended restaurants list based on the sort option selected"""

        # Get the current sort option
        sort_option = self.sort_variable.get()

        # Get all items in the listbox
        items = self.listbox.get(0, tk.END)

        # Sort the items based on the current sort option
        if sort_option == "Best Match":
            items = sorted(items)
        elif sort_option == "Rating - High to Low":
            items = sorted(items, key=lambda x: float(
                x.split("Rating: ")[1].split(",")[0]), reverse=True)
        elif sort_option == "Rating - Low to High":
            items = sorted(items, key=lambda x: float(
                x.split("Rating: ")[1].split(",")[0]))
        elif sort_option == "Price - High to Low":
            items = sorted(items, key=lambda x: x.count("$"), reverse=True)
        elif sort_option == "Price - Low to High":
            items = sorted(items, key=lambda x: x.count("$"))

        # Clear the listbox and add the sorted items
        self.listbox.delete(0, tk.END)
        for item in items:
            self.listbox.insert(tk.END, item)

    def get_food_type_filter(self, food_type_str):
        """ Filtering the data by food types entered and getting the filter string for the specificied food types

        Args: 
            food_type_str(str): user input of food types 

        Returns: a joined string of filter options for food types
        """

        # Return an empty string if no food type is specified
        if not food_type_str:
            return ""

        # Split the food type string into a list of individual food types
        food_types = [c.strip() for c in food_type_str.split(",")]

        # Create a filter string for each food type
        filters = []
        for food_type in food_types:
            filters.append(f"{food_type.lower().replace(' ', '-')}")

        # Join the filter strings with commas and return the result
        return ",".join(filters)

    def get_price_value(self, price_str):
        """Converts the price_str (user input) corresponding numeric values to use in the API

        Args: 
            price_str(str): string represenation of the price

        Returns: 
            str or none: The numeric representation of the price or None if not found
        """

        if price_str == "$":
            return "1"
        elif price_str == "$$":
            return '2'
        elif price_str == "$$$":
            return '3'
        elif price_str == "$$$$":
            return '4'
        else:
            print("Invalid Price")
            return None

    # Start the mainloop
if __name__ == "__main__":
    yelp_search = YelpRestaurantSearch(API_KEY)
    yelp_search.root.mainloop()