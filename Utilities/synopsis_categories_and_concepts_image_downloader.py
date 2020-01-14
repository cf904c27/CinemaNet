from google_images_download import google_images_download   #importing the library
from multiprocessing import Pool
import os
import argparse

# please see https://github.com/Synopsis/CinemaNet/blob/master/Labels.md for specifics.

# the following categories and concepts are meant to capture both general image understanding
# as well as terminology useful to photographers, cinematographers, visual artists and those working with visual media.
# this is the beginning of a quasi 'knowledge graph', using a reverse domain labelling system
# allowing us to add labels without polluting existing label name spaces

# due to limitations of label length in Googles Auto ML, we have removed the prefix
#'synopsis.image.' from every cateogry and concept in this script.

# We add those back during clean up of our CoreML models

# During training of each particular categories classifier, we also include a 'None of the above'
# label to help the system discriminate the various concepts each category contains.

# This script does *not* prune each cateogry/concept - it just helps us get a lot of images which may or may not be relevant to the concept

# This script does *not* fetch the 'None of the above' images.

# top level dictionary key is top level category directory name
# value is a dictionary of the concept name (sub folder) and human search terms for google image search

parser = argparse.ArgumentParser(
    description='''
    ============================================================================
        				Download the CinemaNet Dataset
    ============================================================================

    Usage
    --------

	python synopsis_categories_and_concepts_image_downloader.py

	## If you need to specify where `chromedriver` is installed
    python synopsis_categories_and_concepts_image_downloader.py \
		--chromedriver_path /usr/loca/bin/chromedriver

    ''', formatter_class=argparse.RawTextHelpFormatter)

parser.add_argument('--chromedriver_path', type=str, required=False,
                    default="/usr/local/bin/chromedriver",
                    help='chromedriver location')
args = parser.parse_args()

categories_and_concepts = {

	# What is the overall color saturation of the image?
	"color_saturation" : [
	{ "color_saturation_desaturated" : ["Desaturated photography", "Desaturated colors photography", "Desaturated tones photography"]},
	{ "color_saturation_muted" : ["muted photography", "muted colors photography", "muted tones photography"]},
	{ "color_saturation_neutral" : ["neutral photography", "neutral colors photography", "neutral tones photography"]},
	{ "color_saturation_pastel" : ["Pastel photography", "Pastel colors photography", "Pastel tones photography"]},
	{ "color_saturation_saturated" : ["Saturated photography", "Saturated colors photography"]},
	],

	# How do the colors in the image relate to one another?
	# do we need a `none of the above`?
	"color_theory" : [
	# contains NA when training
	{ "color_theory_analagous" : ["Analagous photography", "Analagous color photography"]},
	{ "color_theory_complementary" : ["complementary photography", "Complementary color photography"]},
	{ "color_theory_monochromatic" : ["Monochromatic photography", "Monochromatic color photography", ]},
	],

	# Overall color tone of the image
	"color_tones" : [
	# contains NA when training
	{ "color_tones_blackwhite" :  ["Black and White photography", "B&W photography"] },
	{ "color_tones_cool" : ["Cool Tones photography", "Cool colors photography"]},
	{ "color_tones_warm" : ["Warm Tones  photography", "Warm colors  photography"]},
	],

	# Is the image useful for keying?
	"color_key" : [
	# contains NA when training
	{ "color_key_luma" : ["luma matte", "matte footage"]},
	{ "color_key_green" : ["green screen footage"]},
	{ "color_key_blue" : ["blue screen footage  -death -bsod"]},
	],

	# color.dominant is created manually

	"composition_pattern" : [
	# contains NA when training
	{ "composition_pattern_tile" : ["tiled patterns"]},
	{ "composition_pattern_spiral" : ["spiral patterns",]},
	# needs better search terms?
	# { "composition_pattern_reflect" : ["glide reflection pattern"]},
	{ "composition_pattern_stripe" : ["striped patterns"]},
	{ "composition_pattern_spot" : ["spot patterns", "dot patterns"]},
	{ "composition_pattern_fractal" : ["fractal patterns"]},
	],

	"composition_spatial" : [
 	{ "composition_spatial_perspective" : ["perspective photography", "vanishing point photography"]},
	# needs better search terms?
	{ "composition_spatial_orthographic" : ["orthographic photography", "orthographic photography"]},
	# needs better search terms?
	{ "composition_spatial_isometric" : ["isometric photography"]},
	# needs better search terms?
	{ "composition_spatial_open" : ["open composition photography",]},
	# needs better search terms?
	{ "composition_spatial_closed" : ["spot texture", "spotted animal"]},
	{ "composition_spatial_dense" : ["dense photography ", "maximalist photography"]},
	{ "composition_spatial_sparse" : ["minimal photography"]},
	{ "composition_spatial_horizon" : ["horizon", "vanishing point horizon photography"]},
	{ "composition_spatial_verticality" : ["Verticality", "Verticality photography"]},
	{ "composition_spatial_horitzontality" : ["horizontality photography -geography -geology"]},
	{ "composition_spatial_diagonality" : ["diagonality composition photography"]},
	# remove images with the fucking grid over lay ahhhhhhhh
	{ "composition_spatial_ruleofthirds" : ["rule of thirds composition photography"] },
	{ "composition_spatial_negative " : ["negative space photography"] },
	{ "composition_spatial_symmetric " : ["symmetrical photography"] },

	# sub-category
	{ "composition_spatial_centered" : ["centered composition", "centered photography"] },
    { "composition_spatial_offcentered" : ["off centered photography", "off centered composition"] },

 	],


	# train natural vs synthetic in one classifier
	"composition_texture" : [
	{ "composition_texture_natural" : ["natural texture", "organic texture"]},
	{ "composition_texture_synthetic" : ["synthetic texture", "technical texture"]},

	# train harmonious vs dissonant in one classifier
	{ "composition.texture.harmonious" : ["harmonious texture", "harmonious photography composition", "rythmic photography","ordered pattern"]},
	{ "composition.texture.dissonant" : ["disordered pattern", "chaotic texture", "messy pattern", "messy texture", "disordered photography"]},

	#train smooth vs rough in one classifier
	{ "composition_texture_smooth" : ["smooth texture", "smooth photography"]},
	{ "composition_texture_rough" : ["rough texture", "rough texture photography"]},

	# train cracked vs patterned (continuous?)
	{ "composition_texture_cracked" : ["rough texture", "rough photography"]},
	{ "composition_texture_patterned" : ["pattern texture", "pattern photography"]},
	],

 	#is the camera is angled up or down?
	"shot_angle" : [
	# contains NA when training
	{ "shot_angle_aerial" : ["aerial photography", "aerial shot"]},
	{ "shot_angle_high" : ["high angle shot", "high angle shot film"]},
	{ "shot_angle_eyelevel" : ["eye level shot", "eye level shot camera angle"]},
	{ "shot_angle_low" : ["low angle shot", "low angle shot cinematography"]},
	],

	# is the camera rotated about its 'z axis'? (rotated about the lens)
	"shot_level" : [
	# contains NA when training
	{ "shot_level_level" : ["level shot"]},
	{ "shot_level_tilted" : ["tilted shot", "dutch angle shot", "oblique angle shot"]},
	],

	#
	"shot_type" : [
	# contains NA when training
	{ "shot_type_portrait" : ["portrait shot", "two shot cinematography"]},
	{ "shot_type_twoshot" : ["two shot", "eye level shot camera angle"]},
	{ "shot_type_master" : ["the master shot cinematography", "the master shot", "band photo"]},
	# Trained as a seperate concept - but still a type (ie, can have a over the shoulder two shot)
	{ "shot)type_overtheshoulder" : ["over the shoulder shot", "over the shoulder shot cinematography"]},
	],

	# how far are we from the shot subject?
	"shot_framing" : [
	{ "shot_framing_extremecloseup" : ["extreme close up shot", "extreme close up shot cinematography"]},
	{ "shot_framing_closeup" : ["close up shot", "close up shot cinematography"]},
	{ "shot_framing_medium" : ["medium shot", "medium shot cinematography"]},
	{ "shot_framing_long" : ["long shot", "long shot cinematography"]},
	{ "shot_framing_extemelong" : ["extreme long shot", "extreme long shot cinematography"]},
	],

	# is the image completely, partially or not in focus?
	"shot_focus" : [
	# contains NA when training
	{ "shot_focus_deep" : ["deep focus shot", "deep focus shot cinematography"]},
	{ "shot_focus_shallow" : ["shallow focus shot", "shallow focus shot cinematography"]},
	{ "shot_focus_out" : ["out of focus", "out of focus shot"]},
	],

	# describe the lighting environment
	"shot_lighting" : [
	# contains NA when training
	{ "shot_lighting_soft" : ["soft lighting cinematography", "soft lighting"]},
	{ "shot_lighting_hard" : ["hard lighting cinematography", "hard lighting"]},
	{ "shot_lighting_lowkey" : ["low key lighting", "low key lighting cinematography"]},
	{ "shot_lighting_highkey" : ["high key lighting", "high key lighting cinematography"]},
	{ "shot_lighting_silhouette" : ["silhouette lighting", "silhouette lighting cinematography"]},
	],

	# what is the - generally speaking - subject of the shot, if any
	"shot_subject" : [
	# contains NA when training
	{ "shot_subject_person" : ["diverse portraits photography", "portraits of people", "people -lineart -clipart -animation"]},
	{ "shot_subject_animal" : ["wildlife photography"]},
	{ "shot_subject_object" : ["object photography", "still life photography"]},
	{ "shot_subject_text" : ["typographic design", "movie title design"]},
	{ "shot_subject_location" : ["location photography", "establishing shot"]},
	],

	# I cant figure out a better way to get diverse results :( - this feels gross - help me.
	# maybe https://www.ibm.com/blogs/research/2019/01/diversity-in-faces/ ?
	# faces, body, bodies, limb, limbs might be too specific with the plurals? Maybe make one category?
	"shot_subject_person" : [
	{ "shot_subject_person_face" : ["male face", "female face", "african american face", "asian face", "old face", "diverse faces photography -collage"]},
	{ "shot_subject_person_body" : ["diverse human figure photography", "diverse body shapes portraits"]},
	{ "shot_subject_person_arms" : ["arms photography", "arms outreached photography", "arms crossed photography"]},
	{ "shot_subject_person_hands" : ["hands photography", "fist photography", "holding hands photography"]},
	],

	# self explanatory
	"shot_timeofday" : [
	# contains NA when training
	{ "shot_timeofday_twilight" : ["twilight time of day", "dusk", "sunset", "sunrise"]},
	{ "shot_timeofday_day" : ["midday photography"]},
	{ "shot_timeofday_night" : ["night photography"]},
	],

	# self explanatory
	"shot_weather" : [
	# contains NA when training
	{ "shot_weather_sunny" : ["Sunny weather"]},
	{ "shot_weather_cloudy" : ["Cloudy weather"]},
	{ "shot_weather_raining" : ["Rainy weather"]},
	{ "shot_weather_snowing" : ["Snowy weather"]},
	# foggy?
	# stormy?
	],

	# self explanatory
	"shot_location" : [
	# contains NA when training

	# Trained as a seperate concepts
	{"shot_location_interior" : ["Indoors", "Interior", "inside"]},
	{"shot_location_exterior" : ["Outdoors", "Exterior", "outside"]},

	# Specific nature (exterior) categories if we can identify them
	{"shot_location_exterior_beach" : ["Beach"]},
	{"shot_location_exterior_canyon" : ["Canyon"]},
	{"shot_location_exterior_cave" : ["Cave entrance"]},
	{"shot_location_exterior_desert" : ["Desert"]},
	{"shot_location_exterior_forest" : ["Forest"]},
	{"shot_location_exterior_glacier" : ["Glacier"]},
	{"shot_location_exterior_lake" : ["Lake"]},
	{"shot_location_exterior_mountains" : ["Mountains"]},
	{"shot_location_exterior_ocean" : ["Ocean"]},
	{"shot_location_exterior_plains" : ["Plains"]},
	{"shot_location_exterior_polar" : ["antarctic terrain landscape -toy -map", "arctic terrain landscape -toy -map"]},
	{"shot_location_exterior_river" : ["River"]},
	{"shot_location_exterior_sky" : ["Sky"]},
	{"shot_location_exterior_space" : ["astrophotography"]},
	{"shot_location_exterior_wetlands" : ["Swamp landscape", "Marsh landscape", "Bog landscape"]},

	# Specific township (exterior) categories if we can identify them
	{"shot_location_exterior_city" : ["City"]},
	{"shot_location_exterior_town" : ["Town"]},
	{"shot_location_exterior_suburb" : ["Suburb"]},
	{"shot_location_exterior_park" : ["Park"]},
	{"shot_location_exterior_playground" : ["Playground"]},
	{"shot_location_exterior_sidewalk" : ["city sidewalk photography"]},
	{"shot_location_exterior_road" : ["Road", "Street"]},

	# Specific building (exterior) categories if we can identify them
	{"shot_location_exterior_house" : ["House exterior"]},
	{"shot_location_exterior_mansion" : ["Mansion exterior"]},
	{"shot_location_exterior_apartment" : ["Apartment building exterior"]},
	{"shot_location_exterior_castle" : ["Castle"]},
	{"shot_location_exterior_skyscraper" : ["Skyscraper"]},
	{"shot_location_exterior_palace" : ["Palace exterior"]},
	{"shot_location_exterior_office" : ["Office building"]},
	{"shot_location_exterior_farm" : ["Farm"]},
	{"shot_location_exterior_industrial" : ["industrial plant"]},
	{"shot_location_exterior_restaurant" : ["Restaurant exterior", "Bar exterior", "pub exterior", "Cafe exterior"]},
	{"shot_location_exterior_church" : ["Church building"]},
	{"shot_location_exterior_temple" : ["Temple exterior"]},
	{"shot_location_exterior_mosque" : ["Mosque exterior" ]},
	{"shot_location_exterior_synagogue" : ["Synagogue exterior"]},
	{"shot_location_exterior_cathedral" : ["Cathedral exterior"]},
	{"shot_location_exterior_monastery" : ["Monastery exterior"]},
	{"shot_location_exterior_stadium" : ["stadium exterior"]},
	{"shot_location_exterior_theater" : ["theater exterior"]},
	{"shot_location_exterior_auto_repair_shop" : ["auto repair shop exterior"]},
	{"shot_location_exterior_mall" : ["Mall exterior"]},
	{"shot_location_exterior_port" : ["Port exterior" ]},
	{"shot_location_exterior_pier" : ["Pier"]},
	{"shot_location_exterior_warehouse" : ["Warehouse building"]},
	{"shot_location_exterior_ruins" : ["Ruins", "modern ruins"]},
	{"shot_location_exterior_airport" : ["Airport terminal exterior"]},
	{"shot_location_exterior_station_train" : ["Train Station exterior"]},
	{"shot_location_exterior_station_gas" : ["Gas Station exterior"]},
	{"shot_location_exterior_bus_stop" : ["Bus stop"]},
	{"shot_location_exterior_station_subway" : ["Subway entrance -sandwich -food",]},
	{"shot_location_exterior_store" : ["Store exterior"]},
	{"shot_location_exterior_hospital" : ["Hospital building"]},
	{"shot_location_exterior_school" : ["School building"]},
	{"shot_location_exterior_library" : ["Library building"]},
	{"shot_location_exterior_parkinglot" : ["Parking Lot"]},
	{"shot_location_exterior_bridge" : ["Bridge"]},
	{"shot_location_exterior_tunnel" : ["Tunnel entrance"]},
	{"shot_location_exterior_military_base" : ["military barracks exterior", "military base aerial", "military base soldiers outside", "military base obstacle course"]},
	{"shot_location_exterior_station_police" : ["police station exterior", "state trooper building", "police headquarters"]},
	{"shot_location_exterior_station_fire" : ["police station exterior", "state trooper building", "police headquarters"]},
	{"shot_location_exterior_prison": ["prison exterior", "prison yard prisoners", "prison yard guard", "prison fenc"]},
	{"shot_location_exterior_courthouse": ["courthouse outside", "courthouse protest", "courthouse steps talking", "courthouse steps press conference"]},

	# Specific vehicle (exterior) categories if we can identify them
	{"shot_location_exterior_car" : ["Car"]},
	{"shot_location_exterior_bus" : ["Bus"]},
	{"shot_location_exterior_truck" : ["Truck"]},
	{"shot_location_exterior_motorcycle" : ["Motorcycle riding"]}, #riding removes all white images background images
	{"shot_location_exterior_bicycle" : ["Bicycle riding"]}, #riding removes all white background images
	{"shot_location_exterior_bus" : ["Bus"]},
	{"shot_location_exterior_train" : ["Train"]},
	{"shot_location_exterior_boat" : ["Boat"]},
	{"shot_location_exterior_airplane" : ["Airplane"]},
	{"shot_location_exterior_helicopter" : ["Helicopter"]},
	{"shot_location_exterior_spacecraft" : ["spacecraft"]},

	# Specific room (interior) categories if we can identify them
	{"shot_location_interior_cave" : ["Cave interior", "people inside cave"]},
	{"shot_location_interior_lobby" : ["Lobby", "busy lobby"]},
	{"shot_location_interior_foyer" : ["foyer", "opening front door"]},
	{"shot_location_interior_hallway" : ["Hallway", "person in hallway"]},
	{"shot_location_interior_livingroom" : ["Living Room", "interracial living room"]},
	{"shot_location_interior_diningroom" : ["Dining Room", "dining room eating"]},
	{"shot_location_interior_kitchen" : ["Kitchen", "cooking in kitchen"]},
	{"shot_location_interior_closet" : ["Closet", "people looking in closet", "hiding in closet"]},
	# way too many white people - this feels so wrong - but necessary
	{"shot_location_interior_bedroom" : ["white people sleeping", "african american sleeping", "asian people sleeping", "indian people sleeping bedroom", "watching tv in bed", "kissing bedroom", "interracial bedroom"]},
	{"shot_location_interior_bathroom" : ["Bathroom", "men at urinals", "people brushing teeth", "people in shower", "people in bathroom", "girl talk bathroom"]},
	{"shot_location_interior_auditorium" : ["Auditorium interior", "crowded auditorium"]},
	{"shot_location_interior_gym" : ["Gym interior", "people at the gym", "people working out"]},
	{"shot_location_interior_hospital" : ["Emergency Room"]},
	{"shot_location_interior_study" : ["home study interior", "home office working"]},
	{"shot_location_interior_stairwell" : ["Stairwell", "stairwell walking", "stairwell crowded"]},
	{"shot_location_interior_elevator" : ["Elevator interior", "people in elevator"]},
	{"shot_location_interior_auto_repair_shop" : ["auto mechanic", "auto repair shop interior"]},
	{"shot_location_interior_factory" : ["factory line", "factory floor", "factory working"]},
	{"shot_location_interior_warehouse" : ["warehouse jobs"]},
	{"shot_location_interior_dungeon" : ["real castle dungeon -dragons -game -videogame -cartoon -minecraft"]},
	{"shot_location_interior_throneroom" : ["throneroom"]},
	{"shot_location_interior_classroom" : ["classroom"]},
	{"shot_location_interior_cafeteria" : ["cafeteria interior", "crowded cafeteria"]},
	{"shot_location_interior_office" : ["executive office working"]},
	{"shot_location_interior_office_cubicle" : ["people working cubicle"]},
	{"shot_location_interior_office_open" : ["openoffice interior", "open office people"]},
	{"shot_location_interior_conferenceroom" : ["conferenceroom", "people in conference room"]},
	{"shot_location_interior_barn" : ["animals inside barn", "people inside barn"]},
	{"shot_location_interior_restaurant" : ["busy restaurant", "quiet restaurant", "restaurant customers"]},
	{"shot_location_interior_commercialkitchen" : ["commercial kitchen cooking", "cooks in kitchen"]},
	{"shot_location_interior_bar" : ["busy bar", "lonely bar"]},
	{"shot_location_interior_cafe" : ["cafe interior", "cafe customerts"]},
	{"shot_location_interior_arena" : ["arena interior", "full arena"]},
	{"shot_location_interior_stage" : ["stage", "stage performance", "stage rehearsal", "stage solo"]},
	{"shot_location_interior_dancefloor" : ["people dancing nightclub", "people dancing bar"]},
	{"shot_location_interior_airport" : ["airport travellers", "airport terminal", "airport security", "airport luggage claim"]},
	{"shot_location_interior_station_train" : ["train station interior", "train station commuters"]},
	{"shot_location_interior_station_bus" : ["bus station interior", "bus station waiting"]},
	{"shot_location_interior_station_subway" : ["subway platform", "subway turnstyle", "subway station commuters", "subway platform commuters"]},
	{"shot_location_interior_store" : ["store interior", "store customers"]},
	{"shot_location_interior_store_aisle" : ["store aisle", "aisle shoppers"]},
	{"shot_location_interior_store_checkout" : ["store checkout", "cashier"]},
	{"shot_location_interior_mall" : ["mall interior", "busy mall", "shopping at mall"]},
	{"shot_location_interior_nave" : ["church nave", "people in church nave"]},
	{"shot_location_interior_prayer_hall" : ["prayer hall", "call to prayer hall"]},
	{"shot_location_interior_pulpit" : ["church interior pulpit", "church interior pulpit sermon"]},
	{"shot_location_interior_synagogue" : ["synagogue interior","synagogue praying"]},
	{"shot_location_interior_meditation" : ["temple meditation hall", "temple meditation hall prayers"]},
	{"shot_location_interior_crypt" : ["crypt"]},
	{"shot_location_interior_cloister" : ["cloister"]},
	{"shot_location_interior_prison" : ["jail cell people", "prison interior"]},
	{"shot_location_interior_station_police" : ["police precinct interior"]},
	{"shot_location_interior_station_fire" : ["fire station garage", "fire station locker room"]},
	{"shot_location_interior_command_center" : ["command center",]},
	{"shot_location_interior_courtroom" : ["courtroom", "courtroom law and order"]},

	# specific vehicle categories
	{"shot_location_interior_car" : ["Car interior cinematography"]},
	{"shot_location_interior_bus" : ["Crowded Bus interior", "people in bus", "kids inside school bus"]},
	{"shot_location_interior_truck" : ["truck inside driver"]},
	{"shot_location_interior_train" : ["inside train passengers"]},
	{"shot_location_interior_helicopter" : ["helicopter piloting", "helicopter cabin"]},
	{"shot_location_interior_subway" : ["subway car interior", "subway car commuters"]},
	{"shot_location_interior_boat" : ["boat cabin interior"]},
	{"shot_location_interior_airplane_cabin" : ["Airplane passengers",]},
	{"shot_location_interior_airplane_cockpit" : ["Airplane cockpit pilots"]},
	{"shot_location_interior_spacecraft" : ["spacecraft interior", "astronaut inside spacecraft"]},
	],


 }

#print categories_and_classes

def download_images(arguments):
			response = google_images_download.googleimagesdownload()   #class instantiation
			paths = response.download(arguments)
			print(paths)

allArguments = []

try:
    os.stat("Data/download/")
except:
    os.mkdir("Data/")
    os.mkdir("Data/download/")

for category_key in categories_and_concepts:
	# concepts is an array of dictionaries

	try:
	    os.stat("Data/download/" + category_key)
	except:
	    os.mkdir("Data/download/" + category_key)

	print ("Category: " + category_key)
	category_concepts = categories_and_concepts[category_key]
	for concept in category_concepts:
		for concept_key in concept:
			print ("Concept: " + concept_key)
			searchterms = ", ".join(concept[concept_key])
			print ("Search Terms: " + searchterms)

			try:
			    os.stat("Data/download/" + category_key + "/" + concept_key)
			except:
			    os.mkdir("Data/download/" + category_key + "/" + concept_key)

			response = google_images_download.googleimagesdownload()   #class instantiation
			arguments = { "chromedriver" : args.chromedriver_path, "keywords" : searchterms, "limit" : 300, "print_urls" : False, "output_directory" : "Data/download/"+category_key, "image_directory" : concept_key,  "size" : "medium", "format" : "jpg" , "no_numbering" : True }
			#arguments = { "keywords" : searchterms, "limit" : 100, "print_urls" : False, "output_directory" : "Data/download/"+category_key, "image_directory" : concept_key,  "size" : "medium", "save_source" : concept_key + "sources", "format" : "jpg" }
			allArguments.append(arguments)

# concurrent google image downloaders
pool = Pool(processes=10)
results = pool.map(download_images, allArguments)

print(results)
