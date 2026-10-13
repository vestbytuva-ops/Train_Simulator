import pygame


class Tog:
    def __init__(self, navn, masse):
        self.navn = navn
        self.masse = masse
        self.fart = 0
        self.posisjon = 0

    def ok_fart(self, endring):
        self.fart += endring

    def brems(self, reduksjon):
        self.fart = max(0, self.fart - reduksjon)

    def oppdater(self, dt):
        self.posisjon += self.fart * dt

    def tegn(self, skjerm, kamera):
        verden_x = 100 + self.posisjon * 5
        skjerm_x = round(verden_x - kamera.x)

        pygame.draw.rect(
            skjerm,
            (200, 50, 50),
            (skjerm_x, 355, 120, 45)
        )


class Kamera:
    def __init__(self):
        self.x = 0

    def oppdater(self, tog):
        tog_x = 100 + tog.posisjon * 5

        # Følg toget når det passerer x = 300 på skjermen.
        self.x = max(0, tog_x - 300)


pygame.init()

skjerm = pygame.display.set_mode((900, 500))
pygame.display.set_caption("Train Simulator")
klokke = pygame.time.Clock()

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
        tog1.ok_fart(2 * dt)

    if taster[pygame.K_LEFT]:
        tog1.brems(4 * dt)

    # Oppdater toget før kameraet følger etter.
    tog1.oppdater(dt)
    kamera.oppdater(tog1)

    skjerm.fill((135, 206, 235))

    # Tegn sviller som ligger fast i spillverdenen.
    start = int(kamera.x // 40) * 40

    for verden_x in range(start, start + 940, 40):
        skjerm_x = round(verden_x - kamera.x)

        pygame.draw.rect(
            skjerm,
            (110, 80, 45),
            (skjerm_x, 398, 24, 10)
        )

    # Tegn den flate skinnen.
    pygame.draw.line(
        skjerm,
        (70, 70, 70),
        (0, 400),
        (900, 400),
        4
    )

    tog1.tegn(skjerm, kamera)

    pygame.display.flip()

pygame.quit()