from score_viewer.naming import extract_song_name

CASES = {
    "112_Beethoven's 9th - 4th Horn in F -2024-11-08.pdf": "112_Beethoven's 9th",
    "112_Beethoven's 9th - 1st Horn in F -2024-11-08.pdf": "112_Beethoven's 9th",
    "001_Opening Tune_2025 - Horn in F 3rd -2025-11-22 .pdf": "001_Opening Tune_2025",
    "054_Tokyo Disneyland Electrical Parade - 1st Horn in F -2022-02-15のコピー.pdf":
        "054_Tokyo Disneyland Electrical Parade",
    "047_An Affair to Remember - 4th Horn in F.pdf": "047_An Affair to Remember",
    "107_輝く未来 - Horn in F 2nd - 2024-09-08.pdf": "107_輝く未来",
    "080_レオケの新世界交響曲_2nd Horn in F_2023-09-09.pdf": "080_レオケの新世界交響曲",
    "010 ANPANMAN's Mood (Ver2)-3rd Horn in F-2022-07-21.pdf":
        "010 ANPANMAN's Mood (Ver2)",
    "010_In_The_Anpanman's_Mood-4th Horn in F-20190117.pdf":
        "010_In_The_Anpanman's_Mood",
    "021_I can't take my eyes off you_20200115_1,3 Horn in F.pdf":
        "021_I can't take my eyes off you",
    "083_Radetzky March - 4th Horn in F -2023-10-31.pdf": "083_Radetzky March",
}


def test_extract_song_name():
    for filename, expected in CASES.items():
        assert extract_song_name(filename) == expected, filename
