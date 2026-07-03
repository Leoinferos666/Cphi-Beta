def moisture_content(w1, w2, w3):

    return round(
        ((w2 - w3) / (w3 - w1)) * 100,
        2
    )