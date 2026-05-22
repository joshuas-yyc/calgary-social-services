"""
Seed real Calgary social services data.
Run: .venv/bin/python seed_real.py
"""
from app.database import init_db, db

# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------

ORGS = [
    {
        "name": "Calgary Drop-In Centre",
        "description": "24/7 emergency shelter, meals, health services, and housing support for adults experiencing homelessness.",
        "website": "https://www.calgarydropin.ca",
        "indigenous_led": False,
        "locations": [
            {
                "address": "1 Dermot Baldwin Way SE",
                "quadrant": "SE",
                "community": "East Village",
                "wheelchair_accessible": True,
                "contacts": [
                    {"kind": "phone", "value": "403-263-4303", "is_primary": True},
                    {"kind": "facebook", "value": "https://www.facebook.com/CalgaryDropIn"},
                    {"kind": "twitter", "value": "https://twitter.com/CalgaryDropIn"},
                ],
                "services": [
                    {
                        "name": "Emergency Overnight Shelter",
                        "description": "Safe overnight shelter for adults. Beds, meals, and basic hygiene provided. No reservation required.",
                        "category": "housing",
                        "cost_model": "free",
                        "access_mode": "walk_in",
                        "is_24_7": True,
                        "populations": ["Adults", "People Experiencing Homelessness"],
                    },
                    {
                        "name": "Day Program",
                        "description": "Drop-in daytime services: hot meals, showers, laundry, clothing, and access to case managers.",
                        "category": "poverty-reduction",
                        "cost_model": "free",
                        "access_mode": "walk_in",
                        "is_24_7": False,
                        "populations": ["Adults", "People Experiencing Homelessness"],
                    },
                    {
                        "name": "Housing Support Services",
                        "description": "Case management to help individuals transition out of shelter into stable housing.",
                        "category": "housing",
                        "cost_model": "free",
                        "access_mode": "referral",
                        "is_24_7": False,
                        "populations": ["Adults", "People Experiencing Homelessness"],
                    },
                ],
            }
        ],
    },
    {
        "name": "Alpha House Society",
        "description": "Provides detox, withdrawal management, and recovery support services for people struggling with addiction in Calgary.",
        "website": "https://www.alphahousecalgary.com",
        "indigenous_led": False,
        "locations": [
            {
                "address": "203 9 Ave SE",
                "quadrant": "SE",
                "community": "Downtown",
                "wheelchair_accessible": True,
                "contacts": [
                    {"kind": "phone", "value": "403-234-7388", "is_primary": True},
                    {"kind": "web", "value": "https://www.alphahousecalgary.com"},
                    {"kind": "facebook", "value": "https://www.facebook.com/AlphaHouseCalgary"},
                ],
                "services": [
                    {
                        "name": "Detox / Withdrawal Management",
                        "description": "Medical and social detox for adults dependent on alcohol or other substances. 24/7 intake.",
                        "category": "detox",
                        "cost_model": "free",
                        "access_mode": "walk_in",
                        "is_24_7": True,
                        "populations": ["Adults"],
                    },
                    {
                        "name": "DOAP Team (Downtown Outreach Addictions Partnership)",
                        "description": "Street-level outreach for people in active addiction, providing harm reduction supplies and connections to services.",
                        "category": "harm-reduction",
                        "cost_model": "free",
                        "access_mode": "walk_in",
                        "is_24_7": False,
                        "populations": ["Adults", "People Experiencing Homelessness"],
                    },
                ],
            }
        ],
    },
    {
        "name": "CUPS Calgary",
        "description": "Integrated health, education, housing, and social programs for low-income Calgarians, with a focus on breaking the cycle of poverty.",
        "website": "https://www.cupscalgary.ca",
        "indigenous_led": False,
        "locations": [
            {
                "address": "1001 10 Ave SW",
                "quadrant": "SW",
                "community": "Beltline",
                "wheelchair_accessible": True,
                "contacts": [
                    {"kind": "phone", "value": "403-221-8780", "is_primary": True},
                    {"kind": "web", "value": "https://www.cupscalgary.ca"},
                    {"kind": "facebook", "value": "https://www.facebook.com/cupscalgary"},
                    {"kind": "twitter", "value": "https://twitter.com/cupscalgary"},
                    {"kind": "instagram", "value": "https://www.instagram.com/cupscalgary"},
                ],
                "services": [
                    {
                        "name": "Primary Health Care",
                        "description": "Walk-in medical clinic serving low-income adults and families. GPs, nurses, and mental health counsellors on site.",
                        "category": "mental-health",
                        "cost_model": "free",
                        "access_mode": "walk_in",
                        "is_24_7": False,
                        "populations": ["Adults", "Families"],
                    },
                    {
                        "name": "Child Development Programs",
                        "description": "Early childhood education and family support for children 0-6 in vulnerable families.",
                        "category": "youth-services",
                        "cost_model": "free",
                        "access_mode": "referral",
                        "is_24_7": False,
                        "populations": ["Families", "Youth"],
                    },
                    {
                        "name": "Housing Stability Support",
                        "description": "Case management, landlord mediation, and financial assistance to help families maintain housing.",
                        "category": "housing",
                        "cost_model": "free",
                        "access_mode": "referral",
                        "is_24_7": False,
                        "populations": ["Adults", "Families"],
                    },
                ],
            }
        ],
    },
    {
        "name": "The Mustard Seed",
        "description": "Christian social services organization providing housing, food security, addictions recovery, and community for people experiencing poverty.",
        "website": "https://www.themustardseed.ca",
        "indigenous_led": False,
        "locations": [
            {
                "address": "102 11 Ave SE",
                "quadrant": "SE",
                "community": "Downtown",
                "wheelchair_accessible": True,
                "contacts": [
                    {"kind": "phone", "value": "403-269-1319", "is_primary": True},
                    {"kind": "web", "value": "https://www.themustardseed.ca"},
                    {"kind": "facebook", "value": "https://www.facebook.com/themustardseedcalgary"},
                    {"kind": "instagram", "value": "https://www.instagram.com/mustardseedcalgary"},
                ],
                "services": [
                    {
                        "name": "Emergency Food Bank",
                        "description": "Walk-in food hamper program for individuals and families. No appointment needed; ID required.",
                        "category": "poverty-reduction",
                        "cost_model": "free",
                        "access_mode": "walk_in",
                        "is_24_7": False,
                        "populations": ["Adults", "Families"],
                    },
                    {
                        "name": "Street Outreach",
                        "description": "Evening outreach to individuals experiencing homelessness — warm meals, supplies, and connection to shelter.",
                        "category": "poverty-reduction",
                        "cost_model": "free",
                        "access_mode": "walk_in",
                        "is_24_7": False,
                        "populations": ["Adults", "People Experiencing Homelessness"],
                    },
                    {
                        "name": "Recovery Community",
                        "description": "Peer-support recovery community with programming, mentorship, and sober social activities.",
                        "category": "recovery-community",
                        "cost_model": "free",
                        "access_mode": "walk_in",
                        "is_24_7": False,
                        "populations": ["Adults"],
                    },
                ],
            }
        ],
    },
    {
        "name": "Distress Centre Calgary",
        "description": "24/7 crisis intervention, emotional support, and suicide prevention via phone and chat. Also provides community information and referrals.",
        "website": "https://www.distresscentre.com",
        "indigenous_led": False,
        "locations": [
            {
                "address": "1716 16 Ave NW",
                "quadrant": "NW",
                "community": "Capitol Hill",
                "wheelchair_accessible": True,
                "contacts": [
                    {"kind": "crisis_line", "value": "403-266-4357", "is_primary": True},
                    {"kind": "phone", "value": "403-266-1605"},
                    {"kind": "web", "value": "https://www.distresscentre.com"},
                    {"kind": "facebook", "value": "https://www.facebook.com/DistressCentreCalgary"},
                    {"kind": "twitter", "value": "https://twitter.com/distresscentre"},
                ],
                "services": [
                    {
                        "name": "24/7 Crisis Line",
                        "description": "Confidential telephone crisis counselling available 24 hours a day, 7 days a week. Also available via online chat.",
                        "category": "crisis-services",
                        "cost_model": "free",
                        "access_mode": "walk_in",
                        "is_24_7": True,
                        "populations": ["Adults", "Youth"],
                    },
                    {
                        "name": "211 Alberta Helpline",
                        "description": "Free community resource referral service connecting Calgarians with social, health, and government services.",
                        "category": "crisis-services",
                        "cost_model": "free",
                        "access_mode": "walk_in",
                        "is_24_7": True,
                        "populations": ["Adults", "Families", "Youth", "Seniors"],
                    },
                ],
            }
        ],
    },
    {
        "name": "Inn from the Cold",
        "description": "Emergency shelter, transitional housing, and family support services for families and children experiencing homelessness.",
        "website": "https://www.innfromthecold.org",
        "indigenous_led": False,
        "locations": [
            {
                "address": "560 11 Ave SW",
                "quadrant": "SW",
                "community": "Beltline",
                "wheelchair_accessible": True,
                "contacts": [
                    {"kind": "phone", "value": "403-263-8384", "is_primary": True},
                    {"kind": "web", "value": "https://www.innfromthecold.org"},
                    {"kind": "facebook", "value": "https://www.facebook.com/InnFromTheCold"},
                    {"kind": "instagram", "value": "https://www.instagram.com/innfromthecold"},
                    {"kind": "twitter", "value": "https://twitter.com/InnFromTheCold"},
                ],
                "services": [
                    {
                        "name": "Family Emergency Shelter",
                        "description": "Emergency shelter for families with children experiencing homelessness. Families stay together in private rooms.",
                        "category": "housing",
                        "cost_model": "free",
                        "access_mode": "referral",
                        "is_24_7": True,
                        "populations": ["Families"],
                    },
                    {
                        "name": "Prevention and Diversion",
                        "description": "Financial assistance and case management to help families at risk of homelessness maintain their housing.",
                        "category": "housing",
                        "cost_model": "free",
                        "access_mode": "referral",
                        "is_24_7": False,
                        "populations": ["Families"],
                    },
                ],
            }
        ],
    },
    {
        "name": "Calgary Food Bank",
        "description": "Provides emergency food hampers and long-term food support to Calgarians in need. Distributes millions of pounds of food annually.",
        "website": "https://www.calgaryfoodbank.com",
        "indigenous_led": False,
        "locations": [
            {
                "address": "5000 11 St SE",
                "quadrant": "SE",
                "community": "Manchester",
                "wheelchair_accessible": True,
                "contacts": [
                    {"kind": "phone", "value": "403-253-2059", "is_primary": True},
                    {"kind": "web", "value": "https://www.calgaryfoodbank.com"},
                    {"kind": "facebook", "value": "https://www.facebook.com/CalgaryFoodBank"},
                    {"kind": "twitter", "value": "https://twitter.com/CalgaryFoodBank"},
                    {"kind": "instagram", "value": "https://www.instagram.com/calgaryfoodbank"},
                ],
                "services": [
                    {
                        "name": "Emergency Food Hamper",
                        "description": "Emergency food assistance for households in crisis. 4–7 days of food provided. Requires registration.",
                        "category": "poverty-reduction",
                        "cost_model": "free",
                        "access_mode": "appointment",
                        "is_24_7": False,
                        "populations": ["Adults", "Families", "Seniors"],
                    },
                ],
            }
        ],
    },
    {
        "name": "Wood's Homes",
        "description": "Child and youth mental health services including residential treatment, community outreach, crisis intervention, and family therapy.",
        "website": "https://www.woodshomes.ca",
        "indigenous_led": False,
        "locations": [
            {
                "address": "1104 16 Ave NW",
                "quadrant": "NW",
                "community": "Hounsfield Heights",
                "wheelchair_accessible": True,
                "contacts": [
                    {"kind": "phone", "value": "403-270-4102", "is_primary": True},
                    {"kind": "crisis_line", "value": "403-299-9699"},
                    {"kind": "web", "value": "https://www.woodshomes.ca"},
                    {"kind": "facebook", "value": "https://www.facebook.com/WoodsHomes"},
                    {"kind": "twitter", "value": "https://twitter.com/WoodsHomes"},
                    {"kind": "instagram", "value": "https://www.instagram.com/woodshomes"},
                ],
                "services": [
                    {
                        "name": "Youth Crisis Stabilization (Eastside)",
                        "description": "Walk-in crisis support for children and youth up to age 17. Available 24/7. No referral required.",
                        "category": "crisis-services",
                        "cost_model": "free",
                        "access_mode": "walk_in",
                        "is_24_7": True,
                        "age_max": 17,
                        "populations": ["Youth"],
                    },
                    {
                        "name": "Outpatient Mental Health – Youth",
                        "description": "Individual, group, and family counselling for youth with mental health and behavioural challenges.",
                        "category": "mental-health",
                        "cost_model": "free",
                        "access_mode": "referral",
                        "is_24_7": False,
                        "age_max": 17,
                        "populations": ["Youth", "Families"],
                    },
                ],
            }
        ],
    },
    {
        "name": "Calgary Counselling Centre",
        "description": "Professional counselling for individuals, couples, families, and youth. Sliding-scale fees based on income. No one turned away for inability to pay.",
        "website": "https://www.calgarycc.com",
        "indigenous_led": False,
        "locations": [
            {
                "address": "940 6 Ave SW",
                "quadrant": "SW",
                "community": "Downtown West End",
                "wheelchair_accessible": True,
                "contacts": [
                    {"kind": "phone", "value": "403-691-5991", "is_primary": True},
                    {"kind": "web", "value": "https://www.calgarycc.com"},
                    {"kind": "facebook", "value": "https://www.facebook.com/CalgaryCounsellingCentre"},
                    {"kind": "twitter", "value": "https://twitter.com/calgarycounsell"},
                    {"kind": "instagram", "value": "https://www.instagram.com/calgarycounsellingcentre"},
                ],
                "services": [
                    {
                        "name": "Individual Counselling",
                        "description": "One-on-one counselling for depression, anxiety, trauma, grief, and life transitions. Sliding-scale fees.",
                        "category": "mental-health",
                        "cost_model": "sliding_scale",
                        "access_mode": "appointment",
                        "is_24_7": False,
                        "populations": ["Adults"],
                    },
                    {
                        "name": "Couples Counselling",
                        "description": "Relationship counselling for couples navigating conflict, communication issues, or major life changes.",
                        "category": "mental-health",
                        "cost_model": "sliding_scale",
                        "access_mode": "appointment",
                        "is_24_7": False,
                        "populations": ["Adults"],
                    },
                    {
                        "name": "Youth Counselling",
                        "description": "Counselling for youth aged 10–17 dealing with anxiety, depression, family issues, or school challenges.",
                        "category": "mental-health",
                        "cost_model": "free",
                        "access_mode": "appointment",
                        "is_24_7": False,
                        "age_max": 17,
                        "populations": ["Youth"],
                    },
                ],
            }
        ],
    },
    {
        "name": "YWCA Calgary",
        "description": "Empowering women and their families with shelter, housing, counselling, and violence prevention programs.",
        "website": "https://www.ywcacalgary.com",
        "indigenous_led": False,
        "locations": [
            {
                "address": "320 5 Ave SE",
                "quadrant": "SE",
                "community": "Downtown",
                "wheelchair_accessible": True,
                "contacts": [
                    {"kind": "phone", "value": "403-263-1550", "is_primary": True},
                    {"kind": "crisis_line", "value": "403-263-1550"},
                    {"kind": "web", "value": "https://www.ywcacalgary.com"},
                    {"kind": "facebook", "value": "https://www.facebook.com/YWCACalgary"},
                    {"kind": "twitter", "value": "https://twitter.com/YWCACalgary"},
                    {"kind": "instagram", "value": "https://www.instagram.com/ywcacalgary"},
                ],
                "services": [
                    {
                        "name": "Emergency Shelter for Women",
                        "description": "Emergency shelter for women and their children fleeing domestic violence. 24/7 crisis intake.",
                        "category": "crisis-services",
                        "cost_model": "free",
                        "access_mode": "walk_in",
                        "is_24_7": True,
                        "gender_restriction": "women",
                        "populations": ["Women", "Families"],
                    },
                    {
                        "name": "Violence Prevention Counselling",
                        "description": "Individual and group counselling for women who have experienced domestic or sexual violence.",
                        "category": "mental-health",
                        "cost_model": "free",
                        "access_mode": "referral",
                        "is_24_7": False,
                        "gender_restriction": "women",
                        "populations": ["Women"],
                    },
                    {
                        "name": "Transitional Housing",
                        "description": "Supported transitional housing for women leaving abusive situations, with on-site support workers.",
                        "category": "housing",
                        "cost_model": "sliding_scale",
                        "access_mode": "referral",
                        "is_24_7": False,
                        "gender_restriction": "women",
                        "populations": ["Women", "Families"],
                    },
                ],
            }
        ],
    },
    {
        "name": "Kerby Centre",
        "description": "Services and programs for adults 55+ in Calgary: health, social connection, housing navigation, and crisis support for older adults.",
        "website": "https://www.kerbycentre.com",
        "indigenous_led": False,
        "locations": [
            {
                "address": "1133 7 Ave SW",
                "quadrant": "SW",
                "community": "Downtown West End",
                "wheelchair_accessible": True,
                "contacts": [
                    {"kind": "phone", "value": "403-265-0661", "is_primary": True},
                    {"kind": "crisis_line", "value": "403-265-0661"},
                    {"kind": "web", "value": "https://www.kerbycentre.com"},
                    {"kind": "facebook", "value": "https://www.facebook.com/KerbyCentre"},
                    {"kind": "twitter", "value": "https://twitter.com/KerbyCentre"},
                ],
                "services": [
                    {
                        "name": "Kerby Rotary Shelter",
                        "description": "Emergency shelter specifically for adults 55+. Provides overnight shelter, meals, and support services.",
                        "category": "housing",
                        "cost_model": "free",
                        "access_mode": "walk_in",
                        "is_24_7": True,
                        "age_min": 55,
                        "populations": ["Seniors", "People Experiencing Homelessness"],
                    },
                    {
                        "name": "Elder Abuse Response",
                        "description": "Crisis intervention and counselling for older adults experiencing abuse, neglect, or financial exploitation.",
                        "category": "crisis-services",
                        "cost_model": "free",
                        "access_mode": "walk_in",
                        "is_24_7": False,
                        "age_min": 55,
                        "populations": ["Seniors"],
                    },
                    {
                        "name": "Seniors Drop-In Programs",
                        "description": "Social programs, fitness classes, meals, and wellness activities for adults 55+.",
                        "category": "poverty-reduction",
                        "cost_model": "sliding_scale",
                        "access_mode": "walk_in",
                        "is_24_7": False,
                        "age_min": 55,
                        "populations": ["Seniors"],
                    },
                ],
            }
        ],
    },
    {
        "name": "Calgary Outlink",
        "description": "Support, resources, and community for LGBTQ2S+ individuals and their families in Calgary.",
        "website": "https://www.calgaryoutlink.ca",
        "indigenous_led": False,
        "locations": [
            {
                "address": "223 12 Ave SW",
                "quadrant": "SW",
                "community": "Beltline",
                "wheelchair_accessible": True,
                "contacts": [
                    {"kind": "phone", "value": "403-234-8973", "is_primary": True},
                    {"kind": "web", "value": "https://www.calgaryoutlink.ca"},
                    {"kind": "facebook", "value": "https://www.facebook.com/CalgaryOutlink"},
                    {"kind": "twitter", "value": "https://twitter.com/CalgaryOutlink"},
                    {"kind": "instagram", "value": "https://www.instagram.com/calgaryoutlink"},
                ],
                "services": [
                    {
                        "name": "LGBTQ2S+ Peer Support",
                        "description": "Drop-in peer support groups and one-on-one peer matching for LGBTQ2S+ youth and adults.",
                        "category": "mental-health",
                        "cost_model": "free",
                        "access_mode": "walk_in",
                        "is_24_7": False,
                        "populations": ["LGBTQ2S+", "Youth", "Adults"],
                    },
                    {
                        "name": "Information and Referrals",
                        "description": "Confidential phone and in-person information and referrals to LGBTQ2S+-affirming services across Calgary.",
                        "category": "crisis-services",
                        "cost_model": "free",
                        "access_mode": "walk_in",
                        "is_24_7": False,
                        "populations": ["LGBTQ2S+"],
                    },
                ],
            }
        ],
    },
    {
        "name": "Centre for Newcomers",
        "description": "Settlement services, employment programs, language training, and community integration for immigrants and refugees in Calgary.",
        "website": "https://www.centrefornewcomers.ca",
        "indigenous_led": False,
        "locations": [
            {
                "address": "4920 106 Ave SE",
                "quadrant": "SE",
                "community": "Forest Lawn",
                "wheelchair_accessible": True,
                "contacts": [
                    {"kind": "phone", "value": "403-569-3125", "is_primary": True},
                    {"kind": "web", "value": "https://www.centrefornewcomers.ca"},
                    {"kind": "facebook", "value": "https://www.facebook.com/CentreForNewcomers"},
                    {"kind": "twitter", "value": "https://twitter.com/C4Ncalgary"},
                    {"kind": "instagram", "value": "https://www.instagram.com/centrefornewcomers"},
                ],
                "services": [
                    {
                        "name": "Settlement and Orientation",
                        "description": "Initial settlement support for new immigrants and refugees: banking, housing, health care navigation, and school registration.",
                        "category": "newcomer-refugee",
                        "cost_model": "free",
                        "access_mode": "walk_in",
                        "is_24_7": False,
                        "populations": ["Newcomers / Refugees"],
                    },
                    {
                        "name": "Employment Services",
                        "description": "Resume writing, job search, interview preparation, and workplace skills training for newcomers.",
                        "category": "newcomer-refugee",
                        "cost_model": "free",
                        "access_mode": "walk_in",
                        "is_24_7": False,
                        "populations": ["Newcomers / Refugees", "Adults"],
                    },
                    {
                        "name": "Language Training (LINC)",
                        "description": "Free Language Instruction for Newcomers to Canada (LINC) English classes for eligible permanent residents and refugees.",
                        "category": "newcomer-refugee",
                        "cost_model": "free",
                        "access_mode": "appointment",
                        "is_24_7": False,
                        "populations": ["Newcomers / Refugees"],
                    },
                ],
            }
        ],
    },
    {
        "name": "Hull Services",
        "description": "Mental health, addictions, and complex needs services for vulnerable children, youth, and families across Calgary.",
        "website": "https://www.hullservices.ca",
        "indigenous_led": False,
        "locations": [
            {
                "address": "4825 Mt Royal Gate SW",
                "quadrant": "SW",
                "community": "Mount Royal",
                "wheelchair_accessible": True,
                "contacts": [
                    {"kind": "phone", "value": "403-242-6644", "is_primary": True},
                    {"kind": "web", "value": "https://www.hullservices.ca"},
                    {"kind": "facebook", "value": "https://www.facebook.com/HullServices"},
                    {"kind": "twitter", "value": "https://twitter.com/HullServices"},
                ],
                "services": [
                    {
                        "name": "Residential Treatment – Youth",
                        "description": "Structured residential treatment for youth with serious mental health challenges and complex behavioural needs.",
                        "category": "residential-inpatient",
                        "cost_model": "free",
                        "access_mode": "referral",
                        "is_24_7": True,
                        "age_max": 18,
                        "populations": ["Youth"],
                    },
                    {
                        "name": "Family Support Services",
                        "description": "In-home and community-based support for families at risk of child intervention involvement.",
                        "category": "mental-health",
                        "cost_model": "free",
                        "access_mode": "referral",
                        "is_24_7": False,
                        "populations": ["Families", "Youth"],
                    },
                ],
            }
        ],
    },
    {
        "name": "HIV Community Link",
        "description": "Support, education, and harm reduction services for people living with or affected by HIV in Southern Alberta.",
        "website": "https://www.hivcommunitylink.org",
        "indigenous_led": False,
        "locations": [
            {
                "address": "301 1011 10 Ave SW",
                "quadrant": "SW",
                "community": "Beltline",
                "wheelchair_accessible": True,
                "contacts": [
                    {"kind": "phone", "value": "403-228-0155", "is_primary": True},
                    {"kind": "web", "value": "https://www.hivcommunitylink.org"},
                    {"kind": "facebook", "value": "https://www.facebook.com/hivcommunitylink"},
                    {"kind": "twitter", "value": "https://twitter.com/HIVCommunityLnk"},
                    {"kind": "instagram", "value": "https://www.instagram.com/hivcommunitylink"},
                ],
                "services": [
                    {
                        "name": "Harm Reduction Supplies",
                        "description": "Free distribution of sterile needles, safer use supplies, and naloxone kits. No referral required.",
                        "category": "harm-reduction",
                        "cost_model": "free",
                        "access_mode": "walk_in",
                        "is_24_7": False,
                        "populations": ["Adults"],
                    },
                    {
                        "name": "HIV Support and Navigation",
                        "description": "Case management and peer support for people living with HIV. Help navigating treatment, housing, and benefits.",
                        "category": "mental-health",
                        "cost_model": "free",
                        "access_mode": "walk_in",
                        "is_24_7": False,
                        "populations": ["Adults"],
                    },
                ],
            }
        ],
    },
    {
        "name": "Elbow River Healing Lodge",
        "description": "Culturally grounded healing and wellness programs for Indigenous peoples in Calgary, integrating traditional healing practices with Western approaches.",
        "website": "https://www.natiivecentrecalgary.org",
        "indigenous_led": True,
        "locations": [
            {
                "address": "135 2 Ave SE",
                "quadrant": "SE",
                "community": "Downtown",
                "wheelchair_accessible": True,
                "contacts": [
                    {"kind": "phone", "value": "403-232-6400", "is_primary": True},
                    {"kind": "web", "value": "https://www.nativecalcalgary.org"},
                ],
                "services": [
                    {
                        "name": "Indigenous Healing Programs",
                        "description": "Traditional healing circles, ceremonies, Elder guidance, and land-based healing for Indigenous peoples experiencing addiction or trauma.",
                        "category": "indigenous-healing",
                        "cost_model": "free",
                        "access_mode": "walk_in",
                        "is_24_7": False,
                        "populations": ["Indigenous", "Adults"],
                    },
                    {
                        "name": "Cultural Supports and Navigation",
                        "description": "Help navigating urban services while maintaining cultural connections. Includes Indigenous social worker support.",
                        "category": "indigenous-services",
                        "cost_model": "free",
                        "access_mode": "walk_in",
                        "is_24_7": False,
                        "populations": ["Indigenous"],
                    },
                ],
            }
        ],
    },
    {
        "name": "Boys & Girls Clubs of Calgary",
        "description": "After-school programs, youth development, and summer camps for children and youth across Calgary.",
        "website": "https://www.bgccalgary.org",
        "indigenous_led": False,
        "locations": [
            {
                "address": "#200 1111 6 Ave SW",
                "quadrant": "SW",
                "community": "Downtown West End",
                "wheelchair_accessible": True,
                "contacts": [
                    {"kind": "phone", "value": "403-541-0550", "is_primary": True},
                    {"kind": "web", "value": "https://www.bgccalgary.org"},
                    {"kind": "facebook", "value": "https://www.facebook.com/BGCCalgary"},
                    {"kind": "instagram", "value": "https://www.instagram.com/bgccalgary"},
                    {"kind": "twitter", "value": "https://twitter.com/BGCCalgary"},
                ],
                "services": [
                    {
                        "name": "After-School Programs",
                        "description": "Safe, structured programming for youth after school — homework help, recreation, and mentorship.",
                        "category": "youth-services",
                        "cost_model": "sliding_scale",
                        "access_mode": "referral",
                        "is_24_7": False,
                        "age_max": 18,
                        "populations": ["Youth"],
                    },
                ],
            }
        ],
    },
]

# ---------------------------------------------------------------------------
# Loader
# ---------------------------------------------------------------------------

def get_category_id(conn, slug):
    row = conn.execute("SELECT id FROM categories WHERE slug=?", (slug,)).fetchone()
    return row["id"] if row else None


def get_population_id(conn, name):
    row = conn.execute("SELECT id FROM populations WHERE name=?", (name,)).fetchone()
    return row["id"] if row else None


def seed():
    init_db()
    with db() as conn:
        # Create a source record for this seed
        cur = conn.execute(
            """INSERT INTO sources(title, source_type, notes)
               VALUES(?, ?, ?)""",
            ("Public organizational websites / direct knowledge", "website",
             "Seed data compiled from public sources: org websites, 211 Alberta, City of Calgary directories."),
        )
        source_id = cur.lastrowid

        for org_data in ORGS:
            # Insert org
            cur = conn.execute(
                """INSERT INTO organizations(name, description, website, status, indigenous_led)
                   VALUES(?,?,?,?,?)""",
                (org_data["name"], org_data["description"], org_data.get("website"),
                 "active", 1 if org_data.get("indigenous_led") else 0),
            )
            org_id = cur.lastrowid
            conn.execute(
                """INSERT INTO edits(entity_type, entity_id, action, editor, reason)
                   VALUES('org',?,'create','seed','Initial real data seed')""",
                (org_id,),
            )

            for loc_data in org_data.get("locations", []):
                cur = conn.execute(
                    """INSERT INTO locations(organization_id, address, quadrant, community,
                       wheelchair_accessible, status)
                       VALUES(?,?,?,?,?,?)""",
                    (org_id, loc_data["address"], loc_data.get("quadrant"),
                     loc_data.get("community"),
                     1 if loc_data.get("wheelchair_accessible") else 0, "active"),
                )
                loc_id = cur.lastrowid

                for c in loc_data.get("contacts", []):
                    conn.execute(
                        "INSERT INTO contacts(owner_type, owner_id, kind, value, is_primary) VALUES(?,?,?,?,?)",
                        ("location", loc_id, c["kind"], c["value"], 1 if c.get("is_primary") else 0),
                    )
                    # Also attach primary phone/web/social to the org
                    if c.get("is_primary") or c["kind"] in ("facebook", "twitter", "instagram", "linkedin", "youtube", "tiktok"):
                        conn.execute(
                            "INSERT INTO contacts(owner_type, owner_id, kind, value, is_primary) VALUES(?,?,?,?,?)",
                            ("org", org_id, c["kind"], c["value"], 1 if c.get("is_primary") else 0),
                        )

                for svc_data in loc_data.get("services", []):
                    cat_id = get_category_id(conn, svc_data.get("category"))
                    cur = conn.execute(
                        """INSERT INTO services(location_id, name, description, primary_category_id,
                           cost_model, access_mode, referral_required, is_24_7, age_min, age_max,
                           gender_restriction, status, verified_at, verified_by)
                           VALUES(?,?,?,?,?,?,?,?,?,?,?,?,CURRENT_TIMESTAMP,'seed')""",
                        (loc_id, svc_data["name"], svc_data.get("description"), cat_id,
                         svc_data.get("cost_model", "unknown"),
                         svc_data.get("access_mode", "walk_in"),
                         1 if svc_data.get("access_mode") == "referral" else 0,
                         1 if svc_data.get("is_24_7") else 0,
                         svc_data.get("age_min"), svc_data.get("age_max"),
                         svc_data.get("gender_restriction", "none"),
                         "active"),
                    )
                    svc_id = cur.lastrowid

                    for pop_name in svc_data.get("populations", []):
                        pop_id = get_population_id(conn, pop_name)
                        if pop_id:
                            conn.execute(
                                "INSERT OR IGNORE INTO service_populations VALUES(?,?)", (svc_id, pop_id)
                            )
                    if cat_id:
                        conn.execute(
                            "INSERT OR IGNORE INTO service_categories VALUES(?,?)", (svc_id, cat_id)
                        )
                    conn.execute(
                        """INSERT INTO edits(entity_type, entity_id, action, editor, reason)
                           VALUES('service',?,'create','seed','Initial real data seed')""",
                        (svc_id,),
                    )

        print(f"Seeded {len(ORGS)} organizations.")


if __name__ == "__main__":
    seed()
