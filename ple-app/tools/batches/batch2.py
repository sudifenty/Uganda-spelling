#!/usr/bin/env python3
"""Batch 2 — additional original SST practice questions, P.4 to P.7.

Nothing here is copied from a PLE paper or textbook. Each question is written to
the level of its own class. IDs are assigned by the builder, not here.
"""
from qhelpers import M, T, F, P

# ══════════════════════════════════════════════════════════════════════════
# P.4  — home, school, community, own district. Concrete and familiar.
# ══════════════════════════════════════════════════════════════════════════
P4 = [
 # Family & home
 M("P4","Our Family","Family members","Easy","Your mother's sister is your ______.",["Aunt","Uncle","Cousin","Niece"],"A","Your mother's sister is called your aunt."),
 M("P4","Our Family","Family members","Easy","Your father's father is your ______.",["Uncle","Grandfather","Brother","Cousin"],"B","The father of your father or mother is your grandfather."),
 F("P4","Our Family","Family duties","Easy","Sweeping the compound at home is one of the ______ of a child.",["duties","responsibilities","work"],"Children help at home by doing simple duties."),
 M("P4","Our Family","Family needs","Medium","Which one is a want rather than a need?",["Food","Shelter","A television","Water"],"C","Needs keep us alive. A television is nice to have but not needed."),
 T("P4","Our Family","Family care","Easy","Parents have a duty to send their children to school.","A","Parents must provide care, food and education for their children."),
 M("P4","Our Home","Home safety","Medium","Which item at home should a young child NOT play with?",["A ball","A panga","A book","A skipping rope"],"B","Sharp tools like a panga can cause serious injury."),
 M("P4","Our Home","Housing","Easy","Which material is used to build a permanent house?",["Grass","Bricks","Banana leaves","Papyrus"],"B","Bricks make strong, permanent walls."),
 # School
 M("P4","Our School","School members","Easy","Who helps the head teacher to lead learners in a school?",["The cook","The prefects","The visitors","The parents"],"B","Prefects are learners chosen to help lead other learners."),
 M("P4","Our School","School property","Medium","A learner breaks a school window while playing. What should she do?",["Hide and say nothing","Report it to a teacher","Blame a friend","Run home"],"B","Telling the truth is honest and helps the school repair the window.","scenario"),
 F("P4","Our School","School work","Easy","The book in which a learner writes class work is called an ______ book.",["exercise"],"Learners write their work in exercise books."),
 T("P4","Our School","School rules","Easy","Coming to school on time is a good school habit.","A","Being on time means you do not miss lessons."),
 M("P4","Our School","Learning","Medium","Why is a school library useful to learners?",["For sleeping","For reading and finding information","For cooking","For playing football"],"B","A library keeps books that help learners read and learn more."),
 # Community
 M("P4","Our Community","Community needs","Easy","Which one is a source of clean water in a community?",["A borehole","A rubbish pit","A road","A shop"],"A","Boreholes give safe water for drinking."),
 M("P4","Our Community","Community services","Easy","Where are letters and parcels handled?",["At the market","At the post office","At the church","At the garden"],"B","The post office handles letters and parcels."),
 M("P4","Our Community","Community life","Medium","Neighbours join together to repair a village path. This is called ______.",["Quarrelling","Communal work","Trading","Travelling"],"B","Communal work is people working together for the good of all."),
 F("P4","Our Community","Community leaders","Easy","A person chosen by people to lead them is called a ______.",["leader"],"Leaders are chosen to guide and speak for the people."),
 M("P4","Our Community","Community services","Hard","A village has one well that often breaks down. What is the best thing for the community to do?",["Wait for it to break completely","Choose a group to look after and repair it","Stop using water","Blame the leaders"],"B","Caring for shared property keeps it working for everyone.","scenario"),
 # Leadership, rules, citizenship
 M("P4","Leadership","School leaders","Easy","Who is in charge of one class?",["The class teacher","The cook","The gate keeper","The nurse"],"A","Each class has a class teacher who looks after it."),
 M("P4","Leadership","Qualities","Medium","Which behaviour shows that a village leader can be trusted?",["Telling the truth to the people","Hiding village money","Shouting at everyone","Refusing to hold meetings"],"A","A leader who tells the truth and is open with people earns their trust."),
 T("P4","Rules","Why rules matter","Easy","Rules help people to live together peacefully.","A","Rules guide behaviour so people live together well."),
 M("P4","Good Citizenship","Behaviour","Medium","Which action shows good citizenship in a community?",["Throwing rubbish in the road","Helping an elderly neighbour","Breaking a water tap","Shouting at visitors"],"B","Helping others is a mark of a good citizen."),
 M("P4","Good Citizenship","Property","Hard","You see a friend writing on a school wall. What is the best thing to do?",["Join in","Politely tell him to stop and clean it","Laugh at him","Write on another wall"],"B","Protecting school property helps everyone and stops damage.","scenario"),
 # Uganda, districts, regions
 F("P4","Our District","Districts","Easy","The area smaller than a region but bigger than a village is called a ______.",["district"],"Uganda is divided into districts for easier administration."),
 M("P4","Our District","Regions","Medium","Which region of Uganda lies in the far north?",["Central","Northern","Western","Eastern"],"B","The Northern region lies in the north of Uganda."),
 M("P4","Our District","Uganda","Easy","Which one is the money used in Uganda?",["Shilling","Dollar","Pound","Franc"],"A","Uganda uses the Uganda Shilling."),
 F("P4","Our District","Neighbours","Medium","The country found to the south of Uganda is ______.",["tanzania"],"Tanzania borders Uganda on the south."),
 # Physical features
 M("P4","Physical Features","Landforms","Easy","A raised piece of land smaller than a mountain is called a ______.",["Hill","Valley","Lake","Plain"],"A","A hill is raised land, but lower than a mountain."),
 M("P4","Physical Features","Water bodies","Easy","A large body of water surrounded by land is called a ______.",["River","Lake","Road","Hill"],"B","A lake is water surrounded by land."),
 F("P4","Physical Features","Water bodies","Medium","Water that flows in a channel from a highland to a lake is called a ______.",["river"],"Rivers flow from high ground down to lakes or seas."),
 # Weather
 M("P4","Weather","Weather types","Easy","Which weather has a lot of clouds but no rain?",["Sunny","Cloudy","Windy","Rainy"],"B","Cloudy weather means the sky is covered by clouds."),
 M("P4","Weather","Weather recording","Medium","Where in a school are weather instruments kept?",["In the kitchen","At the weather station","In the library","Under a desk"],"B","A weather station is an open place where instruments are kept."),
 T("P4","Weather","Weather and clothes","Easy","People wear heavy clothes when the weather is cold.","A","Warm clothing protects the body from cold."),
 M("P4","Weather","Weather and farming","Hard","Why do farmers plant seeds at the start of the rainy season?",["So seeds get enough water to grow","Because the soil is dry","To avoid weeds","So birds eat them"],"A","Young plants need steady rain to grow well.","cause_effect"),
 # Environment & resources
 M("P4","Environment","Pollution","Medium","Which action pollutes a river?",["Planting trees along it","Pouring rubbish into it","Fetching water carefully","Fencing it"],"B","Rubbish makes river water dirty and unsafe."),
 F("P4","Environment","Conservation","Medium","Planting trees to replace those cut down helps to protect the ______.",["environment"],"Trees hold the soil, give shade and help bring rain."),
 M("P4","Natural Resources","Uses","Easy","Which natural resource is used for making bricks?",["Soil","Air","Sunlight","Wind"],"A","Bricks are moulded from clay soil."),
 M("P4","Natural Resources","Uses","Medium","Which natural resource gives us fish?",["Forests","Water bodies","Rocks","Air"],"B","Fish are caught from lakes, rivers and swamps."),
 # Transport & communication
 M("P4","Transport","Water transport","Easy","Which means of transport is used on a lake?",["Boat","Bus","Bicycle","Lorry"],"A","Boats and canoes move people and goods on water."),
 M("P4","Transport","Road safety","Medium","Where should a pedestrian walk along a busy road?",["In the middle","On the walkway at the side","Behind vehicles","On the tarmac"],"B","Walkways keep people away from moving vehicles."),
 F("P4","Communication","Traditional","Medium","Long ago, people passed messages in a village by beating a ______.",["drum"],"Drums were beaten to call people or warn of danger."),
 M("P4","Communication","Mass media","Medium","Which one reaches many people at the same time?",["A letter","A radio","A whisper","A note"],"B","Radio sends the same message to very many listeners at once."),
 # Agriculture, trade, markets
 M("P4","Agriculture","Crops","Easy","Which one is a food crop?",["Coffee","Maize","Cotton","Tobacco"],"B","Maize is grown mainly to be eaten."),
 M("P4","Agriculture","Animals","Easy","Which animal gives us milk?",["Cow","Dog","Cat","Hen"],"A","Cows are kept for milk and meat."),
 F("P4","Agriculture","Poultry","Easy","The keeping of birds such as hens for eggs and meat is called ______.",["poultry","poultry keeping","poultry farming"],"Poultry keeping is rearing birds like hens and ducks."),
 M("P4","Trade","Buying and selling","Medium","A person who sells goods in small quantities to people is called a ______.",["Retailer","Farmer","Doctor","Teacher"],"A","A retailer sells small amounts directly to buyers."),
 M("P4","Markets","Market goods","Medium","Which goods are usually sold in a food market?",["Bricks and sand","Tomatoes and beans","Iron sheets","Books"],"B","Food markets sell farm produce like vegetables and grains."),
 M("P4","Markets","Money","Hard","Mary has 2,000 shillings. She buys a book at 1,200 shillings. How much is left?",["600 shillings","800 shillings","1,000 shillings","1,200 shillings"],"B","2,000 minus 1,200 leaves 800 shillings.","application"),
 # Health, sanitation, safety
 M("P4","Health","Disease prevention","Easy","Sleeping under a treated mosquito net prevents ______.",["Malaria","Cough","Broken bones","Toothache"],"A","Mosquito nets stop mosquito bites that spread malaria."),
 M("P4","Health","Food","Medium","Which meal is the most balanced?",["Only posho","Posho, beans and greens","Only tea","Only sugarcane"],"B","A balanced meal mixes different food groups."),
 F("P4","Health","Sanitation","Easy","Human waste should be disposed of in a ______.",["latrine","toilet","pit latrine"],"Using a latrine keeps germs away from people and water."),
 T("P4","Safety","Water safety","Medium","Children should swim in a lake without an adult watching them.","B","Swimming without an adult is dangerous. Always be supervised."),
 M("P4","Safety","Fire safety","Medium","Which one can start a fire at home?",["A closed book","A lit candle left alone","A plastic cup","A blanket folded away"],"B","An unattended flame can set nearby things alight."),
 # Culture & national identity
 M("P4","Culture","Traditional food","Easy","Which one is a traditional Ugandan food?",["Matooke","Pizza","Burger","Pasta"],"A","Matooke is a common traditional food in Uganda."),
 F("P4","Culture","Language","Medium","The language spoken by a group of people as their mother tongue is called their ______ language.",["local","native","mother"],"A local language is the one a community grew up speaking."),
 M("P4","National Identity","National anthem","Medium","What should you do when the National Anthem is being sung?",["Keep walking","Stand still and quiet","Sit down","Talk to friends"],"B","Standing still and quiet shows respect for the country."),
 M("P4","National Identity","National symbols","Hard","Why does a country have national symbols such as a flag?",["To decorate offices","To show the country's identity and unity","To sell to visitors","To replace money"],"B","Symbols stand for the country and bring people together.","cause_effect"),
 # Map basics
 M("P4","Map Skills","What a map is","Easy","A drawing of a place as seen from above is called a ______.",["Map","Photo","Story","Song"],"A","A map shows a place from above, drawn on paper."),
 M("P4","Map Skills","Map symbols","Medium","On a map, a small drawing that stands for a real thing is called a ______.",["Title","Symbol","Frame","Number"],"B","Symbols stand for real features like schools or roads."),
 M("P4","Direction","Cardinal points","Medium","Which direction is opposite North?",["East","West","South","North East"],"C","South is directly opposite North."),
 M("P4","Direction","Using direction","Hard","The market is East of the school. In which direction is the school from the market?",["North","South","East","West"],"D","If the market is east of the school, the school is west of the market.","application"),
 P("P4","Economic Activities","Workers and work","Medium","Match each worker with what they produce or provide.",[["Farmer","Food crops"],["Fisherman","Fish"],["Carpenter","Furniture"],["Tailor","Clothes"]],"Different workers provide different goods and services."),
 M("P4","Economic Activities","Types of work","Hard","Why do people in a community do different kinds of work?",["To confuse each other","So that all the different needs of the community are met","Because work is easy","To avoid farming"],"B","When people specialise, the community gets all the goods and services it needs.","cause_effect"),
]

# ══════════════════════════════════════════════════════════════════════════
# P.5 — Uganda as a country: relief, drainage, resources, map skills.
# ══════════════════════════════════════════════════════════════════════════
P5 = [
 M("P5","Physical Features","Relief","Easy","Land that is flat and raised high above sea level is called a ______.",["Plateau","Valley","Delta","Bay"],"A","A plateau is high, fairly flat land."),
 M("P5","Physical Features","Mountains","Easy","Mount Elgon is found near which town?",["Mbale","Kabale","Arua","Masaka"],"A","Mount Elgon rises near Mbale in eastern Uganda."),
 F("P5","Physical Features","Islands","Medium","A piece of land completely surrounded by water is called an ______.",["island"],"Islands such as the Ssese Islands sit in Lake Victoria."),
 M("P5","Physical Features","Rift Valley","Hard","Lakes Albert, Edward and George lie in the ______.",["Eastern Rift Valley","Western Rift Valley","Central plateau","Coastal plain"],"B","These lakes lie in the Western branch of the Rift Valley."),
 M("P5","Drainage","Rivers","Easy","The River Nile leaves Lake Victoria at ______.",["Jinja","Gulu","Mbarara","Fort Portal"],"A","The Nile begins its journey north at Jinja."),
 F("P5","Drainage","Swamps","Medium","Low, wet land covered with papyrus is called a ______.",["swamp","wetland"],"Swamps hold water and support plants such as papyrus."),
 M("P5","Climate","Elements of weather","Easy","Which instrument shows the direction from which the wind is blowing?",["Thermometer","Rain gauge","Wind vane","Barometer"],"C","A wind vane turns to point towards where the wind comes from."),
 M("P5","Climate","Seasons","Medium","A long period without rainfall is called a ______.",["Wet season","Dry season","Cold season","Windy season"],"B","A dry season is a long spell with little or no rain."),
 M("P5","Climate","Rainfall types","Hard","Rain that falls when moist air is forced to rise over a mountain is called ______ rainfall.",["Relief","Convectional","Frontal","Cyclonic"],"A","Air rising over highlands cools and drops relief rainfall."),
 M("P5","Vegetation","Forests","Medium","Which vegetation grows in areas with heavy rainfall all year?",["Desert scrub","Tropical rain forest","Short grass","Thorn bush"],"B","Heavy, year-round rain supports thick rain forest."),
 F("P5","Vegetation","Savanna","Medium","Vegetation made up of tall grass with scattered trees is called ______.",["savanna","savannah","savanna grassland"],"Savanna is grassland with a few scattered trees."),
 M("P5","Soils","Soil erosion","Hard","Which farming method best reduces soil erosion on a slope?",["Digging up and down the slope","Contour ploughing across the slope","Burning the grass","Leaving soil bare"],"B","Ploughing across the slope slows running water."),
 M("P5","Soils","Soil fertility","Medium","Which practice improves soil fertility naturally?",["Adding manure","Burning all the grass","Continuous digging","Overgrazing"],"A","Manure returns plant food to the soil."),
 M("P5","Natural Resources","Water","Easy","Which one is a use of water in the home?",["Cooking","Building roads","Mining","Weaving"],"A","Water is used at home for cooking, washing and drinking."),
 M("P5","Natural Resources","Forests","Medium","Which product comes from forests?",["Timber","Copper","Salt","Cement"],"A","Trees in forests are cut for timber."),
 F("P5","Mining","Salt","Medium","Salt is traditionally mined at Lake ______ in western Uganda.",["katwe"],"Lake Katwe in Kasese is known for salt mining."),
 M("P5","Mining","Effects","Hard","Which problem is most likely where open mining takes place?",["More forests grow","Large pits and destroyed land","Cleaner rivers","More rainfall"],"B","Open mining leaves pits and damages the land surface.","cause_effect"),
 M("P5","Agriculture","Farming systems","Easy","Growing crops only for the family to eat is called ______ farming.",["Subsistence","Commercial","Plantation","Mixed"],"A","Subsistence farming feeds the farmer's own household."),
 M("P5","Agriculture","Mixed farming","Medium","A farmer who grows crops and also keeps animals practises ______ farming.",["Mixed","Shifting","Plantation","Nomadic"],"A","Mixed farming combines crops and livestock on one farm."),
 M("P5","Agriculture","Plantations","Hard","Why are tea and sugarcane usually grown on large plantations?",["They need very little land","They need large areas and are processed in bulk","They grow in water only","They are food crops"],"B","Plantation crops are grown in bulk to feed a factory nearby.","cause_effect"),
 M("P5","Fishing","Methods","Medium","Which fishing method is allowed and safe for the lake?",["Using poison","Using a net with legal mesh size","Using explosives","Draining the lake"],"B","Legal nets let young fish escape and grow."),
 F("P5","Fishing","Fish farming","Medium","Rearing fish in man-made ponds is called fish ______.",["farming"],"Fish farming raises fish in ponds to increase supply."),
 M("P5","Trade","Barter","Easy","Exchanging goods for other goods without money is called ______ trade.",["Barter","Retail","Wholesale","Foreign"],"A","Barter trade exchanges goods directly."),
 M("P5","Trade","Exports","Medium","Selling goods to other countries is called ______.",["Importation","Exportation","Retailing","Bartering"],"B","Exportation is selling goods abroad."),
 M("P5","Transport","Road transport","Medium","Which is an advantage of road transport over water transport in Uganda?",["It reaches most parts of the country","It is only for heavy goods","It needs no fuel","It works only at night"],"A","Roads reach nearly every district, unlike lakes and rivers."),
 M("P5","Communication","Media","Medium","Which one is an example of print media?",["Newspaper","Radio","Television","Telephone"],"A","Newspapers are printed, so they are print media."),
 M("P5","Population","Population growth","Hard","What is the main reason Uganda's population keeps growing?",["Many people leave the country","Births are more than deaths","There is no farming","People marry late"],"B","When births outnumber deaths, population grows.","cause_effect"),
 M("P5","Settlement","Settlement patterns","Medium","Houses built close together along a road form a ______ settlement.",["Linear","Scattered","Nucleated","Circular"],"A","Linear settlements stretch in a line along a road or river."),
 M("P5","Urban and Rural","Differences","Medium","Which feature is more common in an urban area than a rural area?",["Large gardens","Tall buildings and many shops","Cattle grazing","Forests"],"B","Towns have many buildings, shops and services close together."),
 M("P5","Urban and Rural","Rural life","Hard","Why do many young people move from villages to towns?",["To look for jobs and services","Because villages have no land","To avoid rainfall","Because towns are quiet"],"A","Towns offer jobs, schools and services that attract young people.","cause_effect"),
 M("P5","Leadership","Central government","Easy","Who is the head of state of Uganda?",["The President","The Speaker","The Chief Justice","The Mayor"],"A","The President is the head of state."),
 F("P5","Government","Ministries","Medium","A person appointed to head a government ministry is called a ______.",["minister"],"Ministers head ministries and are appointed by the President."),
 M("P5","Citizenship","Duties","Medium","Which one is a duty of every citizen?",["Obeying the laws","Ignoring taxes","Damaging property","Refusing to vote"],"A","Citizens must obey the laws of the country."),
 M("P5","Culture","Cultural practices","Medium","Which one helps to keep a community's culture alive?",["Traditional dances and songs","Ignoring elders","Forgetting local language","Refusing ceremonies"],"A","Dances, songs and ceremonies pass culture to the young."),
 M("P5","African Communities","Ways of life","Hard","The Karimojong keep moving with their animals mainly because ______.",["they enjoy travelling","they search for pasture and water","they dislike villages","the animals are wild"],"B","In dry areas, herders move to find grass and water.","cause_effect"),
 M("P5","History","Early Uganda","Medium","The Bachwezi are remembered in Ugandan history for ruling the empire of ______.",["Bunyoro-Kitara","Buganda","Ankole","Busoga"],"A","The Bachwezi ruled the Bunyoro-Kitara empire."),
 F("P5","History","Independence","Medium","The colonial power that ruled Uganda before independence was ______.",["britain","the british","british"],"Uganda was a British protectorate until 1962."),
 M("P5","Environment","Conservation","Medium","Which practice protects a forest?",["Selective cutting and replanting","Burning it","Clearing it for building","Cutting all trees at once"],"A","Cutting a few trees and replanting keeps a forest alive."),
 M("P5","Community Development","Projects","Hard","A village wants clean water. Which project is most useful?",["Building a borehole","Building a stadium","Buying uniforms","Planting flowers"],"A","A borehole directly solves the need for clean water.","scenario"),
 M("P5","Map Skills","Scale","Hard","On a map of scale 1:100,000, 1 cm represents ______.",["1 kilometre","10 kilometres","100 metres","10 metres"],"A","100,000 cm equals 1 km.","map_skill"),
 M("P5","Map Skills","Direction","Medium","Which direction lies between South and West?",["South East","South West","North West","North East"],"B","South West lies halfway between South and West.","map_skill"),
 M("P5","Map Skills","Symbols","Medium","On a map, a small aeroplane symbol usually shows a ______.",["Airport","School","Market","Hospital"],"A","Map symbols stand for real features like airports.","map_skill"),
 T("P5","Map Skills","Map elements","Easy","Every good map should have a title, a key and a scale.","A","Title, key and scale help a reader understand a map."),
 M("P5","Social Services","Education","Medium","Which programme helps Ugandan children attend primary school free of tuition?",["Universal Primary Education","National Service","Youth Fund","Road Fund"],"A","UPE was introduced so more children could attend primary school."),
 M("P5","Natural Resources","Conservation","Hard","Which resource can be used up completely and never replaced?",["Copper ore","Forests","Fish","Grass"],"A","Minerals such as copper are non-renewable: once mined, they are gone for good.","comparison"),
]

# ══════════════════════════════════════════════════════════════════════════
# P.6 — East Africa, industry, government, regional history, map work.
# ══════════════════════════════════════════════════════════════════════════
P6 = [
 M("P6","East Africa","Countries","Easy","Which country lies to the south west of Uganda?",["Kenya","Rwanda","South Sudan","Ethiopia"],"B","Rwanda borders Uganda in the south west."),
 F("P6","East Africa","Capital cities","Easy","The capital city of Kenya is ______.",["nairobi"],"Nairobi is Kenya's capital and largest city."),
 M("P6","East Africa","Physical features","Medium","Mount Kenya lies in which country?",["Kenya","Tanzania","Uganda","Burundi"],"A","Mount Kenya is Africa's second highest mountain."),
 M("P6","East Africa","Coast","Medium","Which East African country has NO sea coast?",["Kenya","Tanzania","Uganda","Somalia"],"C","Uganda is landlocked, with no coastline."),
 M("P6","Physical Features","Lakes","Medium","Lake Kyoga was formed mainly by ______.",["Faulting","The flooding of a river valley","Volcanic action","Wind"],"B","Lake Kyoga formed when river valleys were flooded."),
 M("P6","Physical Features","Mountains","Hard","Which mountain is a block mountain formed by faulting?",["Mount Elgon","Mount Rwenzori","Mount Muhavura","Mount Kilimanjaro"],"B","Rwenzori is a block mountain pushed up between faults."),
 F("P6","Drainage","Rivers","Medium","The river that flows from Lake Victoria through Lake Kyoga is called the ______ Nile.",["victoria"],"The stretch between Lake Victoria and Lake Kyoga is the Victoria Nile."),
 M("P6","Climate","Climate and altitude","Hard","Why is Kabale cooler than Soroti?",["It is nearer the Equator","It lies at a higher altitude","It has fewer trees","It is nearer a lake"],"B","Temperature falls as altitude increases.","cause_effect"),
 M("P6","Vegetation","Montane vegetation","Hard","Vegetation found on high mountain slopes is described as ______.",["Montane","Mangrove","Desert","Coastal"],"A","Montane vegetation grows on cool, high mountain slopes."),
 M("P6","Soils","Volcanic soils","Medium","Why are volcanic soils good for farming?",["They are very fertile","They hold no water","They are stony","They are salty"],"A","Volcanic soils are rich in plant food."),
 M("P6","Natural Resources","Minerals","Medium","Which mineral is associated with Kilembe?",["Copper","Gold","Salt","Diamond"],"A","Kilembe in Kasese is known for copper."),
 M("P6","Agriculture","Cash crops","Medium","Which cash crop is grown mainly in the drier parts of eastern Uganda?",["Cotton","Tea","Cocoa","Rubber"],"A","Cotton suits the warmer, drier east."),
 M("P6","Industry","Location factors","Hard","Why are many industries located in and around Kampala?",["Cheap land only","Large market, labour and good transport","Cool climate","Many forests"],"B","Industries locate where there are buyers, workers and transport.","cause_effect"),
 M("P6","Industry","Types","Medium","A factory that turns sugarcane into sugar is a ______ industry.",["Processing","Mining","Service","Construction"],"A","Processing industries change raw materials into finished goods."),
 M("P6","Trade","Balance of trade","Hard","A country that imports more than it exports has ______.",["A trade surplus","An unfavourable balance of trade","No trade","Free trade"],"B","Importing more than you export gives an unfavourable balance."),
 M("P6","Transport","Air transport","Medium","Uganda's main international airport is at ______.",["Entebbe","Gulu","Arua","Soroti"],"A","Entebbe International Airport handles most international flights."),
 M("P6","Transport","Water transport","Hard","Which is a disadvantage of water transport on Lake Victoria?",["It is very cheap","It is slow and limited to the lake shores","It carries heavy goods","It needs no fuel"],"B","Boats are slow and can only serve places on the shore."),
 M("P6","Communication","Modern communication","Medium","Which service allows people to send written messages instantly using the internet?",["Email","Telegram drum","Letter","Newspaper"],"A","Email sends written messages instantly over the internet."),
 M("P6","Population","Census","Medium","Information collected during a census helps the government to ______.",["Plan services such as schools and hospitals","Increase taxes only","Choose a president","Draw the flag"],"A","Census data guides planning for services."),
 M("P6","Migration","Types","Hard","A person who moves to another country because of war is called a ______.",["Tourist","Refugee","Trader","Pilgrim"],"B","Refugees flee their country because of war or persecution."),
 M("P6","Settlement","Factors","Hard","Which factor most discourages settlement in an area?",["Fertile soils","Frequent flooding and disease","Good roads","Reliable rainfall"],"B","People avoid places that are unsafe or unhealthy.","cause_effect"),
 M("P6","Urbanisation","Solutions","Hard","Which is the best long-term solution to congestion in a growing town?",["Ban all vehicles","Plan the town and improve public transport","Close the schools","Stop building houses"],"B","Planning and good public transport ease congestion.","scenario"),
 M("P6","Government","Executive","Medium","The arm of government that puts laws into action is the ______.",["Legislature","Executive","Judiciary","Electoral Commission"],"B","The Executive implements laws and runs government."),
 M("P6","Government","Parliament","Medium","Who presides over sittings of Parliament?",["The President","The Speaker","The Chief Justice","The Prime Minister"],"B","The Speaker chairs parliamentary sittings."),
 M("P6","Leadership","Local government","Medium","Which council level serves a sub-county?",["LC I","LC II","LC III","LC V"],"C","LC III is the sub-county council."),
 M("P6","Citizenship","Rights","Medium","Which one is a right of a child in Uganda?",["The right to education","The right to skip school","The right to work full time","The right to break laws"],"A","Every child has a right to education."),
 M("P6","Rights and Responsibilities","Balance","Hard","Why does every right come with a responsibility?",["Rights are not important","Because your freedom must not harm others","To reduce freedom","Because leaders say so"],"B","Exercising a right responsibly protects other people's rights."),
 M("P6","East African Community","Benefits","Medium","Which is a benefit of the East African Community to member states?",["Free movement of goods and people","Higher visa fees","Closed borders","Separate currencies only"],"A","The EAC allows easier movement of goods and people."),
 M("P6","East African Community","Challenges","Hard","Which problem can slow down cooperation in a regional bloc?",["Shared language","Political disagreements between members","Good roads","Common market"],"B","Disagreements between governments slow joint decisions."),
 M("P6","African Geography","Regions","Medium","Egypt is found in which part of Africa?",["North Africa","West Africa","Central Africa","Southern Africa"],"A","Egypt lies in North Africa."),
 M("P6","African Geography","Deserts","Medium","The Kalahari Desert is found in ______ Africa.",["North","Southern","West","East"],"B","The Kalahari lies in southern Africa."),
 M("P6","African Peoples","Communities","Hard","The Tuareg of the Sahara are best described as ______.",["Fishermen","Nomadic herders and traders","Miners","Sailors"],"B","The Tuareg move across the desert herding and trading."),
 M("P6","History","Missionaries","Medium","Which group of missionaries arrived in Buganda in 1879?",["The White Fathers","The Arabs","The Portuguese","The Germans"],"A","Catholic White Fathers reached Buganda in 1879."),
 M("P6","History","Slave trade","Hard","Which of these was a result of the slave trade in East Africa?",["Growth of villages","Loss of population and insecurity","More schools","Better farming"],"B","Slave raiding depopulated areas and caused fear.","cause_effect"),
 F("P6","History","Kingdoms","Medium","The king of Buganda is given the title ______.",["kabaka"],"The Kabaka is the king of Buganda."),
 M("P6","History","Colonial rule","Hard","Which of these was a reason Europeans wanted colonies in Africa?",["To get raw materials and markets","To learn African languages","To reduce their own population","To build African kingdoms"],"A","Colonies supplied raw materials and bought European goods."),
 M("P6","Culture","Cultural heritage","Medium","Which one is an example of Uganda's cultural heritage?",["The Kasubi Tombs","A shopping mall","A tarmac road","A power dam"],"A","The Kasubi Tombs are an important cultural heritage site."),
 M("P6","Environmental Conservation","Wetlands","Hard","Why should wetlands not be drained for building?",["They store water and control floods","They have no use","They cause disease only","They block roads"],"A","Wetlands store water, reduce floods and support wildlife.","cause_effect"),
 M("P6","Map Work","Scale","Hard","Two towns are 6 cm apart on a map of scale 1:50,000. The real distance is ______.",["3 kilometres","6 kilometres","30 kilometres","300 metres"],"A","6 cm x 50,000 = 300,000 cm = 3 km.","map_skill"),
 M("P6","Map Work","Relief","Hard","Widely spaced contour lines on a map show ______.",["A steep slope","A gentle slope","A cliff","A river"],"B","Contours far apart mean the land rises slowly.","map_skill"),
 M("P6","Map Work","Interpretation","Hard","A map shows scattered huts, gardens and a cattle track. This area is most likely ______.",["An industrial town","A rural farming area","A port","An airport"],"B","Huts, gardens and tracks suggest rural farming.","map_skill"),
 M("P6","Community Development","Participation","Medium","Which action best shows community participation in a project?",["Waiting for government only","Contributing labour and ideas","Complaining","Ignoring meetings"],"B","Communities succeed when members contribute effort and ideas."),
 P("P6","East Africa","Physical features","Hard","Match each feature with its country.",[["Mount Kilimanjaro","Tanzania"],["Mount Kenya","Kenya"],["Mount Rwenzori","Uganda"],["Lake Tanganyika","Tanzania and neighbours"]],"Knowing where features lie helps in map work."),
]

# ══════════════════════════════════════════════════════════════════════════
# P.7 — PLE-style revision. Original questions on the same skills.
# ══════════════════════════════════════════════════════════════════════════
P7 = [
 # Geography
 M("P7","Geography","Neighbouring countries","Easy","Which country borders Uganda to the north?",["Kenya","South Sudan","Tanzania","Rwanda"],"B","South Sudan lies to the north of Uganda."),
 F("P7","Geography","Location","Easy","Uganda is described as a landlocked country because it has no ______.",["sea","coastline","sea coast","port"],"A landlocked country has no direct access to the sea."),
 M("P7","Geography","Physical Features","Medium","Which of these is a man-made lake in Uganda?",["Lake Wamala","Lake Bunyonyi","Lake Kyoga","No lake listed"],"D","Uganda's named lakes here are natural; reservoirs behind dams are man-made."),
 M("P7","Geography","Swamps","Medium","Which is an economic use of swamps in Uganda?",["Making papyrus mats and crafts","Mining copper","Growing tea","Rearing camels"],"A","Papyrus from swamps is used for mats, baskets and crafts."),
 M("P7","Geography","Climate","Hard","Which factor explains why Entebbe has a moderate climate?",["It is far from water","The influence of Lake Victoria","It is a desert","It is very high"],"B","Large water bodies moderate nearby temperatures.","cause_effect"),
 M("P7","Geography","Vegetation","Medium","Which vegetation type is found in the Karamoja region?",["Tropical rain forest","Dry savanna and thorn bush","Mangrove","Montane forest"],"B","Low rainfall gives Karamoja dry savanna and thorn bush."),
 M("P7","Geography","Soils","Hard","Why is continuous cropping without manure harmful?",["It adds nutrients","It removes plant nutrients and lowers yields","It stops erosion","It improves soil"],"B","Crops take nutrients out; without replacement the soil is exhausted.","cause_effect"),
 M("P7","Geography","Population","Medium","Population density is best described as the number of people ______.",["In a country","Per square kilometre","Born each year","Who can vote"],"B","Density compares population with the area of land."),
 M("P7","Geography","Settlement","Hard","Why is settlement sparse in the Kidepo area?",["Fertile soil","Wildlife protection and dry conditions","Good roads","Many industries"],"B","Protected park land and dryness limit settlement.","cause_effect"),
 M("P7","Geography","Mining","Medium","Which mineral is quarried for building stone and road making?",["Limestone","Granite","Cobalt","Tin"],"B","Granite is quarried and crushed for construction."),
 M("P7","Geography","Industry","Hard","Which industry would most likely be set up near a large fishing landing site?",["Cement making","Fish processing","Textile weaving","Steel rolling"],"B","Processing near the source keeps fish fresh and cuts transport cost.","application"),
 M("P7","Geography","Tourism","Medium","Which is a benefit of tourism to Uganda's economy?",["It earns foreign exchange","It reduces employment","It destroys parks","It stops trade"],"A","Tourists spend foreign currency in the country."),
 M("P7","Geography","Tourism","Hard","Which action best protects wildlife while still allowing tourism?",["Allowing hunting","Controlled visits with trained guides","Removing all fences","Building factories in parks"],"B","Managed visits earn money without harming animals.","scenario"),
 M("P7","Geography","Environmental Conservation","Hard","Which practice reduces the effects of deforestation most directly?",["Planting trees and using energy-saving stoves","Burning charcoal freely","Clearing forests for farms","Draining swamps"],"A","Replanting and using less fuelwood reduce forest loss."),
 M("P7","Geography","Transport","Medium","Which mode is most suitable for carrying heavy goods over long distances by land?",["Bicycle","Railway","Motorcycle","Foot"],"B","Railways carry bulky, heavy goods cheaply over land."),
 # Map Work
 M("P7","Map Work","Direction","Easy","Which is an intermediate direction?",["North","South East","West","South"],"B","Intermediate directions lie between cardinal points.","map_skill"),
 M("P7","Map Work","Direction","Medium","A person facing South West turns 90° clockwise. They now face ______.",["North West","South East","North East","West"],"A","From SW, a quarter turn clockwise gives NW.","map_skill"),
 M("P7","Map Work","Scale","Hard","A map has a scale of 1:25,000. A road measures 8 cm. Its real length is ______.",["2 kilometres","20 kilometres","200 metres","8 kilometres"],"A","8 x 25,000 = 200,000 cm = 2 km.","map_skill"),
 M("P7","Map Work","Symbols","Medium","A blue line marked on a map most likely shows a ______.",["Road","River","Railway","Boundary"],"B","Blue is used for water features such as rivers.","map_skill"),
 M("P7","Map Work","Key","Medium","Why must a map have a key?",["To make it colourful","To explain what the symbols mean","To show the price","To hide details"],"B","Without a key a reader cannot interpret the symbols.","map_skill"),
 M("P7","Map Work","Grid references","Hard","In a grid reference, which figures are read first?",["Northings","Eastings","Either","The middle ones"],"B","Read eastings (along) before northings (up).","map_skill"),
 M("P7","Map Work","Drainage","Hard","A river on a map bends and has many small streams joining it. These streams are called ______.",["Tributaries","Deltas","Estuaries","Lakes"],"A","Streams that join a bigger river are tributaries.","map_skill"),
 M("P7","Map Work","Interpretation","Hard","A map shows a settlement at the meeting point of three roads. This settlement most likely grew because of ______.",["Mining","Its position as a route centre for trade","Fishing","Forestry"],"B","Route centres attract trade and settlement.","map_skill"),
 # History
 M("P7","History","Early people","Medium","Early people in Africa first got food by ______.",["Farming","Hunting and gathering","Mining","Trading"],"B","Before farming, people hunted animals and gathered wild food."),
 M("P7","History","Migration","Hard","The Bantu are believed to have entered East Africa mainly from the ______.",["North east","West and south west","Far north","East coast"],"B","Bantu groups are believed to have moved in from the west and south west."),
 M("P7","History","Kingdoms","Medium","Which kingdom was ruled by the Bahinda dynasty?",["Ankole","Buganda","Busoga","Toro"],"A","The Bahinda dynasty ruled Ankole."),
 M("P7","History","Explorers","Medium","Which two explorers are associated with reaching Lake Victoria region in the 1860s?",["Speke and Grant","Lugard and Portal","Mackay and Lourdel","Stanley and Kagwa"],"A","Speke and Grant travelled in the Lake Victoria region in the 1860s."),
 M("P7","History","Missionaries","Hard","Which of these was an effect of missionary work in Uganda?",["Growth of schools and hospitals","End of all trade","Loss of all languages","Removal of kingdoms"],"A","Missionaries founded many early schools and health centres.","cause_effect"),
 M("P7","History","Arab traders","Medium","Which goods did Arab traders mainly seek in the East African interior?",["Ivory and slaves","Tea and coffee","Cement and steel","Books"],"A","Ivory and slaves were the main goods sought."),
 M("P7","History","Colonial administration","Hard","Under indirect rule, the British governed mainly through ______.",["European settlers","Existing local chiefs and rulers","Soldiers only","Traders"],"B","Indirect rule used local rulers to administer for the British."),
 M("P7","History","Uganda's history","Medium","The Uganda Agreement of 1900 was signed between the British and ______.",["Bunyoro","Buganda","Ankole","Busoga"],"B","The 1900 Agreement was made with Buganda."),
 M("P7","History","Independence","Medium","Which political party led Uganda at independence in 1962?",["UPC","DP","NRM","KY"],"A","The Uganda People's Congress led the government at independence."),
 M("P7","History","African nationalism","Hard","What was the main aim of African nationalist movements?",["To keep colonial rule","To win self-rule and independence","To increase taxes","To divide countries"],"B","Nationalists campaigned for their countries to govern themselves."),
 M("P7","History","East African history","Hard","Why did the first East African Community collapse in 1977?",["Lack of trade","Political differences and mistrust among members","Too many members","Shortage of roads"],"B","Political disagreements between the three states broke it up.","cause_effect"),
 # Civics
 M("P7","Civics","Citizenship","Medium","A person who becomes a citizen of Uganda after living there for the required period gains citizenship by ______.",["Birth","Registration or naturalisation","Adoption only","Election"],"B","Long residence can lead to citizenship by registration or naturalisation."),
 M("P7","Civics","Rights","Medium","Which is a fundamental human right?",["The right to life","The right to break laws","The right to avoid taxes","The right to damage property"],"A","The right to life is a basic human right."),
 M("P7","Civics","Duties","Medium","Which is a duty of a citizen towards the environment?",["Protecting forests and water sources","Dumping waste in rivers","Burning wetlands","Cutting all trees"],"A","Citizens must protect the environment for everyone."),
 M("P7","Civics","Democracy","Hard","Which practice best shows democracy at work?",["Free and fair elections","Rule by one family","Silencing opponents","Cancelling votes"],"A","Democracy lets people choose leaders in free, fair elections."),
 M("P7","Civics","Rule of law","Hard","The rule of law means ______.",["Leaders are above the law","Everyone, including leaders, obeys the law","Only citizens obey laws","Laws apply to the poor only"],"B","Under the rule of law nobody is above the law."),
 M("P7","Civics","Constitution","Medium","The constitution of a country is best described as ______.",["A list of taxes","The supreme law that guides how a country is governed","A history book","A map"],"B","A constitution is the supreme law of the land."),
 M("P7","Civics","Local government","Medium","Which body makes by-laws for a district?",["The district council","Parliament","The Cabinet","The courts"],"A","District councils pass by-laws for their areas."),
 M("P7","Civics","Elections","Medium","Which body organises national elections in Uganda?",["The Electoral Commission","The Judiciary","Parliament","The Police"],"A","The Electoral Commission organises and supervises elections."),
 M("P7","Civics","National unity","Hard","Which action best promotes national unity?",["Treating all tribes equally","Favouring one region","Refusing a national language","Blocking travel"],"A","Equal treatment builds trust and unity."),
 M("P7","Civics","Peace","Hard","Two groups disagree over grazing land. Which approach is most likely to bring lasting peace?",["Force","Negotiation and a shared agreement","Ignoring it","Fencing everything secretly"],"B","Agreements reached together tend to last.","scenario"),
 M("P7","Civics","National symbols","Medium","Which national symbol is played or sung at official ceremonies?",["The National Anthem","The Coat of Arms","The map","The currency"],"A","The National Anthem is sung at official events."),
 # East Africa
 F("P7","East Africa","Capitals","Easy","The capital city of Rwanda is ______.",["kigali"],"Kigali is Rwanda's capital city."),
 M("P7","East Africa","Economic activities","Medium","Which activity is most important along the East African coast?",["Fishing and tourism","Copper mining","Wheat growing only","Reindeer herding"],"A","Coastal areas depend on fishing and tourism."),
 M("P7","East Africa","Trade","Hard","Why does Uganda pay more for imported goods than Kenya does?",["Uganda has no money","Goods must travel far inland from the sea port","Uganda buys less","Kenya has no port"],"B","Inland transport from Mombasa adds cost.","cause_effect"),
 M("P7","East Africa","Regional cooperation","Medium","A common market among neighbouring countries mainly helps by ______.",["Widening the market for goods","Closing borders","Raising tariffs","Banning travel"],"A","A common market lets goods sell across all member states."),
 # Africa
 M("P7","Africa","Countries","Easy","Which is the largest country in Africa by area?",["Algeria","Nigeria","Kenya","Ghana"],"A","Algeria is Africa's largest country by area."),
 M("P7","Africa","Physical features","Medium","The Atlas Mountains are found in ______ Africa.",["North","West","East","Southern"],"A","The Atlas Mountains lie in north west Africa."),
 M("P7","Africa","Climate","Hard","Why does the Sahel suffer frequent droughts?",["It is near the sea","It receives low and unreliable rainfall","It has many rivers","It is mountainous"],"B","The Sahel borders the desert and gets little, unreliable rain.","cause_effect"),
 M("P7","Africa","Economic activities","Medium","Which country is a leading producer of cocoa in West Africa?",["Ghana","Egypt","Libya","Somalia"],"A","Ghana is a major cocoa producer."),
 M("P7","Africa","Population","Hard","Why are river valleys such as the Nile Valley densely populated?",["Water for farming and settlement","Cold weather","No soil","Many mountains"],"A","Reliable water supports farming and dense settlement.","cause_effect"),
 M("P7","Africa","Independence","Medium","Most African countries gained independence during which period?",["1600s","1700s","1950s and 1960s","2000s"],"C","The wave of African independence came in the 1950s and 1960s."),
 P("P7","Civics","Arms of government","Hard","Match each arm of government with its main work.",[["Legislature","Makes laws"],["Executive","Implements laws"],["Judiciary","Interprets laws"],["Electoral Commission","Organises elections"]],"Each body has a separate role, which prevents abuse of power."),
]

EXTRA = {"P4": P4, "P5": P5, "P6": P6, "P7": P7}
