# Módszertan, érvényességi kör és ellenőrzés

## Vizsgált feladat

A `main.py` két determinisztikusan generált szintetikus háromszöghálót készít (hullámos tórusz, deformált gömb), majd mindkettőből négy kijelölt geometriai környezetben háromszögeket távolít el. A `HoleDetector` az egyszer szereplő élekből peremhurkokat épít; mind a négy algoritmus ezeket próbálja lefedni.

Az implementáció nem kezel automatikusan tetszőleges külső mesh-fájlt. A nyitott peremhurkok bejárása és a nemsíkbeli sokszögek háromszögelése bonyolult, hibás, nem-manifold vagy önmetsző bemeneteknél nem általánosan bizonyított.

## Algoritmusok

1. **Centroid Fan:** a hurok súlypontját új csúcsként használó legyező.
2. **Ear Clipping:** a hurok folyamatos háromszögelése új csúcs nélkül, pontozással kiválasztott fülekkel.
3. **Multi-Ring Laplacian:** két belső gyűrű és középpont, majd 25 Jacobi-jellegű szomszédátlagoló iteráció.
4. **Multi-Ring Biharmonic TPS:** a Laplacian foltból induló, lokális SVD-koordinátarendszerben vékony lemez spline-illesztés.

## A metrikák tényleges definíciója

Legyenek `p_i` a hozzáadott háromszögek súlypontjai és `q_j` az eredeti háló összes háromszögének súlypontjai. A program:

`d_i = min_j ||p_i - q_j||`

`RMSE_hiba = sqrt(mean(d_i ** 2))`

`Hausdorff_hiba = max(d_i)`

Ezek a diszkrét súlypontkészleteken alapuló, **egyirányú** közelségi mutatók. Nem mérik a tényleges legközelebbi háromszögfelület-távolságot, nem szimmetrikusak, a háromszögek területével sem súlyoznak. Emiatt a „Hausdorff” mező nem teljes/szimmetrikus Hausdorff-távolság.

Az eltelt idő mérése a kitöltőfüggvény körül történik (`time.perf_counter`). Nem tartalmazza az ábrák és kimeneti fájlok előállítását. Más eszközökön eltérhet.

## Topológiai ellenőrzés

A javítás után a peremél-számlálót, a maradék hurokszámot és a pótolt háromszögszámot tároljuk. A 0 peremél **nem bizonyít** önmagában szigorú geometriai vízzáróságot, önmetszésmentességet vagy megfelelő felületminőséget. A korábban exportált OBJ-ket ettől külön is ellenőrizni érdemes.

## Reprodukálhatóság

A két beépített modell és a geometriai értékek determinisztikusak az ellenőrzött függőségek mellett. A futásidő, a generálás időbélyege, valamint kisebb numerikus eltérések gépfüggők lehetnek. A PNG-kép vizuális megjelenése Matplotlib/verzió szerint változhat. A jelenlegi ellenőrzés nem képez teljes körű matematikai validációt vagy tetszőleges külső adatkészleten végzett benchmarkot.

A demonstrációs prezentáció és a személyes munkanapló nincs része a beadási forráscsomagnak, mert külön frissítést, illetve adatvédelmi felülvizsgálatot igényel.
