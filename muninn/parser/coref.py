# place functions here until they fit into any other group or new group emerges
import spacy

conference_help_text = ("""My name is Valji Snoreshort. I am 25 years old. I am level 3 gnome warrior with short beard. 

My Equipment:I use short sword with shield on melee combat. For a range combat I use short bow and arrows. As a backup weapon I have common dagger. I am wearing common clothes.Over my clothes I wear padded armor, chain-mail shirt, chain-mail trousers, hardened leather boots. My head is protected with plate helmet. I own bed roll. I place rest of my adventurer equipment I put into my travelers backpack, it contains: 2 unidentified magical scroll and basic adventurer supplies such as food, water, bottle of lamp oil, tinder, flint, and and 2 torches. 
""")
# conference_help_text = "The cats were startled by the dog as it growled at them."

# noinspection SpellCheckingInspection
nlp = spacy.load("en_coreference_web_trf")
print("loaded nlp")

doc = nlp(conference_help_text)
print("doc analyzed")
print(doc.text)
print(doc.spans)
