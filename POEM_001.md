POEM ID: 001  
Title: Units update for better astrodynamics support  
authors: robfalck (Rob Falck)  
Competing POEMs: N/A  
Related POEMs: N/A  
Associated implementation PR: https://github.com/OpenMDAO/OpenMDAO/pull/1101  

Status:
  
- [ ] Active
- [ ] Requesting decision
- [ ] Accepted
- [ ] Rejected
- [x] Integrated


Motivation
----------
Changes some existing unit definitions and adds others to make
OpenMDAO more suitable to astrodynamics applications "out of the box."


Description
-----------

This POEM proposes the following changes:

* The astronomical unit abbreviation is changed from `ua` to the International
Astronomical Union (IAU) standard of `au`. [1]
* The definition of the astronomical unit is changed from `1.49597870691e11*m`
to the IAU standard of `1.49597870700e11*m` [1]
* The definition of light year is changed from `9.46073e15*m` to the IAU
definition of `c0*365.25*d` [2]
* The unit of parsec with abbreviation of `pc` is added with a definition
of `648000/pi*au` [3]


References
----------

1. Luzum, B., Capitaine, N., Fienga, A., Folkner, W., Fukushima, T., Hilton. J., Hohenkerk, C., Krasinsky,
G., Petit, G., Pitjeva, E., Soffel, M., Wallace, P., 2011, “The IAU 2009 system of astronomical constants: the report of the IAU Working Group on Numerical Standards for Fundamental Astronomy,”
Celest. Mech. Dyn. Astr. 110, 293–304.
2. Wilkins, George A., and Donald H. Sadler. The IAU Style Manual
(1989): The Preparation of Astronomical Papers and Reports. D. Reidel, 1989.
3. Mamajek, E. E., et al. "IAU 2015 Resolution B2 on Recommended Zero
Points for the Absolute and Apparent Bolometric Magnitude Scales." arXiv
preprint arXiv:1510.06262 (2015).
