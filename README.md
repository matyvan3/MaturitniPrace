# Třídička sběratelských karet Magic: The Gathering

Maturitní projekt na Gymnáziu Jana Keplera

## Účel
Cílem práce je vytvořit stroj pro automatizované třídění karet MTG podle uživatelem vybraných vlastností (barva, cena nebo edice) na až 25 skupin + ostatní

## Způsob použití
Srovnaný balíček karet je vložen do zásobníku, na výběrovém panelu jsou navoleny chtěné charakteristiky k třídění a stroj je spuštěn stiskem tlačítka

## Jak to funguje?
Po stisknutí tlačítka opakuje stroj do opětovného stisknutí či do vyčerpání všech karet stejný cyklus:
- Vyfotí kartu
- Získá z obrázku poomocí OCR její název
- Vyhledá jej v databázi karet
- Porovná atributy aktuální karty s kartami již zatřízenými
- Umístí aktuální kartu na hromádku s kartami shodných atributů či na novou, pokud zatím neexistuje žádná kompatibilní
