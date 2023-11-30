
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
| [002](POEM_002.md) | New capability for user to send a termination signal to an OpenMDAO process so that SNOPT in pyoptsparse can terminate cleanly. | [Ken Moore](https://github.com/Kenneth-T-Moore) | integrated |
| [003](POEM_003.md) | Allowing addition of I/O during Configure | [Anil Yildirim](https://github.com/anilyil); [Justin Gray](https://github.com/justinsgray); [Rob Falck](https://github.com/robfalck) | integrated |
| [004](POEM_004.md) | Creating Interpolant Class For 1D Splines | [Danny Kilkenny](https://github.com/DKilkenny) | integrated |
| [005](POEM_005.md) | An OpenMDAO Plugin System | [Bret Naylor](https://github.com/naylor-b) | integrated |
| [006](POEM_006.md) | Re-work the user experience in the N2 diagram | [Herb Schilling](https://github.com/hschilling) | integrated |
| [007](POEM_007.md) | String Compatibility for ExternalCodeComp and ExternalCodeImplicitComp Command Options | [Danny Kilkenny](https://github.com/DKilkenny) | integrated |
| [008](POEM_008.md) | Nonlinear Solver Refactor | [Danny Kilkenny](https://github.com/DKilkenny) | integrated |
| [009](POEM_009.md) | setup/configure API Changes | [Rob Falck](https://github.com/robfalck) | rejected |
| [010](POEM_010.md) | add argument `recordable` to options.declare | [Rob Falck](https://github.com/robfalck) | integrated |
| [011](POEM_011.md) | Expand problem recording options | [Rob Falck](https://github.com/robfalck); [Herb Schilling](https://github.com/hschilling) | integrated |
| [012](POEM_012.md) | Give the user the option to select the LAPACK driver for use in the SVD used in KrigingSurrogate | [Herb Schilling](https://github.com/hschilling) | integrated |
| [013](POEM_013.md) | Unit conversion enhancements | [Rob Falck](https://github.com/robfalck) | integrated |
| [014](POEM_014.md) | Removal of XDSM viewer to be replaced by third-party plugin | [Rob Falck](https://github.com/robfalck) | integrated |
| [015](POEM_015.md) | Automatic creation of IndepVarComp outputs for all unconnected inputs | [Justin Gray](https://github.com/justingray) | integrated |
| [016](POEM_016.md) | Linear algebra components can perform multiple calculations. | [Rob Falck](https://github.com/robfalck) | integrated |
| [017](POEM_017.md) | User can specify units when adding design variables, constraints, and objectives. | [Ken Moore](https://github.com/Kenneth-T-Moore) | integrated |
| [018](POEM_018.md) | indices and src_indices can contain slices | [Ken Moore](https://github.com/Kenneth-T-Moore) | integrated |
| [019](POEM_019.md) | Random Vectors in Directional Derivatives | [Kevin Jacobson](https://github.com/kejacobson) | integrated |
| [020](POEM_020.md) | KSComp option to automatically add corresponding constraint | [Rob Falck](https://github.com/robfalck) | integrated |
| [021](POEM_021.md) | _post_configure moved to public API | [Rob Falck](https://github.com/robfalck) | rejected |
| [022](POEM_022.md) | POEM 022: Shape inputs/outputs by connection or copy from another component variable | [Josh Anibal](https://github.com/joanibal) | integrated |
| [023](POEM_023.md) | Remove reconfigure code from the current code base | [Bret Naylor](https://github.com/naylor-b) | integrated |
| [024](POEM_024.md) | Calculating ExecComp Jacobian with symbolic derivatives | [Péter Onódi](https://github.com/onodip) | rejected |
| [025](POEM_025.md) | allow GA to seek pareto frontier | [Ken Moore](https://github.com/Kenneth-T-Moore) | integrated |
| [026](POEM_026.md) | Remove support for factorial function in ExecComp | [Steve Ryan](https://github.com/swryan) | integrated |
| [027](POEM_027.md) | Approximation flag and state tracking | [John Jasa](https://github.com/johnjasa) | integrated |
| [028](POEM_028.md) | check_partials input warnings | [Eliot Aretskin-Hariton](https://github.com/ehariton) | rejected |
| [029](POEM_029.md) | Retrieval of IO Variable Metadata | [Bret Naylor](https://github.com/naylor-b) | integrated |
| [030](POEM_030.md) | User Accessible Complex Step | [Justin Gray](https://github.com/justinsgray) | integrated |
| [031](POEM_031.md) | Improved Aitken Relaxation | [justinsgray](https://github.com/justinsgray) | integrated |
| [032](POEM_032.md) | Detailed Driver Scaling Report | [Justin Gray](https://github.com/justinsgray) | integrated |
| [033](POEM_033.md) | Linear Constraints in Check Totals | [justinsgray](https://github.com/justinsgray) | integrated |
| [034](POEM_034.md) | Units library function to simplify units. | [Ken Moore](https://github.com/Kenneth-T-Moore) | rejected |
| [035](POEM_035.md) | More generalized behavior in promoted inputs. | [Rob Falck](https://github.com/robfalck) | integrated |
| [036](POEM_036.md) | Serialization of Kriging training weights | [dakror](https://github.com/dakror) | integrated |
| [037](POEM_037.md) | Give list_problem_vars the option to output unscaled variables. | [optional real name](https://github.com/Kenneth-T-Moore) | integrated |
| [038](POEM_038.md) | Raise an error if a user declares a sub-jacobian to have a value of zero. | [Kenneth-T-Moore](https://github.com/Kenneth-T-Moore) | accepted |
| [039](POEM_039.md) | User Function Registration in ExecComp | [Justin Gray](https://github.com/justinsgray) | integrated |
| [040](POEM_040.md) | Integration with IPython notebooks | [robfalck](https://github.com/robfalck) | integrated |
| [041](POEM_041.md) | Add expressions to ExecComp after instantiation | [robfalck](https://github.com/robfalck) | integrated |
| [042](POEM_042.md) | DOEDriver different number of levels for different DVs. | [Péter Onódi](https://github.com/onodip) | integrated |
| [043](POEM_043.md) | No `src_indices` warning when both components are distributed | [Mark Leader](https://github.com/markleader) | rejected |
| [044](POEM_044.md) | OpenMDAO-Specific Warnings | [Rob Falck](https://github.com/robfalck) | integrated |
| [045](POEM_045.md) | Promote-as change | [robfalck](https://github.com/robfalck) | rejected |
| [046](POEM_046.md) | Definition of serial and distributed variables | justinsgray, naylor-b, joanibal, anilyildirim, kejacobson | integrated |
| [047](POEM_047.md) | Component I/O independance from Problem Object | Andrew Ellis | integrated |
| [048](POEM_048.md) | Semistructured Training Data for MetaModel | [justinsgray](https://github.com/justinsgray) | integrated |
| [049](POEM_049.md) | Removal of matrix-matrix derivative APIs | justinsgray, naylor-b | integrated |
| [050](POEM_050.md) | Fix val/value inconsistency in the API | [robfalck](https://github.com/robfalck) | integrated |
| [051](POEM_051.md) | Modifications to relative step sizing in finite difference | [Ken Moore](https://github.com/Kenneth-T-Moore) | integrated |
| [052](POEM_052.md) | Function based component definition for OpenMDAO | justinsgray, Ben Margolis, Kenny Lyons | rejected |
| [053](POEM_053.md) | Make src_indices behave in the same way as indices applied to a normal numpy array | naylor-b, swryan | integrated |
| [054](POEM_054.md) | Specifying source array as flat or non-flat when setting src_indices or dv or constraint indices | [naylor-b](https://github.com/naylor-b) | integrated |
| [055](POEM_055.md) | Min/Max Variable Print Option for Arrays | Andrew Ellis | integrated |
| [056](POEM_056.md) | Function based API usable by OpenMDAO and others | Bret Naylor | integrated |
| [057](POEM_057.md) | OpenMDAO function based components | Bret Naylor | integrated |
| [058](POEM_058.md) | Fixed grid interpolation methods | [Kenneth-T-Moore](https://github.com/Kenneth-T-Moore) | integrated |
| [059](POEM_059.md) | Unitless And Percentage Based Units | Andrew Ellis | integrated |
| [060](POEM_060.md) | Reports | [robfalck](https://github.com/robfalck) | integrated |
| [061](POEM_061.md) | The `openmdao:allow_desvar` tag | @robfalck | integrated |
| [062](POEM_062.md) | Stricter Option Naming | @naylor-b | integrated |
| [063](POEM_063.md) | Allow multiple responses on a single variable | @robfalck | integrated |
| [064](POEM_064.md) | Simple Caching for Matrix-Free Derivative APIs | jsgray | rejected |
| [065](POEM_065.md) | Add a 'proc_group' option to add_subsystem | @naylor-b | integrated |
| [066](POEM_066.md) | Adopt NEP29 | @robfalck | integrated |
| [067](POEM_067.md) | Add a method to Vector to compute a hash. | @naylor-b | integrated |
| [068](POEM_068.md) | Nonlinear Solver System Output Caching | [Andrew Lamkin](https://github.com/lamkina) | integrated |
| [069](POEM_069.md) | Declare residual names for implicit components | [Josh Anibal](https://github.com/joanibal) | integrated |
| [070](POEM_070.md) | Inputs report | @robfalck | integrated |
| [071](POEM_071.md) | POEM_071 - Change ExecComp to use `declare_coloring` | [Rob Falck](https://github.com/robfalck) | integrated |
| [072](POEM_072.md) | Add ability to modify bounds and scaling of implicit outputs and optimizer variables after creation. | [Rob Falck](https://github.com/robfalck) | integrated |
| [073](POEM_073.md) | Add ability for DOEDriver to compute and record total derivatives. | [Tucker Babcock](https://github.com/tuckerbabcock) | integrated |
| [074](POEM_074.md) | Suggest variables close in name on failed connection attempt | [Josh Anibal](https://github.com/joanibal) | integrated |
| [075](POEM_075.md) | Convention for distributed/serial variables and when to allreduce | [Kevin Jacobson](https://github.com/kejacobson) | integrated |
| [076](POEM_076.md) | Directional total derivative checks | [Kevin Jacobson](https://github.com/kejacobson) | integrated |
| [077](POEM_077.md) | Derivative checks with multiple step sizes | [Kevin Jacobson](https://github.com/kejacobson) | integrated |
| [078](POEM_078.md) | Add ability to filter inputs to only those that are connected to IndepVarComp. | [Rob Falck](https://github.com/robfalck) | integrated |
| [079](POEM_079.md) | Raise exception if the initial design point exceeds bounds. | [Rob Falck](https://github.com/robfalck) | integrated |
| [080](POEM_080.md) | Add an activation function to the standard component set. | [Rob Falck](https://github.com/robfalck) | rejected |
| [081](POEM_081.md) | Add Submodel Component to standard component set. | [Nate Steffen](https://github.com/nsteffen) | integrated |
| [082](POEM_082.md) | Add ability to easily retrieve all independent variables within a Problem. | [Rob Falck](https://github.com/robfalck) | integrated |
| [083](POEM_083.md) | Specifying order when adding a subsystem | [Rob Falck](https://github.com/robfalck) | rejected |
| [084](POEM_084.md) | Add a set of jax functions and documentation on using jax with OpenMDAO. | [Rob Falck](https://github.com/robfalck) | integrated |
| [085](POEM_085.md) | Export view_connections to csv | [Carl Recine](https://github.com/crecine) | integrated |
| [086](POEM_086.md) | Top-level setting of system options. | [Rob Falck](https://github.com/robfalck) | integrated |
| [087](POEM_087.md) | Expand functionality of dynamic shaping. | [Bret Naylor](https://github.com/naylor-b) | integrated |
| [088](POEM_088.md) | User-configurable load_case functionality. | [Rob Falck](https://github.com/robfalck) | integrated |
| [089](POEM_089.md) | Optimization efficiency improvements (relevance reduction revisited). | [Rob Falck](https://github.com/robfalck) | integrated |
| [090](POEM_090.md) | Auto ordering of Group subsystems. | [Bret Naylor](https://github.com/naylor-b) | integrated |
| [091](POEM_091.md) | Eliminate combined jacobian-based and matrix free capability in a single component. | [Bret Naylor](https://github.com/naylor-b) | integrated |
| [092](POEM_092.md) | User-defined function hook for pre-processing option set. | [Ken Moore](https://github.com/Kenneth-T-Moore) | integrated |

