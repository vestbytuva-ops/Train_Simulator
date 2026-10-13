import pygame
from bisect import bisect_right
from math import atan2, cos, degrees, hypot, pi, sin


BREDDE = 900
HOYDE = 500
PIKSLER_PER_METER = 5
START_X = 100
SKINNE_Y = 400


class Bane:
    def __init__(self):
        self.flat_lengde = 80
        self.bakke_bredde = 320
        self.bakke_hoyde = 12

        self.punkter = []
        self.avstander = [0.0]

        # Lag punkter som beskriver én jevn bakke.
        for x in range(0, self.bakke_bredde + 1, 2):
            hoyde = self.bakke_hoyde * (
                1 - cos(2 * pi * x / self.bakke_bredde)
            ) / 2

            self.punkter.append((x, hoyde))

            if len(self.punkter) > 1:
                forrige_x, forrige_hoyde = self.punkter[-2]

                lengde = hypot(
                    x - forrige_x,
                    hoyde - forrige_hoyde
                )

                self.avstander.append(
                    self.avstander[-1] + lengde
                )

        self.bakke_lengde = self.avstander[-1]

    def punkt(self, posisjon):
        # Første del av banen er flat.
        if posisjon <= self.flat_lengde:
            return posisjon, 0.0

        rest = posisjon - self.flat_lengde

        # Gjenta bakken videre langs banen.
        runde = int(rest // self.bakke_lengde)
        lokal_posisjon = rest % self.bakke_lengde

        # Finn hvilke to banepunkter posisjonen ligger mellom.
        i = bisect_right(self.avstander, lokal_posisjon) - 1
        i = min(i, len(self.punkter) - 2)

        andel = (
            (lokal_posisjon - self.avstander[i])
            / (self.avstander[i + 1] - self.avstander[i])
        )

        x1, h1 = self.punkter[i]
        x2, h2 = self.punkter[i + 1]

        x = x1 + (x2 - x1) * andel
        hoyde = h1 + (h2 - h1) * andel

        verden_x = (
            self.flat_lengde
            + runde * self.bakke_bredde
            + x
        )

        return verden_x, hoyde

    def vinkel(self, posisjon):
        x1, h1 = self.punkt(posisjon - 0.5)
        x2, h2 = self.punkt(posisjon + 0.5)

        return atan2(h2 - h1, x2 - x1)

    def skjermpunkt(self, posisjon, kamera):
        x, hoyde = self.punkt(posisjon)

        skjerm_x = START_X + x * PIKSLER_PER_METER - kamera.x
        skjerm_y = SKINNE_Y - hoyde * PIKSLER_PER_METER

        return round(skjerm_x), round(skjerm_y)

    def tegn(self, skjerm, kamera, tog_posisjon):
        start = int(tog_posisjon // 2) * 2 - 80
        punkter = []

        # Beregn den synlige delen av banen.
        for posisjon in range(start, start + 300, 2):
            punkter.append(
                self.skjermpunkt(posisjon, kamera)
            )

        # Tegn bakken under skinnene.
        terreng = punkter + [
            (punkter[-1][0], HOYDE),
            (punkter[0][0], HOYDE)
        ]

        pygame.draw.polygon(
            skjerm, (75, 155, 75), terreng
        )

        # Svillene har faste plasseringer langs banen.
        start_sviller = int(start // 8) * 8

        for posisjon in range(start_sviller, start + 300, 8):
            x, y = self.skjermpunkt(posisjon, kamera)

            pygame.draw.rect(
                skjerm,
                (110, 80, 45),
                (x - 10, y, 20, 8)
            )

        pygame.draw.lines(
            skjerm, (70, 70, 70), False, punkter, 4
        )


class Tog:
    def __init__(self, navn, masse):
        self.navn = navn
        self.masse = masse
        self.motorkraft = 40000
        self.rullemotstand = 1500
        self.luftmotstand_faktor = 8

        self.fart = 0
        self.posisjon = 0

        # Lag et togbilde som kan roteres.
        self.bilde = pygame.Surface(
            (120, 45), pygame.SRCALPHA
        )
        self.bilde.fill((200, 50, 50))

    def gi_gass(self, dt):
        akselerasjon = self.motorkraft / self.masse
        self.fart += akselerasjon * dt

    def brems(self, reduksjon):
        self.fart = max(0, self.fart - reduksjon)

    def beregn_motstand(self):
        luftmotstand = self.luftmotstand_faktor * self.fart ** 2
        return self.rullemotstand + luftmotstand

    def oppdater(self, dt):
        if self.fart > 0:
            motstand = self.beregn_motstand()
            akselerasjon = -motstand / self.masse

            self.fart = max(
                0,
                self.fart + akselerasjon * dt
            )

        # Posisjonen måles langs skinnene.
        self.posisjon += self.fart * dt

    def tegn(self, skjerm, kamera, bane):
        skinne_x, skinne_y = bane.skjermpunkt(
            self.posisjon, kamera
        )

        vinkel = bane.vinkel(self.posisjon)

        rotert_bilde = pygame.transform.rotate(
            self.bilde, degrees(vinkel)
        )

        # Plasser bildet over skinnen, også når det roteres.
        halv_hoyde = self.bilde.get_height() / 2

        senter_x = skinne_x - sin(vinkel) * halv_hoyde
        senter_y = skinne_y - cos(vinkel) * halv_hoyde

        rektangel = rotert_bilde.get_rect(
            center=(round(senter_x), round(senter_y))
        )

        skjerm.blit(rotert_bilde, rektangel)


class Kamera:
    def __init__(self):
        self.x = 0

    def oppdater(self, tog, bane):
        verden_x, hoyde = bane.punkt(tog.posisjon)

        tog_x = START_X + verden_x * PIKSLER_PER_METER
        self.x = max(0, tog_x - 300)


pygame.init()

skjerm = pygame.display.set_mode((BREDDE, HOYDE))
pygame.display.set_caption("Train Simulator")

klokke = pygame.time.Clock()
font = pygame.font.Font(None, 32)

bane = Bane()
tog1 = Tog("Lokomotiv 1", 20000)
kamera = Kamera()

kjorer = True

while kjorer:
    dt = klokke.tick(60) / 1000

    for hendelse in pygame.event.get():
        if hendelse.type == pygame.QUIT:
            kjorer = False

    taster = pygame.key.get_pressed()

    if taster[pygame.K_RIGHT]:
        tog1.gi_gass(dt)

    if taster[pygame.K_LEFT]:
        tog1.brems(4 * dt)

    tog1.oppdater(dt)
    kamera.oppdater(tog1, bane)

    skjerm.fill((135, 206, 235))

    bane.tegn(skjerm, kamera, tog1.posisjon)
    tog1.tegn(skjerm, kamera, bane)

    fart_kmt = tog1.fart * 3.6

    fart_tekst = font.render(
        f"Fart: {fart_kmt:.1f} km/t",
        True,
        (20, 20, 20)
    )

    distanse_tekst = font.render(
        f"Distanse: {tog1.posisjon:.0f} m",
        True,
        (20, 20, 20)
    )

    skjerm.blit(fart_tekst, (20, 20))
    skjerm.blit(distanse_tekst, (20, 55))

    pygame.display.flip()

pygame.quit()