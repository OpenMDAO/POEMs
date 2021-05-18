
# OpenMDAO POEM Process

The POEM process is the official mechanism for proposing, discussing, revising, and ultimately approving or rejecting all changes to the [OpenMDAO](https://openmdao.org) project which effect its user interaction. 
The process involves writing, reading, and discussing documents called POEMs (**p**roposal for **O**penMDAO **e**nhance**m**ent). 

This process governs all API changes, feature additions, and feature removals to the OpenMDAO project. 
It is also recursive because it governs any changes to itself. 

The process serves two primary and equally important purposes: 

1) Announce all changes to the user interface of OpenMDAO to users of the framework **before** they are added to the main repository

2) Provide a mechanism for external users to propose changes to the user interface for OpenMDAO

##  How does it work?

The rules are described in the [POEM_000.md](https://github.com/OpenMDAO/POEMs/blob/master/POEM_000.md) document in this repository. 
The OpenMDAO POEMs repository (i.e. this repo) contains a full record of all POEMs submitted, starting November 1st, 2019.
Both the core development team and external users participate, and input on any POEM is welcome from any user at any time.

##  How can I keep up to date on POEMs?

All POEM activity is managed within this repository, via PRs and comments to those PRs. 
The best way to track that activity is to star and watch this repository. 
That way, github's built in notification system to get emails when things are changing. 
[Github has lots of great docs on this!](https://help.github.com/en/github/receiving-notifications-about-activity-on-github/watching-and-unwatching-repositories)

## List of POEMs

| POEM ID | Title | Author | Status |
| ------- | ----- | ------ | ------ |
| [000](POEM_000.md) | POEM Purpose and Guidelines | [Justin S. Gray](https://github.com/justinsgray) | integrated |
| [001](POEM_001.md) | Units update for better astrodynamics support | [Rob Falck](https://github.com/robfalck) | integrated |
| [002](POEM_002.md) | New capability for user to send a termination signal to an OpenMDAO process so that SNOPT in pyoptsparse can terminate cleanly. | [Kenneth-T-Moore](https://github.com/Kenneth-T-Moore) | integrated |
| [003](POEM_003.md) | Allowing addition of I/O during Configure | [Anil Yildirim](https://github.com/anilyil); [Justin Gray](https://github.com/justinsgray); [Rob Falck](https://github.com/robfalck) | integrated |
| [004](POEM_004.md) | Creating Interpolant Class For 1D Splines | [DKilkenny](https://github.com/DKilkenny) | integrated |
| [005](POEM_005.md) | An OpenMDAO Plugin System | [naylor-b](https://github.com/naylor-b) | integrated |
| [006](POEM_006.md) | Re-work the user experience in the N2 diagram | [Herb Schilling](https://github.com/hschilling) | integrated |
| [007](POEM_007.md) | String Compatibility for ExternalCodeComp and ExternalCodeImplicitComp Command Options | [Danny Kilkenny](https://github.com/DKilkenny) | integrated |
| [008](POEM_008.md) | Nonlinear Solver Refactor | [Danny Kilkenny](https://github.com/DKilkenny) | integrated |
| [009](POEM_009.md) | setup/configure API Changes | [Rob Falck](https://github.com/robfalck) | rejected |
| [010](POEM_010.md) | add argument `recordable` to options.declare | [Rob Falck](https://github.com/robfalck) | integrated |
| [011](POEM_011.md) | Expand problem recording options | [Rob Falck](https://github.com/robfalck); [Herb Schilling](https://github.com/hschilling) | integrated |
| [012](POEM_012.md) | Give the user the option to select the LAPACK driver for use in the SVD used in KrigingSurrogate | [Herb Schilling](https://github.com/hschilling) | integrated |
| [013](POEM_013.md) | Unit conversion enhancements | [Rob Falck](https://github.com/robfalck) | integrated |
| [014](POEM_014.md) | Removal of XDSM viewer to be replaced by third-party plugin | [Rob Falck](https://github.com/robfalck) | integrated |
| [015](POEM_015.md) | Automatic creation of IndepVarComp outputs for all unconnected inputs | [justingray](https://github.com/justingray) | integrated |
| [016](POEM_016.md) | Linear algebra components can perform multiple calculations. | [Rob Falck](https://github.com/robfalck) | integrated |
| [017](POEM_017.md) | User can specify units when adding design variables, constraints, and objectives. | [Kenneth-T-Moore](https://github.com/Kenneth-T-Moore) | integrated |
| [018](POEM_018.md) | indices and src_indices can contain slices | [Kenneth-T-Moore](https://github.com/Kenneth-T-Moore) | integrated |
| [019](POEM_019.md) | Random Vectors in Directional Derivatives | [Kevin Jacobson](https://github.com/kejacobson) | integrated |
| [020](POEM_020.md) | KSComp option to automatically add corresponding constraint | [Rob Falck](https://github.com/robfalck) | integrated |
| [021](POEM_021.md) | _post_configure moved to public API | [Rob Falck](https://github.com/robfalck) | rejected |
| [022](POEM_022.md) | POEM 022: Shape inputs/outputs by connection or copy from another component variable | [Josh Anibal](https://github.com/joanibal) | integrated |
| [023](POEM_023.md) | Remove reconfigure code from the current code base | [Bret Naylor](https://github.com/naylor-b) | integrated |
| [024](POEM_024.md) | Calculating ExecComp Jacobian with symbolic derivatives | [Péter Onódi](https://github.com/onodip) | rejected |
| [025](POEM_025.md) | allow GA to seek pareto frontier | [Kenneth-T-Moore](https://github.com/Kenneth-T-Moore) | integrated |
| [026](POEM_026.md) | Remove support for factorial function in ExecComp | [swryan](https://github.com/swryan) | integrated |
| [027](POEM_027.md) | Approximation flag and state tracking | [johnjasa](https://github.com/johnjasa) | integrated |
| [028](POEM_028.md) | check_partials input warnings | Eliot Aretskin-Hariton | rejected |
| [029](POEM_029.md) | Retrieval of IO Variable Metadata | [Bret Naylor](https://github.com/naylor-b) | integrated |
| [030](POEM_030.md) | User Accessible Complex Step | [Justin Gray](https://github.com/justinsgray) | integrated |
| [031](POEM_031.md) | Improved Aitken Relaxation | [justinsgray](https://github.com/justinsgray) | integrated |
| [032](POEM_032.md) | Detailed Driver Scaling Report | justinsgray, Eliot Aretskin-Hariton | integrated |
| [033](POEM_033.md) | Linear Constraints in Check Totals | [justinsgray](https://github.com/justinsgray) | integrated |
| [034](POEM_034.md) | Units library function to simplify units. | [optional real name](https://github.com/Kenneth-T-Moore) | rejected |
| [035](POEM_035.md) | More generalized behavior in promoted inputs. | [robfalck](https://github.com/robfalck) | integrated |
| [036](POEM_036.md) | Serialization of Kriging training weights | [dakror](https://github.com/dakror) | integrated |
| [037](POEM_037.md) | Give list_problem_vars the option to output unscaled variables. | [optional real name](https://github.com/Kenneth-T-Moore) | integrated |
| [038](POEM_038.md) | Raise an error if a user declares a sub-jacobian to have a value of zero. | [Kenneth-T-Moore](https://github.com/Kenneth-T-Moore) | accepted |
| [039](POEM_039.md) | User Function Registration in ExecComp | @justinsgray, @robfalck | integrated |
| [040](POEM_040.md) | Integration with IPython notebooks | [robfalck](https://github.com/robfalck) | integrated |
| [041](POEM_041.md) | Add expressions to ExecComp after instantiation | @robfalck | integrated |
| [042](POEM_042.md) | DOEDriver different number of levels for different DVs. | Péter Onódi | integrated |
| [043](POEM_043.md) | No `src_indices` warning when both components are distributed | [Mark Leader](https://github.com/markleader) | rejected |
| [044](POEM_044.md) | OpenMDAO-Specific Warnings | [robfalck](https://github.com/robfalck) | accepted |
| [045](POEM_045.md) | Promote-as change | [robfalck](https://github.com/robfalck) | rejected |
| [046](POEM_046.md) | Definition of serial and distributed variables | justinsgray, naylor-b, joanibal, anilyildirim, kejacobson | integrated |
| [047](POEM_047.md) | Component I/O independance from Problem Object | Andrew Ellis | integrated |
| [049](POEM_049.md) | Removal of matrix-matrix derivative APIs | justinsgray, naylor-b | accepted |

