SINGLE_CONFIG = {
    # 🗓️ Put your date here in MMDDYY format (e.g., September 29, 2026 is "092926")
    "date": "092926",
    
    # ⛪ Type your church or group name here (shows up nicely in the booklet header!)
    "organization": "Organization",
    
    # 🎉 Type your special mass or event name here (e.g., "Sunday Mass", "Feast of St. Michael")
    "event_name": "Event Name",
    
    "hymns": {
        "opening": {
            # 🎵 Your opening hymn title goes here
            "title": "Khúc Ca Mở Lễ",
            # 🎶 The refrain or chorus lyrics
            "chorus": "Chorus",
            "verses": {
                # 📜 Add as many verses as you need here ("verse1", "verse2", etc.)
                "verse1": "Verse 1", 
                "verse2": "Verse 2"
            }
        },
        "offertory": {
            # 🥖 Your offertory song title
            "title": "Tiến Lễ Tin Yêu",
            "chorus": "ĐK. Chorus",
            "verses": {"verse1": "Verse 1"}
        },
        "communion": {
            # 🍞 Your communion song title
            "title": "Con Thờ Lạy Chúa",
            "chorus": "Chorus",
            "verses": {"verse1": "Verse 1"}
        },
        "recessional": {
            # 🚶‍♂️ Closing hymn title
            "title": "Salve Regina",
            # If your closing song doesn't use verses/chorus, you can just paste the full text here!
            "text": "Salve Regina Text"
        }
    },
    
    # 🌐 Language settings for your readings! 
    # Options for "lang": 
    #   - "eng" (pulls automatically from USCCB)
    #   - "viet" (pulls automatically from Thanh Linh)
    # "option_index": usually 0 (picks the first reading option if there's an "OR" choice)
    
    "reading1": {"lang": "eng", "option_index": 0},
    "psalm":    {"lang": "viet", "option_index": 0},
    "reading2": {"lang": "eng", "option_index": 0},
    "alleluia": {"lang": "viet", "option_index": 0},
    "gospel":   {"lang": "eng", "option_index": 0}
}