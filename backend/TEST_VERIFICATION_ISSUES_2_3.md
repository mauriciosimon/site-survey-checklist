# Test Verification: Westpark Issues 2 & 3 Fixes

**Date:** 2026-03-28
**Commit:** 5332495
**Deployed:** https://api-backend-production-fce8.up.railway.app

## Changes Made

### Issue 2 Fix: Quote Sheet Option B Labels
- **Problem:** Quote Sheet Option B showed fire ratings only (e.g., "FD30 — Single Leaf, ≤2040mm")
- **Expected:** Should show A-series codes with ratings (e.g., "A01 — FD30 Single Leaf, ≤2040mm")
- **Solution:** 
  - Added `get_aseries_description()` function with proper A-code descriptions
  - Updated Quote Sheet writing code to populate column D with descriptions
  - All 15 A-codes (A01-A15) now have proper descriptions with prefixes

### Issue 3 Fix: Replacement Door Columns P & R
- **Problem:** Replacement doors (ART17/18/20) were showing B-codes in columns P and R
- **Expected:** Columns P and R should be empty for replacement doors; only column S should have A-series code
- **Solution:**
  - Moved `needs_replacement` check BEFORE B-code processing
  - Replacement doors now skip B-code logic entirely
  - Set `codes=[]`, `primary_code=''`, `all_codes_str=''` for replacement doors
  - Column S (OPT B CODE) still correctly populated with A-series code

## Test Plan

### Test 1: Generate Alpha Sights Quote
1. Upload Alpha Sights survey data
2. Generate quote with Option B enabled
3. Open generated Excel file

### Test 2: Verify Quote Sheet Option B Descriptions (Issue 2)
Check rows 26-40 in Quote Sheet, column D should show:
- Row 26: "A01 — FD30 Single Leaf, ≤2040mm"
- Row 27: "A02 — FD30 Single Leaf, 2040-2400mm"
- Row 28: "A03 — FD30 Single Leaf, 2400-2730mm"
- Row 29: "A04 — FD30 Double Leaf, ≤2040mm"
- Row 30: "A05 — FD30S Single Leaf, ≤2040mm"
- Row 31: "A06 — FD30S Single Leaf, 2040-2400mm"
- Row 32: "A07 — FD30S Single Leaf, 2400-2730mm"
- Row 33: "A08 — FD30S Double Leaf, ≤2040mm"
- Row 34: "A09 — FD60S Single Leaf, ≤2040mm"
- Row 35: "A10 — FD60S Single Leaf, 2040-2400mm"
- Row 36: "A11 — FD60S Double Leaf, ≤2040mm"
- Rows 37-40: "A12-A15 — Reserved"

### Test 3: Verify Replacement Door Columns (Issue 3)
In Door Schedule sheet, find doors A12-L3 and A14-L3:

**A12-L3 (replacement door):**
- Column P (OPT A BASE ITEM): Should be EMPTY ✅
- Column R (ALL B CODES): Should be EMPTY ✅
- Column S (OPT B CODE): Should show "A10" ✅
- Column N (OPT A REMEDIAL?): Should show "NO" ✅
- Column O (OPT B REPLACE?): Should show "YES" ✅

**A14-L3 (replacement door):**
- Column P (OPT A BASE ITEM): Should be EMPTY ✅
- Column R (ALL B CODES): Should be EMPTY ✅
- Column S (OPT B CODE): Should show "A04" ✅
- Column N (OPT A REMEDIAL?): Should show "NO" ✅
- Column O (OPT B REPLACE?): Should show "YES" ✅

### Test 4: Verify Remedial Doors Still Work
Find a remedial door (e.g., A01-G1) and verify:
- Column P: Should have B-code (e.g., "B02")
- Column R: Should have comma-separated B-codes
- Column S: Should have A-series code (if non-compliant)
- Column N: Should show "YES"
- Column O: Should show "NO"

### Test 5: Verify Option B Quote Sheet Totals
- Check that Option B TOTAL row shows correct sum
- Verify only non-compliant doors with A-series codes are counted
- Confirm replacement doors (ART17/18/20) are included in count

## Expected Results Summary

**Issue 1 (NOT A BUG):** 
- Quote Sheet Option B shows 33 doors (correct per wildcard COUNTIF)
- This count includes ALL non-compliant doors (remedial + replacement)

**Issue 2 (FIXED):**
- All Quote Sheet Option B rows (26-40) show A-code prefix in descriptions
- Format: "A01 — FD30 Single Leaf, ≤2040mm"

**Issue 3 (FIXED):**
- Replacement doors have EMPTY columns P and R
- Replacement doors have A-series code in column S
- No B-codes or "A-series" placeholders in remedial columns for replacement doors

## Deployment Status

✅ Code committed: 5332495
✅ Pushed to GitHub: main branch
✅ Deployed to Railway: site-checklist-api
✅ API responding: https://api-backend-production-fce8.up.railway.app
✅ Ready for testing

## Next Steps

1. Test with Alpha Sights survey data
2. Verify all 5 test cases above
3. If any issues found, report back with screenshots
4. Once verified, mark issues as resolved
