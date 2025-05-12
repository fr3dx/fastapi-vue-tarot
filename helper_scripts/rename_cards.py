import json
import os

# A JSON tarot cards and descriptions
tarot_data = [
  {
    "key": "fool",
    "description": "A kezdetek és új lehetőségek jelképe. A Bolond a szabadságot, az ártatlanságot és a kalandvágyat szimbolizálja, de figyelmeztet a meggondolatlanság veszélyeire is."
  },
  {
    "key": "magician",
    "description": "A hatalom és képességek kártyája. A Mágus az akaraterőt, a manifesztációt és a leleményességet jelképezi, de utalhat megtévesztésre és illúziókra is."
  },
  {
    "key": "high_priestess",
    "description": "A spiritualitás és a tudatalatti jelképe. A Főpapnő az intuíciót, a titokzatosságot és a belső bölcsességet szimbolizálja, de jelezheti az elfojtott érzéseket is."
  },
  {
    "key": "empress",
    "description": "A kreativitás és termékenység kártyája. Az Uralkodónő a nőiességet, a gondoskodást és a bőséget jelképezi, de utalhat bizonytalanságra és kreatív blokkokra is."
  },
  {
    "key": "emperor",
    "description": "A stabilitás és tekintély jelképe. Az Uralkodó a védelem, a gyakorlatiasság és a fegyelem szimbóluma, de figyelmeztethet a rugalmatlanságra és zsarnokságra is."
  },
  {
    "key": "hierophant",
    "description": "A tudás és hagyomány kártyája. A Főpap a spiritualitást, az oktatást és az alkalmazkodást jelképezi, de jelezheti a lázadást és a tudatlanságot is."
  },
  {
    "key": "lovers",
    "description": "A szerelem és kapcsolatok jelképe. A Szeretők a harmóniát, a romantikát és az értékeket szimbolizálják, de utalhatnak konfliktusokra és egyensúlytalanságra is."
  },
  {
    "key": "chariot",
    "description": "Az összpontosítás és akaraterő kártyája. A Diadalszekér az irányítást, az ambíciót és a céltudatosságot jelképezi, de figyelmeztethet az agresszióra és céltalanságra is."
  },
  {
    "key": "strength",
    "description": "Az önbizalom és belső erő jelképe. Az Erő a bátorságot, a befolyást és a magabiztosságot szimbolizálja, de jelezheti az önbizalomhiányt és gyengeséget is."
  },
  {
    "key": "hermit",
    "description": "A befelé fordulás és bölcsesség kártyája. A Remete az önvizsgálatot, a magányt és a megértést jelképezi, de utalhat elszigetelődésre is."
  },
  {
    "key": "wheel_of_fortune",
    "description": "A változás és sorsforduló jelképe. A Szerencsekerék a ciklusokat, a sors irányítását és az új lehetőségeket szimbolizálja, de figyelmeztet a változások elkerülhetetlenségére is."
  },
  {
    "key": "justice",
    "description": "Az igazságosság és egyensúly kártyája. Az Igazságosság a tisztességet, a felelősséget és a döntéshozatalt jelképezi, de jelezheti az elfogultságot is."
  },
  {
    "key": "hanged_man",
    "description": "Az áldozat és szemléletváltás jelképe. Az Akasztott Ember a lemondást, a türelmet és az új perspektívát szimbolizálja, de utalhat stagnálásra is."
  },
  {
    "key": "death",
    "description": "A változás és átalakulás kártyája. A Halál a lezárást, az újrakezdést és a megújulást jelképezi, de figyelmeztethet az ellenállásra is."
  },
  {
    "key": "temperance",
    "description": "A kiegyensúlyozottság és harmónia jelképe. A Mértékletesség az egyensúlyt, a türelmet és az alkalmazkodást szimbolizálja, de jelezheti a mértéktelenséget is."
  },
  {
    "key": "devil",
    "description": "A kötöttségek és kísértések kártyája. Az Ördög a függőségeket, az illúziókat és a materializmust jelképezi, de utalhat a felszabadulás szükségességére is."
  },
  {
    "key": "tower",
    "description": "A hirtelen változás és összeomlás jelképe. A Torony a megrázkódtatásokat, az igazság feltárását és az újjáépítés lehetőségét szimbolizálja."
  },
  {
    "key": "star",
    "description": "A remény és inspiráció kártyája. A Csillag a gyógyulást, a spiritualitást és az optimizmust jelképezi, de figyelmeztethet a csalódottságra is."
  },
  {
    "key": "moon",
    "description": "Az illúziók és intuíció jelképe. A Hold a tudatalattit, a félelmeket és a megérzéseket szimbolizálja, de jelezheti a félrevezetést is."
  },
  {
    "key": "sun",
    "description": "A boldogság és siker kártyája. A Nap az örömöt, a vitalitást és a beteljesülést jelképezi, de utalhat a túlzott optimizmusra is."
  },
  {
    "key": "judgement",
    "description": "Az újjászületés és ítélet jelképe. Az Ítélet az önvizsgálatot, a megbocsátást és az új kezdeteket szimbolizálja, de figyelmeztethet az önkritikára is."
  },
  {
    "key": "world",
    "description": "A teljesség és beteljesülés kártyája. A Világ a siker, az egység és a lezárás szimbóluma, de jelezheti a befejezetlenséget is."
  },
  {
    "key": "ace_of_wands",
    "description": "Az új kezdetek és inspiráció kártyája. Az energiát, lelkesedést és a kreatív lehetőségeket jelképezi."
  },
  {
    "key": "two_of_wands",
    "description": "A tervezés és döntéshelyzet jelképe. Az ambíció és a jövőorientált gondolkodás jelenik meg benne."
  },
  {
    "key": "three_of_wands",
    "description": "A fejlődés és lehetőségek kártyája. A növekedés, előrelépés és sikeres tervek megvalósulása."
  },
  {
    "key": "four_of_wands",
    "description": "Az ünneplés és stabilitás jelképe. Családi harmónia, közösségi örömök és biztonság."
  },
  {
    "key": "five_of_wands",
    "description": "A konfliktus és versengés kártyája. Küzdelem, nézeteltérés, de fejlődést is hozhat."
  },
  {
    "key": "six_of_wands",
    "description": "A győzelem és elismerés kártyája. A siker, dicsőség és vezetői képességek megjelenése."
  },
  {
    "key": "seven_of_wands",
    "description": "Az önvédelem és állhatatosság jelképe. Küzdelem a pozíció megtartásáért, bátorság és kitartás."
  },
  {
    "key": "eight_of_wands",
    "description": "A gyors előrehaladás és dinamizmus kártyája. Gyors cselekvés, kommunikáció és sikeres megoldások."
  },
  {
    "key": "nine_of_wands",
    "description": "A kitartás és védelem kártyája. A nehézségeken való túljutás és az erőfeszítések véghezvitele."
  },
  {
    "key": "ten_of_wands",
    "description": "A terhek és felelősség jelképe. A túlterheltség, a munka és a végső cél elérése érdekében tett erőfeszítések."
  },
  {
    "key": "page_of_wands",
    "description": "A kíváncsiság és új ötletek kártyája. Fiatalos energia, kreativitás és új kezdetek."
  },
  {
    "key": "knight_of_wands",
    "description": "A bátorság és kalandvágy jelképe. Elszántság, cselekvésre való készség és hirtelen impulzusok."
  },
  {
    "key": "queen_of_wands",
    "description": "A magabiztosság és vezetői képességek kártyája. Belső erő, kreativitás és társadalmi kapcsolatok."
  },
  {
    "key": "king_of_wands",
    "description": "A tekintély és döntéshozatal jelképe. A vezetés, tervezés és stratégiai gondolkodás szimbóluma."
  },
  {
    "key": "ace_of_cups",
    "description": "A szeretet és érzelmek új kezdetének jelképe. A szerelem, öröm és érzelmi gazdagság kártyája."
  },
  {
    "key": "two_of_cups",
    "description": "A kapcsolat és harmónia jelképe. Két ember közötti erős kötelék, szerelmi kapcsolatok és egyensúly."
  },
  {
    "key": "three_of_cups",
    "description": "Az öröm és ünneplés kártyája. Barátságok, közösségi események és örömteli pillanatok."
  },
  {
    "key": "four_of_cups",
    "description": "Az érzelmi elégedetlenség és unalom kártyája. A befelé fordulás, új lehetőségek elutasítása."
  },
  {
    "key": "five_of_cups",
    "description": "A bánat és veszteség kártyája. Elvesztett lehetőségek, csalódás, de még mindig léteznek új esélyek."
  },
  {
    "key": "six_of_cups",
    "description": "A múlt és nosztalgia jelképe. Gyermeki boldogság, régi emlékek és egyszerű örömök."
  },
  {
    "key": "seven_of_cups",
    "description": "A választás és illúziók kártyája. Sokféle lehetőség, de elkerülhetjük a tiszta döntést."
  },
  {
    "key": "eight_of_cups",
    "description": "Az elengedés és elindulás kártyája. Az érzelmi kötődésektől való elszakadás, új irányba való elindulás."
  },
  {
    "key": "nine_of_cups",
    "description": "A beteljesülés és öröm kártyája. Az érzelmi elégedettség és a kívánságok teljesülése."
  },
  {
    "key": "ten_of_cups",
    "description": "A boldogság és harmónia kártyája. Családi összhang, szeretet és a teljes érzelmi teljesség."
  },
  {
    "key": "page_of_cups",
    "description": "A kreativitás és érzelmi felfedezés kártyája. Új érzelmek, kíváncsiság és érzékenység megjelenése."
  },
  {
    "key": "knight_of_cups",
    "description": "A romantika és érzelmek kártyája. Szenvedélyes, intuitív cselekedetek és érzelmi utazások."
  },
  {
    "key": "queen_of_cups",
    "description": "A törődés és empátia jelképe. Az érzelmek kifejezése, megértés és intuíció."
  },
  {
    "key": "king_of_cups",
    "description": "A bölcsesség és érzelmi egyensúly kártyája. A vezetés érzelem és indulatok kezelésével."
  },
  {
    "key": "ace_of_swords",
    "description": "A tisztánlátás és új gondolatok kártyája. A mentális tisztaság, igazság és kommunikáció kezdete."
  },
  {
    "key": "two_of_swords",
    "description": "A döntés és konfliktus kártyája. A választás előtt állás, belső harc és egyensúly keresése."
  },
  {
    "key": "three_of_swords",
    "description": "A fájdalom és veszteség kártyája. A szívfájdalom, csalódás és érzelmi gyógyulás."
  },
  {
    "key": "four_of_swords",
    "description": "A pihenés és megújulás jelképe. A pihenés, gyógyulás és a mentális nyugalom keresése."
  },
  {
    "key": "five_of_swords",
    "description": "A vereség és harcok kártyája. A konfliktusok, csalódások és győzelem árán elért sikerek."
  },
  {
    "key": "six_of_swords",
    "description": "A menekülés és utazás kártyája. A nehézségek elhagyása és a jobb jövő felé való elindulás."
  },
  {
    "key": "seven_of_swords",
    "description": "A titkok és csalás kártyája. A manipuláció, taktikai lépések és az elkerülés."
  },
  {
    "key": "eight_of_swords",
    "description": "A korlátok és akadályok kártyája. A mentális csapdák, blokkok és a korlátozó gondolatok."
  },
  {
    "key": "nine_of_swords",
    "description": "A félelmek és aggodalmak kártyája. Az éjszakai félelmek, a szorongás és az önmarcangolás."
  },
  {
    "key": "ten_of_swords",
    "description": "A vég és zárás kártyája. A fájdalmas befejezés, de egyúttal az új kezdet lehetősége."
  },
  {
    "key": "page_of_swords",
    "description": "Az új gondolatok és kíváncsiság kártyája. Friss ötletek, gyors cselekvés és szellemi kihívások."
  },
  {
    "key": "knight_of_swords",
    "description": "A bátor cselekvés és kockázatvállalás kártyája. A gyors döntések, logikus gondolkodás és határozott lépések."
  },
  {
    "key": "queen_of_swords",
    "description": "A tisztánlátás és racionalitás jelképe. Az éles elme, függetlenség és világos gondolkodás."
  },
  {
    "key": "king_of_swords",
    "description": "A döntéshozatal és igazságosság kártyája. A tisztesség, logika és bölcsesség vezetői képessége."
  },
  {
    "key": "ace_of_pentacles",
    "description": "Az új anyagi lehetőségek kártyája. A gazdagság, stabilitás és a földi javak kezdeti ígérete."
  },
  {
    "key": "two_of_pentacles",
    "description": "Az egyensúly és döntés kártyája. A pénzügyi helyzetek, a munka és magánélet közötti egyensúly keresése."
  },
  {
    "key": "three_of_pentacles",
    "description": "Az együttműködés és munka kártyája. Közös erőfeszítések és sikeres csapatmunka."
  },
  {
    "key": "four_of_pentacles",
    "description": "A birtoklás és biztonság kártyája. A vagyon megőrzése, de figyelmeztethet a túlzott ragaszkodásra."
  },
  {
    "key": "five_of_pentacles",
    "description": "A veszteség és anyagi nehézségek kártyája. Az anyagi hiány és a segítség keresése."
  },
  {
    "key": "six_of_pentacles",
    "description": "A generozitás és egyensúly kártyája. Az adás és kapás, az igazságos elosztás szimbóluma."
  },
  {
    "key": "seven_of_pentacles",
    "description": "A türelem és hosszú távú célok kártyája. A befektetett munka, amely végül megtérül."
  },
  {
    "key": "eight_of_pentacles",
    "description": "A munka és fejlődés kártyája. A mesterségbeli tudás, szorgalom és a szakmai fejlődés."
  },
  {
    "key": "nine_of_pentacles",
    "description": "A gazdagság és önállóság kártyája. A siker, a pénzügyi függetlenség és az élvezet."
  },
  {
    "key": "ten_of_pentacles",
    "description": "A hagyomány és hosszú távú biztonság jelképe. Családi örökség, stabilitás és generációkon átívelő értékek."
  },
  {
    "key": "page_of_pentacles",
    "description": "Az új lehetőségek és tanulás kártyája. A kezdetek, a tanulás és a pénzügyi lehetőségek."
  },
  {
    "key": "knight_of_pentacles",
    "description": "A munka és felelősség kártyája. A megbízhatóság, kitartás és hosszú távú célok elérésére való törekvés."
  },
  {
    "key": "queen_of_pentacles",
    "description": "A gondoskodás és anyagi jólét jelképe. A stabilitás, család és a pénzügyi biztonság."
  },
  {
    "key": "king_of_pentacles",
    "description": "A pénzügyi siker és bölcsesség kártyája. A gazdagság, sikeres üzleti döntések és az anyagi világ irányítása."
  }
]

# JSON adatokat tartalmazó lista dictionary-kként

# Szótár létrehozása a jelenlegi fájlnévből a kívánt kulcsra történő leképezéshez
# Itt meg kell adnod a jelenlegi fájlnevek és a json key közötti kapcsolatot.
# Példa: '00-the-fool.png' -> 'fool'
# 'Cups01.png' -> 'ace_of_cups'
# Ez egy manuális lépés, mivel a fájlnevek és a kulcsok között nincs egyértelmű minta a JSON-ban.
filename_to_key = {
    '00-the-fool.png': 'fool',
    '01-the-magician.png': 'magician',
    '02-the-high-priestess.png': 'high_priestess',
    '03-the-empress.png': 'empress',
    '04-the-emperor.png': 'emperor',
    '05-the-hierophant.png': 'hierophant',
    '06-the-lovers.png': 'lovers',
    '07-the-chariot.png': 'chariot',
    '08-strength.png': 'strength',
    '09-the-hermit.png': 'hermit',
    '10-wheel-of-fortune.png': 'wheel_of_fortune',
    '11-justice.png': 'justice',
    '12-the-hanged-man.png': 'hanged_man',
    '13-death.png': 'death',
    '14-temperance.png': 'temperance',
    '15-the-devil.png': 'devil',
    '16-the-tower.png': 'tower',
    '17-the-star.png': 'star',
    '18-the-moon.png': 'moon',
    '19-the-sun.png': 'sun',
    '20-judgement.png': 'judgement',
    '21-the-world.png': 'world',
    'Cups01.png': 'ace_of_cups',
    'Cups02.png': 'two_of_cups',
    'Cups03.png': 'three_of_cups',
    'Cups04.png': 'four_of_cups',
    'Cups05.png': 'five_of_cups',
    'Cups06.png': 'six_of_cups',
    'Cups07.png': 'seven_of_cups',
    'Cups08.png': 'eight_of_cups',
    'Cups09.png': 'nine_of_cups',
    'Cups10.png': 'ten_of_cups',
    'Cups11.png': 'page_of_cups',
    'Cups12.png': 'knight_of_cups',
    'Cups13.png': 'queen_of_cups',
    'Cups14.png': 'king_of_cups',
    'Pentacles01.png': 'ace_of_pentacles',
    'Pentacles02.png': 'two_of_pentacles',
    'Pentacles03.png': 'three_of_pentacles',
    'Pentacles04.png': 'four_of_pentacles',
    'Pentacles05.png': 'five_of_pentacles',
    'Pentacles06.png': 'six_of_pentacles',
    'Pentacles07.png': 'seven_of_pentacles',
    'Pentacles08.png': 'eight_of_pentacles',
    'Pentacles09.png': 'nine_of_pentacles',
    'Pentacles10.png': 'ten_of_pentacles',
    'Pentacles11.png': 'page_of_pentacles',
    'Pentacles12.png': 'knight_of_pentacles',
    'Pentacles13.png': 'queen_of_pentacles',
    'Pentacles14.png': 'king_of_pentacles',
    'Swords01.png': 'ace_of_swords',
    'Swords02.png': 'two_of_swords',
    'Swords03.png': 'three_of_swords',
    'Swords04.png': 'four_of_swords',
    'Swords05.png': 'five_of_swords',
    'Swords06.png': 'six_of_swords',
    'Swords07.png': 'seven_of_swords',
    'Swords08.png': 'eight_of_swords',
    'Swords09.png': 'nine_of_swords',
    'Swords10.png': 'ten_of_swords',
    'Swords11.png': 'page_of_swords',
    'Swords12.png': 'knight_of_swords',
    'Swords13.png': 'queen_of_swords',
    'Swords14.png': 'king_of_swords',
    'Wands01.png': 'ace_of_wands',
    'Wands02.png': 'two_of_wands',
    'Wands03.png': 'three_of_wands',
    'Wands04.png': 'four_of_wands',
    'Wands05.png': 'five_of_wands',
    'Wands06.png': 'six_of_wands',
    'Wands07.png': 'seven_of_wands',
    'Wands08.png': 'eight_of_wands',
    'Wands09.png': 'nine_of_wands',
    'Wands10.png': 'ten_of_wands',
    'Wands11.png': 'page_of_wands',
    'Wands12.png': 'knight_of_wands',
    'Wands13.png': 'queen_of_wands',
    'Wands14.png': 'king_of_wands',
}


# Létrehozzuk a key-description szótárt a JSON adatokból
key_to_description = {item["key"]: item["description"] for item in tarot_data}

# Átnevezés a jelenlegi könyvtárban
current_directory = "." # Jelenlegi könyvtár

for filename in os.listdir(current_directory):
    if filename.endswith(".png"):
        # Megkeressük a fájlhoz tartozó key-t a filename_to_key szótárban
        key_to_rename = filename_to_key.get(filename)

        if key_to_rename:
            # Megkeressük a key-hez tartozó description-t a key_to_description szótárban
            new_filename = f"{key_to_rename}.png"

            old_path = os.path.join(current_directory, filename)
            new_path = os.path.join(current_directory, new_filename)

            try:
                os.rename(old_path, new_path)
                print(f"Sikeresen átnevezve: {filename} -> {new_filename}")
            except FileNotFoundError:
                print(f"Hiba: A fájl {filename} nem található.")
            except FileExistsError:
                print(f"Hiba: A cél fájl {new_filename} már létezik.")
            except Exception as e:
                print(f"Hiba az átnevezés során {filename}: {e}")
        else:
            print(f"Nem található key a fájlhoz: {filename}")

print("Átnevezési folyamat befejeződött.")
