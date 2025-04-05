# Team Name: Team P
# Team Members:
#   Paciencia, Linzel Marie
#   Pillar, Gisele Joy
#   Payo, Rigil Kent
#   Plarisan, Hubert Harold
import requests
import urllib.parse

route_url = "https://graphhopper.com/api/1/route?"
key = "d25591a8-cbbc-456d-8e3d-8a5f63420189"

def geocoding(location, key):
    while not location.strip():
        location = input("Enter the location again: ")
    geocode_url = "https://graphhopper.com/api/1/geocode?"
    url = geocode_url + urllib.parse.urlencode({"q": location, "limit": "1", "key": key})

    try:
        replydata = requests.get(url)
        replydata.raise_for_status()
        json_data = replydata.json()
        json_status = replydata.status_code

        if json_status == 200 and len(json_data["hits"]) != 0:
            lat = (json_data["hits"][0]["point"]["lat"])
            lng = (json_data["hits"][0]["point"]["lng"])
            name = json_data["hits"][0]["name"]
            value = json_data["hits"][0]["osm_value"]
            country = json_data["hits"][0].get("country", "")
            state = json_data["hits"][0].get("state", "")

            if state and country:
                new_loc = name + ", " + state + ", " + country
            elif country:
                new_loc = name + ", " + country
            else:
                new_loc = name
            print(f"Geocoding API URL for {new_loc} (Location Type: {value})\n{url}")
        else:
            lat = "null"
            lng = "null"
            new_loc = location
            if json_status != 200:
                print(f"Geocode API status: {json_status}\nError message: {json_data.get('message', 'No message provided')}")
        return json_status, lat, lng, new_loc
    except requests.exceptions.RequestException as e:
        print(f"Error during geocoding API request for '{location}': {e}")
        return None, "null", "null", location
    except (KeyError, IndexError, TypeError) as e:
        print(f"Error processing geocoding API response for '{location}': {e}")
        print(f"Raw response: {replydata.text if 'replydata' in locals() else 'No response'}")
        return None, "null", "null", location

while True:
    print("\n+++++++++++++++++++++++++++++++++++++++++++++")
    print("Vehicle profiles available on Graphhopper:")
    print("+++++++++++++++++++++++++++++++++++++++++++++")
    print("car, bike, foot")
    print("+++++++++++++++++++++++++++++++++++++++++++++")
    profile = ["car", "bike", "foot"]
    vehicle = input("Enter a vehicle profile from the list above: ").lower()
    if vehicle in ["quit", "q"]:
        break
    elif vehicle in profile:
        pass
    else:
        vehicle = "car"
        print("No valid vehicle profile was entered. Using the car profile.")

    loc1 = input("Starting Location: ")
    if loc1.lower() in ["quit", "q"]:
        break
    orig_status, orig_lat, orig_lng, orig_loc = geocoding(loc1, key)
    if orig_status is None:
        continue

    loc2 = input("Destination: ")
    if loc2.lower() in ["quit", "q"]:
        break
    dest_status, dest_lat, dest_lng, dest_loc = geocoding(loc2, key)
    if dest_status is None:
        continue

    unit = input("Output distance in (miles/km): ").lower()
    if unit not in ["miles", "km"]:
        print("Invalid unit. Using kilometers (km).")
        unit = "km"

    print("=================================================")
    if orig_status == 200 and dest_status == 200 and orig_lat != "null" and orig_lng != "null" and dest_lat != "null" and dest_lng != "null":
        op = f"&point={orig_lat}%2C{orig_lng}"
        dp = f"&point={dest_lat}%2C{dest_lng}"
        paths_url = route_url + urllib.parse.urlencode({"key": key, "vehicle": vehicle}) + op + dp
        try:
            paths_response = requests.get(paths_url)
            paths_response.raise_for_status()
            paths_status = paths_response.status_code
            paths_data = paths_response.json()
            print(f"Routing API Status: {paths_status}\nRouting API URL:\n{paths_url}")
            print("=================================================")
            print(f"Directions from {orig_loc} to {dest_loc} by {vehicle}")
            print("=================================================")
            if paths_status == 200 and "paths" in paths_data and len(paths_data["paths"]) > 0:
                distance_meters = paths_data["paths"][0]["distance"]
                time_ms = paths_data["paths"][0]["time"]
                sec = int(time_ms / 1000 % 60)
                minute = int(time_ms / 1000 / 60 % 60)
                hour = int(time_ms / 1000 / 60 / 60)

                if unit == "miles":
                    distance = distance_meters / 1000 / 1.61
                    unit_str = "miles"
                else:
                    distance = distance_meters / 1000
                    unit_str = "km"

                print(f"Distance Traveled: {distance:.1f} {unit_str}")
                print(f"Trip Duration: {hour:02d}:{minute:02d}:{sec:02d}")
                print("=================================================")
                if "instructions" in paths_data["paths"][0]:
                    for each in range(len(paths_data["paths"][0]["instructions"])):
                        instruction = paths_data["paths"][0]["instructions"][each]
                        path = instruction.get("text", "No instruction")
                        instruction_distance_meters = instruction.get("distance", 0)
                        if unit == "miles":
                            instruction_distance = instruction_distance_meters / 1000 / 1.61
                        else:
                            instruction_distance = instruction_distance_meters / 1000
                        print(f"{path} ( {instruction_distance:.1f} {unit_str} )")
                    print("=============================================")
                else:
                    print("No detailed instructions found in the routing response.")
            else:
                print(f"Error in routing response: {paths_data.get('message', 'No message provided')}")
                print("*************************************************")
        except requests.exceptions.RequestException as e:
            print(f"Error during routing API request: {e}")
            print("*************************************************")
        except (KeyError, IndexError, TypeError) as e:
            print(f"Error processing routing API response: {e}")
            print(f"Raw response: {paths_response.text if 'paths_response' in locals() else 'No response'}")
            print("*************************************************")
    else:
        print("Could not retrieve valid coordinates for both starting and destination locations.")
        print("*************************************************")