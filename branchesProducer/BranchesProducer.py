from coffea import processor
import awkward as ak
import numpy as np
import sys

sys.path.append("../utilities/")
import nameUtilities as nameutl
import coffeaUtilities as cfutl
import awkwardArrayUtilities as akutl
import PtEtaPhiMLorentzVectorUtilities as vecutl
import physicsUtilities as phutl
import variablesComputation.awkwardArray.jetVariables as jetvars
import variablesComputation.awkwardArray.eventVariables as evtvars


def get_met(events, met_collection_name="MET"):
    """Get met collection.

    Args:
        events (awkward.Array): the Events TTree opened with uproot.
        jet_type (str): AK4 or AK8

    Returns:
        awkward.Array: ak array with field pt, eta, phi, mass,
            that can be used as a coffea PtEtaPhiMLorentzVector.
    """

    met_branch = eval("events." + met_collection_name)

    met = ak.zip(
        {
            "pt"    : met_branch.pt,
            "mass"  : ak.zeros_like(met_branch.pt),
            "eta"   : ak.zeros_like(met_branch.pt),
            "phi"   : met_branch.phi,
        },
        with_name="PtEtaPhiMLorentzVector",
    )

    return met


def get_jets(events, jet_type):
    """Get jet collection for a given jet type.

    Args:
        events (awkward.Array): the Events TTree opened with uproot.
        jet_type (str): AK4 or AK8

    Returns:
        awkward.Array: ak array with field pt, eta, phi, mass,
            that can be used as a coffea PtEtaPhiMLorentzVector.
    """

    jet_collection = nameutl.jet_algo_name_to_jet_collection_name(jet_type)
    jet_branch = eval("events." + jet_collection)

    jets = ak.zip(
        {
            "pt"    : jet_branch.pt,
            "mass"  : jet_branch.mass,
            "eta"   : jet_branch.eta,
            "phi"   : jet_branch.phi,
        },
        with_name="PtEtaPhiMLorentzVector",
    )

    jets = ak.with_field(jets, vecutl.momentum(jets), where="momentum")

    return jets


def get_pf_cands(events, jet_type):
    """Get jet pf candidates collection for a given jet type.

    Args:
        events (awkward.Array): the Events TTree opened with uproot.
        jet_type (str): AK4 or AK8

    Returns:
        awkward.Array: ak array with field jetIdx, pt, eta, phi, mass,
            charge and pdgId that can be used as a coffea
            PtEtaPhiMLorentzVector.
    """

    # For now a quick and dirty hack to switch between 102X and 106X
    # Will be obsolete when using only 106X

    ## For 102X
    if jet_type == "AK8":
        jet_pf_cands = events.FatJetPFCands
    else:
        jet_pf_cands = events.JetPFCands
    pf_cands = ak.zip(
        {
            "jetIdx": jet_pf_cands.jetIdx,
            "pt"    : jet_pf_cands.pt,
            "mass"  : jet_pf_cands.mass,
            "eta"   : jet_pf_cands.eta,
            "phi"   : jet_pf_cands.phi,
            "charge": jet_pf_cands.charge,
            "pdgId" : jet_pf_cands.pdgId,
        },
        with_name="PtEtaPhiMLorentzVector",
    )
    
    ## For 106X
    #jet_pf_cands_idx_info = eval("events.JetPFCands"+jet_type)
    #jet_pf_cands = events.JetPFCands[jet_pf_cands_idx_info.candIdx]
    #pf_cands = ak.zip(
    #    {
    #        "jetIdx": jet_pf_cands_idx_info.jetIdx,
    #        "pt"    : jet_pf_cands.pt,
    #        "mass"  : jet_pf_cands.mass,
    #        "eta"   : jet_pf_cands.eta,
    #        "phi"   : jet_pf_cands.phi,
    #        "charge": jet_pf_cands.charge,
    #        "pdgId" : jet_pf_cands.pdgId,
    #    },
    #    with_name="PtEtaPhiMLorentzVector",
    #)

    pf_cands = ak.with_field(pf_cands, vecutl.rapidity(pf_cands), where="rapidity")

    return pf_cands


def get_collection_size(events, collection):
    return ak.count(getattr(events, collection).pt, axis=1)


class BranchesProducer(processor.ProcessorABC):
    """Processor for computing new branches to be added to a new ROOT file.

    The class must implement the following methods:
        * __init__: Define the branches to be computed
        * process: Calculation of the new quantities and accumulation into
                   the branches.
    """


    def __init__(self):
        """Define the branches to be computed.

        New branches to be computed are defined in the class attribute
        _accumulator (coffea.processor.dict_accumulator).

        Args:
            None
        
        Returns:
            None
        """

        self.jet_types = ["AK4", "AK8"]  # capitals used because capitals are used in PFNanoAOD

        ## Define accumulator
        #  By using dict_accumulator, the branches type do not have to be defined
        self._accumulator = processor.dict_accumulator({})


    @property
    def accumulator(self):
        return self._accumulator


    def process(self, events):
        """Compute new quantities to be added to the ROOT NTuple.

        Args:
            events (awkward.Array): the Events TTree opened with uproot.

        Returns:
            coffea.processor.dict_accumulator
        """

        ## Define accumulator
        output = self.accumulator.identity()

        output["genWeight"] = cfutl.accumulate(events.genWeight)

        met = get_met(events, "MET")

        for jet_type in self.jet_types:

            jet_collection = nameutl.jet_algo_name_to_jet_collection_name(jet_type)

            jets = get_jets(events, jet_type)
            jet_pf_cands = get_pf_cands(events, jet_type)
            njets = get_collection_size(events, jet_collection)
            sum_pfcands_pt = jetvars.calculate_sum_pfcands_pt(jet_pf_cands, jagged=False)

            output["n" + jet_collection] = cfutl.accumulate(njets)
            output[jet_collection + "_ptD"] = cfutl.accumulate(jetvars.calculate_ptD(jet_pf_cands))
            output[jet_collection + "_girth"] = cfutl.accumulate(jetvars.calculate_girth(jet_pf_cands, jets, njets=njets))
            axis_major, axis_minor, axis_avg = jetvars.calculate_axes(jet_pf_cands, jets, njets=njets)
            output[jet_collection + "_axisMajor"] = cfutl.accumulate(axis_major)
            output[jet_collection + "_axisMinor"] = cfutl.accumulate(axis_minor)
            output[jet_collection + "_axisAvg"] = cfutl.accumulate(axis_avg)

            mr = evtvars.calculate_razor_MR(jets, njets=njets)
            mrt = evtvars.calculate_razor_MRT(jets, met, njets=njets)
            output["RazorMR_" + jet_collection] = cfutl.accumulate(mr)
            output["RazorMRT_" + jet_collection] = cfutl.accumulate(mrt)
            output["RazorR_" + jet_collection] = cfutl.accumulate(evtvars.calculate_razor_R(mr, mrt))

            if jet_type == "AK8":

                output[jet_collection + "_chHEF"] = cfutl.accumulate(jetvars.calculate_chHEF(jet_pf_cands, jets, njets=njets))
                output[jet_collection + "_neHEF"] = cfutl.accumulate(jetvars.calculate_neHEF(jet_pf_cands, jets, njets=njets))

                beta = 1
                e2b1 = jetvars.calculate_ecf_e2(jet_pf_cands, beta, sum_pfcands_pt=sum_pfcands_pt)
                #e3b1 = jetvars.calculate_ecfs_e3(jet_pf_cands, beta, sum_pfcands_pt=sum_pfcands_pt, calculate_ecfgs=False)
                v1e3b1, v2e3b1, e3b1 = jetvars.calculate_ecfs_e3(jet_pf_cands, beta, sum_pfcands_pt=sum_pfcands_pt, calculate_ecfgs=True)
                #e4b1 = jetvars.calculate_ecfs_e4(jet_pf_cands, beta, sum_pfcands_pt=sum_pfcands_pt, calculate_ecfgs=False)
                v1e4b1, v2e4b1, v3e4b1, v4e4b1, v5e4b1, e4b1 = jetvars.calculate_ecfs_e4(jet_pf_cands, beta, sum_pfcands_pt=sum_pfcands_pt, calculate_ecfgs=True)
                output[jet_collection + "_e2b1"] = cfutl.accumulate(e2b1)
                output[jet_collection + "_v1e3b1"] = cfutl.accumulate(v1e3b1)
                output[jet_collection + "_v2e3b1"] = cfutl.accumulate(v2e3b1)
                output[jet_collection + "_e3b1"] = cfutl.accumulate(e3b1)
                output[jet_collection + "_v1e4b1"] = cfutl.accumulate(v1e4b1)
                output[jet_collection + "_v2e4b1"] = cfutl.accumulate(v2e4b1)
                output[jet_collection + "_v3e4b1"] = cfutl.accumulate(v3e4b1)
                output[jet_collection + "_v4e4b1"] = cfutl.accumulate(v4e4b1)
                output[jet_collection + "_v5e4b1"] = cfutl.accumulate(v5e4b1)
                output[jet_collection + "_e4b1"] = cfutl.accumulate(e4b1)
                output[jet_collection + "_c2b1"] = cfutl.accumulate(jetvars.calculate_ecf_c(1., e2b1, e3b1))
                output[jet_collection + "_d2b1"] = cfutl.accumulate(jetvars.calculate_ecf_d(1., e2b1, e3b1))
                output[jet_collection + "_m2b1"] = cfutl.accumulate(jetvars.calculate_ecf_m(e2b1, v1e3b1))
                output[jet_collection + "_n2b1"] = cfutl.accumulate(jetvars.calculate_ecf_n(e2b1, v2e3b1))

                efp_degree = 6
                efps = jetvars.calculate_efps(jet_pf_cands, efp_degree)
                # Not storing EFP0, which is always 1, on purpose
                for idx, efp in enumerate(efps[1:]):
                    output[jet_collection + "_efp%dd%d" %(idx+1, efp_degree)] = cfutl.accumulate(efp)

        return output


    def postprocess(self, accumulator):
        return accumulator

