POEM ID: 040  
Title: Integration with IPython notebooks  
authors: [robfalck]  
Competing POEMs: N/A  
Related POEMs: N/A  
Associated implementation PR:

##  Status

- [ ] Active
- [ ] Requesting decision
- [ ] Accepted
- [ ] Rejected
- [x] Integrated


## Motivation

IPython notebooks are a great way to help new users experiment with Python packages without bogging them down with installation requirements.
In particular, https://colab.research.google.com/ is heavily used by the machine learning community, and Tensorflow provides numerous examples and documentation via notebooks executed there.

## Description

This POEM proposes changes to OpenMDAO to make it more user-friendly when run within a notebook environment.

### Proposals

1. The n2 command should automatically display the output HTML in the notebook.

The following code will display the n2 diagram in the notebook:

```
from IPython.core.display import display, HTML
from string import Template
import json
om.n2(p, show_browser=False)
HTML('n2.html')
```

Ideally the n2 command `om.n2(p)` will be smart enough to determine if the code is being run from within a notebook.

2. `view_connections` should likewise display the generated HTML directly in the notebook.

3. The `list_` methods (`list_outputs`, `list_sources`, etc.) should print a well-formatted table if within a notebook.

4. Functions and methods which generate static plots show show those in the notebook (`partial_deriv_plot`, total jacobian coloring viewers, etc)

5. Functions which generate interactive plots should show those within the notebook as well with widgets to control them (specifically, the view_mm capability).

6. A future repo will be created to house OpenMDAO examples in notebook form, which will be tested whenever OpenMDAO is updated.  Google has some solid documentation about best practices for curating notebooks.
