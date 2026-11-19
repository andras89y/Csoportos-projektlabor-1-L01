# 3D rekonstrukció – feljavítás

**Széchenyi István Egyetem · Csoportos Projektlabor 1 · L01 csoport · 2026/27/1**

A projekt négy háromszögháló-lyukkitöltő algoritmust hasonlít össze két beépített, szintetikus tesztgeometrián (hullámos tórusz és deformált gömb). A hiányzó háromszögeket és a tesztmodelleket a program automatikusan állítja elő. Külső OBJ-modell beolvasását a jelenlegi változat **nem** támogatja.

A módszerek: **Centroid Fan**, **Ear Clipping**, **Multi-Ring Laplacian**, **Multi-Ring Biharmonic TPS**.

## Tartalom

- [`01_Program/main.py`](01_Program/main.py) – futtatható Python-program.
- [`01_Program/requirements.txt`](01_Program/requirements.txt) – Python-függőségek.
- [`01_Program/MODSZERTAN.md`](01_Program/MODSZERTAN.md) – algoritmusok, mérési mutatók és érvényességi kör.
- [`02_Tesztek/test_reproducibility.py`](02_Tesztek/test_reproducibility.py) – négy automatikus teszt.
- [`02_Tesztek/mintaeredmenyek/`](02_Tesztek/mintaeredmenyek/) – két összehasonlító kép, CSV és HTML/TXT-jegyzőkönyv.

## Indítás Windows alatt

Szükséges: **Python 3.13**, működő `py` Python Launcher, és internet a könyvtárak telepítéséhez. Töltsd le a repót a **Code → Download ZIP** menüvel, csomagold ki, majd nyiss PowerShellt a kicsomagolt projekt gyökérmappájában:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r 01_Program\requirements.txt
.\.venv\Scripts\python.exe 01_Program\main.py
```

A virtuális környezetet nem kell aktiválni. Nem szükséges más forrásfájlokat kézzel összeválogatni. A program a `01_Program/Lyukkitoltes_Eredmenyek/` mappába ment, amelyet automatikusan létrehoz.

## Automatikus tesztek

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s 02_Tesztek -v
```

A teszt ellenőrzi a négy lyuk jelenlétét mindkét szintetikus modellen, mind a négy módszer topológiai peremzárását, a metrikák matematikai számítását és a teljes kimenetgenerálást. A teljes futtatási próba ideiglenes könyvtárban dolgozik.

## Linux / grafikus felület nélküli futtatás

```bash
python3.13 -m venv .venv
.venv/bin/python -m pip install -r 01_Program/requirements.txt
MPLBACKEND=Agg .venv/bin/python 01_Program/main.py
.venv/bin/python -m unittest discover -s 02_Tesztek -v
```

**Ellenőrzött környezet:** Linux, Python 3.13.5, NumPy 2.3.5, Matplotlib 3.10.8. A Windows-futtatás éles ellenőrzését a GitHub Actions workflow is megpróbálja elvégezni; csak a sikeres futás után tekinthető ott is ellenőrzöttnek.

## Kimenetek

A program a `01_Program/Lyukkitoltes_Eredmenyek/` mappába írja az alábbi **17 fájlt**:

| Fájltípus | Darab | Funkció |
| --- | ---: | --- |
| OBJ (`*.obj`) | 12 | Eredeti, sérült és javított hálók |
| PNG (`*.png`) | 2 | A két modell hat-hat nézetes összehasonlítása |
| CSV | 1 | Nyolc mérés pontosvesszővel tagolva |
| HTML | 1 | Relatív képútvonalas jegyzőkönyv |
| TXT | 1 | Szöveges mérési jegyzőkönyv |

Újrafuttatáskor a kimeneti fájlok felülíródnak. A futással létrejövő könyvtár nem kerül verziókövetés alá. A `02_Tesztek/mintaeredmenyek` mappában ellenőrzött példafájlok vannak, a HTML-t és a két PNG-t ugyanabban a könyvtárban kell tartani.

## Mérési értékek és korlátok

A CSV `RMSE_hiba` és `Hausdorff_hiba` mezői a program **egyirányú, háromszög-súlypont alapú közelítő mutatói**, nem folytonos felületek közötti, szimmetrikus Hausdorff-távolságot jelentenek. A nulla nyitott peremél a tesztelt hálók peremzárását igazolja, de önmagában nem bizonyítja az önmetszésmentességet vagy az általános hálójavítási képességet. A futásidők gépfüggők; nem a teljes ábra- és fájlgenerálás idejét mérik. Részletesen: [módszertan](01_Program/MODSZERTAN.md).

Ez a repó az L01 csoport egyetemi projektjének futtatható és dokumentált változata. A személyes munkanaplók, belső egyeztetések és prezentációk nem tartoznak a nyilvános forráscsomaghoz.

**Licenc:** jelenleg nincs külön nyílt forráskódú licenc megadva; a közzététel nem jelent automatikus újrafelhasználási engedélyt.
