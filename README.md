# Třídička sběratelských karet Magic: The Gathering

Maturitní projekt na Gymnáziu Jana Keplera

## Účel
Cílem práce je vytvořit stroj pro automatizované třídění karet MTG podle uživatelem vybraných parametrů do alespoň 25 kategorií
Stroj je určen jako pomoc při třídění sbírky či například hledání karet vhodných do herního balíčku

## Způsob použití
Srovnaný balíček karet je lícem vzhůru vložen do pravého zásobníku, poté z plochy spuštěn skript SorterEngine.py
V GUI, které se objeví, si uživatel nastaví kategorie třídění pro jednotlivé výstupní balíčky, počedmž zvolí možnost uložit a zavřít
Následně již stroj automaticky třídí, dokud v zásobníku jsou karty

## Jak to funguje?
Po nastavení opakuje stroj do vyčerpání všech karet stejný cyklus:
- Vyfotí kartu
- Získá z obrázku poomocí OCR její název
- Porovná jej se seznamem karetšš
- Porovná parametry aktuální karty s parametry pro výstupní balíčky
- Umístí aktuální kartu na odpovídající balíček či na balíček odkládací
