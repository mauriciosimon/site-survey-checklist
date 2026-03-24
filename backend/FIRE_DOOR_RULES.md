# Fire Door Quoting - Business Logic Rules

**Version:** 1.0  
**Last Updated:** 2026-03-24  
**Owner:** Westpark Fire Safety

## Overview

This document defines the complete extraction, mapping, and output rules for the Fire Door Quoting system. All changes to business logic MUST be documented here.

---

## 1. Survey Types

### Type 1 (PDF Format)
- **Source:** FireDNA, RiskBase, BM TRADA surveys
- **Format:** PDF text files
- **Key Feature:** Contains ART (Asset Remedial Tracking) codes
- **Fire Strategy:** Always included (complete survey)
- **Option B Pricing:** ALWAYS available (not PENDING)

### Type 2 (Excel Format)
- **Source:** Manual Excel surveys
- **Format:** `.xlsx` or `.xls`
- **Key Feature:** Fault text descriptions (no ART codes)
- **Fire Strategy:** NOT included
- **Option B Pricing:** PENDING (requires fire strategy drawings)

---

## 2. Door ID Rules

### Type 1 (PDF)
- **Rule:** Door IDs MUST include floor suffix
- **Format:** `{ID}-{FLOOR}` (e.g., `A01-L2`, `A02-L3`)
- **Reason:** Multiple floors may have same door numbers
- **Example:**
  ```
  Floor 2: A01-L2, A02-L2, A03-L2
  Floor 3: A01-L3, A02-L3, A03-L3
  ```

### Type 2 (Excel)
- **Rule:** Use door IDs exactly as they appear in the survey
- **Format:** Typically numeric (e.g., `1`, `2`, `3`) or alphanumeric
- **No suffix required** (Excel surveys typically use unique IDs)

---

## 3. Fire Rating Extraction

### Type 1 (PDF)
- **Required Field:** Fire rating is MANDATORY for every door
- **Valid Values:**
  - FD30 (30-minute fire door)
  - FD30S (30-minute with smoke seals)
  - FD60 (60-minute fire door)
  - FD90 (90-minute fire door)
  - FD120 (120-minute fire door)
  - Nominal (non-fire-rated door)
  - Unknown (ONLY if truly missing from source)
  
- **Extraction Source:** 
  - Look for explicit "Fire Rating:" field
  - Parse from door description
  - Check compliance status text
  
- **Validation:** If ALL doors show "Unknown", extraction is failing

### Type 2 (Excel)
- **Fire Rating:** May be in separate column or embedded in description
- **Fallback:** If not present, mark as "Unknown"

---

## 4. ART Code → B-Code Mapping

### Type 1 (PDF with ART Codes)
**Source:** `BMTrada_ART_Codes_RateCard_Mapping.csv`

**Mapping Logic:**
1. Extract ART codes from PDF (e.g., ART01, ART02)
2. Map to WestPark B-codes via CSV lookup
3. If ART code not in CSV, log warning and skip

**Complete ART → B-Code Mappings (from BMTrada_ART_Codes_RateCard_Mapping.csv):**
- **ART01** → B11 (Hardwood re-lip — min density 640kg/m3)
- **ART02** → B12 (Hardwood timber insert per void/hole)
- **ART03** → B06 (Fire-stop frame-to-wall gap — intumescent mastic / ablative batt)
- **ART04** → B01 / B10 (B01 if gap issue requires seals; B10 if alignment issue)
- **ART05** → B03 (Replace overhead door closer — CE-marked BS EN 1154)
- **ART06** → B10 (Adjust / re-hang door leaf)
- **ART07** → B10 (Adjust / re-hang door leaf — address moisture cause first)
- **ART08** → B04 (Replace / fix hinge set — BS EN 1935 Grade 11)
- **ART09** → B10 (Adjust / re-hang door leaf)
- **ART10** → B05 (Replace lever handles / latch / lock — CE-marked ironmongery)
- **ART11** → B01 / B02 (B01 if smoke seals required; B02 if intumescent only)
- **ART12** → B05 (Replace lever handles / latch set — CE-marked ironmongery)
- **ART13** → B04 (Replace / fix hinge set — check screws vs full hinge replacement)
- **ART14** → **NO EQUIVALENT** — Damaged glazing. Flag door for manual review (see Section 4.1)
- **ART15** → B11 (Same repair as ART01 — hardwood re-lip)
- **ART16** → B06 (Fire-stop frame-to-wall gap)
- **ART17** → Replacement required (see Section 6 - Option B)
- **ART18** → Replacement required (see Section 6 - Option B)
- **ART19** → B07 (Add / replace fire door signage — 2 signs per leaf)
- **ART20** → Replacement required (see Section 6 - Option B)
- **ART21** → B06 (Fire-stop / refit architrave)
- **ART22** → B01 (Supply & fit intumescent + smoke seals)
- **ART23** → **FLAG FOR MANUAL REVIEW** — No applicable repair technique (see Section 4.2)
- **ART24** → Reserved / not in published list

### 4.1 Special Case: ART14 (Damaged Glazing)
**Rule:** ART14 has no B-code equivalent in the current rate card.

**Action:**
1. Do NOT auto-price this door in Option A
2. Flag the door in Notes column: "ART14 - Damaged glazing - Manual review required"
3. Mark Opt A as "NO" (manual pricing needed)

**Reason:** Gap in rate card — may require new B13 line item for glazing repairs.

### 4.2 Special Case: ART23 (No Applicable Repair Technique)
**Rule:** ART23 means damage is present but no accepted repair technique exists. Door likely needs replacement.

**Action:**
1. Do NOT auto-price this door in Option A or Option B
2. Flag the door in Notes column: "ART23 - No repair technique - Manual review required"
3. Mark both Opt A and Opt B as "NO"
4. Recommend manual inspection and quote

### 4.3 Multiple B-Codes Per Door (Type 1)
**Rule:** When a Type 1 door has multiple ART codes mapping to different B-codes:

**Priority for Column P (Primary B-Code):**
Use this priority order to select the single B-code for Quote Sheet formulas:
1. **B01** (seals) — highest priority
2. **B03** (closer)
3. **B04** (hinges)
4. **B10** (adjust/rehang)
5. **B05** (latch/handles)
6. **B02** (intumescent only)
7. **B06** (fire-stopping)
8. **B07** (signage)
9. **B11** (lipping)
10. **B12** (void infill)

**Column K (Action Description):**
List ALL applicable B-codes as a comma-separated list.

**Example:**
- Door has ART11 (B01/B02), ART05 (B03), ART08 (B04)
- Column P (Primary): B01 (highest priority)
- Column K: "B01, B03, B04"

### Type 2 (Excel with Fault Text)
**Source:** `map_fault_to_bcode()` function

**Mapping Rules:**
1. **Seals (B01):**
   - "seal" + ("coming away" OR "worn" OR "damaged" OR "missing" OR "not fitted")
   - Examples: "seals worn", "smoke seal damaged", "seals not fitted"

2. **Intumescent Only (B02):**
   - "intumescent" + NOT "smoke"
   - Example: "intumescent strip damaged"

3. **Self-Closing (B03):**
   - "closing" + NOT ("not closing" OR "not catching")
   - "closer" + any variation
   - Example: "door not closing properly"

4. **Hinges (B04):**
   - "hinge" OR "hinges"
   - Example: "hinges loose"

5. **Latch/Handles (B05):**
   - "latch" OR "handle" OR "lock"
   - Example: "latch not catching"

6. **Fire-Stopping (B06):**
   - "fire stop" OR "fire-stop" OR "firestopping"
   - Example: "inadequate fire-stopping"

7. **Signage (B07):**
   - "sign" OR "signage"
   - Example: "fire door sign missing"

8. **Hold-Open Devices (B08):**
   - "perco" OR "hold open" OR "hold-open"
   - Example: "Perco chains installed"

9. **Door Lipping (B11):**
   - "lipping" OR "re-lip"
   - Example: "door requires re-lipping"

10. **Adjust/Rehang (B10):**
    - "catching" OR "not catching" OR "adjust" OR "rehang"
    - Example: "door catching on floor"

11. **Void Infill (B12):**
    - "void" OR "hollow"
    - Example: "door leaf void requires infill"

**Priority Order (when multiple codes match):**
1. B01 (seals) — highest priority
2. B03 (closer)
3. B04 (hinges)
4. B10 (adjust/rehang)
5. Other codes

---

## 5. Option A (Remedial Works)

### Calculation Logic
1. Count doors with `Opt A = YES` in Door Schedule
2. Group by B-code (Base Item)
3. Calculate: `QTY × RATE = TOTAL` for each B-code
4. Write numbers directly (not formulas) to Quote Sheet

### Quote Sheet Structure
- **Rows 11-22:** Individual B-code line items (A.01–A.12)
- **Row 23:** Option A TOTAL (SUM of rows 11-22)
- **Columns:**
  - C: QTY (number)
  - E: RATE (number from Rate Card)
  - F: TOTAL (number = QTY × RATE)

### Client Summary
- **C10:** NET COST (Option A total)
- **D10:** OPTION A TOTAL (same as C10)
- **D13:** TOTAL INVESTMENT (sum of all options)

**Critical:** All three cells MUST be numbers (not formulas) to display immediately in Excel.

---

## 6. Option B (Full Replacement)

### Type 1 (PDF) - ALWAYS PRICED
**Rule:** Option B MUST be priced based on fire rating and leaf configuration

**B-Series Codes (Replacement Doors) - from WestPark Rate Card:**
- **B.01:** FD30 — Single Leaf, Paint Grade, Height up to 2040mm
- **B.02:** FD30 — Single Leaf, Paint Grade, Height 2040–2400mm
- **B.03:** FD30 — Single Leaf, Paint Grade, Height 2400–2730mm
- **B.04:** FD30 — Double Leaf, Paint Grade, Height up to 2040mm
- **B.05:** FD30S — Single Leaf, Paint Grade + Smoke Seals, Height up to 2040mm
- **B.06:** FD30S — Single Leaf, Paint Grade + Smoke Seals, Height 2040–2400mm
- **B.07:** FD30S — Single Leaf, Paint Grade + Smoke Seals, Height 2400–2730mm
- **B.08:** FD30S — Double Leaf, Paint Grade + Smoke Seals, Height up to 2040mm
- **B.09:** FD60S — Single Leaf, Paint Grade + Smoke Seals, Height up to 2040mm
- **B.10:** FD60S — Single Leaf, Paint Grade + Smoke Seals, Height 2040–2400mm
- **B.11:** FD60S — Double Leaf, Paint Grade + Smoke Seals, Height up to 2040mm
- **B.12:** E/O Hardwood Veneer Finish (per door)
- **B.13:** E/O External Grade Specification (per door)
- **B.14:** E/O Fire-Rated Vision Panel up to 300 x 600mm
- **B.15:** E/O Fire-Rated Vision Panel over 300 x 600mm

**Note:** B.12-B.15 are "E/O" (Extra Over) items added to base door codes.

**Pricing Logic:**
1. Extract fire rating from survey (FD30, FD30S, FD60S, etc.)
2. Extract leaf configuration (single/double)
3. Extract height (≤2040, 2040–2400, 2400–2730)
4. Map to corresponding B-series replacement code (B.01–B.15)
5. Calculate: `QTY × RATE = TOTAL`

**Example:**
- 5 doors: FD30, single leaf, 2100mm height
- Code: B.02 (FD30 — Single Leaf, Paint Grade, Height 2040–2400mm)
- Rate: £450 per door (from Rate Card)
- Total: 5 × £450 = £2,250

### Type 2 (Excel) - PENDING
**Rule:** Option B shows "PENDING — fire strategy required"

**Reason:** Type 2 surveys lack fire strategy drawings needed to specify replacement doors

**Output:**
- Quote Sheet rows 26–40: All zeros or blank
- Client Summary E11: "PENDING — fire strategy required"
- UI Message: Display warning after download (see Type 2 Survey Notice)

---

## 7. COMPLIANT Logic

**Rule:** Door is COMPLIANT only if it has NO codes AND NO faults

**Logic:**
```python
if not codes and not faults:
    status = "COMPLIANT"
else:
    status = "YES" if needs_remedial else "NO"
```

**Common Mistake:** Using OR instead of AND
- ❌ Wrong: `not codes or not faults` (too permissive)
- ✅ Correct: `not codes and not faults` (strict)

---

## 8. Excel Output Requirements

### Quote Sheet
1. **Header Fields (rows 2–6):**
   - B2: Quote Ref (WP-2026-XXX)
   - B3: Date (DD/MM/YYYY format)
   - B4: Client name
   - B5: Site (blank for Type 2)
   - B6: Building (blank for Type 2)

2. **Line Items (rows 11–22):**
   - Write calculated NUMBERS (not formulas)
   - QTY, RATE, TOTAL all numeric

3. **Option A TOTAL (row 23):**
   - F23 = calculated number (SUM of rows 11–22)

### Client Summary
1. **Header Fields:**
   - B3: Client (copied from Quote Sheet B4)
   - B4: Site (copied from Quote Sheet B5)
   - B5: Building (copied from Quote Sheet B6)
   - E6: Date (copied from Quote Sheet B3)
   - B7: Quote Ref (copied from Quote Sheet B2)

2. **Totals (rows 10, 13):**
   - C10: NET COST (Option A total)
   - D10: OPTION A TOTAL
   - E11: OPTION B TOTAL (or "PENDING" for Type 2)
   - D13: TOTAL INVESTMENT

**Critical:** Write numbers, not formulas. Excel cached values issue.

### Door Schedule
1. **Column Mapping:**
   - A: Door ID (with floor suffix for Type 1)
   - B: Location
   - C–I: Door details (type, rating, config, size, finish, seals, closer)
   - N: Opt A (YES/NO/COMPLIANT)
   - O: Opt B (YES/NO)
   - P: Base Item (B-code for Quote Sheet formulas)

2. **Color Coding:**
   - Green (COMPLIANT): No faults, no remedial work needed
   - Yellow (YES): Faults found, remedial work needed
   - Red (NO): Unable to inspect or critical issues

---

## 9. Type 2 Survey Notice

**When:** User generates quote from Type 2 survey (Excel format)

**Where:** Frontend UI, below download button

**Message:**
> ⚠️ Option B (full replacement) could not be priced — fire strategy drawings were not included in this survey. To unlock Option B pricing, ask the client for their fire strategy drawings and forward to the estimating team.

**Implementation:**
- Backend: Set `X-Survey-Type: TYPE_2` header in response
- Frontend: Read header and conditionally show message

---

## 10. Validation Rules

### Pre-Processing Checks
1. **File Format:**
   - Valid: .pdf, .xlsx, .xls, .txt
   - Invalid: All others → HTTP 400

2. **Client Name:**
   - Required field
   - Must be non-empty string
   - Used in output filename and headers

3. **Door Data:**
   - Minimum 1 door required
   - Maximum ~200 doors (practical limit)

### Post-Extraction Checks
1. **Fire Rating (Type 1 only):**
   - If ALL doors show "Unknown", log ERROR
   - Check extraction logic

2. **Option B Pricing (Type 1 only):**
   - If 0 replacement doors but survey shows faults, log WARNING
   - Verify Opt B column logic

3. **Totals:**
   - If Option A total = £0 but faults exist, log ERROR
   - Check B-code mapping and rate lookup

---

## 11. Rate Card Management

### Database Priority
1. **Primary Source:** PostgreSQL database (rate_card_items table)
2. **Fallback:** CSV file if database unavailable
3. **Admin:** Users can edit prices via /rates endpoint

### Rate Structure
- **ART Code:** BMTrada standard code for repairs (ART01, ART02... ART24)
- **B-Code (Remedial):** WestPark internal code for repairs (B01-B12)
  - Maps from ART codes via CSV
  - Used in Option A (remedial works)
- **B-Code (Replacement):** WestPark replacement door codes (B.01–B.15)
  - Used in Option B (full replacement)
  - Note: Different from remedial B-codes despite similar naming
- **Quote Sheet Labels:** 
  - Option A rows use "A.01"–"A.12" labels (corresponds to B01-B12 remedial codes)
  - Option B rows use "B.01"–"B.15" labels (replacement door codes)
- **Unit Price:** £ per item/door

---

## 12. Compliance Notes

### Type 1 Compliance Note
```
This report identifies fire doors requiring remedial works to achieve compliance with Approved Document B and the Regulatory Reform (Fire Safety) Order 2005. Works are categorized as Option A (remedial works) or Option B (full replacement). All prices exclude VAT and are subject to site survey confirmation.
```

### Type 2 Compliance Note
```
This report identifies fire doors requiring remedial works based on visual inspection. Option A provides remedial works to address identified faults. Option B (full replacement) cannot be priced without fire strategy drawings - please request these from the client if replacement doors are required. All prices exclude VAT and are subject to site survey confirmation.
```

**Rule:** Use the correct note based on survey type. Do not mix Type 1 and Type 2 language.

---

## 13. Known Issues & Fixes

### Issue: Excel Shows £0 on Open
- **Cause:** openpyxl cannot reliably set cached formula values
- **Solution:** Write calculated numbers directly (not formulas)
- **Affected Cells:** Quote Sheet totals, Client Summary totals

### Issue: Duplicate Door IDs
- **Cause:** Multiple floors with same numbering (A01, A02...)
- **Solution:** Add floor suffix to Door ID (A01-L2, A01-L3)
- **Type:** Type 1 surveys only

### Issue: Ghost Rows from Previous Extraction
- **Cause:** Template not fully cleared before population
- **Solution:** Clear extended range (A–V) in Door Schedule before writing

---

## 14. Change Log

### 2026-03-24
- Created initial FIRE_DOOR_RULES.md
- Documented all extraction, mapping, and output rules
- Added Type 1 vs Type 2 differentiation
- Added Option B pricing rules
- Added validation and compliance notes
- Added known issues section

---

## 15. Maintenance

**When to Update This File:**
- Any change to extraction logic
- New B-code or A-code added
- New fault text pattern
- Change to validation rules
- Change to output format
- Bug fix that affects business logic

**Review Frequency:** Monthly or after major changes

**Approval Required:** Mauricio Lopez (owner)

---

*End of FIRE_DOOR_RULES.md*
