import pandas as pd
import pickle
from src.dataframe_functions import *
from src.yolk_functions import *
from src.sprayer import Sprayer
sprayer = Sprayer()

import warnings
warnings.filterwarnings("ignore", category=RuntimeWarning)

# Load Input Data

print(sprayer.dye("### Loading Data... ###", "OKCYAN"))

manifesto_path = 'data/manifesto/MPDataset_MPDS2025a_stata14.dta'
manifesto = pd.read_stata(manifesto_path,convert_categoricals=False, convert_missing=False)

paged_path = 'data/paged/PAGED-basic.csv'
paged = pd.read_csv(paged_path)

paged_party_path = 'data/paged/REPDEM-Basic-party-dataset.csv'
paged_party = pd.read_csv(paged_party_path)

# Choose Cases

cases = ["Austria", "Belgium", "Denmark", "Finland", "France", "Germany", "Greece", "Iceland", "Ireland", "Italy", "Luxembourg", "Netherlands", "Norway", "Portugal", "Spain", "Sweden", "Switzerland", "United Kingdom"]

print(sprayer.dye("### Searching Data by Cases... ###", "OKCYAN"))
print("Manifesto: ", end="")
manifesto_case_selection = choose_cases(manifesto, "countryname", cases=cases)
print("PAGED: ", end="")
paged_case_selection = choose_cases(paged, "country_name", cases=cases)

# Define variable to measure ideological stance of a party

state_variables = ["per401", "per402", "per407", "per410", "per414", "per505", "per507", "per702"]
market_variables = ["per403", "per404", "per405", "per406", "per409", "per412", "per413", "per415", "per504", "per506", "per701"]

progressive_variables = ["per601", "per603", "per605", "per608", "per704"]
conservative_variables = ["per201", "per202", "per503", "per602", "per604" , "per607"]

# Build the dict

print(sprayer.dye("### Building Dict... ###", "OKCYAN"))

accuracy = 0.1
parliament_bib = {}

for n, (index, row) in enumerate(paged_case_selection.iterrows()):
    country = row.country_name
    election_date = pd.to_datetime(row.elecdate)

    print("Progress: " + f"{n}/{paged_case_selection.shape[1]} " + sprayer.dye(f"({round(n/paged_case_selection.shape[1] * 100, 2)} %) ", "OKCYAN"))
    print(f"Processing: {country}, {election_date.year}")

    print(f"Getting Meta Data...")
    enp = row.enpp
    polarization_rile = row.parl_polar_rile
    polarization_prosser = row.parl_polar_prosser
    bicam = row.inst_bicam
    pos_parl = row.inst_posparl
    seat_share_lp = row.largest_party_share

    minority_cab = row.cab_minority
    minority_formal = row.cab_formal_minority
    cab_date_in = pd.to_datetime(row.date_in)
    cab_date_out = pd.to_datetime(row.date_out)

    args = [country, election_date]
    cols = []
    column_names = ["countryname", "edate"]
    manifesto_country_election = group_it(manifesto_case_selection, args, cols, *column_names)

    try:
        member_manifesto_id = [party for party, seatshare in zip(manifesto_country_election.party, manifesto_country_election.absseat) if seatshare > 0]
        member_names = [party for party, seatshare in zip(manifesto_country_election.partyabbrev, manifesto_country_election.absseat) if seatshare > 0]
    except:
        member_manifesto_id = []
        member_names = []

    cabinet_name = row.cab_name
    try:
        cabinet_member = row.cab_composition1.split(",")
        cabinet_member_paged_id = [int(cmid) for cmid in row.cab_composition2.split(",")]
    except AttributeError:
        cabinet_member = []
        cabinet_member_paged_id = []
            
    cabinet_member_manifesto_id = []
    for pid in cabinet_member_paged_id:
        mid = paged_party[paged_party.party_id == pid].manifesto_id.dropna().unique()
        if len(mid) == 1:
            mid = mid[0]
            cabinet_member_manifesto_id.append(mid)
        # If there is no Manifesto ID matching the PAGED ID, -1 is appended.
        elif len(mid) > 1:
            print(f"PAGED ID {pid} has ambigous Manifesto ID: {mid}. Searching for year specific Manifesto ID...")
            mid_found = False
            for id_ in mid:
                if len(manifesto_country_election) != 0:
                    if id_ in manifesto_country_election.party:
                        cabinet_member_manifesto_id.append(id_)
                        mid_found = True
                        print(f"Manifesto ID found.")
                        break
            if not mid_found:
                print(f"Manifesto ID not found.")
                cabinet_member_manifesto_id.append(-1)
        else:
            print(f"PAGED ID {pid} has no Manifesto ID")
            cabinet_member_manifesto_id.append(-1)
    
    if len(manifesto_country_election) == 0:
        cabinet_eco = []
        cabinet_soc = []
        parliament_eco = []
        parliament_soc = []
        eco_soc_cabinet = None
        yolk_center, yolk_radius = [], 0
        print(sprayer.fail("No Data on Party Stance."))
    else:
        eco = manifesto_country_election[state_variables].sum(axis=1) - manifesto_country_election[market_variables].sum(axis=1)
        eco.index = manifesto_country_election.party
        soc = manifesto_country_election[progressive_variables].sum(axis=1) - manifesto_country_election[conservative_variables].sum(axis=1)
        soc.index = manifesto_country_election.party

        eco = pd.concat([eco, pd.Series({-1:None})])
        soc = pd.concat([soc, pd.Series({-1:None})])
        cabinet_eco = [eco[mid] if mid in eco.index else eco[-1] for mid in cabinet_member_manifesto_id]
        cabinet_soc = [soc[mid] if mid in soc.index else soc[-1] for mid in cabinet_member_manifesto_id]
        parliament_eco = [eco[mid] if mid in eco.index else eco[-1] for mid in member_manifesto_id]
        parliament_soc = [soc[mid] if mid in soc.index else soc[-1] for mid in member_manifesto_id]

        try:
            eco_soc_cabinet = (np.mean(cabinet_eco), np.mean(cabinet_soc))
        except:
            eco_soc_cabinet = None
        
        try:
            print(f"Searching for Yolk with Accuracy {accuracy}...")
            points = [(e,s) for e,s in zip(parliament_eco,parliament_soc)]
            yolk_center, yolk_radius = calculate_yolk(points, accuracy=accuracy)
        except:
            print(sprayer.fail(f"Yolk Calculation Failed."))
            yolk_center, yolk_radius = [], 0

    parliament_bib[index] = {
        "country": country,
        "election_date": election_date,
        "member":{
            "name": member_names,
            "manifesto_id": member_manifesto_id,
            "stance_eco": parliament_eco,
            "stance_soc": parliament_soc
        },
        "enp": enp,
        "polarization": {
            "rile": polarization_rile,
            "prosser": polarization_prosser
        },
        "bicameralism": bicam,
        "positive_parliamentarism": pos_parl,
        "seat_share_largest_party": seat_share_lp,
        "yolk": {
            "center": yolk_center,
            "radius": yolk_radius
        },
        "cabinet": {
            "name": cabinet_name,
            "date_in": cab_date_in,
            "date_out": cab_date_out,
            "minority_cab": minority_cab,
            "minority_formal": minority_formal,
            "member": cabinet_member,
            "paged_id": cabinet_member_paged_id,
            "manifesto_id": cabinet_member_manifesto_id,
            "stance_eco": cabinet_eco,
            "stance_soc": cabinet_soc,
            "eco_soc_mean": eco_soc_cabinet
        }
        }

with open('parliament_bib.pkl', 'wb') as file:
    pickle.dump(parliament_bib, file)