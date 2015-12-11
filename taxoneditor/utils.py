def lookupMajorGroup(phylum):
"""
Dictionary function translating GBIF phylum values to UCJEPS major group
Input the phylum; get back the major group
"""
    MajorGroups = {
        'Magnoliophyta': 'Spermatophytes',
        'Streptophyta': 'Spermatophytes',
        'Pteridophyta': 'Pteridophytes',
        'Bryophyta': 'Bryophytes',
        'Chlorophyta': 'Algae',
        'Bacillariophyta': 'Algae',
        'Rhodophyta': 'Algae',
        'Pinophyta': 'Spermatophytes',
        'Lycopodiophyta': 'Pteridophytes',
        'Marchantiophyta': 'Bryophytes',
        'Cycadophyta': 'Spermatophytes',
        'Prasinophyta': 'Algae',
        'Equisetophyta': 'Pteridophytes',
        'Gnetophyta': 'Spermatophytes',
        'Ginkgophyta': 'Spermatophytes',
        'Anthocerotophyta': 'Bryophytes',
        'Psilophyta': 'Pteridophytes',
        'Cyanidiophyta': 'Algae',
        'Glaucophyta': 'Algae',
        'phylum': 'not found',
    }
    return MajorGroups[phylum]