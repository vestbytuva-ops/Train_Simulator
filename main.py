import pygame
from bisect import bisect_right
from math import atan2, cos, degrees, hypot, pi, sin, tan


BREDDE = 900
HOYDE = 500
PIKSLER_PER_METER = 5
START_X = 100
SKINNE_Y = 400

TYNGDEAKSELERASJON = 9.81
FYSIKK_DT = 1 / 120


class Bane:
    def __init__(self):
        self.flat_lengde = 80
        self.bakke_bredde = 320
        self.bakke_hoyde = 12

        self.punkter = []
        self.avstander = [0.0]

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
        if posisjon <= self.flat_lengde:
            return posisjon, 0.0

        rest = posisjon - self.flat_lengde

        runde = int(rest // self.bakke_lengde)
        lokal_posisjon = rest % self.bakke_lengde

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

        for posisjon in range(start, start + 300, 2):
            punkter.append(
                self.skjermpunkt(posisjon, kamera)
            )

        terreng = punkter + [
            (punkter[-1][0], HOYDE),
            (punkter[0][0], HOYDE)
        ]

        pygame.draw.polygon(
            skjerm, (75, 155, 75), terreng
        )

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

        # Forenklede øvingsverdier.
        self.motorkraft = 40000          # Maksimal kraft i N
        self.motoreffekt = 350000        # Maksimal effekt i W
        self.bremsekraft = 80000
        self.rullemotstand = 1500
        self.luftmotstand_faktor = 8

        self.gass = 0
        self.bremsing = 0

        self.fart = 0.0
        self.posisjon = 0.0
        self.forrige_posisjon = 0.0
        self.distanse = 0.0

        self.bilde = pygame.Surface(
            (120, 45), pygame.SRCALPHA
        )
        self.bilde.fill((200, 50, 50))

    def gi_gass(self, aktiv):
        self.gass = 1 if aktiv else 0

    def brems(self, aktiv):
        self.bremsing = 1 if aktiv else 0

    def beregn_motorkraft(self):
        if self.gass == 0:
            return 0.0

        # Unngå deling på null når toget står stille.
        fart = max(abs(self.fart), 0.1)

        kraft_fra_effekt = self.motoreffekt / fart

        tilgjengelig_kraft = min(
            self.motorkraft,
            kraft_fra_effekt
        )

        return tilgjengelig_kraft * self.gass

    def beregn_motstand(self):
        luftmotstand = self.luftmotstand_faktor * self.fart ** 2
        return self.rullemotstand + luftmotstand

    def oppdater(self, dt, bane):
        self.forrige_posisjon = self.posisjon

        vinkel = bane.vinkel(self.posisjon)

        kraft_motor = self.beregn_motorkraft()

        kraft_bakke = (
            -self.masse
            * TYNGDEAKSELERASJON
            * sin(vinkel)
        )

        drivkraft = kraft_motor + kraft_bakke

        motkraft = (
            self.beregn_motstand()
            + self.bremsekraft * self.bremsing
        )

        # Motstand og brems kan holde toget stille.
        if abs(self.fart) < 0.001:
            if abs(drivkraft) <= motkraft:
                self.fart = 0.0
                return

            retning = 1 if drivkraft > 0 else -1

        else:
            retning = 1 if self.fart > 0 else -1

        samlet_kraft = drivkraft - retning * motkraft

        akselerasjon = samlet_kraft / self.masse
        ny_fart = self.fart + akselerasjon * dt

        if self.fart * ny_fart < 0:
            ny_fart = 0.0

        self.fart = ny_fart

        flytting = self.fart * dt
        self.posisjon += flytting
        self.distanse += abs(flytting)

    def interpolert_posisjon(self, andel):
        return (
            self.forrige_posisjon
            + (self.posisjon - self.forrige_posisjon) * andel
        )

    def tegn(self, skjerm, kamera, bane, posisjon):
        skinne_x, skinne_y = bane.skjermpunkt(
            posisjon, kamera
        )

        vinkel = bane.vinkel(posisjon)

        rotert_bilde = pygame.transform.rotate(
            self.bilde, degrees(vinkel)
        )

        halv_hoyde = self.bilde.get_height() / 2

        senter_x = skinne_x - sin(vinkel) * halv_hoyde
        senter_y = skinne_y - cos(vinkel) * halv_hoyde

        rektangel = rotert_bilde.get_rect(
            center=(round(senter_x), round(senter_y))
        )

        skjerm.blit(rotert_bilde, rektangel)


class Kamera:
    def __init__(self):
        self.x = 0.0

    def oppdater(self, posisjon, bane):
        verden_x, hoyde = bane.punkt(posisjon)

        tog_x = START_X + verden_x * PIKSLER_PER_METER
        skjerm_x = tog_x - self.x

        if skjerm_x > 300:
            self.x = tog_x - 300

        elif skjerm_x < 100:
            self.x = tog_x - 100


pygame.init()

skjerm = pygame.display.set_mode((BREDDE, HOYDE))
pygame.display.set_caption("Train Simulator")

klokke = pygame.time.Clock()
font = pygame.font.Font(None, 32)

bane = Bane()
tog1 = Tog("Lokomotiv 1", 20000)
kamera = Kamera()

akkumulator = 0.0
kjorer = True

while kjorer:
    frame_dt = min(klokke.tick(60) / 1000, 0.1)

    for hendelse in pygame.event.get():
        if hendelse.type == pygame.QUIT:
            kjorer = False

    if not kjorer:
        break

    taster = pygame.key.get_pressed()

    tog1.gi_gass(taster[pygame.K_RIGHT])
    tog1.brems(taster[pygame.K_LEFT])

    akkumulator += frame_dt

    while akkumulator >= FYSIKK_DT:
        tog1.oppdater(FYSIKK_DT, bane)
        akkumulator -= FYSIKK_DT

    andel = akkumulator / FYSIKK_DT
    visuell_posisjon = tog1.interpolert_posisjon(andel)

    kamera.oppdater(visuell_posisjon, bane)

    skjerm.fill((135, 206, 235))

    bane.tegn(skjerm, kamera, visuell_posisjon)
    tog1.tegn(skjerm, kamera, bane, visuell_posisjon)

    if tog1.fart > 0.01:
        retning = "fremover"
    elif tog1.fart < -0.01:
        retning = "bakover"
    else:
        retning = "stille"

    fart_kmt = abs(tog1.fart) * 3.6
    helning = tan(bane.vinkel(visuell_posisjon)) * 100
    motorkraft_kn = tog1.beregn_motorkraft() / 1000

    fart_tekst = font.render(
        f"Fart: {fart_kmt:.1f} km/t ({retning})",
        True,
        (20, 20, 20)
    )

    distanse_tekst = font.render(
        f"Distanse: {tog1.distanse:.0f} m",
        True,
        (20, 20, 20)
    )

    helning_tekst = font.render(
        f"Helning: {helning:.1f} %",
        True,
        (20, 20, 20)
    )

    motorkraft_tekst = font.render(
        f"Motorkraft: {motorkraft_kn:.1f} kN",
        True,
        (20, 20, 20)
    )

    skjerm.blit(fart_tekst, (20, 20))
    skjerm.blit(distanse_tekst, (20, 55))
    skjerm.blit(helning_tekst, (20, 90))
    skjerm.blit(motorkraft_tekst, (20, 125))

    pygame.display.flip()

pygame.quit()