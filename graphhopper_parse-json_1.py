# Team Name: Team P
# Team Members:
#   Paciencia, Linzel Marie
#   Pillar, Gisele Joy
#   Payo, Rigil Kent
#   Plarisan, Hubert Harold
import requests
import urllib.parse
import logging
from datetime import datetime

# Configure logging
log_filename = f"route_planner_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(filename=log_filename, level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logging.info("Application started.")

route_url = "https://graphhopper.com/api/1/route?"
key = "d25591a8-cbbc-456d-8e3d-8a5f63420189"

def geocoding(location, key):
    while not location.strip():
        location = input("Enter the location again: ")
    geocode_url = "https://graphhopper.com/api/1/geocode?"
    url = geocode_url + urllib.parse.urlencode({"q": location, "limit": "1", "key": key})
    logging.info(f"Geocoding request for: {location}, URL: {url}")

    try:
        replydata = requests.get(url)
        replydata.raise_for_status()
        json_data = replydata.json()
        json_status = replydata.status_code
        logging.info(f"Geocoding API status: {json_status}")

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
            logging.info(f"Geocoding successful. Coordinates: {lat}, {lng}, Formatted location: {new_loc}")
        else:
            lat = "null"
            lng = "null"
            new_loc = location
            if json_status != 200:
                error_message = json_data.get('message', 'No message provided')
                print(f"Geocode API status: {json_status}\nError message: {error_message}")
                logging.warning(f"Geocoding failed for '{location}'. Status: {json_status}, Error: {error_message}")
        return json_status, lat, lng, new_loc
    except requests.exceptions.RequestException as e:
        print(f"Error during geocoding API request for '{location}': {e}")
        logging.error(f"Geocoding API request failed for '{location}': {e}")
        return None, "null", "null", location
    except (KeyError, IndexError, TypeError) as e:
        print(f"Error processing geocoding API response for '{location}': {e}")
        logging.error(f"Error processing geocoding API response for '{location}': {e}. Raw response: {replydata.text if 'replydata' in locals() else 'No response'}")
        return None, "null", "null", location

while True:
    print("\n+++++++++++++++++++++++++++++++++++++++++++++")
    print("Vehicle profiles available on Graphhopper:")
    print("+++++++++++++++++++++++++++++++++++++++++++++")
    print("car, bike, foot")
    print("+++++++++++++++++++++++++++++++++++++++++++++")
    profile = ["car", "bike", "foot"]
    vehicle = input("Enter a vehicle profile from the list above: ").lower()
    logging.info(f"User entered vehicle profile: {vehicle}")
    if vehicle in ["quit", "q"]:
        logging.info("Application exiting.")
        break
    elif vehicle in profile:
        pass
    else:
        vehicle = "car"
        print("No valid vehicle profile was entered. Using the car profile.")
        logging.info(f"Invalid vehicle profile. Defaulting to: {vehicle}")

    loc1 = input("Starting Location: ")
    logging.info(f"User entered starting location: {loc1}")
    if loc1.lower() in ["quit", "q"]:
        logging.info("Application exiting.")
        break
    orig_status, orig_lat, orig_lng, orig_loc = geocoding(loc1, key)
    if orig_status is None:
        continue

    loc2 = input("Destination: ")
    logging.info(f"User entered destination: {loc2}")
    if loc2.lower() in ["quit", "q"]:
        logging.info("Application exiting.")
        break
    dest_status, dest_lat, dest_lng, dest_loc = geocoding(loc2, key)
    if dest_status is None:
        continue

    unit = input("Output distance in (miles/km): ").lower()
    logging.info(f"User selected distance unit: {unit}")
    if unit not in ["miles", "km"]:
        print("Invalid unit. Using kilometers (km).")
        unit = "km"
        logging.info(f"Invalid distance unit. Defaulting to: {unit}")

    print("=================================================")
    if orig_status == 200 and dest_status == 200 and orig_lat != "null" and orig_lng != "null" and dest_lat != "null" and dest_lng != "null":
        op = f"&point={orig_lat}%2C{orig_lng}"
        dp = f"&point={dest_lat}%2C{dest_lng}"
        paths_url = route_url + urllib.parse.urlencode({"key": key, "vehicle": vehicle}) + op + dp
        logging.info(f"Routing request URL: {paths_url}")
        try:
            paths_response = requests.get(paths_url)
            paths_response.raise_for_status()
            paths_status = paths_response.status_code
            paths_data = paths_response.json()
            logging.info(f"Routing API status: {paths_status}")
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
                logging.info(f"Route found. Distance: {distance:.1f} {unit_str}, Duration: {hour:02d}:{minute:02d}:{sec:02d}")
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
                        logging.info(f"Instruction {each+1}: {path} ({instruction_distance:.1f} {unit_str})")
                    print("=============================================")
                else:
                    print("No detailed instructions found in the routing response.")
                    logging.warning("No detailed instructions found in the routing response.")

                # --- Simple Map Integration ---
                map_zoom = 13  # Adjust for desired zoom level
                map_width = 600
                map_height = 400
                map_url = f"https://www.openstreetmap.org/export/embed.html?bbox={min(float(orig_lng), float(dest_lng))},{min(float(orig_lat), float(dest_lat))},{max(float(orig_lng), float(dest_lng))},{max(float(orig_lat), float(dest_lat))}&layer=mapnik&marker={orig_lat},{orig_lng}&marker={dest_lat},{dest_lng}"
                print("\n===================== MAP ======================")
                print(f"Open this URL in your web browser to see a simple map:")
                print(map_url)
                print("=================================================")
                logging.info(f"Map URL generated: {map_url}")

            else:
                error_message = paths_data.get('message', 'No message provided')
                print(f"Error in routing response: {error_message}")
                logging.error(f"Error in routing response: {error_message}")
                print("*************************************************")
        except requests.exceptions.RequestException as e:
            print(f"Error during routing API request: {e}")
            logging.error(f"Error during routing API request: {e}")
            print("*************************************************")
        except (KeyError, IndexError, TypeError) as e:
            print(f"Error processing routing API response: {e}")
            logging.error(f"Error processing routing API response: {e}. Raw response: {paths_response.text if 'paths_response' in locals() else 'No response'}")
            print("*************************************************")
    else:
        print("Could not retrieve valid coordinates for both starting and destination locations.")
        logging.warning("Could not retrieve valid coordinates for both starting and destination locations.")
        print("*************************************************")

logging.info("Application finished.")