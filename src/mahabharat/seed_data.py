"""
Pre-seeded Mahabharata character graph.
This gives the system reliable, hand-verified entity relationships
from day one — merged with LLM-extracted data during build.

Sources: Mahabharata critical edition, standardized English names.
"""

SEED_ENTITIES = [
    # Kuru Lineage
    {"name": "Shantanu", "type": "character", "description": "King of Hastinapura, Kuru dynasty ancestor, married Ganga and Satyavati"},
    {"name": "Ganga", "type": "character", "description": "River goddess, first wife of Shantanu, mother of Bhishma"},
    {"name": "Satyavati", "type": "character", "description": "Second wife of Shantanu, mother of Chitragupta and Vichitravirya"},
    {"name": "Bhishma", "type": "character", "description": "Son of Shantanu and Ganga, took vow of celibacy (Bhishma Pratigya), commander of Kaurava forces"},
    {"name": "Chitragupta", "type": "character", "description": "Son of Shantanu and Satyavati, died young without heirs"},
    {"name": "Vichitravirya", "type": "character", "description": "Son of Shantanu and Satyavati, married Ambika and Ambalika"},
    {"name": "Ambika", "type": "character", "description": "Wife of Vichitravirya, mother of Dhritarashtra through Vyasa's niyoga"},
    {"name": "Ambalika", "type": "character", "description": "Wife of Vichitravirya, mother of Pandu through Vyasa's niyoga"},
    {"name": "Vyasa", "type": "character", "description": "Son of Satyavati and sage Parashara, author of Mahabharata, father of Dhritarashtra, Pandu, and Vidura"},

    # Kauravas
    {"name": "Dhritarashtra", "type": "character", "description": "Blind king of Hastinapura, father of the hundred Kauravas, married Gandhari"},
    {"name": "Gandhari", "type": "character", "description": "Princess of Gandhara, wife of Dhritarashtra, blindfolded herself out of devotion, mother of 100 Kauravas"},
    {"name": "Duryodhana", "type": "character", "description": "Eldest of the 100 Kauravas, primary antagonist, bitter rival of Pandavas"},
    {"name": "Dushasana", "type": "character", "description": "Second Kaurava, dragged Draupadi in court, killed by Bhima"},
    {"name": "Shakuni", "type": "character", "description": "Brother of Gandhari, uncle of Kauravas, master of dice, instigated the dice game"},

    # Pandavas
    {"name": "Pandu", "type": "character", "description": "King of Hastinapura, father of the five Pandavas, married Kunti and Madri, cursed to die on union with a woman"},
    {"name": "Kunti", "type": "character", "description": "First wife of Pandu, mother of Yudhishthira, Bhima, and Arjuna, also mother of Karna (before marriage)"},
    {"name": "Madri", "type": "character", "description": "Second wife of Pandu, mother of Nakula and Sahadeva (via Ashwini Kumaras), died on Pandu's funeral pyre"},
    {"name": "Yudhishthira", "type": "character", "description": "Eldest Pandava, son of Dharma (Yama), known for truth and righteousness, lost everything in dice game"},
    {"name": "Bhima", "type": "character", "description": "Second Pandava, son of Vayu, immense strength, killed Duryodhana, Dushasana, and Jarasandha"},
    {"name": "Arjuna", "type": "character", "description": "Third Pandava, son of Indra, greatest archer, recipient of Bhagavad Gita from Krishna"},
    {"name": "Nakula", "type": "character", "description": "Fourth Pandava, son of Ashwini Kumaras and Madri, known for beauty and skill with horses"},
    {"name": "Sahadeva", "type": "character", "description": "Fifth Pandava, son of Ashwini Kumaras and Madri, known for wisdom and astrology"},
    {"name": "Draupadi", "type": "character", "description": "Wife of all five Pandavas, daughter of Drupada, also called Panchali and Krishnaa, humiliated in the dice game"},

    # Krishna and Yadavas
    {"name": "Krishna", "type": "character", "description": "Avatar of Vishnu, Pandava ally and charioteer of Arjuna, delivered Bhagavad Gita, prince of Dwarka"},
    {"name": "Balarama", "type": "character", "description": "Elder brother of Krishna, guru of Duryodhana and Bhima in mace fighting"},
    {"name": "Subhadra", "type": "character", "description": "Sister of Krishna and Balarama, wife of Arjuna, mother of Abhimanyu"},

    # Karna
    {"name": "Karna", "type": "character", "description": "Eldest son of Kunti and Sun god Surya, raised by charioteer Adhiratha, loyal ally of Duryodhana, greatest rival of Arjuna"},
    {"name": "Adhiratha", "type": "character", "description": "Charioteer who adopted and raised Karna"},
    {"name": "Radha", "type": "character", "description": "Wife of Adhiratha, foster mother of Karna"},

    # Teachers
    {"name": "Drona", "type": "character", "description": "Brahmin military teacher of both Pandavas and Kauravas, father of Ashwatthama, commander of Kaurava forces"},
    {"name": "Ashwatthama", "type": "character", "description": "Son of Drona, killed Pandava sons at night after Kurukshetra war, bears a gem on his forehead"},
    {"name": "Kripa", "type": "character", "description": "Royal preceptor of Hastinapura, brother-in-law of Drona, survived the war"},
    {"name": "Parashurama", "type": "character", "description": "Warrior sage, taught Drona and Karna the use of arms"},

    # Drupada's family
    {"name": "Drupada", "type": "character", "description": "King of Panchala, father of Draupadi and Dhrishtadyumna, enemy turned ally of Pandavas"},
    {"name": "Dhrishtadyumna", "type": "character", "description": "Son of Drupada, commander of Pandava forces, killed Drona"},
    {"name": "Shikhandi", "type": "character", "description": "Son/daughter of Drupada, reborn to kill Bhishma, key to Bhishma's death"},

    # Abhimanyu and next gen
    {"name": "Abhimanyu", "type": "character", "description": "Son of Arjuna and Subhadra, killed in Chakravyuha formation at Kurukshetra"},
    {"name": "Ghatotkacha", "type": "character", "description": "Son of Bhima and demoness Hidimbi, killed by Karna using Vasavi Shakti"},
    {"name": "Parikshit", "type": "character", "description": "Son of Abhimanyu, grandson of Arjuna, next king after Pandavas, bitten by Takshaka"},

    # Other key figures
    {"name": "Vidura", "type": "character", "description": "Half-brother of Dhritarashtra and Pandu (son of Vyasa), wisest minister of Hastinapura, incarnation of Yama"},
    {"name": "Jarasandha", "type": "character", "description": "King of Magadha, powerful ruler killed by Bhima with Krishna's guidance"},
    {"name": "Shalya", "type": "character", "description": "King of Madra, uncle of Nakula and Sahadeva (brother of Madri), forced to fight for Kauravas"},
    {"name": "Hidimbi", "type": "character", "description": "Rakshasa woman who married Bhima, mother of Ghatotkacha"},

    # Places
    {"name": "Hastinapura", "type": "place", "description": "Capital of the Kuru kingdom, seat of the Kaurava and Pandava conflict"},
    {"name": "Indraprastha", "type": "place", "description": "Capital built by the Pandavas on barren land given by Dhritarashtra"},
    {"name": "Kurukshetra", "type": "place", "description": "Battlefield where the 18-day war was fought between Pandavas and Kauravas"},
    {"name": "Dwarka", "type": "place", "description": "Krishna's kingdom, submerged in the sea after the Mahabharata war"},
    {"name": "Panchala", "type": "place", "description": "Kingdom of King Drupada, home of Draupadi"},

    # Key events
    {"name": "Kurukshetra War", "type": "event", "description": "18-day war between Pandavas and Kauravas, resulted in Pandava victory"},
    {"name": "Dice Game", "type": "event", "description": "Rigged game of dice by Shakuni, Yudhishthira lost kingdom, wife, and freedom"},
    {"name": "Swayamvara", "type": "event", "description": "Draupadi's bride-choosing ceremony, won by Arjuna"},
    {"name": "Bhagavad Gita", "type": "concept", "description": "Divine discourse by Krishna to Arjuna on the battlefield of Kurukshetra"},
    {"name": "Chakravyuha", "type": "concept", "description": "Spiral military formation used by Kauravas; Abhimanyu entered but couldn't exit"},
]

SEED_RELATIONSHIPS = [
    # Shantanu family
    {"source": "Shantanu", "relation": "IS_FATHER_OF", "target": "Bhishma", "context": "Son of Shantanu and Ganga"},
    {"source": "Ganga", "relation": "IS_MOTHER_OF", "target": "Bhishma", "context": "Ganga bore Bhishma, then returned to heaven"},
    {"source": "Shantanu", "relation": "IS_HUSBAND_OF", "target": "Ganga", "context": "First marriage of Shantanu"},
    {"source": "Shantanu", "relation": "IS_HUSBAND_OF", "target": "Satyavati", "context": "Second marriage after Ganga"},
    {"source": "Satyavati", "relation": "IS_MOTHER_OF", "target": "Chitragupta", "context": "First biological son with Shantanu"},
    {"source": "Satyavati", "relation": "IS_MOTHER_OF", "target": "Vichitravirya", "context": "Second biological son with Shantanu"},
    {"source": "Shantanu", "relation": "IS_FATHER_OF", "target": "Chitragupta", "context": "Son with Satyavati"},
    {"source": "Shantanu", "relation": "IS_FATHER_OF", "target": "Vichitravirya", "context": "Son with Satyavati"},
    {"source": "Satyavati", "relation": "IS_MOTHER_OF", "target": "Vyasa", "context": "Born to Satyavati and sage Parashara before marriage"},

    # Vyasa niyoga
    {"source": "Vyasa", "relation": "IS_FATHER_OF", "target": "Dhritarashtra", "context": "Born through niyoga with Ambika"},
    {"source": "Vyasa", "relation": "IS_FATHER_OF", "target": "Pandu", "context": "Born through niyoga with Ambalika"},
    {"source": "Vyasa", "relation": "IS_FATHER_OF", "target": "Vidura", "context": "Born through niyoga with a maid"},
    {"source": "Ambika", "relation": "IS_MOTHER_OF", "target": "Dhritarashtra", "context": "Born blind due to Ambika closing her eyes"},
    {"source": "Ambalika", "relation": "IS_MOTHER_OF", "target": "Pandu", "context": "Born pale due to Ambalika's fear"},

    # Kaurava family
    {"source": "Dhritarashtra", "relation": "IS_HUSBAND_OF", "target": "Gandhari", "context": "Gandhari blindfolded herself to share husband's affliction"},
    {"source": "Dhritarashtra", "relation": "IS_FATHER_OF", "target": "Duryodhana", "context": "Eldest of 100 Kaurava sons"},
    {"source": "Dhritarashtra", "relation": "IS_FATHER_OF", "target": "Dushasana", "context": "Second Kaurava son"},
    {"source": "Gandhari", "relation": "IS_MOTHER_OF", "target": "Duryodhana", "context": "Born from Gandhari's womb after two years"},
    {"source": "Gandhari", "relation": "IS_MOTHER_OF", "target": "Dushasana", "context": "Second of 100 sons"},
    {"source": "Gandhari", "relation": "IS_SISTER_OF", "target": "Shakuni", "context": "Shakuni is Gandhari's brother from Gandhara"},
    {"source": "Shakuni", "relation": "IS_UNCLE_OF", "target": "Duryodhana", "context": "Uncle through Gandhari"},

    # Pandava family
    {"source": "Pandu", "relation": "IS_HUSBAND_OF", "target": "Kunti", "context": "First wife of Pandu"},
    {"source": "Pandu", "relation": "IS_HUSBAND_OF", "target": "Madri", "context": "Second wife of Pandu"},
    {"source": "Kunti", "relation": "IS_MOTHER_OF", "target": "Yudhishthira", "context": "Son of Dharma (Yama) invoked by Kunti"},
    {"source": "Kunti", "relation": "IS_MOTHER_OF", "target": "Bhima", "context": "Son of Vayu invoked by Kunti"},
    {"source": "Kunti", "relation": "IS_MOTHER_OF", "target": "Arjuna", "context": "Son of Indra invoked by Kunti"},
    {"source": "Kunti", "relation": "IS_MOTHER_OF", "target": "Karna", "context": "Born before marriage with Sun god Surya"},
    {"source": "Madri", "relation": "IS_MOTHER_OF", "target": "Nakula", "context": "Son of Ashwini Kumaras"},
    {"source": "Madri", "relation": "IS_MOTHER_OF", "target": "Sahadeva", "context": "Son of Ashwini Kumaras"},
    {"source": "Shalya", "relation": "IS_BROTHER_OF", "target": "Madri", "context": "Shalya is Madri's brother, hence uncle of Nakula and Sahadeva"},

    # Pandava siblings
    {"source": "Yudhishthira", "relation": "IS_BROTHER_OF", "target": "Bhima", "context": "Pandava brothers"},
    {"source": "Yudhishthira", "relation": "IS_BROTHER_OF", "target": "Arjuna", "context": "Pandava brothers"},
    {"source": "Yudhishthira", "relation": "IS_BROTHER_OF", "target": "Nakula", "context": "Pandava brothers (half)"},
    {"source": "Yudhishthira", "relation": "IS_BROTHER_OF", "target": "Sahadeva", "context": "Pandava brothers (half)"},
    {"source": "Bhima", "relation": "IS_BROTHER_OF", "target": "Arjuna", "context": "Pandava brothers"},
    {"source": "Nakula", "relation": "IS_BROTHER_OF", "target": "Sahadeva", "context": "Twin Pandava brothers, sons of Madri"},
    {"source": "Karna", "relation": "IS_BROTHER_OF", "target": "Yudhishthira", "context": "Half-brothers through Kunti, unknown to them"},
    {"source": "Karna", "relation": "IS_BROTHER_OF", "target": "Arjuna", "context": "Half-brothers through Kunti, bitter rivals"},

    # Draupadi marriages
    {"source": "Draupadi", "relation": "IS_WIFE_OF", "target": "Yudhishthira", "context": "First husband"},
    {"source": "Draupadi", "relation": "IS_WIFE_OF", "target": "Bhima", "context": "Second husband"},
    {"source": "Draupadi", "relation": "IS_WIFE_OF", "target": "Arjuna", "context": "Third husband, won her at swayamvara"},
    {"source": "Draupadi", "relation": "IS_WIFE_OF", "target": "Nakula", "context": "Fourth husband"},
    {"source": "Draupadi", "relation": "IS_WIFE_OF", "target": "Sahadeva", "context": "Fifth husband"},
    {"source": "Draupadi", "relation": "IS_DAUGHTER_OF", "target": "Drupada", "context": "Born from a yajna fire"},
    {"source": "Dhrishtadyumna", "relation": "IS_SON_OF", "target": "Drupada", "context": "Born to kill Drona"},
    {"source": "Shikhandi", "relation": "IS_SON_OF", "target": "Drupada", "context": "Born to bring about Bhishma's death"},

    # Krishna family
    {"source": "Krishna", "relation": "IS_BROTHER_OF", "target": "Balarama", "context": "Brothers, sons of Vasudeva and Devaki"},
    {"source": "Krishna", "relation": "IS_BROTHER_OF", "target": "Subhadra", "context": "Sister of Krishna"},
    {"source": "Subhadra", "relation": "IS_WIFE_OF", "target": "Arjuna", "context": "Arjuna married Subhadra with Krishna's blessing"},
    {"source": "Subhadra", "relation": "IS_MOTHER_OF", "target": "Abhimanyu", "context": "Son of Arjuna and Subhadra"},
    {"source": "Arjuna", "relation": "IS_FATHER_OF", "target": "Abhimanyu", "context": "Son born to Subhadra"},

    # Abhimanyu / next gen
    {"source": "Abhimanyu", "relation": "IS_SON_OF", "target": "Arjuna", "context": "Arjuna's son, killed in Chakravyuha"},
    {"source": "Abhimanyu", "relation": "IS_FATHER_OF", "target": "Parikshit", "context": "Parikshit born posthumously"},
    {"source": "Ghatotkacha", "relation": "IS_SON_OF", "target": "Bhima", "context": "Son of Bhima and Hidimbi"},
    {"source": "Hidimbi", "relation": "IS_WIFE_OF", "target": "Bhima", "context": "Rakshasa woman who married Bhima in the forest"},

    # Karna
    {"source": "Adhiratha", "relation": "IS_FATHER_OF", "target": "Karna", "context": "Adoptive father, charioteer who raised Karna"},
    {"source": "Radha", "relation": "IS_MOTHER_OF", "target": "Karna", "context": "Foster mother of Karna"},
    {"source": "Karna", "relation": "IS_ALLY_OF", "target": "Duryodhana", "context": "Closest friend and ally of Duryodhana"},
    {"source": "Karna", "relation": "IS_ENEMY_OF", "target": "Arjuna", "context": "Lifelong rivals, each vowed to kill the other"},

    # Teachers
    {"source": "Drona", "relation": "IS_TEACHER_OF", "target": "Arjuna", "context": "Drona trained Arjuna as his finest student"},
    {"source": "Drona", "relation": "IS_TEACHER_OF", "target": "Yudhishthira", "context": "Taught all Pandavas"},
    {"source": "Drona", "relation": "IS_TEACHER_OF", "target": "Bhima", "context": "Taught all Pandavas"},
    {"source": "Drona", "relation": "IS_TEACHER_OF", "target": "Duryodhana", "context": "Taught all princes of Hastinapura"},
    {"source": "Drona", "relation": "IS_TEACHER_OF", "target": "Karna", "context": "Drona refused to teach Karna fully"},
    {"source": "Drona", "relation": "IS_FATHER_OF", "target": "Ashwatthama", "context": "Ashwatthama is Drona's son"},
    {"source": "Parashurama", "relation": "IS_TEACHER_OF", "target": "Drona", "context": "Drona learned weapons from Parashurama"},
    {"source": "Parashurama", "relation": "IS_TEACHER_OF", "target": "Karna", "context": "Karna learned from Parashurama by deceiving him"},
    {"source": "Kripa", "relation": "IS_TEACHER_OF", "target": "Pandavas", "context": "First teacher of princes"},

    # Rivalries and alliances
    {"source": "Duryodhana", "relation": "IS_ENEMY_OF", "target": "Pandavas", "context": "Lifelong enmity leading to Kurukshetra war"},
    {"source": "Bhishma", "relation": "IS_ALLY_OF", "target": "Kauravas", "context": "Fought for Kauravas despite love for Pandavas"},
    {"source": "Krishna", "relation": "IS_ALLY_OF", "target": "Arjuna", "context": "Arjuna's charioteer and divine guide"},
    {"source": "Drupada", "relation": "IS_ENEMY_OF", "target": "Drona", "context": "Former friends turned enemies over kingdom"},

    # Deaths and killings
    {"source": "Bhima", "relation": "KILLED", "target": "Duryodhana", "context": "Killed in mace fight, struck thigh against rules"},
    {"source": "Bhima", "relation": "KILLED", "target": "Dushasana", "context": "Killed to fulfill vow after Draupadi's humiliation"},
    {"source": "Bhima", "relation": "KILLED", "target": "Jarasandha", "context": "Killed in wrestling with Krishna's guidance"},
    {"source": "Arjuna", "relation": "KILLED", "target": "Karna", "context": "Killed with Anjalikastra when Karna's chariot was stuck"},
    {"source": "Karna", "relation": "KILLED", "target": "Ghatotkacha", "context": "Used Vasavi Shakti (meant for Arjuna) to kill Ghatotkacha"},
    {"source": "Dhrishtadyumna", "relation": "KILLED", "target": "Drona", "context": "Beheaded Drona after he was tricked by false news of Ashwatthama's death"},
    {"source": "Ashwatthama", "relation": "KILLED", "target": "Dhrishtadyumna", "context": "Killed in revenge after Kurukshetra war, at night"},
    {"source": "Shikhandi", "relation": "KILLED", "target": "Bhishma", "context": "Bhishma laid down arms facing Shikhandi (his past enemy Amba)"},

    # Participation
    {"source": "Pandavas", "relation": "PARTICIPATED_IN", "target": "Kurukshetra War", "context": "Fought against Kauravas"},
    {"source": "Kauravas", "relation": "PARTICIPATED_IN", "target": "Kurukshetra War", "context": "Fought against Pandavas"},
    {"source": "Arjuna", "relation": "PARTICIPATED_IN", "target": "Swayamvara", "context": "Won Draupadi by shooting the eye of a rotating fish"},
    {"source": "Yudhishthira", "relation": "PARTICIPATED_IN", "target": "Dice Game", "context": "Lost everything including Draupadi"},
    {"source": "Abhimanyu", "relation": "PARTICIPATED_IN", "target": "Chakravyuha", "context": "Entered but was killed, unable to exit"},

    # Locations
    {"source": "Pandavas", "relation": "RULES_OVER", "target": "Indraprastha", "context": "Built and ruled by Pandavas"},
    {"source": "Dhritarashtra", "relation": "RULES_OVER", "target": "Hastinapura", "context": "Blind king of Hastinapura"},
    {"source": "Krishna", "relation": "RULES_OVER", "target": "Dwarka", "context": "Krishna's kingdom"},
    {"source": "Drupada", "relation": "RULES_OVER", "target": "Panchala", "context": "King of Panchala"},
    {"source": "Kurukshetra War", "relation": "FOUGHT_AT", "target": "Kurukshetra", "context": "The great battle was fought on the field of Kurukshetra"},
]


def get_seed_data():
    return SEED_ENTITIES, SEED_RELATIONSHIPS
