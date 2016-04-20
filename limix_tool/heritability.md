Heritability
============

- Prevalence: $D$
\[
l = g + e + o
\]

\[
p(g) = \mathcal N(g; 0, h^2)\\
p(e) = \mathcal N(e; 0, 1-h^2)\\
\]

\[
o = \Phi^{-1}(D)
\]


- Ascertainment: $A$

\[
l_c = g_c + e_c + o
\]

\[
p(g_c | e_c) = \frac{1-A}{\Phi(|o|-e)} p(g=g_c)\
                            \delta_{g+e_c<|o|}\
               + \frac{A}{\Phi(1-L_{e_c})} p(g=g_c)\
                            \delta_{g>L_{e_c}}
\]

\[
L_{x} = |o| - x
\]

\[
p(g_c, e_c) = \frac{1-A}{1-D} p(g=g_c) p(e=e_c) \delta_{g_c+e_c<|o|}\
              + \frac{A}{D} p(g=g_c) p(e=e_c) \delta_{g_c+e_c>|o|}
\]
