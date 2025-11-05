from arpakana.arpabet import arpabet_to_kana


def test_正常系_基本単語() -> None:
    # hello
    assert arpabet_to_kana("HH AH0 L OW1") == "ハロウ"
    # sky
    assert arpabet_to_kana("S K AY") == "スカイ"
    # blue
    assert arpabet_to_kana(["B", "L", "UW"]) == "ブルー"
    # train
    assert arpabet_to_kana("T R EY N") == "トゥレイン"
    #bout
    assert arpabet_to_kana("B AW1 T") == "バウトゥ"
    # 'cause
    assert arpabet_to_kana("K AH0 Z") == "カズ"
    # 'course
    assert arpabet_to_kana("K AO1 R S") == "コース"
    # 'm
    assert arpabet_to_kana("AH0 M") == "アム"
    # frisco
    assert arpabet_to_kana("F R IH1 S K OW0") == "フリスコウ"

def test_正常系_長い発音() -> None:
    arpabet_sequence = ['P', 'OH', 'K', 'S', 'DX', 'T', 'AO', 'K', 'IH', 'JH', 'EH', 'L', 'K', 'IH', 'JH', 'IH', 'K', 'OH', 'K', 'UW', 'R', 'AE', 'K', 'UW', 'DX', 'EH', 'K', 'IH', 'V', 'AE', 'N', 'JH', 'IH', 'G', 'AE', 'T', 'OH', 'R', 'AE', 'K', 'S', 'AE', 'N', 'EH', 'N', 'AE']
    assert arpabet_to_kana(arpabet_sequence) == "ポークスルトーキジェルキジコークーラクーレキヴァンジガトーラクサネナ"

def test_正常系_複合子音() -> None:
    assert arpabet_to_kana("K Y UW1 Z") == "キューズ"
def test_正常系_ER()->None:
    # amateurish
    assert arpabet_to_kana("AE1 M AH0 CH ER2 IH0 SH") == "アマチャリシュ"
    # ameliorate
    assert arpabet_to_kana("AH0 M IY1 L Y ER0 EY2 T") == "アミーリャレイトゥ"
    # bird
    assert arpabet_to_kana("B ER1 D") == "バード"

def test_正常系_未知トークン() -> None:
    assert arpabet_to_kana("XYZ", unknown="*") == "*"
