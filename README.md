# arpakana

ARPAbet音素記号を日本語のカナ文字へ変換するためのPythonライブラリです。

## 📖 概要

`arpakana` は、Carnegie Mellon University Pronouncing Dictionary形式のARPAbetを入力として、対応するカタカナ列を出力します。


## 💡 使用例

```bash
uv add arpakana
```

```python
from arpakana import arpabet_to_kana

greeting = arpabet_to_kana("HH AH0 L OW1")
assert greeting == "ハロウ"

words = ["B", "L", "UW"]
assert arpabet_to_kana(words) == "ブルー"

fallback = arpabet_to_kana("XYZ", unknown="*")
assert fallback == "*"

# 語境界の音素を連結した場合は、境界同化で生じた摩擦音の
# 不要な促音化を抑制できます。
connected = arpabet_to_kana(
    "D IH1 JH UW1",
    geminate_intervocalic=False,
)
assert connected == "ディジュー"
```

## 📄 ライセンス

このプロジェクトはMITライセンスの下で提供されています。詳細は [LICENSE](LICENSE) を参照してください。
