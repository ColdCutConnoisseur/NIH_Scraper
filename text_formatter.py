"""Helper functions for formatting text in output"""

def title_case_text(original_text):

    to_lower = original_text.lower()

    # Cap hyphens

    hyphen_split = to_lower.split('-')

    capped_hyphens = '-'.join([word.capitalize() for word in hyphen_split])

    print(capped_hyphens)

    exempt_words = ['of', 'at', 'to']

    # Cap Spaces
    space_split = capped_hyphens.split(' ')

    all_capped_words = []

    for word in space_split:
        if word not in exempt_words and '-' not in word:
            all_capped_words.append(word.capitalize())

        else:
            if '-' in word:
                word = word[0].upper() + word[1:]
                
            all_capped_words.append(word)

    return ' '.join(all_capped_words)


if __name__ == "__main__":
    test1 = title_case_text("PARTNER AT JOHN-BIGSBY-RUTH")

    print(test1)
