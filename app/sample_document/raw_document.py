raw_documents = [
    {
        "type": "claim_form",
        "content": (
            "Claimant: John A. Doe. Date of Birth: March 15 1988. "
            "Policy ID: POLICY-456. Claimant ID: USER-123. "
            "Phone: +1 (555) 204-7891. Email: john.doe@email.com. "
            "Address: 14 Crescent Drive Houston TX 77001. Licence: TX-DL-994827. "
            "Vehicle: 2019 Toyota Camry SE. VIN: 1HGBH41JXMN109186. Plate: HOU-4492-TX. Mileage: 54320. "
            "Incident date: June 7 2026. Time: 14:35 CST. "
            "Location: I-610 W Loop northbound near Exit 18A Houston TX. "
            "Claim type: collision rear-end impact. Weather: clear dry. "
            "Other party: Jane Smith. Other vehicle: 2021 Honda Civic plate TX-9912-AB. "
            "Description: claimant was driving northbound on I-610 W Loop when other vehicle failed to "
            "brake and struck the rear of insured vehicle at estimated 35 mph. No injuries reported."
        ),
    },
    {
        "type": "police_report",
        "content": (
            "Report number: HPD-2026-061407. Agency: Houston Police Department. "
            "Report date: June 7 2026. Filing date: June 8 2026. "
            "Officer: Sgt. Marcus L. Webb. Badge: HPD-3847. Precinct: HPD District 4. "
            "Party 1: John A. Doe. Licence TX-DL-994827. Vehicle: 2019 Toyota Camry HOU-4492-TX. "
            "Party 2: Jane Smith. Licence TX-DL-778312. Vehicle: 2021 Honda Civic TX-9912-AB. "
            "Narrative: officers responded at 14:35 hours to two-vehicle collision on I-610 W Loop "
            "northbound near Exit 18A. Vehicle 2 driver stated unable to stop due to traffic deceleration. "
            "No injuries reported by either party. Both drivers cooperative. "
            "Violation cited: failure to maintain safe following distance TX TRC 545.062. "
            "Party cited: Jane Smith Vehicle 2. Contributory fault: Vehicle 2 100 percent. "
            "Road conditions: dry clear visibility. Estimated speed at impact: 35 mph."
        ),
    },
    {
        "type": "repair_invoice",
        "content": (
            "Shop: Elite Auto Body and Collision. Licence: TX-AB-20194. "
            "Address: 2201 Westheimer Rd Houston TX. Phone: 713-555-0192. "
            "Invoice number: EAB-2026-00891. Invoice date: June 9 2026. "
            "Vehicle: 2019 Toyota Camry SE. VIN: 1HGBH41JXMN109186. "
            "Line items: "
            "rear bumper assembly OEM replacement qty 1 unit price 620.00 total 620.00. "
            "rear quarter panel repair and repaint qty 2 unit price 480.00 total 960.00. "
            "trunk lid realignment and seal replacement qty 1 unit price 210.00 total 210.00. "
            "left tail light assembly OEM replacement qty 1 unit price 185.00 total 185.00. "
            "body labour 14 hours at 95 per hour total 1330.00. "
            "paint materials primer and consumables qty 1 total 175.00. "
            "subtotal 3480.00. tax 8.25 percent 287.10. total claimed 3767.10. "
            "Warranty: 12 months parts lifetime paintwork defects."
        ),
    },
    {
        "type": "damage_photos",
        "content": (
            "Photo 1 rear bumper primary impact zone: significant deformation across full width of rear bumper "
            "with deep crease approximately 40cm wide. Paint transfer consistent with silver vehicle. "
            "Photo 2 rear left quarter panel: dent approximately 15cm diameter with paint scraping. "
            "Photo 3 rear right quarter panel: minor scrape and paint loss near tail light housing. "
            "Photo 4 trunk lid: misalignment of approximately 2cm on left hinge visible from top view. "
            "Photo 5 interior driver area: airbag intact not deployed dashboard warning lights active. "
            "Photo 6 full vehicle driver side overview: rear damage visible no damage to front or sides."
        ),
    },
]