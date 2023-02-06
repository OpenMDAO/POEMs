import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl

import pathlib

this_dir = pathlib.Path(__file__).parent

print(this_dir)

def tanh(x, mu=1, z=0, a=-1, b=1):
    dy = b - a
    tanh_term = np.tanh((x - z) / mu)
    return 0.5 * dy * (1 + tanh_term) + a

x = np.linspace(-10, 10, 1000)

fig, ax = plt.subplots(1, 1, figsize=(8, 6))
for mu in [1, 0.5, 0.1, 0.01]:
    y = tanh(x, mu=mu, z=0, a=-1, b=1)
    plt.plot(x, y, label=f'$\mu$ = {mu}')
fig.suptitle('Impact of $\mu$ on response.', fontsize=22)
ax.set_xlabel('x', fontsize=14)
ax.set_ylabel('response', fontsize=14)
ax.grid()
ax.legend()

fig.savefig(this_dir / 'tanh_mu_impact.png', transparent=False)

fig, ax = plt.subplots(1, 1, figsize=(8, 6))
for z in [-5, -2, 0, 2, 5]:
    y = tanh(x, mu=1, z=z, a=-1, b=1)
    plt.plot(x, y, label=f'$z$ = {z}')
fig.suptitle('Impact of $z$ on response.', fontsize=22)
ax.set_xlabel('x', fontsize=14)
ax.set_ylabel('response', fontsize=14)
ax.grid()
ax.legend()
fig.savefig(this_dir / 'tanh_z_impact.png', transparent=False)

fig, ax = plt.subplots(1, 1, figsize=(8, 6))
for a in [-10, -5, -1, 0, 1, 5, 10]:
    b = -a
    y = tanh(x, mu=1, z=0, a=a, b=b)
    plt.plot(x, y, label=f'$a$ = {a}; $b$ = {b}')
fig.suptitle('Impact of $a$ and $b$ on response.', fontsize=22)
ax.set_xlabel('x', fontsize=14)
ax.set_ylabel('response', fontsize=14)
ax.grid()
ax.legend()
fig.savefig(this_dir / 'tanh_ab_impact.png', transparent=False)