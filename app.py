import streamlit as st
import random
import math
import matplotlib.pyplot as plt
from io import BytesIO


# ----------------- LOGICA DEL TABLERO -----------------

COLORES = [
    "red", "blue", "green", "magenta",
    "cyan", "yellow", "#CC6600", "#800080"
]


def board_size(num_equipos, base_cartas, factor_color, factor_negro):

    n_color_cells = sum(range(1, base_cartas + 2)) - sum(range(1, base_cartas + 2 - num_equipos))
    Nc = math.ceil(n_color_cells / factor_color)

    n0 = math.sqrt(Nc)

    Nmin = max(1, math.floor(n0 * 0.5))
    Nmax = math.ceil(n0 * 1.5)

    best_err = float("inf")
    best_aspect = float("inf")
    N = M = 1

    for n in range(Nmin, Nmax + 1):

        m = round(Nc / n)
        if m < 1:
            continue

        prodNM = n * m
        err = abs(prodNM - Nc)
        aspect = max(n, m) / min(n, m)

        if (err < best_err) or (err == best_err and aspect < best_aspect):
            best_err = err
            best_aspect = aspect
            N, M = n, m

    Nb = round(factor_negro * Nc)
    Nw = N * M - Nb - n_color_cells

    return N, M, n_color_cells, Nw, Nb


def dibujar_tablero(N, M, matriz, colores):

    fig, ax = plt.subplots()

    for i in range(N):
        for j in range(M):
            ax.add_patch(plt.Rectangle(
                (j, N-i),
                1, 1,
                color=matriz[i][j],
                ec="black"
            ))

    x0 = M + 0.5

    for k, col in enumerate(colores):

        ax.add_patch(plt.Rectangle(
            (x0, N-k-0.2),
            0.8, 0.8,
            color=col,
            ec="black"
        ))

        ax.text(
            x0 + 1.0, N-k+0.3,
            f"{k+1}º",
            fontsize=12,
            weight="bold"
        )

    ax.text(
        x0, N+0.8,
        "ORDEN DE EQUIPOS",
        fontsize=12,
        weight="bold"
    )

    ax.set_xlim(0, M + 3)
    ax.set_ylim(0, N + 1)
    ax.set_aspect("equal")
    ax.axis("off")

    return fig


# ----------------- GENERADOR AUTOMATICO -----------------

def generar_auto(num_equipos, base_cartas):

    factor_color = 17 / 25
    factor_negro = 1 / 25

    N, M, Nc, Nw, Nb = board_size(
        num_equipos,
        base_cartas,
        factor_color,
        factor_negro
    )

    colores = COLORES[:num_equipos]
    random.shuffle(colores)

    cartas_equipo = [
        base_cartas + 2 - i
        for i in range(1, num_equipos + 1)
    ]

    total = N * M
    matriz = [["white"] * M for _ in range(N)]

    posiciones = list(range(total))
    random.shuffle(posiciones)

    idx = 0

    for k in range(num_equipos):
        for _ in range(cartas_equipo[k]):
            pos = posiciones[idx]
            r = pos // M
            c = pos % M
            matriz[r][c] = colores[k]
            idx += 1

    for _ in range(Nb):
        pos = posiciones[idx]
        r = pos // M
        c = pos % M
        matriz[r][c] = "black"
        idx += 1

    return N, M, matriz, colores


# ----------------- GENERADOR PERSONALIZADO -----------------

def generar_pers(filas, cols, equipos, cartas, negros):

    total = filas * cols

    colores = COLORES[:equipos]
    random.shuffle(colores)

    matriz = [["white"] * cols for _ in range(filas)]

    posiciones = list(range(total))
    random.shuffle(posiciones)

    idx = 0

    for k in range(equipos):
        for _ in range(cartas[k]):
            pos = posiciones[idx]
            r = pos // cols
            c = pos % cols
            matriz[r][c] = colores[k]
            idx += 1

    for _ in range(negros):
        pos = posiciones[idx]
        r = pos // cols
        c = pos % cols
        matriz[r][c] = "black"
        idx += 1

    return matriz, colores


# ----------------- APP WEB -----------------

st.set_page_config(layout="centered", page_title="Generador de Tableros")

st.title("Generador de Tableros")

modo = st.tabs(["Automático", "Personalizado"])


# ----------- AUTOMÁTICO -----------

with modo[0]:

    equipos = st.number_input("Número de equipos", 2, 8, 2, key="auto_equipos")
    base = st.number_input("Base de cartas", 1, 20, 8)

    if st.button("Generar tablero automático"):

        N, M, matriz, colores = generar_auto(equipos, base)

        fig = dibujar_tablero(N, M, matriz, colores)

        st.pyplot(fig)

        buf = BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight")
        st.download_button(
            "Descargar como imagen",
            buf.getvalue(),
            "tablero_automatico.png",
            "image/png"
        )


# ----------- PERSONALIZADO -----------

with modo[1]:

    filas = st.number_input("Filas", 1, 20, 5)
    cols = st.number_input("Columnas", 1, 20, 5)

    equipos = st.number_input("Número de equipos", 2, 8, 2, key="pers_equipos")


    st.write("Cartas por equipo")

    cartas = []
    for i in range(equipos):
        cartas.append(
            st.number_input(f"Equipo {i+1}", 0, 50, 5)
        )

    negros = st.number_input("Casillas negras", 0, 20, 1)

    if st.button("Generar tablero personalizado"):

        matriz, colores = generar_pers(filas, cols, equipos, cartas, negros)

        fig = dibujar_tablero(filas, cols, matriz, colores)

        st.pyplot(fig)

        buf = BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight")
        st.download_button(
            "Descargar como imagen",
            buf.getvalue(),
            "tablero_personalizado.png",
            "image/png"
        )
