#!/usr/bin/env python3
"""Parse food data from PDF content and generate JSON."""

import json
import re

# Category and subcategory mappings
CATEGORY_MAP = {
    "Živočíšne potraviny": "ANIMAL_PRODUCTS",
    "Rastlinné potraviny": "PLANT_PRODUCTS",
    "Nápoje": "BEVERAGES",
    "Potravinové aditíva, prídavné látky, pomocné látky": "FOOD_ADDITIVES",
    "Doplnky stravy, lieky, liečivá, stimulanty": "DIETARY_SUPPLEMENTS",
    "Prípravky, zmesi": "PREPARATIONS",
}

SUBCATEGORY_MAP = {
    # Animal products
    "Vajcia": "EGGS",
    "Mliečne výrobky": "DAIRY",
    "Mäso": "MEAT",
    "Ryby": "FISH",
    "Mořské plody": "SEAFOOD",
    "Ostatné": "OTHER",
    # Plant products
    "Zdroje škrobu": "STARCHES",
    "Ořechy": "NUTS",
    "Tuky a oleje": "FATS_OILS",
    "Zelenina": "VEGETABLES",
    "Bylinky": "HERBS",
    "Ovocie": "FRUIT",
    "Semiačka, jadrá": "SEEDS",
    "Huby, riasy, mikroorganizmy": "MUSHROOMS_ALGAE",
    "Sladidlá": "SWEETENERS",
    "Koreniny, dochucovadlá, arómy": "SPICES",
    # Beverages
    "Voda": "WATER",
    "Alkoholické nápoje": "ALCOHOLIC",
    "Čaje": "TEAS",
    "Džúsy, ovocné nektáre": "JUICES",
    "Zeleninové džúsy": "VEGETABLE_JUICES",
    "Kofeínové nápoje": "CAFFEINATED",
    "Rastlinné mlieka": "PLANT_MILKS",
    "Nealko nápoje, limonády": "SOFT_DRINKS",
}

HISTAMINE_LEVEL_MAP = {
    "0": "WELL_TOLERATED",
    "1": "MODERATELY_TOLERATED",
    "2": "POORLY_TOLERATED",
    "3": "VERY_POORLY_TOLERATED",
    "?": "INSUFFICIENT_INFO",
}

FLAG_MAP = {
    "H!": "FAST_SPOILAGE",
    "H": "HIGH_HISTAMINE",
    "A": "OTHER_BIOGENIC_AMINES",
    "L": "HISTAMINE_LIBERATOR",
    "B": "DAO_BLOCKER",
}

# Complete food data extracted from PDF
# Format: (histamine_level, flags, name, notes, category, subcategory)
FOOD_DATA = [
    # ANIMAL PRODUCTS - EGGS
    ("0", [], "vajce prepeličie", "", "ANIMAL_PRODUCTS", "EGGS"),
    ("1", ["L"], "vajce, vajce slepačie", "Žĺtok je kompatibilný. Vaječný bielok aktivuje žírne bunky (najmä v surovom stave ale aj uvarený).", "ANIMAL_PRODUCTS", "EGGS"),
    ("1", ["L"], "vaječný bielok", "Aktivuje žírne bunky (najmä v surovom stave, ale aj uvarený).", "ANIMAL_PRODUCTS", "EGGS"),
    ("0", [], "vaječný žĺtok", "", "ANIMAL_PRODUCTS", "EGGS"),

    # ANIMAL PRODUCTS - DAIRY
    ("1", ["H"], "bezlaktózové mlieko", "Niekedy tolerované dobre, niekedy horšie ako normálne mlieko.", "ANIMAL_PRODUCTS", "DAIRY"),
    ("2", ["H", "A"], "camembert", "", "ANIMAL_PRODUCTS", "DAIRY"),
    ("1", ["H"], "cmar (mierne kyslý, na začiatku fermentácie)", "Fermentácia mliečnymi baktériami.", "ANIMAL_PRODUCTS", "DAIRY"),
    ("1", [], "ghí", "V závislosti od spôsobu výroby s nízkym obsahom histamínu až s miernym obsahom histamínu!", "ANIMAL_PRODUCTS", "DAIRY"),
    ("2", [], "hotové syrové výrobky (s ostatnými/ďalšími prísadami)", "Záleží na zložení a čerstvosti.", "ANIMAL_PRODUCTS", "DAIRY"),
    ("1", ["H"], "jogurt (prírodný neochutený)", "Produkty sa môžu líšiť.", "ANIMAL_PRODUCTS", "DAIRY"),
    ("1", ["H", "A"], "kefír", "", "ANIMAL_PRODUCTS", "DAIRY"),
    ("0", [], "maslo: čerstvé, maslo: smotanové", "Normálne nefermentované maslo.", "ANIMAL_PRODUCTS", "DAIRY"),
    ("1", ["H", "A"], "maslo: s mliečnou kultúrou", "Môže obsahovať malé množstvo histamínu, obvykle dobre tolerované.", "ANIMAL_PRODUCTS", "DAIRY"),
    ("1", ["H"], "mlieko bezlaktózové, mlieko bez laktózy", "Niekedy tolerované dobre, niekedy horšie ako normálne mlieko.", "ANIMAL_PRODUCTS", "DAIRY"),
    ("0", [], "mlieko kozie", "", "ANIMAL_PRODUCTS", "DAIRY"),
    ("0", [], "mlieko ovčie", "", "ANIMAL_PRODUCTS", "DAIRY"),
    ("0", ["H!"], "mlieko surové (nespracované)", "Rýchlo sa kaziace vďaka vysokému obsahu baktérií. Požívať iba čerstvé.", "ANIMAL_PRODUCTS", "DAIRY"),
    ("0", [], "mlieko, pasterizované", "Pokiaľ je črevo citlivé, mlieko môže vadiť.", "ANIMAL_PRODUCTS", "DAIRY"),
    ("1", [], "mlieko, sušené", "Niekedy dobre tolerované, niekedy nie.", "ANIMAL_PRODUCTS", "DAIRY"),
    ("0", [], "mlieko, UHT", "UHT = vysokotepelná úprava", "ANIMAL_PRODUCTS", "DAIRY"),
    ("2", ["H", "A"], "raclette syr", "", "ANIMAL_PRODUCTS", "DAIRY"),
    ("0", [], "sladká smotana (ak je bez prísad)", "Tolerovaná ak je bez fermentácie. Vždy skontrolovať obsah aditív (často se používají stužovače či stabilizátory, napr. E410, E407!", "ANIMAL_PRODUCTS", "DAIRY"),
    ("1", ["H"], "smotana kyslá", "Fermentované mliečnym kvasením! Mierny obsah histamínu.", "ANIMAL_PRODUCTS", "DAIRY"),
    ("0", [], "smotana sladká (bez aditív, neochutená)", "Tolerovaná ak je bez fermentácie. Vždy skontrolovať obsah aditív (často se používají stužovače či stabilizátory, napr. E410, E407!", "ANIMAL_PRODUCTS", "DAIRY"),
    ("0", [], "srvátka: kyslá srvátka", "", "ANIMAL_PRODUCTS", "DAIRY"),
    ("0", [], "srvátka: sladká srvátka", "", "ANIMAL_PRODUCTS", "DAIRY"),
    ("0", [], "syr Butterkäse", "", "ANIMAL_PRODUCTS", "DAIRY"),
    ("2", ["H", "A"], "syr čedar", "", "ANIMAL_PRODUCTS", "DAIRY"),
    ("1", ["H", "A"], "syr feta", "", "ANIMAL_PRODUCTS", "DAIRY"),
    ("2", ["H", "A"], "syr fontina", "", "ANIMAL_PRODUCTS", "DAIRY"),
    ("0", [], "syr Geheimratskäse", "", "ANIMAL_PRODUCTS", "DAIRY"),
    ("0", [], "syr gouda (mladý)", "Iba malé množstvá.", "ANIMAL_PRODUCTS", "DAIRY"),
    ("2", [], "syr gouda (vyzretý)", "", "ANIMAL_PRODUCTS", "DAIRY"),
    ("0", [], "syr krémový (znamená: veľmi mladé syry), neochutené, bez aditív", "", "ANIMAL_PRODUCTS", "DAIRY"),
    ("0", [], "syr mascarpone", "", "ANIMAL_PRODUCTS", "DAIRY"),
    ("0", [], "syr mozzarella", "", "ANIMAL_PRODUCTS", "DAIRY"),
    ("2", ["H", "A"], "syr plesnivý", "", "ANIMAL_PRODUCTS", "DAIRY"),
    ("2", ["H", "A"], "syr raclette", "", "ANIMAL_PRODUCTS", "DAIRY"),
    ("0", [], "syr ricotta", "Zvyčajne sa vyrába s kyselinou citrónovou", "ANIMAL_PRODUCTS", "DAIRY"),
    ("2", ["H", "A"], "syr roquefort", "", "ANIMAL_PRODUCTS", "DAIRY"),
    ("2", ["H", "A"], "syr tavený", "", "ANIMAL_PRODUCTS", "DAIRY"),
    ("2", ["H", "A"], "syr z nepasterizovaného \"surového\" mlieka", "Záleží na hygiene. Vyššie riziko ako pri syroch z pasterizovaného mlieka.", "ANIMAL_PRODUCTS", "DAIRY"),
    ("3", ["H", "A"], "syr: tvrdý, všetky zrejúce syry", "", "ANIMAL_PRODUCTS", "DAIRY"),
    ("2", ["H", "A"], "tavený syr", "", "ANIMAL_PRODUCTS", "DAIRY"),
    ("0", [], "tvaroh", "", "ANIMAL_PRODUCTS", "DAIRY"),
    ("2", ["H", "A"], "výrobky z nespracovaného (surového) mlieka", "", "ANIMAL_PRODUCTS", "DAIRY"),

    # ANIMAL PRODUCTS - MEAT
    ("1", ["H!"], "bravčové (čerstvé, neošetrené)", "Sporné. Väčšinou dobre tolerované, ale rýchlo sa kazí. Histamínový liberátor -> svrbenie?", "ANIMAL_PRODUCTS", "MEAT"),
    ("1", ["H"], "divina", "Vyzreté, ale čerstvé mäso z diviny je často dobre tolerované.", "ANIMAL_PRODUCTS", "MEAT"),
    ("0", ["H!"], "hovädzie (čerstvé)", "", "ANIMAL_PRODUCTS", "MEAT"),
    ("0", ["H!"], "hydina", "", "ANIMAL_PRODUCTS", "MEAT"),
    ("0", [], "jazyk (teľací, hovädzí)", "Skontrolovať prítomnosť netolerovaných surovín, pokiaľ zakúpené ako hotové jedlo. Nikdy nie údené.", "ANIMAL_PRODUCTS", "MEAT"),
    ("0", ["H!"], "kačica, kačacie mäso", "", "ANIMAL_PRODUCTS", "MEAT"),
    ("2", ["H"], "klobásy", "Môže existovať niekoľko výnimiek.", "ANIMAL_PRODUCTS", "MEAT"),
    ("0", ["H!"], "kuracie", "", "ANIMAL_PRODUCTS", "MEAT"),
    ("0", ["H!"], "mäso mleté (skonzumované hneď po pomletí)", "Veľmi závislé od čerstvosti.", "ANIMAL_PRODUCTS", "MEAT"),
    ("2", ["H!", "A"], "mäso mleté (vážené, balené)", "Veľmi závislé od čerstvosti.", "ANIMAL_PRODUCTS", "MEAT"),
    ("3", ["H", "A"], "mäso sušené (všetky druhy)", "", "ANIMAL_PRODUCTS", "MEAT"),
    ("3", ["H"], "mäso údené", "", "ANIMAL_PRODUCTS", "MEAT"),
    ("0", ["H!"], "morčacie, moriak", "", "ANIMAL_PRODUCTS", "MEAT"),
    ("2", ["H"], "párky", "Môže existovať niekoľko výnimiek.", "ANIMAL_PRODUCTS", "MEAT"),
    ("0", ["H!"], "prepeličie", "", "ANIMAL_PRODUCTS", "MEAT"),
    ("0", ["H!"], "pštrosie", "", "ANIMAL_PRODUCTS", "MEAT"),
    ("3", ["H"], "ryba údená, údené ryby (všetky druhy)", "", "ANIMAL_PRODUCTS", "MEAT"),
    ("3", ["H", "A"], "saláma", "", "ANIMAL_PRODUCTS", "MEAT"),
    ("3", ["H", "A"], "šunka (sušená, ošetrená)", "", "ANIMAL_PRODUCTS", "MEAT"),
    ("3", ["H", "A"], "sušená šunka", "", "ANIMAL_PRODUCTS", "MEAT"),
    ("0", ["H!"], "teľacie (čerstvé)", "", "ANIMAL_PRODUCTS", "MEAT"),
    ("3", ["H"], "údené mäso", "", "ANIMAL_PRODUCTS", "MEAT"),
    ("2", ["H!", "L"], "vnútornosti", "", "ANIMAL_PRODUCTS", "MEAT"),
    ("1", ["H"], "zverina", "Vyzreté, ale čerstvé mäso z diviny je často dobre tolerované.", "ANIMAL_PRODUCTS", "MEAT"),

    # ANIMAL PRODUCTS - FISH
    ("3", ["H", "A"], "ančovičky: sardely v konzerve, sardelová pasta", "", "ANIMAL_PRODUCTS", "FISH"),
    ("0", ["H!"], "pstruh obyčajný, dúhový", "Rýchlo podlieha skaze. Rýchle hromadenie histamínu.", "ANIMAL_PRODUCTS", "FISH"),
    ("0", ["H!", "A"], "ryba (čerstvo chytená, hlboko zmrazená)", "Veľmi závislé od čerstvosti a druhu.", "ANIMAL_PRODUCTS", "FISH"),
    ("3", ["H!", "A"], "ryba (kupovaná, chladená)", "Veľmi závislé od čerstvosti a druhu.", "ANIMAL_PRODUCTS", "FISH"),
    ("3", ["H", "A"], "sardely v konzerve, sardelová pasta", "", "ANIMAL_PRODUCTS", "FISH"),
    ("0", ["H!"], "sivoň americký", "Rýchlo podlieha skaze. Rýchle hromadenie histamínu.", "ANIMAL_PRODUCTS", "FISH"),
    ("3", ["H", "A"], "tuniak", "", "ANIMAL_PRODUCTS", "FISH"),
    ("2", [], "údený losos", "", "ANIMAL_PRODUCTS", "FISH"),

    # ANIMAL PRODUCTS - SEAFOOD
    ("2", ["H!", "L"], "garnáty, krevety", "", "ANIMAL_PRODUCTS", "SEAFOOD"),
    ("2", ["H!", "L"], "homár", "", "ANIMAL_PRODUCTS", "SEAFOOD"),
    ("2", ["H!", "L"], "krab", "", "ANIMAL_PRODUCTS", "SEAFOOD"),
    ("2", ["H!", "L"], "krevety", "", "ANIMAL_PRODUCTS", "SEAFOOD"),
    ("2", ["H!", "L"], "langusta", "", "ANIMAL_PRODUCTS", "SEAFOOD"),
    ("2", ["H!", "L"], "lastúrniky (mušle, ustrice, slávky, hrebenatky, ...)", "", "ANIMAL_PRODUCTS", "SEAFOOD"),
    ("2", ["H!", "L"], "mäkkýše", "", "ANIMAL_PRODUCTS", "SEAFOOD"),
    ("2", ["H!", "L"], "morské plody", "", "ANIMAL_PRODUCTS", "SEAFOOD"),
    ("2", ["H!", "L"], "plody mora", "", "ANIMAL_PRODUCTS", "SEAFOOD"),
    ("2", ["H!", "L"], "rak", "", "ANIMAL_PRODUCTS", "SEAFOOD"),
    ("2", ["H!", "L"], "ustrice", "", "ANIMAL_PRODUCTS", "SEAFOOD"),

    # ANIMAL PRODUCTS - OTHER
    ("0", [], "bravčová masť", "", "ANIMAL_PRODUCTS", "OTHER"),
    ("0", [], "sadlo", "", "ANIMAL_PRODUCTS", "OTHER"),

    # PLANT PRODUCTS - STARCHES
    ("0", [], "amarant", "U niektorých ľudí môže spôsobovať hnačky. Jedná sa o pseudoobilninu, nezamieňať s farbivom amarant.", "PLANT_PRODUCTS", "STARCHES"),
    ("0", [], "bataty, sladké zemiaky", "", "PLANT_PRODUCTS", "STARCHES"),
    ("1", [], "bulgur", "Parboiled pšenica", "PLANT_PRODUCTS", "STARCHES"),
    ("1", [], "chlieb", "Problémy spôsobuje prítomnosť: sladu, jódu, dlhej fermentácie kvasníc, pravdepodobne aj ATIs (inhibítori amyláz/triptáz) z obilnín.", "PLANT_PRODUCTS", "STARCHES"),
    ("0", [], "emmer, Triticum dicoccum", "", "PLANT_PRODUCTS", "STARCHES"),
    ("0", [], "gaštany", "", "PLANT_PRODUCTS", "STARCHES"),
    ("1", [], "jačmeň", "", "PLANT_PRODUCTS", "STARCHES"),
    ("2", [], "jačmenný slad, slad", "", "PLANT_PRODUCTS", "STARCHES"),
    ("0", [], "jam, bataty, sladké zemiaky", "", "PLANT_PRODUCTS", "STARCHES"),
    ("0", [], "kamut", "Vyberajte skôr staré odrody. Nové ATI variety sú kultivované a modifikované, zvyčajne nie dobre tolerované.", "PLANT_PRODUCTS", "STARCHES"),
    ("0", [], "konopné semená (Cannabis sativa)", "Nehalucinogénne odrody. Príliš veľa konopných bielkovín môže spôsobiť hnačku.", "PLANT_PRODUCTS", "STARCHES"),
    ("0", [], "konopný proteínový prášok", "Nehalucinogénne odrody. Príliš veľa konopných bielkovín môže spôsobiť hnačku.", "PLANT_PRODUCTS", "STARCHES"),
    ("0", [], "kukurica sladká, zrná kukurice: klas, čerstvá/pasterizovaná", "Ťažko stráviteľná.", "PLANT_PRODUCTS", "STARCHES"),
    ("0", [], "kukurica sladká, zrná kukurice: sušené (múka, kaša)", "", "PLANT_PRODUCTS", "STARCHES"),
    ("0", [], "kukurica sladká, zrná kukurice: z konzervy", "Ťažko stráviteľná. Pravdepodobne nevhodná po dlhom skladovaní alebo vo veľkom množstve.", "PLANT_PRODUCTS", "STARCHES"),
    ("0", [], "kukuričné lupienky (bez aditív ako sú slad alebo kyselina listová)", "Pozor na slad a kyselinu listovú", "PLANT_PRODUCTS", "STARCHES"),
    ("0", [], "maltodextrín", "", "PLANT_PRODUCTS", "STARCHES"),
    ("?", [], "maniok, kasava, cassava (koreňové hľuzy)", "Kyanid inhibuje príjem jódu. Niektoré detoxikačné metódy môžu produkovať histamín.", "PLANT_PRODUCTS", "STARCHES"),
    ("0", [], "ovos", "Vyhnite sa vitamínovaným produktom.", "PLANT_PRODUCTS", "STARCHES"),
    ("1", [], "pečivo", "Problémy spôsobuje prítomnosť: sladu, jódu, dlhej fermentácie kvasníc, pravdepodobne aj ATIs (inhibítori amyláz/triptáz) z obilnín.", "PLANT_PRODUCTS", "STARCHES"),
    ("2", [], "pohánka", "Problémy spôsobuje prítomnosť: sladu, jódu, dlhej fermentácie kvasníc, pravdepodobne aj ATIs (inhibítori amyláz/triptáz) z obilnín.", "PLANT_PRODUCTS", "STARCHES"),
    ("1", [], "pšenica", "Rôzne. Často spôsobujú tráviace problémy ako nafukovanie.", "PLANT_PRODUCTS", "STARCHES"),
    ("0", [], "pšenica khorasan (Triticum turgidum ssp. Turanicum)", "Vyberajte skôr staré odrody. Nové ATI variety sú kultivované a modifikované, zvyčajne nie dobre tolerované.", "PLANT_PRODUCTS", "STARCHES"),
    ("2", ["A", "L"], "pšeničné klíčky", "Putrescín, spermín, spermidín, kadaverín.", "PLANT_PRODUCTS", "STARCHES"),
    ("0", [], "pšeno", "", "PLANT_PRODUCTS", "STARCHES"),
    ("0", [], "quinoa", "Nie vždy dobre tolerovaná?", "PLANT_PRODUCTS", "STARCHES"),
    ("1", [], "raž", "Veľmi málo tolerované.", "PLANT_PRODUCTS", "STARCHES"),
    ("0", [], "ryža", "Po uvarení skladujte v chladničke maximálne 12 - 24 hodín.", "PLANT_PRODUCTS", "STARCHES"),
    ("0", [], "ryža divoká, ryža indiánska", "Nie je príbuzná s ostatnými druhmi ryže.", "PLANT_PRODUCTS", "STARCHES"),
    ("0", [], "ryžové chlebíčky, keksy", "Trocha menej tolerované ako čerstvo uvarená ryža.", "PLANT_PRODUCTS", "STARCHES"),
    ("0", [], "ryžové lupienky", "Pozor na obsah sladu a kyseliny listovej.", "PLANT_PRODUCTS", "STARCHES"),
    ("0", [], "ryžové rezance", "Trocha menej tolerované ako čerstvo uvarená ryža.", "PLANT_PRODUCTS", "STARCHES"),
    ("0", [], "sago (palmový škrob)", "", "PLANT_PRODUCTS", "STARCHES"),
    ("2", [], "slad, jačmenný slad", "", "PLANT_PRODUCTS", "STARCHES"),
    ("0", [], "sladké zemiaky, bataty", "", "PLANT_PRODUCTS", "STARCHES"),
    ("2", ["L"], "slnečnicové semienka", "", "PLANT_PRODUCTS", "STARCHES"),
    ("0", [], "špalda", "Vyberajte skôr staré odrody. Nové ATI variety sú kultivované a modifikované, zvyčajne nie dobre tolerované.", "PLANT_PRODUCTS", "STARCHES"),
    ("0", [], "tapioca, tapioka", "", "PLANT_PRODUCTS", "STARCHES"),
    ("0", [], "Triticum monococcum", "", "PLANT_PRODUCTS", "STARCHES"),
    ("0", [], "zelená špalda", "", "PLANT_PRODUCTS", "STARCHES"),
    ("0", [], "zemiaky, nové, so šupkou", "Tmavé miesto! Zelené škvrny sú toxické! Pravdepodobne nevhodné pre ľudí so salicylátovou intoleranciou.", "PLANT_PRODUCTS", "STARCHES"),
    ("0", [], "zemiaky, ošúpané", "Tmavé miesto! Zelené škvrny sú toxické! Pravdepodobne nevhodné pre ľudí so salicylátovou intoleranciou.", "PLANT_PRODUCTS", "STARCHES"),
    ("0", [], "zemiaky, so šupkou", "Tmavé miesto! Zelené škvrny sú toxické! Pravdepodobne nevhodné pre ľudí so salicylátovou intoleranciou.", "PLANT_PRODUCTS", "STARCHES"),
    ("1", [], "žito", "Veľmi málo tolerované.", "PLANT_PRODUCTS", "STARCHES"),
    ("0", [], "zizánia, ryža divoká", "Nie je príbuzná s ostatnými druhmi ryže.", "PLANT_PRODUCTS", "STARCHES"),

    # PLANT PRODUCTS - NUTS
    ("2", [], "arašidy", "", "PLANT_PRODUCTS", "NUTS"),
    ("0", [], "chufa", "Nie je to orech, ale hľúza.", "PLANT_PRODUCTS", "NUTS"),
    ("2", [], "chufa, zemné mandle, šáchor jedlý: pražené", "Nie je to orech, ale hľúza.", "PLANT_PRODUCTS", "NUTS"),
    ("1", ["A", "L"], "kešu", "", "PLANT_PRODUCTS", "NUTS"),
    ("1", ["L"], "lieskové orechy", "", "PLANT_PRODUCTS", "NUTS"),
    ("0", [], "makadamiové orechy, makadamové orechy", "", "PLANT_PRODUCTS", "NUTS"),
    ("1", [], "mandle", "Malé množstvo tolerované dobre. Môže spôsobovať problemy so spánkom.", "PLANT_PRODUCTS", "NUTS"),
    ("0", [], "para orechy", "Max. 1-2 orechy denne ako dobrý zdroj selénia.", "PLANT_PRODUCTS", "NUTS"),
    ("0", [], "pekanový orech", "", "PLANT_PRODUCTS", "NUTS"),
    ("1", [], "píniové semienka", "Niekoľko druhov. Možno nie všetky rovnako tolerované?", "PLANT_PRODUCTS", "NUTS"),
    ("0", [], "pistácie", "", "PLANT_PRODUCTS", "NUTS"),
    ("0", [], "šáchor jedlý", "Nie je to orech, ale hľúza.", "PLANT_PRODUCTS", "NUTS"),
    ("2", [], "šáchor jedlý, zemné mandle: pražené", "Nie je to orech, ale hľúza.", "PLANT_PRODUCTS", "NUTS"),
    ("0", [], "tigrie oriešky", "Nie je to orech, ale hľúza.", "PLANT_PRODUCTS", "NUTS"),
    ("2", [], "tigrie oriešky: pražené", "Nie je to orech, ale hľúza.", "PLANT_PRODUCTS", "NUTS"),
    ("3", ["A", "L"], "vlašské orechy", "", "PLANT_PRODUCTS", "NUTS"),
    ("0", [], "zemné mandle", "Nie je to orech, ale hľúza.", "PLANT_PRODUCTS", "NUTS"),
    ("2", [], "zemné mandle, šáchor jedlý: pražené", "Nie je to orech, ale hľúza.", "PLANT_PRODUCTS", "NUTS"),

    # PLANT PRODUCTS - FATS_OILS
    ("0", [], "bodliakový olej, saflorový", "", "PLANT_PRODUCTS", "FATS_OILS"),
    ("0", [], "kokosový olej", "Veľmi odporučený.", "PLANT_PRODUCTS", "FATS_OILS"),
    ("0", [], "ľanový olej", "", "PLANT_PRODUCTS", "FATS_OILS"),
    ("0", [], "margarín (bez aditív)", "Skontrolovať nevhodné aditíva.", "PLANT_PRODUCTS", "FATS_OILS"),
    ("0", [], "olej kokosový", "Veľmi odporučený.", "PLANT_PRODUCTS", "FATS_OILS"),
    ("0", [], "olej olivový", "Nevhodné pre ľudí so salycilátovou intoleranciou.", "PLANT_PRODUCTS", "FATS_OILS"),
    ("0", [], "olej palmový", "Neodporúča sa kvôli ekologickým dôvodom. Mimo toho, odporučený.", "PLANT_PRODUCTS", "FATS_OILS"),
    ("0", [], "olej repkový", "", "PLANT_PRODUCTS", "FATS_OILS"),
    ("0", [], "olej slnečnicový", "Jednorázovo bez problémov, dlhodobo môže mať zápalové účinky.", "PLANT_PRODUCTS", "FATS_OILS"),
    ("0", [], "olej z čiernej rasce", "antialergický", "PLANT_PRODUCTS", "FATS_OILS"),
    ("0", [], "olej z kukuričných klíčkov", "", "PLANT_PRODUCTS", "FATS_OILS"),
    ("0", [], "olej z pupalky dvojročnej (Oenothera biennis)", "", "PLANT_PRODUCTS", "FATS_OILS"),
    ("0", ["A"], "olej z tekvicových semien", "Za studena lisovaný olej z pražených tekvicových semienok. Obsahuje veľa spermidínu (biogénny amín). Napriek tomu sa toleruje v obvyklých množstvách.", "PLANT_PRODUCTS", "FATS_OILS"),
    ("2", [], "olej z vlašských orechov", "", "PLANT_PRODUCTS", "FATS_OILS"),
    ("0", [], "olej zo svetlice", "", "PLANT_PRODUCTS", "FATS_OILS"),
    ("0", [], "olivový olej", "Nevhodné pre ľudí so salycilátovou intoleranciou.", "PLANT_PRODUCTS", "FATS_OILS"),
    ("0", [], "repkový olej", "", "PLANT_PRODUCTS", "FATS_OILS"),
    ("1", [], "sójový olej", "", "PLANT_PRODUCTS", "FATS_OILS"),
    ("0", [], "svetlicový olej (bodliakový)", "", "PLANT_PRODUCTS", "FATS_OILS"),
    ("0", ["A"], "tekvicový olej", "Za studena lisovaný olej z pražených tekvicových semienok. Obsahuje veľa spermidínu (biogénny amín). Napriek tomu sa toleruje v obvyklých množstvách.", "PLANT_PRODUCTS", "FATS_OILS"),
    ("0", [], "večerný pupalkový olej", "", "PLANT_PRODUCTS", "FATS_OILS"),

    # PLANT PRODUCTS - VEGETABLES (partial list - there are many more)
    ("0", [], "artičoky", "", "PLANT_PRODUCTS", "VEGETABLES"),
    ("0", [], "asparágus", "", "PLANT_PRODUCTS", "VEGETABLES"),
    ("2", ["H", "L"], "avokádo", "", "PLANT_PRODUCTS", "VEGETABLES"),
    ("2", ["H"], "baklažán", "", "PLANT_PRODUCTS", "VEGETABLES"),
    ("?", [], "bambusové výhonky", "", "PLANT_PRODUCTS", "VEGETABLES"),
    ("2", [], "bôb", "", "PLANT_PRODUCTS", "VEGETABLES"),
    ("0", [], "bok choi", "", "PLANT_PRODUCTS", "VEGETABLES"),
    ("0", [], "brokolica", "", "PLANT_PRODUCTS", "VEGETABLES"),
    ("0", [], "čakanka", "", "PLANT_PRODUCTS", "VEGETABLES"),
    ("1", [], "cesnak", "V malých dávkach a po uvarení zvyčajne dobre tolerovaný.", "PLANT_PRODUCTS", "VEGETABLES"),
    ("2", ["H", "A"], "chilli omáčka, pálivá, fermentovaná", "Stimulujúca štipľavosť a biogénne amíny", "PLANT_PRODUCTS", "VEGETABLES"),
    ("1", ["L"], "chren", "", "PLANT_PRODUCTS", "VEGETABLES"),
    ("1", ["L"], "cibuľa", "Vo väčších množstvách nevhodná.", "PLANT_PRODUCTS", "VEGETABLES"),
    ("0", [], "cibuľa biela", "Ide o druh cibule s bielou šupkou, nie o klasickú cibuľu.", "PLANT_PRODUCTS", "VEGETABLES"),
    ("2", [], "cícer, cícer baraní", "", "PLANT_PRODUCTS", "VEGETABLES"),
    ("1", [], "čili paprička, čerstvá", "Pálenie môže dráždiť.", "PLANT_PRODUCTS", "VEGETABLES"),
    ("0", [], "cuketa, cukina", "", "PLANT_PRODUCTS", "VEGETABLES"),
    ("0", [], "dyňa (rôzne druhy)", "", "PLANT_PRODUCTS", "VEGETABLES"),
    ("0", [], "endívia", "", "PLANT_PRODUCTS", "VEGETABLES"),
    ("2", [], "fazuľa borlotti", "", "PLANT_PRODUCTS", "VEGETABLES"),
    ("0", [], "fenikel", "", "PLANT_PRODUCTS", "VEGETABLES"),
    ("1", [], "hrach siaty (zelený hrášok)", "", "PLANT_PRODUCTS", "VEGETABLES"),
    ("1", [], "hrášok", "", "PLANT_PRODUCTS", "VEGETABLES"),
    ("1", [], "kaleráb, kapusta obyčajná kalerábová", "", "PLANT_PRODUCTS", "VEGETABLES"),
    ("0", [], "kapusta červená", "", "PLANT_PRODUCTS", "VEGETABLES"),
    ("0", [], "kapusta čínska", "", "PLANT_PRODUCTS", "VEGETABLES"),
    ("3", ["H"], "kapusta kvasená", "", "PLANT_PRODUCTS", "VEGETABLES"),
    ("3", ["H"], "kapusta kyslá", "", "PLANT_PRODUCTS", "VEGETABLES"),
    ("1", ["L"], "kapusta ružičková", "", "PLANT_PRODUCTS", "VEGETABLES"),
    ("0", [], "kapusta, biela alebo zelená", "", "PLANT_PRODUCTS", "VEGETABLES"),
    ("0", [], "karfiol", "", "PLANT_PRODUCTS", "VEGETABLES"),
    ("2", ["L"], "kelp (morské riasy), Laminariales", "napr. Ako prísady v ochutených/bylinkových soliach.", "PLANT_PRODUCTS", "VEGETABLES"),
    ("0", [], "ľadový šalát", "", "PLANT_PRODUCTS", "VEGETABLES"),
    ("0", [], "mrkva", "", "PLANT_PRODUCTS", "VEGETABLES"),
    ("2", [], "olivy", "Zvyčajne fermentovaný, s ďalšími nevhodnými prísadami.", "PLANT_PRODUCTS", "VEGETABLES"),
    ("0", [], "pak choi", "", "PLANT_PRODUCTS", "VEGETABLES"),
    ("0", [], "paprika (sladká)", "", "PLANT_PRODUCTS", "VEGETABLES"),
    ("2", [], "paprika (štipľavá)", "", "PLANT_PRODUCTS", "VEGETABLES"),
    ("2", ["H", "L"], "paradajky", "", "PLANT_PRODUCTS", "VEGETABLES"),
    ("0", [], "paštrnák", "", "PLANT_PRODUCTS", "VEGETABLES"),
    ("0", [], "polníček", "", "PLANT_PRODUCTS", "VEGETABLES"),
    ("1", [], "pór", "V malých dávkach dobre tolerovaný.", "PLANT_PRODUCTS", "VEGETABLES"),
    ("2", ["H", "L"], "rajčiaky", "", "PLANT_PRODUCTS", "VEGETABLES"),
    ("0", [], "reďkovky (rod Raphanus), jemné odrody", "", "PLANT_PRODUCTS", "VEGETABLES"),
    ("1", [], "reďkovky (rod Raphanus), ostré odrody", "", "PLANT_PRODUCTS", "VEGETABLES"),
    ("0", [], "repa červená", "", "PLANT_PRODUCTS", "VEGETABLES"),
    ("2", ["L"], "rukola", "", "PLANT_PRODUCTS", "VEGETABLES"),
    ("0", [], "šalát ľadový", "", "PLANT_PRODUCTS", "VEGETABLES"),
    ("0", [], "šalát: listové šaláty", "Hodnotenie je pre rastlinu, nie hotový produkt.", "PLANT_PRODUCTS", "VEGETABLES"),
    ("2", [], "sója (sójové bôby, sójová múka)", "", "PLANT_PRODUCTS", "VEGETABLES"),
    ("2", [], "šošovica, šošovica jedlá", "", "PLANT_PRODUCTS", "VEGETABLES"),
    ("0", [], "špargľa", "", "PLANT_PRODUCTS", "VEGETABLES"),
    ("2", [], "špenát", "", "PLANT_PRODUCTS", "VEGETABLES"),
    ("2", ["A", "L"], "strukoviny (sója, fazuľa, hrach, šošovica)", "", "PLANT_PRODUCTS", "VEGETABLES"),
    ("2", ["L"], "strukoviny a fazule", "Platí pre všetky druhy a odrody. V niektorých prípadoch môžu však existovať výnimky.", "PLANT_PRODUCTS", "VEGETABLES"),
    ("0", [], "tekvica", "", "PLANT_PRODUCTS", "VEGETABLES"),
    ("0", [], "topinambur, slnečnica hľuznatá, slnečnica topinambur", "Hľuza pripravená ako koreňová zelenina. Nevhodné pre osoby citlivé na salicyláty.", "PLANT_PRODUCTS", "VEGETABLES"),
    ("0", [], "uhorka", "", "PLANT_PRODUCTS", "VEGETABLES"),
    ("2", ["H"], "uhorky naložené v slanom náleve (fermentované!)", "Uhorky naložené v slanom náleve a konzervované fermentáciou kyselinou mliečnou.", "PLANT_PRODUCTS", "VEGETABLES"),
    ("2", ["H"], "zaváraná zelenina", "Môžu byť tolerované v závislosti od zložiek (liehový ocot alebo kyselina octová namiesto octu; bez horčice). Nezamieňať s kvasenými nakladanými uhorkami!", "PLANT_PRODUCTS", "VEGETABLES"),
    ("2", ["H"], "zavárané uhorky", "Môžu byť tolerované v závislosti od zložiek (liehový ocot alebo kyselina octová namiesto octu; bez horčice). Nezamieňať s kvasenými nakladanými uhorkami!", "PLANT_PRODUCTS", "VEGETABLES"),
    ("1", [], "zelené fazuľky", "V niektorých prípadoch veľmi dobre tolerované.", "PLANT_PRODUCTS", "VEGETABLES"),
    ("0", [], "zeler (Apium graveolens var. dulce)", "", "PLANT_PRODUCTS", "VEGETABLES"),
    ("0", [], "zeler (Apium graveolens var. rapaceum)", "", "PLANT_PRODUCTS", "VEGETABLES"),
    ("2", ["H"], "žihľava", "", "PLANT_PRODUCTS", "VEGETABLES"),

    # PLANT PRODUCTS - HERBS
    ("0", [], "bazalka", "", "PLANT_PRODUCTS", "HERBS"),
    ("1", ["L"], "cesnak medvedí", "Malé množstvo tolerované dobre.", "PLANT_PRODUCTS", "HERBS"),
    ("2", [], "ďatelina zelená (druhy Trigonella a Trifolium)", "napr. Senovka grécka modrá", "PLANT_PRODUCTS", "HERBS"),
    ("2", [], "grécke seno", "", "PLANT_PRODUCTS", "HERBS"),
    ("0", [], "kerblík třebule, třebule pravá (Anthriscus cerefolium)", "", "PLANT_PRODUCTS", "HERBS"),
    ("1", [], "kôpor, kôpor voňavý (Anethum graveolens)", "Malé množstvá bez problémov, nevhodné pri salicylátovej intolerancii.", "PLANT_PRODUCTS", "HERBS"),
    ("0", [], "mäta (Mentha spicata, spearmint)", "Nevhodná pri salicylátovej intolerancii.", "PLANT_PRODUCTS", "HERBS"),
    ("0", [], "mäta pieporná, mäta", "Nevhodná pri salicylátovej intolerancii.", "PLANT_PRODUCTS", "HERBS"),
    ("1", ["L"], "medvedí cesnak", "Malé množstvo tolerované dobre.", "PLANT_PRODUCTS", "HERBS"),
    ("0", [], "oregano", "", "PLANT_PRODUCTS", "HERBS"),
    ("1", [], "pažítka", "Nevhodná vo väčších množstvách.", "PLANT_PRODUCTS", "HERBS"),
    ("0", [], "petržlen", "", "PLANT_PRODUCTS", "HERBS"),
    ("0", [], "rozmarín", "", "PLANT_PRODUCTS", "HERBS"),
    ("0", [], "šalvia", "", "PLANT_PRODUCTS", "HERBS"),
    ("0", [], "saturejka (Satureja hortensis, Satureja montana)", "", "PLANT_PRODUCTS", "HERBS"),
    ("2", [], "senovka grécka", "", "PLANT_PRODUCTS", "HERBS"),
    ("2", [], "senovka grécka modrá", "", "PLANT_PRODUCTS", "HERBS"),

    # PLANT PRODUCTS - FRUIT (partial list)
    ("0", [], "acerola", "", "PLANT_PRODUCTS", "FRUIT"),
    ("2", ["A", "L"], "ananás", "", "PLANT_PRODUCTS", "FRUIT"),
    ("1", [], "arbus, dyňa červená", "Podozrenie na liberačné účinky", "PLANT_PRODUCTS", "FRUIT"),
    ("2", ["H", "L"], "avokádo", "", "PLANT_PRODUCTS", "FRUIT"),
    ("2", ["A"], "banán", "(Čím zelenší, tým lepsie tolerovaný?)", "PLANT_PRODUCTS", "FRUIT"),
    ("0", [], "baza čierna", "", "PLANT_PRODUCTS", "FRUIT"),
    ("0", [], "broskyňa", "", "PLANT_PRODUCTS", "FRUIT"),
    ("0", [], "brusnica", "", "PLANT_PRODUCTS", "FRUIT"),
    ("0", [], "čerešne", "Sporné.", "PLANT_PRODUCTS", "FRUIT"),
    ("2", ["A", "L"], "citrón", "", "PLANT_PRODUCTS", "FRUIT"),
    ("2", ["L"], "citrónová kôra", "", "PLANT_PRODUCTS", "FRUIT"),
    ("2", ["A", "L"], "citrusy", "", "PLANT_PRODUCTS", "FRUIT"),
    ("0", [], "čučoriedky", "", "PLANT_PRODUCTS", "FRUIT"),
    ("0", [], "ďatle (sušené)", "", "PLANT_PRODUCTS", "FRUIT"),
    ("0", [], "dračie ovocie, pitahaya, pitaya", "Pestuje sa niekoľko druhov. Zatiaľ nie je isté, či sú všetky kompatibilné.", "PLANT_PRODUCTS", "FRUIT"),
    ("0", [], "dula", "", "PLANT_PRODUCTS", "FRUIT"),
    ("0", [], "egreš", "", "PLANT_PRODUCTS", "FRUIT"),
    ("0", [], "figy (čerstvé alebo sušené)", "Môžu spôsobiť preháňanie.", "PLANT_PRODUCTS", "FRUIT"),
    ("0", [], "goji", "", "PLANT_PRODUCTS", "FRUIT"),
    ("0", [], "granátové jablko", "", "PLANT_PRODUCTS", "FRUIT"),
    ("2", ["A", "L"], "grep, grapefruit", "", "PLANT_PRODUCTS", "FRUIT"),
    ("2", [], "guava", "", "PLANT_PRODUCTS", "FRUIT"),
    ("0", [], "hrozienka", "Pokial nie sú sírené. Nevhodné pri salicylátovej intolerancii.", "PLANT_PRODUCTS", "FRUIT"),
    ("0", [], "hrozno", "", "PLANT_PRODUCTS", "FRUIT"),
    ("1", ["A"], "hruška", "", "PLANT_PRODUCTS", "FRUIT"),
    ("0", [], "hurmi kaki", "", "PLANT_PRODUCTS", "FRUIT"),
    ("0", [], "jablko", "", "PLANT_PRODUCTS", "FRUIT"),
    ("0", [], "jablko: golden delicious", "", "PLANT_PRODUCTS", "FRUIT"),
    ("2", ["A", "L"], "jahoda", "", "PLANT_PRODUCTS", "FRUIT"),
    ("0", [], "josta", "Hybrid egrešu a čiernej ríbezle.", "PLANT_PRODUCTS", "FRUIT"),
    ("2", ["A", "L"], "kakao, kakaový prášok (čokoláda atď.)", "", "PLANT_PRODUCTS", "FRUIT"),
    ("0", [], "kakaové maslo", "Prevažne dobre tolerovaná.", "PLANT_PRODUCTS", "FRUIT"),
    ("0", [], "kaki", "", "PLANT_PRODUCTS", "FRUIT"),
    ("0", [], "karambola", "", "PLANT_PRODUCTS", "FRUIT"),
    ("2", ["L"], "kiwi", "", "PLANT_PRODUCTS", "FRUIT"),
    ("1", [], "kokos, kokosové mlieko", "Dobrý zdroj selénu.", "PLANT_PRODUCTS", "FRUIT"),
    ("0", [], "kustovnica čínska", "", "PLANT_PRODUCTS", "FRUIT"),
    ("0", [], "liči", "", "PLANT_PRODUCTS", "FRUIT"),
    ("3", ["A", "L"], "limetka", "", "PLANT_PRODUCTS", "FRUIT"),
    ("2", [], "malina, maliny", "", "PLANT_PRODUCTS", "FRUIT"),
    ("2", [], "mandarinky", "", "PLANT_PRODUCTS", "FRUIT"),
    ("1", [], "mango", "Diskutabilné. Veľmi často dobre tolerované.", "PLANT_PRODUCTS", "FRUIT"),
    ("0", [], "marhuľa", "", "PLANT_PRODUCTS", "FRUIT"),
    ("0", [], "melón (okrem vodového)", "Podozrenie na občasné liberačné účinky (kvôli pesticídom/postrekom?)", "PLANT_PRODUCTS", "FRUIT"),
    ("1", [], "melón vodový, melón červený, melón vodný, dyňa červená", "Podozrenie na liberačné účinky", "PLANT_PRODUCTS", "FRUIT"),
    ("0", [], "moruša", "", "PLANT_PRODUCTS", "FRUIT"),
    ("0", [], "nektarinka", "", "PLANT_PRODUCTS", "FRUIT"),
    ("0", [], "opuncia", "Vyhnite sa kontaktu kože s tŕňmi.", "PLANT_PRODUCTS", "FRUIT"),
    ("0", [], "ostružina", "", "PLANT_PRODUCTS", "FRUIT"),
    ("2", ["A", "L"], "papája", "", "PLANT_PRODUCTS", "FRUIT"),
    ("0", [], "pepino (Solanum muricatum)", "", "PLANT_PRODUCTS", "FRUIT"),
    ("3", ["A", "L"], "pomaranč", "", "PLANT_PRODUCTS", "FRUIT"),
    ("3", ["L"], "pomarančová kôra", "", "PLANT_PRODUCTS", "FRUIT"),
    ("0", [], "rakytník", "", "PLANT_PRODUCTS", "FRUIT"),
    ("1", [], "rebarbora", "Sporné. Veľmi často dobre tolerované. Obsahuje oxaláty.", "PLANT_PRODUCTS", "FRUIT"),
    ("0", [], "ríbezľa čierna, ríbezle čierne", "", "PLANT_PRODUCTS", "FRUIT"),
    ("0", [], "ríbezle červené", "", "PLANT_PRODUCTS", "FRUIT"),
    ("1", ["L"], "šípky", "", "PLANT_PRODUCTS", "FRUIT"),
    ("1", ["L"], "slivka, sušená slivka", "", "PLANT_PRODUCTS", "FRUIT"),
    ("1", [], "slivky", "Tolerované lepšie než iné kultivary sliviek.", "PLANT_PRODUCTS", "FRUIT"),
    ("0", [], "višňa", "", "PLANT_PRODUCTS", "FRUIT"),

    # PLANT PRODUCTS - SEEDS
    ("0", [], "chia semiačka", "", "PLANT_PRODUCTS", "SEEDS"),
    ("0", [], "ľanové semienko", "", "PLANT_PRODUCTS", "SEEDS"),
    ("0", [], "psyllium", "Môže byť užitočné pri hnačke ako aj pri zápche.", "PLANT_PRODUCTS", "SEEDS"),
    ("1", [], "sezam", "V niektorých prípadoch môže vyvolávať hnačky, ale často sa dobre znáša.", "PLANT_PRODUCTS", "SEEDS"),
    ("0", ["A"], "tekvicové semiačka", "Obsahuje veľa spermidínu (biogénny amín). Napriek tomu sa toleruje v obvyklých množstvách.", "PLANT_PRODUCTS", "SEEDS"),

    # PLANT PRODUCTS - MUSHROOMS_ALGAE
    ("3", ["L"], "červené riasy", "Extrémne bohaté na jód.", "PLANT_PRODUCTS", "MUSHROOMS_ALGAE"),
    ("3", ["L"], "chaluhy", "Extrémne bohaté na jód.", "PLANT_PRODUCTS", "MUSHROOMS_ALGAE"),
    ("3", ["L"], "hnedé riasy", "Extrémne bohaté na jód.", "PLANT_PRODUCTS", "MUSHROOMS_ALGAE"),
    ("2", [], "hríb smrekový", "", "PLANT_PRODUCTS", "MUSHROOMS_ALGAE"),
    ("2", [], "hríby", "", "PLANT_PRODUCTS", "MUSHROOMS_ALGAE"),
    ("2", [], "huby", "", "PLANT_PRODUCTS", "MUSHROOMS_ALGAE"),
    ("3", ["L"], "kelp", "Extrémne bohaté na jód.", "PLANT_PRODUCTS", "MUSHROOMS_ALGAE"),
    ("0", [], "kvasnice (čerstvé, sušené, všetky formy)", "Dobre tolerované pokiaľ sú vyrobené za prísnych hygienických podmienok. Výnimky: Npečivo, najmä ak je s dlhou dobou fermentácie. Príliš vysoký obsah glutamátov.", "PLANT_PRODUCTS", "MUSHROOMS_ALGAE"),
    ("0", [], "lingzhi, Ganoderma lingzhi, reishi", "Je označovaná za antialergickú \"liečivú hubu\". Vzhľadom na nedostatok vlastných skúseností zatiaľ neexistuje jednoznačná klasifikácia.", "PLANT_PRODUCTS", "MUSHROOMS_ALGAE"),
    ("3", ["L"], "morské riasy", "Extrémne bohaté na jód.", "PLANT_PRODUCTS", "MUSHROOMS_ALGAE"),
    ("3", ["L"], "riasy", "Extrémne bohaté na jód.", "PLANT_PRODUCTS", "MUSHROOMS_ALGAE"),
    ("1", ["A"], "šampiňóny", "", "PLANT_PRODUCTS", "MUSHROOMS_ALGAE"),
    ("2", [], "smrčok", "", "PLANT_PRODUCTS", "MUSHROOMS_ALGAE"),
    ("0", [], "spirulina, spirulína (Arthrospira)", "", "PLANT_PRODUCTS", "MUSHROOMS_ALGAE"),
    ("1", [], "vodný kefír, vodový kefír", "Môže byť dostatočne kompatibilný, ak neobsahuje nekompatibilné zložky. Riziko: Kontaminácia nepriaznivými mikroorganizmami.", "PLANT_PRODUCTS", "MUSHROOMS_ALGAE"),
    ("3", ["L"], "wakame riasy", "Extrémne bohaté na jód.", "PLANT_PRODUCTS", "MUSHROOMS_ALGAE"),
    ("3", ["L"], "zelené riasy", "Extrémne bohaté na jód.", "PLANT_PRODUCTS", "MUSHROOMS_ALGAE"),

    # PLANT PRODUCTS - SWEETENERS
    ("0", [], "agáve nektár, agáve sirup", "Vysoký obsah fruktózy.", "PLANT_PRODUCTS", "SWEETENERS"),
    ("0", [], "brezový cukor, xylitol, xylit, E967", "", "PLANT_PRODUCTS", "SWEETENERS"),
    ("0", [], "cukor (repkový, trstinový)", "Používať striedmo, nie ako hlavný výživok.", "PLANT_PRODUCTS", "SWEETENERS"),
    ("0", [], "dextróza", "Glukózový sirup môže obsahovat vysoký obsah fruktózy, glukóza fruktózu neobsahuje.", "PLANT_PRODUCTS", "SWEETENERS"),
    ("0", [], "fruktóza", "Veľké množstvo môže spôsobiť tráviace problémy.", "PLANT_PRODUCTS", "SWEETENERS"),
    ("0", [], "glukóza", "Glukózový sirup môže obsahovat vysoký obsah fruktózy, glukóza fruktózu neobsahuje.", "PLANT_PRODUCTS", "SWEETENERS"),
    ("0", [], "invertný cukor", "", "PLANT_PRODUCTS", "SWEETENERS"),
    ("0", [], "izomalt, E953", "Ťažko stráviteľný. Nadmerná konzumácia môže mať laxatívny účinok.", "PLANT_PRODUCTS", "SWEETENERS"),
    ("0", [], "javorový sirup", "", "PLANT_PRODUCTS", "SWEETENERS"),
    ("0", [], "karamel (skaramelizovaný cukor)", "", "PLANT_PRODUCTS", "SWEETENERS"),
    ("2", [], "koreň sladkého drievka", "", "PLANT_PRODUCTS", "SWEETENERS"),
    ("0", [], "laktóza (mliečny cukor)", "", "PLANT_PRODUCTS", "SWEETENERS"),
    ("0", [], "maltóza, sladový cukor", "", "PLANT_PRODUCTS", "SWEETENERS"),
    ("0", [], "med", "Diskutabilné. Sporné. Obsahuje prirodzene vysoký obsah kyseliny benzoovej.", "PLANT_PRODUCTS", "SWEETENERS"),
    ("0", [], "sacharóza", "Používať striedmo, nie ako hlavný výživok.", "PLANT_PRODUCTS", "SWEETENERS"),
    ("2", [], "sladový extrakt", "", "PLANT_PRODUCTS", "SWEETENERS"),
    ("0", [], "sorbitol, sorbitolový cukor, E420, glucitol", "Preháňadlo, diuretikum. Nezlúčiteľné s intoleranciou sorbitolu a dedičnou fruktózovou intoleranciou.", "PLANT_PRODUCTS", "SWEETENERS"),
    ("0", [], "stévia (listy, tekuté sladidlo, prášok)", "", "PLANT_PRODUCTS", "SWEETENERS"),
    ("1", [], "umelé sladidlá", "Sukralóza je tolerovaná.", "PLANT_PRODUCTS", "SWEETENERS"),
    ("0", [], "xylitol, xylit, brezový cukor, E967", "", "PLANT_PRODUCTS", "SWEETENERS"),

    # PLANT PRODUCTS - SPICES (partial list)
    ("2", [], "biele korenie", "Malé množstvo tolerované dobre.", "PLANT_PRODUCTS", "SPICES"),
    ("0", [], "bobkový list", "Malé množstá tolerované dobre, pre väčšie nedostatok skúseností.", "PLANT_PRODUCTS", "SPICES"),
    ("0", [], "borievka (bobule)", "", "PLANT_PRODUCTS", "SPICES"),
    ("2", [], "bujón (kvôli kvasnicovému extraktu/mäsovému extrakt/glutamánu)", "Takmer vždy obsahuje nevhodné prísady/aditíva (glutamát, kvasnicový extrakt, korenie/arómy/príchute, mäsové výťažky, nekompatibilnú zeleninu.", "PLANT_PRODUCTS", "SPICES"),
    ("0", [], "černuška siata", "antialergický", "PLANT_PRODUCTS", "SPICES"),
    ("2", [], "čierne korenie", "Malé množstvo tolerované dobre.", "PLANT_PRODUCTS", "SPICES"),
    ("2", ["L"], "horčičné semienko", "Horčičné semienka a výrobky z nich.", "PLANT_PRODUCTS", "SPICES"),
    ("0", [], "jalovec (bobule)", "", "PLANT_PRODUCTS", "SPICES"),
    ("0", [], "kardamón", "Používať striedmo. Ako korenie sa predáva viacero odrôd (rôzna miera tolerancie?).", "PLANT_PRODUCTS", "SPICES"),
    ("2", [], "kari", "", "PLANT_PRODUCTS", "SPICES"),
    ("0", [], "klinček", "Malé množstvo tolerované dobre, žiadne skúsenosti s väčším množstvom.", "PLANT_PRODUCTS", "SPICES"),
    ("0", [], "kmín", "Pozitivní efekt: trávení těžkých jídel. Nezaměňovat s kmínem římským.", "PLANT_PRODUCTS", "SPICES"),
    ("0", [], "koriander", "Dobre tolerované iba malé množstvo.", "PLANT_PRODUCTS", "SPICES"),
    ("0", [], "kurkuma", "", "PLANT_PRODUCTS", "SPICES"),
    ("2", ["L"], "kvasnicový extrakt", "Chemická premena na glutamát.", "PLANT_PRODUCTS", "SPICES"),
    ("1", [], "mak", "Malé množstá tolerované dobre, pre väčšie nedostatok skúseností.", "PLANT_PRODUCTS", "SPICES"),
    ("2", [], "mäsový extrakt", "", "PLANT_PRODUCTS", "SPICES"),
    ("1", [], "muškátový oriešok", "Malé množstá tolerované dobre, pre väčšie nedostatok skúseností.", "PLANT_PRODUCTS", "SPICES"),
    ("3", ["H"], "ocot: balzamiko", "", "PLANT_PRODUCTS", "SPICES"),
    ("1", ["H"], "ocot: jablčný", "Vždy skontrolovať obsah aditív.", "PLANT_PRODUCTS", "SPICES"),
    ("0", [], "ocot: kvasný, liehový", "Nízkohistamínový, ale nie bezhistamínový. Používať striedmo. Vždy skontrolovať obsah aditív.", "PLANT_PRODUCTS", "SPICES"),
    ("3", ["H"], "ocot: vínny (z bieleho vína)", "", "PLANT_PRODUCTS", "SPICES"),
    ("3", ["H"], "ocot: vínny (z červeného vína)", "", "PLANT_PRODUCTS", "SPICES"),
    ("2", [], "paprika pálivá", "Dráždi črevá.", "PLANT_PRODUCTS", "SPICES"),
    ("0", [], "paprika sladká", "", "PLANT_PRODUCTS", "SPICES"),
    ("0", [], "rasca", "Pozitivní efekt: trávení těžkých jídel. Nezaměňovat s kmínem římským.", "PLANT_PRODUCTS", "SPICES"),
    ("0", [], "rasca čierna", "antialergický", "PLANT_PRODUCTS", "SPICES"),
    ("2", ["L"], "rasca rímska", "", "PLANT_PRODUCTS", "SPICES"),
    ("0", [], "rímsky koriander", "antialergický", "PLANT_PRODUCTS", "SPICES"),
    ("0", [], "škorica", "", "PLANT_PRODUCTS", "SPICES"),
    ("3", [], "sójová omáčka", "", "PLANT_PRODUCTS", "SPICES"),
    ("0", [], "tymián", "", "PLANT_PRODUCTS", "SPICES"),
    ("1", [], "vanilka, vanilkový prášok, vanilkový cukor", "Tolerovaná v malých množstvích. Fermentácia! Možné stopy siričitanov?", "PLANT_PRODUCTS", "SPICES"),
    ("1", [], "vanilkový extrakt", "", "PLANT_PRODUCTS", "SPICES"),
    ("1", [], "zázvor", "Malé množstvo tolerované dobre.", "PLANT_PRODUCTS", "SPICES"),

    # BEVERAGES - WATER
    ("0", [], "minerálna voda, neperlivá", "", "BEVERAGES", "WATER"),
    ("1", [], "termálna voda s obsahom síry, fluóru, jódu a kyseliny uhličitej", "", "BEVERAGES", "WATER"),
    ("0", [], "voda z vodovodu", "", "BEVERAGES", "WATER"),

    # BEVERAGES - ALCOHOLIC
    ("3", ["L", "B"], "alkohol", "", "BEVERAGES", "ALCOHOLIC"),
    ("3", ["H", "A", "L", "B"], "alkoholické nápoje", "", "BEVERAGES", "ALCOHOLIC"),
    ("2", ["H", "A", "L", "B"], "brandy", "", "BEVERAGES", "ALCOHOLIC"),
    ("3", ["L", "B"], "etanol", "", "BEVERAGES", "ALCOHOLIC"),
    ("2", ["L", "B"], "liehovina, číra", "", "BEVERAGES", "ALCOHOLIC"),
    ("3", ["H", "A", "L", "B"], "liehovina, prifarbená, ochutená", "", "BEVERAGES", "ALCOHOLIC"),
    ("2", ["L", "B"], "pálenka, číra", "", "BEVERAGES", "ALCOHOLIC"),
    ("3", ["H", "A", "L", "B"], "pálenka, prifarbená, ochutená", "", "BEVERAGES", "ALCOHOLIC"),
    ("2", ["H", "A", "L", "B"], "pivo", "", "BEVERAGES", "ALCOHOLIC"),
    ("2", ["H", "A", "L", "B"], "rum", "", "BEVERAGES", "ALCOHOLIC"),
    ("3", ["H", "A", "L", "B"], "šampanské", "", "BEVERAGES", "ALCOHOLIC"),
    ("3", ["H", "A", "L", "B"], "šumivé víno", "", "BEVERAGES", "ALCOHOLIC"),
    ("3", ["H", "A", "L", "B"], "víno", "", "BEVERAGES", "ALCOHOLIC"),
    ("1", ["L", "B"], "víno bezhistamínové (<0.1 mg/l)", "Stále obsahuje alkohol a siričitany. Vhodné na varenie, po vyprchaní alkoholu dobre tolerované.", "BEVERAGES", "ALCOHOLIC"),
    ("2", ["H", "A", "L", "B"], "víno: biele", "", "BEVERAGES", "ALCOHOLIC"),
    ("3", ["H", "A", "L", "B"], "víno: červené", "", "BEVERAGES", "ALCOHOLIC"),
    ("2", ["H", "A", "L", "B"], "víno: Schilcherwein", "", "BEVERAGES", "ALCOHOLIC"),

    # BEVERAGES - TEAS
    ("0", [], "anízový čaj", "", "BEVERAGES", "TEAS"),
    ("1", [], "bylinne čaje z liečivých bylín (najmä zmesi)", "Nekompatibilné prísady zatiaľ neidentifikované.", "BEVERAGES", "TEAS"),
    ("0", [], "čaj verbena", "Má ukľudňijúci efekt na tráviacu a nervovú sústavu.", "BEVERAGES", "TEAS"),
    ("2", ["H", "B"], "čierny čaj", "", "BEVERAGES", "TEAS"),
    ("0", [], "feniklový čaj", "", "BEVERAGES", "TEAS"),
    ("0", [], "kamilkový čaj", "", "BEVERAGES", "TEAS"),
    ("0", [], "kmínový čaj, rascový čaj", "", "BEVERAGES", "TEAS"),
    ("0", [], "lipový čaj", "", "BEVERAGES", "TEAS"),
    ("1", ["B"], "maté", "", "BEVERAGES", "TEAS"),
    ("0", [], "mätový čaj", "", "BEVERAGES", "TEAS"),
    ("0", [], "roiboos", "Varovanie: Skontrolujte zloženie. Čajové zmesi roiboosu a nekompatibilných zložiek sú často predávané pod názvom Roiboos.", "BEVERAGES", "TEAS"),
    ("0", [], "šalviový čaj", "", "BEVERAGES", "TEAS"),
    ("1", ["B"], "zelený čaj", "", "BEVERAGES", "TEAS"),
    ("1", ["H"], "žihľavový čaj", "", "BEVERAGES", "TEAS"),

    # BEVERAGES - JUICES
    ("0", [], "brusnicový nektár", "", "BEVERAGES", "JUICES"),
    ("3", ["L"], "citrónová šťava, koncentrát citrónovej šťavy", "", "BEVERAGES", "JUICES"),
    ("2", ["L"], "pomarančový džús", "", "BEVERAGES", "JUICES"),

    # BEVERAGES - VEGETABLE_JUICES
    ("2", ["L"], "paradajkový džús", "", "BEVERAGES", "VEGETABLE_JUICES"),

    # BEVERAGES - CAFFEINATED
    ("2", [], "Coca-Cola", "Viď tiež kofeínové, perlivé nápoje, aróma", "BEVERAGES", "CAFFEINATED"),
    ("2", [], "Cola", "Viď tiež kofeínové, perlivé nápoje, aróma", "BEVERAGES", "CAFFEINATED"),
    ("2", ["B"], "energetické nápoje", "Teobromín inhibuje DAO.", "BEVERAGES", "CAFFEINATED"),
    ("1", [], "espresso", "Tolerované lepšie ako káva, ale stále obsahuje kofeín.", "BEVERAGES", "CAFFEINATED"),
    ("1", [], "káva", "Kofeín stimuluje nervy a črevné bunky, čo môže aktivovať žírne bunky.", "BEVERAGES", "CAFFEINATED"),
    ("2", [], "kolové nápoje", "Viď tiež kofeínové, perlivé nápoje, aróma", "BEVERAGES", "CAFFEINATED"),

    # BEVERAGES - PLANT_MILKS
    ("1", [], "ovsený nápoj, ovsené mlieko", "Môže obsahovať malé množstvá histamínu kvôli enzymatickej fermentácii.", "BEVERAGES", "PLANT_MILKS"),
    ("1", [], "ryžové mlieko, ryžový nápoj", "Môže obsahovať malé množstvá histamínu kvôli enzymatickej fermentácii.", "BEVERAGES", "PLANT_MILKS"),
    ("2", [], "sójové mlieko, sójový nápoj", "", "BEVERAGES", "PLANT_MILKS"),

    # BEVERAGES - SOFT_DRINKS
    ("0", [], "bazový sirup", "", "BEVERAGES", "SOFT_DRINKS"),
    ("2", [], "čokoládové nápoje", "", "BEVERAGES", "SOFT_DRINKS"),
    ("2", [], "kakaové nápoje", "", "BEVERAGES", "SOFT_DRINKS"),
    ("1", [], "limonády", "Záleží od zloženia.", "BEVERAGES", "SOFT_DRINKS"),
    ("1", [], "sladké perlivé nápoje", "Záleží od zloženia.", "BEVERAGES", "SOFT_DRINKS"),
    ("1", [], "sóda", "Záleží od zloženia.", "BEVERAGES", "SOFT_DRINKS"),
    ("2", [], "varená čokoláda", "", "BEVERAGES", "SOFT_DRINKS"),

    # DIETARY SUPPLEMENTS
    ("2", ["A", "L"], "guarana, guaraná (Paullinia cupana)", "Ovocie obsahuje kofeín.", "DIETARY_SUPPLEMENTS", None),
    ("2", ["L"], "iodizovaná stolová soľ", "", "DIETARY_SUPPLEMENTS", None),
    ("3", ["L"], "jód", "", "DIETARY_SUPPLEMENTS", None),
    ("3", ["L"], "jodid draselný (napr. aditívum v soli)", "", "DIETARY_SUPPLEMENTS", None),
    ("2", ["L"], "kyselina folová, kyselina listová, vitamín B9", "Diskutabilné. Iný názov: kyselina pterol-L-glutámová (podobná kyseline glutámovej/glutamátom?).", "DIETARY_SUPPLEMENTS", None),
    ("2", ["B"], "teobromín", "", "DIETARY_SUPPLEMENTS", None),
    ("1", [], "vápník", "V malých množstvách je životne dôležitý, vo vysokých dávkach aktivuje žírne bunky", "DIETARY_SUPPLEMENTS", None),
    ("0", [], "výhonok jedle, jedľové púčiky", "Napr. cukrový extrakt ako nátierka na chlieb", "DIETARY_SUPPLEMENTS", None),

    # PREPARATIONS
    ("1", [], "čokoláda biela", "Väčšinou dobre tolerovaná.", "PREPARATIONS", None),
    ("2", ["A"], "čokoláda mliečna, horká", "Tyramín, fenyletylamín.", "PREPARATIONS", None),
    ("2", ["H", "L"], "horčica", "Pripravená (zmes) z horčičného semienka, octu, atď.", "PREPARATIONS", None),
    ("2", [], "kimčchi", "Fermentované. V závislosti od zložiek, mikroorganizmov a výrobného procesu sú väčšinou nezlučiteľné.", "PREPARATIONS", None),
    ("1", [], "marcipán", "Malé množstvá dobre tolerované, ak neobsahuje nepovoleniéé zložky.", "PREPARATIONS", None),
    ("2", ["L"], "pelendrek", "", "PREPARATIONS", None),
    ("1", ["H!"], "seitan", "V závislosti od čerstvosti a použitých surovín!", "PREPARATIONS", None),
    ("0", [], "sladová múka", "Slad (extrakt) je nezlučiteľný. Pečivo so sladovou múkou sa však často znáša dostatočne dobre.", "PREPARATIONS", None),
    ("2", [], "tofu", "", "PREPARATIONS", None),
]


def convert_flag(flag: str) -> str:
    """Convert short flag to full name."""
    if flag == "H!":
        return "FAST_SPOILAGE"
    elif flag == "H":
        return "HIGH_HISTAMINE"
    elif flag == "A":
        return "OTHER_BIOGENIC_AMINES"
    elif flag == "L":
        return "HISTAMINE_LIBERATOR"
    elif flag == "B":
        return "DAO_BLOCKER"
    return flag


def convert_histamine_level(level: str) -> str:
    """Convert numeric level to descriptive name."""
    return HISTAMINE_LEVEL_MAP.get(level, "INSUFFICIENT_INFO")


def generate_json() -> dict:
    """Generate the complete JSON structure."""
    foods = []
    for i, (level, flags, name, notes, category, subcategory) in enumerate(FOOD_DATA, 1):
        food = {
            "id": i,
            "category": category,
            "subcategory": subcategory,
            "name": name,
            "histamineLevel": convert_histamine_level(level),
            "flags": [convert_flag(f) for f in flags],
            "notes": notes
        }
        foods.append(food)

    return {"foods": foods}


def main():
    output_path = '/data/sk.json'

    data = generate_json()

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Generated {len(data['foods'])} food items")
    print(f"Output written to: {output_path}")

    # Print some stats
    categories = {}
    for food in data['foods']:
        cat = food['category']
        categories[cat] = categories.get(cat, 0) + 1

    print("\nItems per category:")
    for cat, count in sorted(categories.items()):
        print(f"  {cat}: {count}")


if __name__ == '__main__':
    main()
