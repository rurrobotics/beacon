# Beacon - Eurobot 2027

[English](README.md)

U `beacon` folderu se nalazi ceo Python kod (paket `beacon`) za Beacon na Eurobot 2027 takmičenju.

## Instalacija i pokretanje

```sh
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

Pokretanje:

```sh
beacon
# ili
python -m beacon
```

## Kamera

Prvo je potrebno izmeniti perspektivu kamere tako da se pikseli poklapaju sa milimetražom table. To se radi na osnovu ID-jeva na tabli.

ID-jevi su ArUco tagovi, i detektuju se koristeći OpenCV biblioteku.

Kamera detektuje položaj protivničkih Sima u poslednjih 15 sekundi, tako što pronalazi ID-jeve i pretvara očitane pikseleu milimetre na tabli. Podaci koji se očitaju sa kamere šalju se na Sime preko komunikacije opisane kasnije.

## Komunikacija između Beacona i Sima

Između TCP i UDP, odabran je protokol UDP radi brzine. Iako postoji rizik gubljenja paketa, nije nam preterano bitno, jer se paketi šalju na svakih 200ms.

RPi5 Pico-u šalje informacije o svim Simama na tabli. Broj Sima ne mora biti unapred poznat broj, neki tim može imati 4, drugi nijednu, itd. Iz tog razloga je potrebno definisati maksimalan broj Sima koji mogu da se nalaze na tabli, i da u toku partije, na osnovu broja ID-jeva koje kamera detektuje, pošalje toliko paketa o informacijama.

Paketi se šalju tako što se spakuju u bajtove preko ```struct.pack()``` i ```struct.unpack()``` u low-endian formatu (u principu je svejedno, ali ovako RPi5 i RPico pakuju podatke), i sastoje se iz dva dela: Header-a i Entry-ja.

### Header ("<BBIB")
| Polje | Značenje | Format | Broj bajtova |  |
| --- | --- | --- | --- | --- |
| ```type``` | Tip paketa | Unsigned Byte (B) | 1 | U slučaju da u budućnosti šaljemo više paketa na Pico, da ih razlikuje. U ovom slučaju za koordinate Sima je 2 |
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