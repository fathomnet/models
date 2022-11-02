import json
from os import PathLike
import urllib.parse
import requests
import enum
from typing import List, Dict

# Formats organism identifications into the classes used for the MATE 2022 ML Challenge.
# Peyton Lee, 5/19/22
# Underwater Remotely Operated Vehicles Team (UWROV) at the University of Washington


class OrganismClass(enum.Enum):
    """ Enum representing the possible classifications for organisms in the MATE 2022 ML
    Challenge Spec.

    Use `.value` to get the string representation (e.g., `ANNELIDA` > 'annelida').

    The classes are:
    - `ANNELIDA`
    - `ARTHROPODA`
    - `CNIDARIA`
    - `ECHINODERMATA`
    - `MOLLUSCA`
    - `PORIFERA`
    - `OTHER_INVERTEBRATES`
    - `VERTEBRATES_FISHES`
    - `UNIDENTIFIED`
    """
    ANNELIDA = "annelida"
    ARTHROPODA = "arthropoda"
    CNIDARIA = "cnidaria"
    ECHINODERMATA = "echinodermata"
    MOLLUSCA = "mollusca"
    PORIFERA = "porifera"
    OTHER_INVERTEBRATES = "other-invertebrates"
    VERTEBRATES_FISHES = "fish"
    UNIDENTIFIED = "unidentified-biology"

    @classmethod
    def from_string(cls, class_name: str) -> "OrganismClass":
        """Returns the matching OrganismClass for a given `class_name` string value."""
        return cls(class_name)

    @classmethod
    def list_values(cls) -> List[str]:
        """Returns the list of string values for all OrganismClass classes."""
        ret = []
        for class_enum in list(cls):
            ret.append(class_enum.value)
        return ret


def get_aphia_id_from_concept(concept_name: str) -> int or None:
    """ Queries the WoRMS Database to find a matching Aphia ID for the highest level of taxonomic
    information in the provided `concept_name`.

    Removes characters after any trailing whitespace or slashes and ignores non-capitalized concepts.
    (This means that this lookup is lossy and should ONLY be used if concepts are expected to be at or
    below the highest level of taxonomic information necessary.)

    Returns:
    - The `int` AphiaID of the highest taxonomic level in the `concept_name`.
    - `None` if no match is found.
    """

    # Additional formatting to get only highest level of taxonomic information (ignores trailing ' sp.', etc.)
    formatted_name = concept_name.split(" ")[0]
    formatted_name = formatted_name.split("/")[0]
    formatted_name = formatted_name.capitalize()

    parsed_name = urllib.parse.quote(formatted_name)
    url = "https://www.marinespecies.org/rest/AphiaIDByName/" + parsed_name
    response = requests.get(url)
    if (response.status_code == 200):  # Successful match
        return response.json()
    elif (response.status_code == 206):
        # Multiple matches, so get the first accepted ID if one exists.
        url = "https://www.marinespecies.org/rest/AphiaRecordsByName/" + parsed_name
        response = requests.get(url)

        if (response.status_code == 200):  # Successful
            for record in response.json():
                if record["status"] == "accepted":
                    return record["AphiaID"]
            return response.json()[0]["AphiaID"]
    else:
        return None


def get_record_from_aphia_id(aphia_id: int) -> object or None:
    """ Gets the matching Aphia Record for the provided AphiaID (`aphia_id`) from WoRMS, as returned
    by the `rest/AphiaRecordByAphiaID/` operation. See
    [the WoRMS documentation](https://www.marinespecies.org/rest/) for more details.

    Returns:
    - A JSON object representing the AphiaRecord.
    - `None` if no such record was found.
    """
    url = "https://www.marinespecies.org/rest/AphiaRecordByAphiaID/{}".format(
        aphia_id)
    response = requests.get(url)
    if response.status_code == 200:  # Successful
        return response.json()
    else:
        return None


def class_from_record(aphia_record: object) -> OrganismClass:
    """Returns the classification of an organism using its AphiaRecord.

    Sorts the classification into one of the 9 OrganismClass classes.

    Returns:
    - The matching classification of the organism if it falls into phyla Annelida, Arthropoda,
    Cnidaria, Echinodermata, Mollusca, Porifera.
    - `OrganismClass.VERTEBRATES_FISHES` if it is a fish (within Agnatha, Chondrichthyes, or
    Osteichthyes).
    - `OrganismClass.UNIDENTIFIED` if it is a non-fish vertebrate (e.g. mammals, amphibians) or a
    non-animal organism.
    - `OrganismClass.OTHER_INVERTEBRATES` if it is an invertebrate chordate
    (Tunicata or Cephalochordata) or any other animal phyla.
    """

    if aphia_record["kingdom"] != "Animalia":
        # Non-animal classifications should be treated as unidentified.
        return OrganismClass.UNIDENTIFIED

    phylum_to_class = {
        "Annelida": OrganismClass.ANNELIDA,
        "Arthropoda": OrganismClass.ARTHROPODA,
        "Cnidaria": OrganismClass.CNIDARIA,
        "Echinodermata": OrganismClass.ECHINODERMATA,
        "Mollusca": OrganismClass.MOLLUSCA,
        "Porifera": OrganismClass.PORIFERA
    }

    if aphia_record["phylum"] in phylum_to_class:  # Easily matched!
        return phylum_to_class[aphia_record["phylum"]]

    # Organism is other, fish, or unidentified.
    if aphia_record["phylum"] == "Chordata":
        # Check if class is either in subphylum Tunicata (tunicates) or
        # Cephalochordata (lancelets). Unforunately the AphiaRecord doesn't give us subphylum
        # so we'll have to go a step further and check classes.
        tunicata_classes = ["Appendicularia", "Ascidiacea",
                            "Larvacea", "Sorberacea", "Thaliacea"]
        cephalochordate_classes = ["Leptocardii"]

        if aphia_record["class"] in tunicata_classes or aphia_record["class"] in cephalochordate_classes:
            return OrganismClass.OTHER_INVERTEBRATES

        # We'll also check to make sure our organism is *actually* a fish!
        fish_classes = ["Actinopteri", "Cladistii", "Coelacanthi", "Dipneusti",
                        "Elasmobranchii", "Holocephali", "Myxini", "Pteromyzonti"]
        # We also add in a weird exception for Scorpaeniformes (scorpionfishes),
        # because they don't have a class.
        if aphia_record["class"] in fish_classes or aphia_record["order"] == "Scorpaeniformes":
            return OrganismClass.VERTEBRATES_FISHES

        # There's also labels in FathomNet for classifications like "Actinopterygii",
        # which technically would slip through these earlier checks. We'll do additional
        # checks for these names too.
        fish_categories = ["Agnatha", "Cyclostomi", "Gnathostomata",
                            "Chondrichthyes", "Osteichthyes", "Actinopterygii", "Sarcopterygii"]
        if aphia_record["scientificname"] in fish_categories:
            return OrganismClass.VERTEBRATES_FISHES

        # If we still can't find an organization, we'll go ahead and return it as unidentified.
        return OrganismClass.UNIDENTIFIED

    # Anything that's not a chordate is an invertebrate.
    return OrganismClass.OTHER_INVERTEBRATES


def lookup_concept_class(concept: str) -> str or None:
    """ Queries WoRMS to look up the corresponding classification label for a concept.

    Note: this makes multiple API calls and runs very slowly, 2-5 seconds per concept!

    Returns:
    - The corresponding string class label of the concept if a match was found.
    - `None` if no matching records were found in WoRMS.
    """
    aphia_id = get_aphia_id_from_concept(concept)
    if aphia_id:
        record = get_record_from_aphia_id(aphia_id)
        if record:
            return class_from_record(record).value
    return None

class ConceptDictionary:
    """Looks up and caches the matching OrganismClass for data concepts."""

    # Matches a string concept name to its string class, None if no match found in WoRMS
    concept_to_class: Dict[str, str or None]

    def __init__(self, dictionary: Dict[str, str or None]=None) -> None:
        """Initializes a new ConceptDictionary.

        Params:
        - `dictionary`: Optional object dictionary to preload values from.
        """
        if dictionary:
            # Naively set our own concept dictionary using the dictionary.
            # TODO: value check.
            self.concept_to_class = dictionary
        else:
            self.concept_to_class = {}

    @classmethod
    def load_from_json(cls, path: PathLike) -> "ConceptDictionary":
        """Loads a concept dictionary JSON from a file.
        
        JSON should be a dict from concept to class (OrganismClass), or none
        """
        with open(path, 'r') as fp:
            return ConceptDictionary(json.load(fp))

    def save_to_json(self, path: PathLike) -> None:
        """Saves this concept dictionary to a file in JSON format."""
        with open(path, 'w') as fp:
            json.dump(fp, self.concept_to_class, sort_keys=True, indent=4)

    def get_class(self, concept: str) -> str or None:
        """Gets the string class label for a concept.
        
        Returns:
        - The string class label (OrganismClass.value) if a match is found.
        - None if no match is found.
        """
        # Check for exact match
        if concept in self.concept_to_class and self.concept_to_class[concept]:
            return self.concept_to_class[concept]

        # Check if concept exists when cropped
        formatted_concept = concept.split(" ")[0]
        formatted_concept = formatted_concept.split("/")[0]
        if formatted_concept in self.concept_to_class and self.concept_to_class[formatted_concept]:
            return self.concept_to_class[formatted_concept]

        # No match found, so we do a lookup.
        org_class = lookup_concept_class(concept)

        # Store the results of the lookup.
        self.concept_to_class[concept] = org_class
        self.concept_to_class[formatted_concept] = org_class

        return org_class
