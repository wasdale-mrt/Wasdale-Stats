"""
Which D4H tags mean what. Tag ids come from the discovery job (31 Oct 2026).

Each tag id is in ONE group. A new tag made in D4H later is "unknown":
it is left off the public pages, and the nightly log prints its name so
it can be added here.

Groups:
  TYPE        - Full Team / Limited / Alert
  ROOT_CAUSE  - why the team was called. Shown on the dashboard and map.
  PLACE       - where. Shown on the dashboard and map.
  TRAINING    - training topics. Not shown. The call-out still counts.
  PRIVATE     - injuries and medical conditions (casualty details).
                Never written to the public files.
  NOT_SHOWN   - kit, vehicles, aircraft, meetings and events.
"""

TYPE = {
    2217: "Full Team",
    2216: "Limited",
    2215: "Alert",
}

# Order matters: when a call-out has several root causes, the FIRST one
# in this list is its colour on the map. All of them still count in the
# root cause chart.
ROOT_CAUSE = {
    3096: "Body Recovery",
    4365: "Suicide",
    2993: "Medical Emergency",
    2594: "Injured",
    2590: "Crag Fast",
    2612: "Benighted",
    2290: "Lost",
    2292: "Missing",
    2291: "Overdue",
    3007: "Split from party",
    2609: "Adverse Weather",
    2301: "Equipment Failure",
    4200: "Unwell",
    2994: "Ambulance Assist",
    2299: "3rd party report (whistles, shouts, lights)",
    2996: "Assistance Requested",
}

PLACE = {
    2211: "Wastwater", 2212: "Screes", 2213: "Scafell Pike", 2218: "Kirk Fell",
    2219: "Great Gable", 2220: "Longlands Base", 2221: "Lingmell Beck Crossing",
    2295: "Greta Gill", 2296: "Corridor Route", 2297: "Wind Gap",
    2589: "Pikes Crag", 2592: "Skew Gill", 2593: "Broad Crag",
    2595: "Lower Screes Path", 2596: "Piers Gill Path", 2597: "Piers Gill Bed",
    2598: "Muncaster Castle", 2599: "Lingmell Col", 2600: "Stand Crag",
    2605: "Ennerdale", 2606: "Styhead", 2607: "Middleboot Knotts",
    2608: "Corney Fell", 2614: "Pillar", 2615: "Eskdale Valley",
    2616: "Langstrath", 2617: "Mickledore", 2618: "Brown Tongue",
    2619: "Upper Esk", 2620: "Little Narrowcove", 2621: "Hollow Stones",
    2622: "Broad Crag Col", 2623: "Ill Crag", 2624: "Quagrigg Moss",
    2626: "Scafell", 2627: "Black Sail Pass", 2628: "Gavel Neese",
    2629: "Blengdale", 2630: "Bow Fell", 2631: "Esk Pike", 2632: "Green Hole",
    2633: "Esk Hause", 2634: "Grains Gill", 2635: "Harter Fell",
    2637: "Middle Fell", 2638: "Broad Stand", 2639: "Green How",
    2640: "Slight Side", 2641: "Yewbarrow", 2642: "Red Pike", 2643: "Haycock",
    2644: "Lingmell", 2645: "Great End", 2646: "Beck Head", 2647: "Whin Rigg",
    2648: "Illgill Head", 2649: "Knotts of the Tongue", 2650: "Hare Crag",
    2651: "Burnmoor Tarn", 2652: "Sour Milk Gill", 2653: "St Bees",
    2654: "Calf Cove", 2655: "Silver How", 2656: "Gosforth",
    2657: "Wellington", 2658: "Wasdale YHA", 2659: "Hardknott",
    2660: "Great Moss", 2661: "Cam Spout", 2662: "Braystones",
    2663: "Stanley Gill", 2664: "Trough House Bridge", 2665: "Black Crag",
    2666: "Mosedale", 2667: "Moasdale", 2668: "Lambfoot Dub",
    2669: "Brantrake", 2670: "Dent Fell", 2716: "Netherbeck",
    2717: "Castle Park", 2995: "Tongue Pots", 3017: "Foxes Tarn",
    3055: "Buckbarrow", 3098: "Lords Rake", 3099: "Red Gill",
    3199: "Blea Tarn", 3203: "Straight Gill", 3243: "Seatallan",
    3587: "Wasdale Valley", 3594: "Devoke Water", 3613: "Lower Esk",
    3617: "Horn Crag", 3631: "Scafell Pike (3 Peakers)", 3781: "Ritson Falls",
    4136: "Egremont", 4137: "Whitehaven", 4167: "Rakehead Crag",
    4197: "Rough Crag", 4199: "Miterdale", 4243: "Bursting Knotts",
    4244: "Great Hall Gill", 4247: "Broadcrag Tarn",
    4351: "Tourist Path (Lower)", 4352: "Mickledore Path Split",
    4353: "Lund Bridge", 4366: "Bengarth", 4370: "Mecklin Woods",
    4410: "Birker Fell", 4652: "Gable Beck", 4653: "Ill Gill", 4788: "Pen",
    4795: "Overbeck (Lower)", 4796: "Overbeck (Upper)", 4808: "Dore Head",
    4823: "Dent", 4824: "Flat Fell", 4940: "Great Lad Crag",
    4995: "Lowther Forest", 5115: "Kern Knotts", 5185: "Scoat Fell",
}

# Swiftwater and rope course topics, plus "Swiftwater Training".
TRAINING = set(range(3060, 3096)) | {2673}

# Injuries and medical conditions: casualty details. Never made public.
PRIVATE = (
    {2288, 2289, 2293, 2294, 2303, 2305, 2591, 2602, 2611, 2613,
     2998, 2999, 3162, 3598}
    | set(range(2563, 2589))
)

NOT_SHOWN = {
    # meetings and events
    2234, 2235, 2236, 2237, 2529, 2530, 3000, 3001, 3002, 3003, 3004,
    3005, 3006, 3244, 3599, 3600, 3601,
    # kit, vehicles, aircraft, drone, boat
    2704, 2705, 2706, 2707, 2708, 2709, 2710, 2711, 2712, 2713, 5187,
    2793, 3010, 3011, 3012, 3013, 3014, 3015, 3016, 3171, 5108, 3100,
    3102, 3103, 3104, 3105, 3106, 3158,
}


def group_of(tag_id):
    if tag_id in TYPE:
        return "type"
    if tag_id in ROOT_CAUSE:
        return "cause"
    if tag_id in PLACE:
        return "place"
    if tag_id in TRAINING:
        return "training"
    if tag_id in PRIVATE:
        return "private"
    if tag_id in NOT_SHOWN:
        return "not_shown"
    return "unknown"
