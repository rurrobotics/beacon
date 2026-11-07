# Beacon - Eurobot 2027

U `src` folderu se nalazi ceo Python kod za Beacon na Eurobot 2027 takmičenju.

## Komunikacija između Beacona i Sima
Odrađeno je testiranje koomunikacije između RPI5 i RPico, gde RPI5 šalje određen broj paketa veličine oko 16 bajtova određenom brzinom i RPico javi nazad koliko je paketa primio. Oba su povezana na 2.4GHz Hotspot sa laptopa.

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