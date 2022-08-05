# Standard Python modules
import sys

# External modules
import openmdao.api as om
import pycycle.api as pyc


class HBTF(pyc.Cycle):
    def initialize(self):
        super().initialize()

    def setup(self):
        # Setup the problem by including all the relavant components here - comp, burner, turbine etc

        # Create any relavent short hands here:
        design = self.options["design"]

        if self.options["thermo_method"] == "TABULAR":
            self.options["thermo_data"] = pyc.AIR_JETA_TAB_SPEC
            FUEL_TYPE = "FAR"
        else:
            self.options["thermo_method"] = "CEA"
            self.options["thermo_data"] = pyc.species_data.janaf
            FUEL_TYPE = "Jet-A(g)"

        self.add_subsystem("fc", pyc.FlightConditions())
        self.add_subsystem("inlet", pyc.Inlet())

        self.add_subsystem(
            "fan",
            pyc.Compressor(map_data=pyc.FanMap, bleed_names=[], map_extrap=True),
            promotes_inputs=[("Nmech", "LP_Nmech")],
        )
        self.add_subsystem("splitter", pyc.Splitter())
        self.add_subsystem("duct4", pyc.Duct())
        self.add_subsystem(
            "lpc", pyc.Compressor(map_data=pyc.LPCMap, map_extrap=True), promotes_inputs=[("Nmech", "LP_Nmech")]
        )
        self.add_subsystem("duct6", pyc.Duct())
        self.add_subsystem(
            "hpc",
            pyc.Compressor(map_data=pyc.HPCMap, bleed_names=["cool1", "cool2", "cust"], map_extrap=True),
            promotes_inputs=[("Nmech", "HP_Nmech")],
        )
        self.add_subsystem("bld3", pyc.BleedOut(bleed_names=["cool3", "cool4"]))
        self.add_subsystem("burner", pyc.Combustor(fuel_type=FUEL_TYPE))
        self.add_subsystem(
            "hpt",
            pyc.Turbine(map_data=pyc.HPTMap, bleed_names=["cool3", "cool4"], map_extrap=True),
            promotes_inputs=[("Nmech", "HP_Nmech")],
        )
        self.add_subsystem("duct11", pyc.Duct())
        self.add_subsystem(
            "lpt",
            pyc.Turbine(map_data=pyc.LPTMap, bleed_names=["cool1", "cool2"], map_extrap=True),
            promotes_inputs=[("Nmech", "LP_Nmech")],
        )
        self.add_subsystem("duct13", pyc.Duct())
        self.add_subsystem("core_nozz", pyc.Nozzle(nozzType="CV", lossCoef="Cv"))

        self.add_subsystem("byp_bld", pyc.BleedOut(bleed_names=["bypBld"]))
        self.add_subsystem("duct15", pyc.Duct())
        self.add_subsystem("byp_nozz", pyc.Nozzle(nozzType="CV", lossCoef="Cv"))

        # Create shaft instances. Note that LP shaft has 3 ports! => no gearbox
        self.add_subsystem("lp_shaft", pyc.Shaft(num_ports=3), promotes_inputs=[("Nmech", "LP_Nmech")])
        self.add_subsystem("hp_shaft", pyc.Shaft(num_ports=2), promotes_inputs=[("Nmech", "HP_Nmech")])
        self.add_subsystem("perf", pyc.Performance(num_nozzles=2, num_burners=1))

        # Connect the inputs to perf group
        self.connect("inlet.Fl_O:tot:P", "perf.Pt2")
        self.connect("hpc.Fl_O:tot:P", "perf.Pt3")
        self.connect("burner.Wfuel", "perf.Wfuel_0")
        self.connect("inlet.F_ram", "perf.ram_drag")
        self.connect("core_nozz.Fg", "perf.Fg_0")
        self.connect("byp_nozz.Fg", "perf.Fg_1")

        # LP-shaft connections
        self.connect("fan.trq", "lp_shaft.trq_0")
        self.connect("lpc.trq", "lp_shaft.trq_1")
        self.connect("lpt.trq", "lp_shaft.trq_2")
        # HP-shaft connections
        self.connect("hpc.trq", "hp_shaft.trq_0")
        self.connect("hpt.trq", "hp_shaft.trq_1")
        # Ideally expanding flow by conneting flight condition static pressure to nozzle exhaust pressure
        self.connect("fc.Fl_O:stat:P", "core_nozz.Ps_exhaust")
        self.connect("fc.Fl_O:stat:P", "byp_nozz.Ps_exhaust")

        # Create a balance component
        # Balances can be a bit confusing, here's some explanation -
        #   State Variables:
        #           (W)        Inlet mass flow rate to implictly balance thrust
        #                      LHS: perf.Fn  == RHS: Thrust requirement (set when TF is instantiated)
        #
        #           (FAR)      Fuel-air ratio to balance Tt4
        #                      LHS: burner.Fl_O:tot:T  == RHS: Tt4 target (set when TF is instantiated)
        #
        #           (lpt_PR)   LPT press ratio to balance shaft power on the low spool
        #           (hpt_PR)   HPT press ratio to balance shaft power on the high spool

        balance = self.add_subsystem("balance", om.BalanceComp())
        if design:
            balance.add_balance("W", eq_units="lbf", units="lbm/s", val=400.0)
            self.connect("balance.W", "fc.W")
            self.connect("perf.Fn", "balance.lhs:W")

            balance.add_balance("FAR", eq_units="degR", lower=1e-4, val=0.017)
            self.connect("balance.FAR", "burner.Fl_I:FAR")
            self.connect("burner.Fl_O:tot:T", "balance.lhs:FAR")
            self.promotes("balance", inputs=[("rhs:FAR", "T4_MAX")])

            # Note that for the following two balances the mult val is set to -1 so that the NET torque is zero
            balance.add_balance("lpt_PR", val=1.5, eq_units="hp", use_mult=True, mult_val=-1)
            self.connect("balance.lpt_PR", "lpt.PR")
            self.connect("lp_shaft.pwr_in_real", "balance.lhs:lpt_PR")
            self.connect("lp_shaft.pwr_out_real", "balance.rhs:lpt_PR")

            balance.add_balance("hpt_PR", val=1.5, lower=1.001, upper=8, eq_units="hp", use_mult=True, mult_val=-1)
            self.connect("balance.hpt_PR", "hpt.PR")
            self.connect("hp_shaft.pwr_in_real", "balance.lhs:hpt_PR")
            self.connect("hp_shaft.pwr_out_real", "balance.rhs:hpt_PR")

            balance.add_balance("hpc_PR", val=7.0, units=None, eq_units=None)
            self.connect("balance.hpc_PR", "hpc.PR")
            self.connect("perf.OPR", "balance.lhs:hpc_PR")

        else:

            # In OFF-DESIGN mode we need to redefine the balances:
            #   State Variables:
            #           (W)        Inlet mass flow rate to balance core flow area
            #                      LHS: core_nozz.Throat:stat:area == Area from DESIGN calculation
            #
            #           (FAR)      Fuel-air ratio to balance Thrust req.
            #                      LHS: perf.Fn  == RHS: Thrust requirement (set when TF is instantiated)
            #
            #           (BPR)      Bypass ratio to balance byp. noz. area
            #                      LHS: byp_nozz.Throat:stat:area == Area from DESIGN calculation
            #
            #           (lp_Nmech)   LP spool speed to balance shaft power on the low spool
            #           (hp_Nmech)   HP spool speed to balance shaft power on the high spool

            balance.add_balance("FAR", val=0.017, lower=1e-4, eq_units="degR")
            self.connect("balance.FAR", "burner.Fl_I:FAR")
            self.connect("burner.Fl_O:tot:T", "balance.lhs:FAR")

            balance.add_balance("W", units="lbm/s", lower=10.0, upper=2000.0, eq_units="inch**2")
            self.connect("balance.W", "fc.W")
            self.connect("core_nozz.Throat:stat:area", "balance.lhs:W")

            balance.add_balance("BPR", lower=2.0, upper=20.0, eq_units="inch**2")
            self.connect("balance.BPR", "splitter.BPR")
            self.connect("byp_nozz.Throat:stat:area", "balance.lhs:BPR")

            # Again for the following two balances the mult val is set to -1 so that the NET torque is zero
            balance.add_balance(
                "lp_Nmech", val=1.5, units="rpm", lower=500.0, eq_units="hp", use_mult=True, mult_val=-1
            )
            self.connect("balance.lp_Nmech", "LP_Nmech")
            self.connect("lp_shaft.pwr_in_real", "balance.lhs:lp_Nmech")
            self.connect("lp_shaft.pwr_out_real", "balance.rhs:lp_Nmech")

            balance.add_balance(
                "hp_Nmech", val=1.5, units="rpm", lower=500.0, eq_units="hp", use_mult=True, mult_val=-1
            )
            self.connect("balance.hp_Nmech", "HP_Nmech")
            self.connect("hp_shaft.pwr_in_real", "balance.lhs:hp_Nmech")
            self.connect("hp_shaft.pwr_out_real", "balance.rhs:hp_Nmech")

        self.add_subsystem(
            "fan_dia",
            om.ExecComp(
                "FanDia = 2.0*(area/(pi*(1.0-hub_tip**2.0)))**0.5",
                area={"val": 7000.0, "units": "inch**2"},
                hub_tip={"val": 0.3125, "units": None},
                FanDia={"val": 100.0, "units": "inch"},
            ),
        )
        self.connect("inlet.Fl_O:stat:area", "fan_dia.area")

        # Set up all the flow connections:
        self.pyc_connect_flow("fc.Fl_O", "inlet.Fl_I")
        self.pyc_connect_flow("inlet.Fl_O", "fan.Fl_I")
        self.pyc_connect_flow("fan.Fl_O", "splitter.Fl_I")
        self.pyc_connect_flow("splitter.Fl_O1", "duct4.Fl_I")
        self.pyc_connect_flow("duct4.Fl_O", "lpc.Fl_I")
        self.pyc_connect_flow("lpc.Fl_O", "duct6.Fl_I")
        self.pyc_connect_flow("duct6.Fl_O", "hpc.Fl_I")
        self.pyc_connect_flow("hpc.Fl_O", "bld3.Fl_I")
        self.pyc_connect_flow("bld3.Fl_O", "burner.Fl_I")
        self.pyc_connect_flow("burner.Fl_O", "hpt.Fl_I")
        self.pyc_connect_flow("hpt.Fl_O", "duct11.Fl_I")
        self.pyc_connect_flow("duct11.Fl_O", "lpt.Fl_I")
        self.pyc_connect_flow("lpt.Fl_O", "duct13.Fl_I")
        self.pyc_connect_flow("duct13.Fl_O", "core_nozz.Fl_I")
        self.pyc_connect_flow("splitter.Fl_O2", "byp_bld.Fl_I")
        self.pyc_connect_flow("byp_bld.Fl_O", "duct15.Fl_I")
        self.pyc_connect_flow("duct15.Fl_O", "byp_nozz.Fl_I")

        # Bleed flows:
        self.pyc_connect_flow("hpc.cool1", "lpt.cool1", connect_stat=False)
        self.pyc_connect_flow("hpc.cool2", "lpt.cool2", connect_stat=False)
        self.pyc_connect_flow("bld3.cool3", "hpt.cool3", connect_stat=False)
        self.pyc_connect_flow("bld3.cool4", "hpt.cool4", connect_stat=False)

        # Specify solver settings:
        newton = self.nonlinear_solver = om.NewtonSolver()
        newton.options["atol"] = 1e-8

        # set this very small, so it never activates and we rely on atol
        newton.options["rtol"] = 1e-99
        newton.options["iprint"] = 2
        newton.options["maxiter"] = 10
        newton.options["solve_subsystems"] = True
        newton.options["max_sub_solves"] = 10
        newton.options["reraise_child_analysiserror"] = False
        newton.options["restart_from_successful"] = True
        newton.options["err_on_non_converge"] = True
        ls = newton.linesearch = om.ArmijoGoldsteinLS()
        ls.options["maxiter"] = 3
        ls.options["rho"] = 0.75

        self.linear_solver = om.DirectSolver()

        super().setup()


def viewer(prob, pt, file=sys.stdout):
    """
    print a report of all the relevant cycle properties
    """

    summary_data = (
        prob[pt + ".fc.Fl_O:stat:MN"],
        prob[pt + ".fc.alt"],
        prob[pt + ".inlet.Fl_O:stat:W"],
        prob[pt + ".perf.Fn"],
        prob[pt + ".perf.Fg"],
        prob[pt + ".inlet.F_ram"],
        prob[pt + ".perf.OPR"],
        prob[pt + ".perf.TSFC"],
        prob[pt + ".splitter.BPR"],
    )

    print(file=file, flush=True)
    print(file=file, flush=True)
    print(file=file, flush=True)
    print("----------------------------------------------------------------------------", file=file, flush=True)
    print("                              POINT:", pt, file=file, flush=True)
    print("----------------------------------------------------------------------------", file=file, flush=True)
    print("                       PERFORMANCE CHARACTERISTICS", file=file, flush=True)
    print("    Mach      Alt       W      Fn      Fg    Fram     OPR     TSFC      BPR ", file=file, flush=True)
    print(" %7.5f  %7.1f %7.3f %7.1f %7.1f %7.1f %7.3f  %7.5f  %7.3f" % summary_data, file=file, flush=True)

    fs_names = [
        "fc.Fl_O",
        "inlet.Fl_O",
        "fan.Fl_O",
        "splitter.Fl_O1",
        "splitter.Fl_O2",
        "duct4.Fl_O",
        "lpc.Fl_O",
        "duct6.Fl_O",
        "hpc.Fl_O",
        "bld3.Fl_O",
        "burner.Fl_O",
        "hpt.Fl_O",
        "duct11.Fl_O",
        "lpt.Fl_O",
        "duct13.Fl_O",
        "core_nozz.Fl_O",
        "byp_bld.Fl_O",
        "duct15.Fl_O",
        "byp_nozz.Fl_O",
    ]
    fs_full_names = [f"{pt}.{fs}" for fs in fs_names]
    pyc.print_flow_station(prob, fs_full_names, file=file)

    comp_names = ["fan", "lpc", "hpc"]
    comp_full_names = [f"{pt}.{c}" for c in comp_names]
    pyc.print_compressor(prob, comp_full_names, file=file)

    pyc.print_burner(prob, [f"{pt}.burner"], file=file)

    turb_names = ["hpt", "lpt"]
    turb_full_names = [f"{pt}.{t}" for t in turb_names]
    pyc.print_turbine(prob, turb_full_names, file=file)

    noz_names = ["core_nozz", "byp_nozz"]
    noz_full_names = [f"{pt}.{n}" for n in noz_names]
    pyc.print_nozzle(prob, noz_full_names, file=file)

    shaft_names = ["hp_shaft", "lp_shaft"]
    shaft_full_names = [f"{pt}.{s}" for s in shaft_names]
    pyc.print_shaft(prob, shaft_full_names, file=file)

    bleed_names = ["hpc", "bld3", "byp_bld"]
    bleed_full_names = [f"{pt}.{b}" for b in bleed_names]
    pyc.print_bleed(prob, bleed_full_names, file=file)


class MPhbtf(pyc.MPCycle):
    def setup(self):

        self.pyc_add_pnt("TOC", HBTF(thermo_method="TABULAR"))  # Create an instace of the High Bypass ratio Turbofan

        # --- Setup TOC point ---
        self.set_input_defaults("TOC.inlet.MN", 0.751)
        self.set_input_defaults("TOC.fan.MN", 0.6)
        self.set_input_defaults("TOC.splitter.BPR", 10.0)
        self.set_input_defaults("TOC.splitter.MN1", 0.45)
        self.set_input_defaults("TOC.splitter.MN2", 0.4518)
        self.set_input_defaults("TOC.duct4.MN", 0.45)
        self.set_input_defaults("TOC.lpc.MN", 0.45)
        self.set_input_defaults("TOC.duct6.MN", 0.3563)
        self.set_input_defaults("TOC.hpc.MN", 0.2442)
        self.set_input_defaults("TOC.bld3.MN", 0.3000)
        self.set_input_defaults("TOC.burner.MN", 0.1025)
        self.set_input_defaults("TOC.hpt.MN", 0.3650)
        self.set_input_defaults("TOC.duct11.MN", 0.3063)
        self.set_input_defaults("TOC.lpt.MN", 0.4127)
        self.set_input_defaults("TOC.duct13.MN", 0.4463)
        self.set_input_defaults("TOC.byp_bld.MN", 0.4489)
        self.set_input_defaults("TOC.duct15.MN", 0.4589)
        self.set_input_defaults("TOC.LP_Nmech", 4666.1, units="rpm")
        self.set_input_defaults("TOC.HP_Nmech", 14705.7, units="rpm")

        # --- Set up bleed values -----
        self.pyc_add_cycle_param("inlet.ram_recovery", 0.9990)
        self.pyc_add_cycle_param("duct4.dPqP", 0.0048)
        self.pyc_add_cycle_param("duct6.dPqP", 0.0101)
        self.pyc_add_cycle_param("burner.dPqP", 0.0540)
        self.pyc_add_cycle_param("duct11.dPqP", 0.0051)
        self.pyc_add_cycle_param("duct13.dPqP", 0.0107)
        self.pyc_add_cycle_param("duct15.dPqP", 0.0149)
        self.pyc_add_cycle_param("core_nozz.Cv", 0.9933)
        self.pyc_add_cycle_param("byp_bld.bypBld:frac_W", 0.005)
        self.pyc_add_cycle_param("byp_nozz.Cv", 0.9939)
        self.pyc_add_cycle_param("hpc.cool1:frac_W", 0.050708)
        self.pyc_add_cycle_param("hpc.cool1:frac_P", 0.5)
        self.pyc_add_cycle_param("hpc.cool1:frac_work", 0.5)
        self.pyc_add_cycle_param("hpc.cool2:frac_W", 0.020274)
        self.pyc_add_cycle_param("hpc.cool2:frac_P", 0.55)
        self.pyc_add_cycle_param("hpc.cool2:frac_work", 0.5)
        self.pyc_add_cycle_param("bld3.cool3:frac_W", 0.067214)
        self.pyc_add_cycle_param("bld3.cool4:frac_W", 0.101256)
        self.pyc_add_cycle_param("hpc.cust:frac_P", 0.5)
        self.pyc_add_cycle_param("hpc.cust:frac_work", 0.5)
        self.pyc_add_cycle_param("hpc.cust:frac_W", 0.0445)
        self.pyc_add_cycle_param("hpt.cool3:frac_P", 1.0)
        self.pyc_add_cycle_param("hpt.cool4:frac_P", 0.0)
        self.pyc_add_cycle_param("lpt.cool1:frac_P", 1.0)
        self.pyc_add_cycle_param("lpt.cool2:frac_P", 0.0)
        self.pyc_add_cycle_param("hp_shaft.HPX", 250.0, units="hp")

        super().setup()


if __name__ == "__main__":

    prob = om.Problem()
    model = prob.model = MPhbtf()

    prob.setup()

    # --- Design point inputs ---
    prob.set_val("TOC.fan.PR", 1.4)
    prob.set_val("TOC.fan.eff", 0.9)
    prob.set_val("TOC.lpc.PR", 1.935)
    prob.set_val("TOC.lpc.eff", 0.9243)
    prob.set_val("TOC.hpc.eff", 0.8707)
    prob.set_val("TOC.hpt.eff", 0.8888)
    prob.set_val("TOC.lpt.eff", 0.8996)
    prob.set_val("TOC.fc.alt", 37000.0, units="ft")
    prob.set_val("TOC.fc.MN", 0.78)
    prob.set_val("TOC.T4_MAX", 2850.0, units="degR")
    prob.set_val("TOC.splitter.BPR", 10.0)

    prob.set_val("TOC.balance.rhs:hpc_PR", 25.0)
    prob.set_val("TOC.balance.rhs:W", 6000.0, units="lbf")

    # --- Design point initial guesses ---
    prob["TOC.balance.FAR"] = 0.025

    prob.set_solver_print(level=-1)
    prob.set_solver_print(level=2, depth=2)

    prob.run_model()

    prob.set_val("TOC.splitter.BPR", -1.0)
    try:
        prob.model.TOC.nonlinear_solver.options["maxiter"] = 3
        prob.run_model()
    except om.AnalysisError:
        prob.set_val("TOC.splitter.BPR", 7.0)
        prob.model.TOC.nonlinear_solver.options["maxiter"] = 15
        prob.run_model()

        print(prob["TOC.T4_MAX"])
