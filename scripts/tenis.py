#!/usr/bin/env python3
"""Mercados secundários do ténis (sets, total e handicap de jogos) a partir do preço justo do vencedor.

Modelo hierárquico de pontos (Newton & Keller 2005; O'Malley 2008): cada jogador ganha os pontos no seu serviço
com probabilidade fixa. Calibra-se ao mercado fixando o nível L = pA + pB (média do circuito) e resolvendo a
diferença d = pA − pB que reproduz a probabilidade justa do vencedor. O modelo puro subestima os 2-0 e
sobrestima os jogos (sets correlacionados); a correção é uma mistura normal em d (σ ≈ 0,065), recentrada para
não mudar P(vencedor). Testado em 8 596 encontros ATP com Pinnacle: ver docs/mercados-secundarios.md.
Só biblioteca padrão.
"""
from functools import lru_cache

# Gauss–Hermite com 5 nós, normalizado para a normal padrão.
NOS = [(0.0, 8 / 15), (1.3556261799742657, 0.2220759220056126), (-1.3556261799742657, 0.2220759220056126),
       (2.8569700138728056, 0.011257411327720691), (-2.8569700138728056, 0.011257411327720691)]


def p_jogo(p):
    """P(quem serve ganha o jogo), com probabilidade p de ganhar cada ponto no serviço."""
    q = 1 - p
    return p ** 4 * (1 + 4 * q + 10 * q * q) + 20 * p ** 3 * q ** 3 * p * p / (1 - 2 * p * q)


def p_tiebreak(pa, pb, alvo=7):
    """P(A ganha o tie-break), servindo A o 1.º ponto (depois B, B, A, A, ...)."""
    empate = pa * (1 - pb) / (pa * (1 - pb) + (1 - pa) * pb)

    @lru_cache(maxsize=None)
    def f(a, b):
        if a >= alvo and a - b >= 2:
            return 1.0
        if b >= alvo and b - a >= 2:
            return 0.0
        if a == b and a >= alvo - 1:
            return empate
        w = pa if ((a + b + 1) // 2) % 2 == 0 else 1 - pb
        return w * f(a + 1, b) + (1 - w) * f(a, b + 1)
    return f(0, 0)


def dist_set(pa, pb, a_primeiro, tb=7):
    """{(jogos A, jogos B): prob} de um set com tie-break a 6-6."""
    ha, hb = p_jogo(pa), p_jogo(pb)
    estados, fim = {(0, 0): 1.0}, {}
    for _ in range(12):
        novos = {}
        for (i, j), pr in estados.items():
            w = ha if ((i + j) % 2 == 0) == a_primeiro else 1 - hb
            for (ni, nj), pp in (((i + 1, j), w), ((i, j + 1), 1 - w)):
                destino = fim if (ni >= 6 and ni - nj >= 2) or (nj >= 6 and nj - ni >= 2) else novos
                destino[(ni, nj)] = destino.get((ni, nj), 0) + pr * pp
        estados = novos
    x = estados.get((6, 6), 0.0)
    if x:
        t = p_tiebreak(pa, pb, tb) if a_primeiro else 1 - p_tiebreak(pb, pa, tb)
        fim[(7, 6)] = fim.get((7, 6), 0) + x * t
        fim[(6, 7)] = fim.get((6, 7), 0) + x * (1 - t)
    return fim


def dist_encontro(pa, pb, melhor_de=3, tb_final=7):
    """{(sets A, sets B, jogos A, jogos B): prob}. Sorteio do serviço 50/50; após um set com n.º ímpar de jogos
    serve primeiro o outro jogador."""
    alvo, cache = melhor_de // 2 + 1, {}

    def ds(a_primeiro, final):
        if (a_primeiro, final) not in cache:
            cache[(a_primeiro, final)] = dist_set(pa, pb, a_primeiro, tb_final if final else 7)
        return cache[(a_primeiro, final)]

    estados, fim = {(0, 0, True, 0, 0): 0.5, (0, 0, False, 0, 0): 0.5}, {}
    while estados:
        novos = {}
        for (sa, sb, a1, ga, gb), pr in estados.items():
            for (i, j), pp in ds(a1, sa == sb == alvo - 1).items():
                nsa, nsb = sa + (i > j), sb + (j > i)
                if alvo in (nsa, nsb):
                    k = (nsa, nsb, ga + i, gb + j)
                    fim[k] = fim.get(k, 0) + pr * pp
                else:
                    k = (nsa, nsb, a1 if (i + j) % 2 == 0 else not a1, ga + i, gb + j)
                    novos[k] = novos.get(k, 0) + pr * pp
        estados = novos
    return fim


def p_vence(dist):
    return sum(v for (sa, sb, _, _), v in dist.items() if sa > sb)


def bissecao(f, alvo, lo, hi, passos=40):
    """Raiz de f(x) = alvo, com f crescente em [lo, hi]."""
    for _ in range(passos):
        m = (lo + hi) / 2
        lo, hi = (m, hi) if f(m) < alvo else (lo, m)
    return (lo + hi) / 2


def distribuicao(p, nivel=1.28, sigma=0.065, melhor_de=3, tb_final=7):
    """Distribuição conjunta de sets e jogos com P(A vence) = p. sigma=0 dá o modelo puro."""
    nos = NOS if sigma > 0 else [(0.0, 1.0)]

    def mistura(d0):
        total = {}
        for z, w in nos:
            d = d0 + sigma * z
            pa, pb = min(max(nivel / 2 + d / 2, 0.05), 0.95), min(max(nivel / 2 - d / 2, 0.05), 0.95)
            for k, v in dist_encontro(pa, pb, melhor_de, tb_final).items():
                total[k] = total.get(k, 0) + w * v
        return total
    return mistura(bissecao(lambda d: p_vence(mistura(d)), p, -0.6, 0.6, 30))


def mercados(dist):
    """Probabilidades dos mercados secundários, do ponto de vista do jogador A."""
    sets, jogos, dif = {}, {}, {}
    for (sa, sb, ga, gb), v in dist.items():
        sets[f"{sa}-{sb}"] = sets.get(f"{sa}-{sb}", 0) + v
        jogos[ga + gb] = jogos.get(ga + gb, 0) + v
        dif[ga - gb] = dif.get(ga - gb, 0) + v
    return {"vence": p_vence(dist), "sets": sets, "jogos": jogos, "diferenca": dif,
            "media_jogos": sum(k * v for k, v in jogos.items()),
            "a_ganha_set": 1 - sets.get("0-2", 0) - sets.get("0-3", 0),
            "b_ganha_set": 1 - sets.get("2-0", 0) - sets.get("3-0", 0)}


def over(m, linha):
    """P(total de jogos > linha); a linha deve ser x,5."""
    return sum(v for k, v in m["jogos"].items() if k > linha)


def cobre(m, linha):
    """P(A cobre o handicap de jogos `linha`, ex.: −3,5 → A ganha por 4 ou mais jogos)."""
    return sum(v for k, v in m["diferenca"].items() if k + linha > 0)


def nivel(cfg, competicao):
    """Nível de serviço L = pA + pB pela competição (média do circuito; config 'tenis_nivel_servico')."""
    niveis = cfg.get("tenis_nivel_servico", {"atp": 1.28, "challenger": 1.22, "wta": 1.14})
    texto = competicao.lower()
    chave = "wta" if "wta" in texto else "challenger" if ("challenger" in texto or "itf" in texto) else "atp"
    return niveis[chave], chave
