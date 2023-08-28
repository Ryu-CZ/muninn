# place functions here until they fit into any other group or new group emerges
import spacy


def main():
    long_text = "I am Valji Snoreshort and I am 25 years old. I am level 3 gnome warrior with short beard. My Equipment: " \
                "I use short sword with shield on melee combat. For a range combat I use short bow and arrows. As a " \
                "backup weapon I have common dagger. I am wearing common clothes.Over my clothes I wear padded armor, " \
                "chain-mail shirt, chain-mail trousers, hardened leather boots. My head is protected with plate helmet. I " \
                "own bed roll. I place rest of my adventurer equipment I put into my travelers backpack, it contains: 2 " \
                "unidentified magical scroll and basic adventurer supplies such as food, water, bottle of lamp oil, " \
                "tinder, flint, and and 2 torches."

    co_reference_help_text = "Valji is 25 years old and he is level 3 gnome warrior. He has a short sword."

    # conference_help_text = "The cats were startled by the dog as it growled at them."
    # noinspection SpellCheckingInspection
    core_ref_model = "en_coreference_web_trf"

    nlp = spacy.load("en_core_web_md")
    nlp_coref = spacy.load(core_ref_model)
    # replace span to keep head(highest rank core of span) of span
    nlp_coref.replace_listeners("transformer", "coref", ["model.tok2vec"])
    nlp_coref.replace_listeners("transformer", "span_resolver", ["model.tok2vec"])

    nlp.add_pipe("coref", source=nlp_coref)
    nlp.add_pipe("span_resolver", source=nlp_coref)
    print("loaded nlps")

    doc = nlp(co_reference_help_text)
    print("doc analyzed")
    print(doc.text)
    print(doc.spans)

    print(doc.spans["coref_head_clusters_1"][1].root)
    print(doc.spans["coref_head_clusters_1"][1].root.sent)


if __name__ == "__main__":
    main()
