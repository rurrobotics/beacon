# Beacon - Eurobot 2027

U `src` folderu se nalazi ceo Python kod za Beacon na Eurobot 2027 takmičenju.

## Komunikacija između Beacona i Sima
Odrađeno je testiranje komunikacije između RPI5 i RPico, gde RPI5 šalje određen broj paketa veličine oko 16 bajtova određenom brzinom i RPico javi nazad koliko je paketa primio. Oba su povezana na 2.4GHz Hotspot sa laptopa.

Beacon treba Simama da šalje pakete informacija o tome gde se nalaze protivničke Sime, dakle dovoljno je pustiti u rad poslednjih 15 sekundi meča i slati nekoliko paketa u sekundi, i korisno je (bar meni) videti koliko dobro ova komunikacija može da radi u zavisnosti od brzine slanja.

Realan cilj je da šaljemo paket na svake 0.2 sekunde bez ikakvih gubitaka.

Dalje sledi analiza rezultata koja samo meni lično znači da vidim koliko će ovo dobro raditi na 2.4GHz i verovatno ću obrisati iz README posle :)

### Kanc - nema smetnji
| Brzina slanja [pkt/s] | Najduže vreme između paketa [ms] | Success Rate [%] |
| --- | --- | --- |
| 1 | 1033ms | 100.00% |
| 5 | 244ms | 100.00% |
| 10 | 203ms | 100.00% |
| 20 | 76ms | 100.00% |

**Zaključak:** Kanc je bomba!


### Promenada - smetnje epskih veličina
| Brzina slanja [pkt/s] | Najduže vreme između paketa | Success Rate [%] |
| --- | --- | --- |
| 1 |  |  |
| 5 |  |  |
| 10 |  |  |
| 20 |  |  |

------------------------------------------------------------------------

RPi5 Pico-u šalje informacije o svim Simama na tabli. Broj Sima ne mora biti unapred poznat broj, neki tim može imati 4, drugi nijednu, itd. Iz tog razloga je potrebno definisati maksimalan broj Sima koji mogu da se nalaze na tabli, i da u toku partije, na osnovu broja ID-jeva koje kamera detektuje, pošalje toliko paketa o informacijama.

Paketi se šalju tako što se spakuju u bajtove preko ```struct.pack()``` i ```struct.unpack()``` u low-endian formatu (u principu je svejedno, ali ovako RPi5 i RPico pakuju podatke), i sastoje se iz dva dela: Header-a i Entry-ja.

### Header ("<BBIB")
| Polje | Značenje | Format | Broj bajtova |  |
| --- | --- | --- | --- | --- |
| ```type``` | Tip paketa | Unsigned Byte (B) | 1 | U slučaju da u budućnosti šaljemo više paketa na Pico, da ih razlikuje. U ovom slučaju za koordinate Sima je 0 |
| ```version``` | Verzija | Unsigned Byte (B) | 1 | Verzija izmene u slučaju da se u budućnosti doda nešto, da Pico zna da treba da odbaci staro |
| ```seq``` | Redni broj paketa | Unsigned Integer (I) | 4 | Ignorišu se stari paketi i duplikati |
| ```n``` | Broj Sima | Unsigned Byte (B) | 1 | Koliko Sima Beacon vidi |

### Entry ("<Bhh")
| Polje | Značenje | Format | Broj bajtova |  |
| --- | --- | --- | --- | --- |
| ```id``` | ID Sime | Unsigned Byte (B) | 1 | Koja je Sima u pitanju |
| ```x_mm``` | X koordinata [mm] | Signed Short (h) | 2 | 0 - 3000 mm |
| ```y_mm``` | Y koordinata [mm] | Signed Short (h) | 2 |0 - 2000 mm |

Ukupna veličina paketa je 7 + n * 5 bajtova. Najveći broj protivničkih Sima koji mogu da se nađu na stolu je 6, dakle najveći broj bajtova koje RPi5 šalje na Pico je 37 (odnosno 64 bajtova zaokruženo)