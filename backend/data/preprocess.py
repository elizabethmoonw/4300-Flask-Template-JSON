import numpy as np
import pandas as pd
import os
import re
from rake_nltk import Rake
from sentence_transformers import SentenceTransformer, util

BASE_DIR = os.path.abspath(".")
DATASET_DIR = os.path.join(BASE_DIR, "data")

# # [TODO] REPLACE WITH FULL SET
df = pd.read_csv(os.path.join(DATASET_DIR, "test.csv"))


def clean_ingredients(data, normalization_map=None):
    """
    Removes rows from df based on specific non-ingredient phrases,
    non-ingredient keywords, or na values, and normalizes ingredient names.
    ----------
    data : DataFrame
        Input df containing 'ingredients' column.
    normalization_map : dict
        A dictionary mapping synonymous ingredient to a standardized form.
    Returns
    -------
    DataFrame
        The cleaned and normalized DataFrame.
    """
    non_ingredient_phrases = [
        "this brand is excluded from most ulta beauty coupons",
        "are subject to change at the manufacturer's discretion. for the most complete and up-to-date information\", refer to the product packaging",
    ]
    non_ingredient_words = {
        "active",
        "inactive",
        "ingredients",
        "may contain",
        "shimmer",
        "matte",
        "sunscreen",
        "emollient",
        # "fair",
        # "neutral",
    }

    if normalization_map is None:
        normalization_map = {
            "aqua": "water",
            "eau": "water",
            "vitamin c": "citric acid",
        }

    normalization_map = {k.lower(): v.lower() for k, v in normalization_map.items()}
    data = data.dropna(subset=["ingredients"])

    for phrase in non_ingredient_phrases:
        data = data[~data["ingredients"].str.contains(phrase, case=False, na=False)]

    def process_ingredients(text):
        text = text.lower()
        for word in non_ingredient_words:
            text = re.sub(r"\b" + word + r"\b", "", text)
        tokens = [token.strip() for token in text.split(",") if token.strip()]
        processed_tokens = [normalization_map.get(token, token) for token in tokens]
        return ", ".join(sorted(set(processed_tokens), key=processed_tokens.index))

    data["ingredients"] = data["ingredients"].apply(process_ingredients)
    return data


def tokenize(text):
    """
    Tokenizes ingredients string into a list of ingredients.
    ----------
    text : str
        The input text string
    Returns
    -------
    list
         A list of tokenized ingredients.
    """
    cleaned_str = re.sub(r"\([^)]*\)|\d+(\.\d+)?%|[\\/:]|^[. ]+|[. ]+$", " ", text)
    cleaned_str = re.sub(r"\s+", " ", cleaned_str).lower().strip()

    tokens = [ing.strip().lower() for ing in cleaned_str.split(",") if ing.strip()]

    return tokens


def extract_keywords(s: str):
    r = Rake()
    r.extract_keywords_from_text(s)
    rankedList = r.get_ranked_phrases_with_scores()
    keywordList = [keyword[1] for keyword in rankedList]
    return keywordList


def best_tags(tags: list[str], review_keywords: list[list[str]]):
    keywords = [x for r in review_keywords for x in r]
    model = SentenceTransformer("all-MiniLM-L6-v2")
    tag_embeddings = model.encode(tags)
    review_embeddings = model.encode(keywords)
    best = set()
    for tag, tag_embed in zip(tags, tag_embeddings):
        for rev_embed in review_embeddings:
            sim = util.pytorch_cos_sim(tag_embed, rev_embed)
            if sim > 0.7:
                best.add(tag)
    return best


makeup_attributes = [
    "matte",
    "drying",
    "glossy",
    "acne-causing",
    "hydrating",
    "long-lasting",
    "smudge-proof",
    "waterproof",
    "sheer",
    "full-coverage",
    "medium coverage",
    "sheer",
    "buildable",
    "shimmery",
    "sparkling",
    "creamy",
    "oil-free",
    "lightweight",
    "heavy",
    "caking",
    "flaky",
    "blendable",
    "opaque",
    "translucent",
    "volumizing",
    "lengthening",
    "clumping",
    "curling",
    "non-comedogenic",
    "hypoallergenic",
    "scented",
    "unscented",
    "moisturizing",
    "dewy",
    "satin",
    "luminous",
    "glittery",
    "brightening",
    "fading",
    "tinted",
    "pigmented",
    "natural",
    "synthetic",
    "vegan",
    "cruelty-free",
    "eco-friendly",
    "renewable",
    "biodegradable",
    "non-toxic",
    "antioxidant-rich",
    "age-defying",
    "soothing",
    "tightening",
    "pore-minimizing",
    "fragrance-free",
    "allergy-tested",
    "non-irritating",
    "therapeutic",
    "medicated",
    "exfoliating",
    "color-correcting",
    "broad-spectrum",
    "nourishing",
    "repairing",
    "rejuvenating",
    "invigorating",
    "fortifying",
    "refreshing",
    "perfumed",
    "soft-focus",
    "illuminating",
    "blurring",
    "antibacterial",
    "antifungal",
    "mineral-based",
    "organic",
    "chemical-free",
    "paraben-free",
    "silicone-free",
    "gluten-free",
    "alcohol-free",
    "collagen-boosting",
    "elasticizing",
    "plumping",
    "lifting",
    "firming",
    "budge-proof",
    "streak-free",
    "non-greasy",
    "foaming",
    "reflective",
    "multi-dimensional",
    "high-shine",
    "subtle",
    "vivid",
    "bold",
    "pastel",
    "neon",
    "metallic",
    "frosted",
    "velvety",
    "buttery",
    "chalky",
    "mousse",
    "gel",
    "liquid",
    "powder",
    "balmy",
    "staining",
    "whipped",
    "airbrushed",
    "HD",
    "radiant",
    "invisible",
    "light-reflecting",
    "color-rich",
    "fade-resistant",
    "heat-resistant",
    "cold-resistant",
    "humidity-resistant",
    "breakout-proof",
    "blemish-hiding",
    "wrinkle-concealing",
    "redness-reducing",
    "pH-balancing",
    "contouring",
    "highlighting",
    "iridescent",
    "holographic",
    "thermal",
    "seasonal",
    "limited edition",
    "luxurious",
    "budget-friendly",
    "economical",
    "expensive",
    "cheap",
    "professional-grade",
    "beginner-friendly",
    "quick-drying",
    "slow-drying",
    "hypoallergenic",
    "non-carcinogenic",
    "reusable",
    "disposable",
    "multi-use",
    "single-use",
    "compact",
    "travel-sized",
    "full-sized",
    "refillable",
    "non-refillable",
    "customizable",
    "standard",
    "classic",
    "modern",
    "retro",
    "trendy",
    "fashionable",
    "outdated",
    "timeless",
    "seasonal",
    "multi-purpose",
    "specialty",
    "enhancing",
    "protective",
    "sealing",
    "primer",
    "second-skin",
    "breathable",
    "non-porous",
]

desc_only_attributes = ["SPF"]

mac_revs = [
    """MAC Studio Fix Powder Plus Foundation is a one-step pressed powder and foundation makeup that gives skin a 12-hour ultra-matte finish while controlling shine and without causing acne. Benefits
Powder and foundation, in one ultra-matte makeup
Medium-to-full correcting coverage, natural finish
Subtly blurs redness and imperfections
For all skin types, especially oily skin
Controls oil and shine, 8 hours
Immediately reduces appearance of pores
Provides stay-true color, 12 hours
Does not cause acne
Non-streaking/non-caking/non-settling, 12 hours
Sweat and humidity-resistant
Photo-friendly
Formulated Without
Phthalates
Paraben
Retinyl Palmitate
Mineral Oil
Petrolatum
Formaldehyde
Polyethylene
Hydroquinone
Triclosan
Coal Tar
Toluene
Lauryl Sulfate
Laureth Sulfate
Gluten""",
    "I'm 52 and have aging skin leaning combo-oily. This is probably the 5th or so power foundation I've tried. My typical routine is a tinted sunscreen with SPF30 and then this over the top for light to medium coverage.",
    "I've bought this powder since 2013 I'm 25 lol this has been my Ride or Die! I use a lighter shade to cut my bronzer and blush! Chefs kiss. Make sure to moisturize well if you have dry skin! Can accentuate texture",
    "I had to return and exchange. When I got outside the store the shade was to light. Check against natural light before buying.",
    "I keep coming back to this foundation. I apply with a kabuki brush to get just the right coverage. Coverage is terrible with the included sponge, but can work for touch ups. If you want to hide redness or uneven skintones, this does the job. As with any powder or matte finish makeup, you have to be careful around fine lines and wrinkles. Too much application, and it will make them stand out. I use a primer and setting spray, and this lasts most of the day with possibly a touch up here and there if I'm having a more active day. My skin is combination, my nose especially can get oily. Blotting every once in awhile helps. No makeup can stop your skin from getting oily as the sebum is produced under your skin then works it way out. This does however prevent shine for some time, and you get no shine if you blot. If you want pore coverage, this works. however similar to lines and wrinkles, apply lightly first if you have large pores. That way the makeup doesn't settle into them making it look worse.",
    "I love this product and for a long time I keep looking so I can purchase c8 and ulta never has it like it's not sold out either they need to carry that shade! We need to have all shades and options",
    'For the price, MAC should be using better quality ingredients. This product is loaded with ingredients that are harmful AND the cause of breakouts\u00e2\u0080\u00a6.talc, mica, titanium dioxide, etc. And they have the nerve to call these "clean ingredients".',
    "I purchased the shade NC10 (I am very fair skinned and always have trouble finding a shade to match my skin tone) and it was perfect!!! I have found that you get more coverage using the sponge that comes with it. And honestly, I was surprised at how much coverage it gives! My routine is to use the sponge that comes in the packaging first for the most coverage and then go over with a big fluffy brush. It smooths things out and gives a little extra coverage. This looks beautiful on my dry skin and lasts all day long. I was hesitant to buy this because usually powders don't do well with my dry skin. However, it looks really great!! (I use a primer before applying too) Definitely recommend! While not cheap, also reasonably priced I feel, and think it would last a while!",
    "I have pretty good skin that's slightly oily. I haven't used any other product for 15 years. I just love the light natural look coverage. When I got my new order of N5, I put it on my face and it was orange! At first I thought, did I get pasty with age. lol Then I compared it with the other N5 I was running out of. There is a big difference in color! Where is the quality control MAC? When I tried to let them know about the issue, they didn't seem to care. Someone else had the same issue on the MAC page. For now I'm going to try something new and maybe come back to MAC after this batch has had time to work itself out. *The color in the left is the new one I just received.",
    "I've been using MAC Studio Fix since 2000. My son is a makeup artist and he recommended it to me and I've been using it ever since because it is such a good product. It's especially good for older women's skin. It glides on easily and it lasts. I never have to touch up when I'm out. Studio Fix doesn't gravitate into my wrinkles either. They don't recommend using power as you get older because most powers go into the wrinkles. But not Studio Fix. It's a nice makeup that doesn't act like most makeup.",
    "I usually don't use powder foundations but I use this a lot! It's perfect. Covers everything: dark spots, pores, acne, red spots, stuff like that. You only need 1 or 2 layers and you are good to go. I highly highly recommend and I will get this again!!!",
    "Haven't used this powder for over 20 years, don't know why I ever stopped. I've had liquid foundation that showed my lines and pores way worse than what this does. Used a primer first then this and my face looks amazing. At 54, super happy wth the coverage. Make sure 2 moisturize 1st if have dry skin like me",
    "I bought this in hopes of simplifying my morning makeup routine to save me time. I have a full time job, a part time job on the weekends, and I go to school part time. I wake up at 5 30am and start putting my makeup on by 6. Usually, I am a do it all makeup person because I like to feel put together for the day. However, I feel that liquid foundation just takes too long that early in the morning with having to blend then add concealer and set everything then go through many other steps to create a full face. It's just too time consuming for how tired I am! So I tried buying bareminerals original foundation, but I found that, that was taking just as much time because it takes forever to build that product up to medium coverage. I have some redness so I need more than sheer coverage. So I was watching youtuber Shelby Wilson who does many powder foundation looks because of the convenience factor, and one of the top powder foundations she recommended was MAC studio fix. So I took a guess at my shade online and bought it. OMG. This has made my life so much easier in the morning!! After letting my moisturizer sink in, I started to buff this onto my face and it was so easy and fast!!! It looks amazing!! Not sure if my shade is spot on, I may go a shade darker, but as for the product itself... truly amazing.",
    "I used to use the perfectly real powder foundation from clinique that was absolutley perfect until they discontinued it. That left me looking for a powder that was either just as good or better. Unfortunately this one did not work and i dont get all of the good reviews. I have combo skin so powders are usually better, especially if you use a tinted moisturizer and then set with this. But i was wrong and i tried for months with this powder but it just goes on too matte and makes you look flat, then the powder gets on your clothes, and soon after it starts to crease and run in florida humidity. I cant wear it for more than a couple of hours without it going bad. Literally i might as well go out bare faced as even that would be better than oily creasing foundation streaks. This makes me look like my face is so extremely oily when i have combo skin. In literally just an hour outside if you scratch your face, EVEN GENTLY, the makeup will be all over your nails. I even would try touching it up throughout the day but it just ends up being a mess of gooey powder and cakey-ness. It would be better to remove the powder and just redo all of your makeup. I also tried using blotting sheets with it but was no use as the powder would wipe off when that does not happen with other brands. Not to mention i have to blot multiple times. Overall i will not buy this again and if you want to take your chances, good luck.",
    'I thought I would never get powder foundation to work for me and my 57 year old post menopausal skin. I never had to wear makeup ever, but after the big "M" that all changed. For my dry skin gals, make sure you do a heavy moisturizer, let sit, then try the elf poreless putty primer or luminating primer. Depending on the look I want, if you want your face to have a nice glow go with the illuminating. Trust me on this, I have purchased so many powder foundations because after never needing, the thought of a heavy mask of makeup really depressed me. I finally tried this way and it worked! You need to find what really works underneath for your skin!! That\\\'s the key!! This powder is the best!! Skin prep is a must before application!!',
    "I absolutely love this foundation! I have tried so many foundations from high end to drugstore and I mean everything! My skin is dry and most foundations I've tried separate on my dry skin. I have recently been using a combo that I make myself of tarte, L'Or\u00c3\u00a9al, and Bare minerals powder foundations ( I combined equal parts in a jar and it worked well for me but it was getting pricey) so I took a leap and decided to try this foundation and I am so glad I did! It covers my redness and lasts all day with no separation or drying and it's so fast to apply! I can't say enough good things about this foundation!",
    "I'm new to MAC foundations and MAC powders. Got shade matched for this winter season and was told by my MAC artist to go a shade darker from my foundation when setting it down with this powder. She was right! Sits super well on top of my foundation. Blurs my pores and keeps my redness at bay. Doesn't flake on my very dry skin. I totally recommend this for anyone who suffers from dry skin patches in the winter.",
    "I used this foundation for 2 weeks, I loved the finish, it made my skin look flawless. but after the 2nd use I started feeling bad breakouts along my face ( I never get breakouts) . at first I thought it was my period. until I noticed after a day of using this foundation my skin increasingly got worse and FAST. I had horrible cystic acne along the sides of my face. it took 2-3 weeks for my face to go back to being clear. So sad.( I also cleaned my face thoroughly after wearing this makeup)",
    "I have oily skin at 37 years old. Liquid foundations have started to show my pores alot and oxidize. But this MAC powder foundation has stayed true. Coverage is easily buildable, all the way to full. Lasts all day. I use it with MAC primer. I have cried in this makeup and it lasted. I even got baptised in this makeup and came out looking fresh!",
    "Thought I HATED powder foundation but this came up on the 21 days of beauty and I decided to give it a try. Game changer. I was shook at how well it paired with my Smashbox primer to create a flawless application. No sinking into the pools. Felt lightweight on my face all day. Best part was it not melting off or getting patchy in the Texas heat and humidity. Stayed on through an hour of hauling heavy boxes around and lasted all day. I'm hooked.",
    "I really like this foundation. I only use foundation to cover my rosacea and this does a great job. It's compact, easy to apply, buildable, and excellent coverage. I also like that it's matte and not shiny and it doesn't rub off or run when I'm sweating. The product lasts me about 3 months too, so that's a plus!",
]

print(best_tags(makeup_attributes, [extract_keywords(rev) for rev in mac_revs]))


# df_cleaned = clean_ingredients(df)
# df_cleaned["tokenized_ingredients"] = df_cleaned.apply(
#     lambda x: tokenize(x["ingredients"]) if pd.notnull(x["ingredients"]) else [], axis=1
# )
# df_cleaned["product_index"] = df_cleaned.index

# df_cleaned.to_json(os.path.join(DATASET_DIR, "clean_dataset.json"), orient="records")
